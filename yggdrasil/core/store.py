"""Graph store abstraction and NetworkX in-memory backend.

GraphStore is the single interface all other components use to read/write the graph.
NetworkXGraphStore is the zero-infrastructure default for development and testing.
Swap it for Neo4jGraphStore (yggdrasil/backends/neo4j.py) in production.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any

import networkx as nx

from yggdrasil.core.edges import Edge, EdgeType
from yggdrasil.core.nodes import AnyNode, Node, NodeType, node_from_dict


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class GraphStore(ABC):
    """Async interface for all graph storage backends."""

    @abstractmethod
    async def upsert_node(self, node: Node) -> None:
        """Insert or update a node. Identified by node_id."""

    @abstractmethod
    async def upsert_edge(self, edge: Edge) -> None:
        """Insert or update an edge. Identified by edge_id."""

    @abstractmethod
    async def get_node(self, node_id: str) -> AnyNode | None:
        """Fetch a node by ID, or None if not found."""

    @abstractmethod
    async def get_edge(self, edge_id: str) -> Edge | None:
        """Fetch an edge by ID, or None if not found."""

    @abstractmethod
    async def get_edges(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        direction: str = "out",        # "out" | "in" | "both"
        only_valid: bool = True,
    ) -> list[Edge]:
        """Return edges connected to node_id, optionally filtered by type and direction."""

    @abstractmethod
    async def neighbors(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        depth: int = 1,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        """BFS neighbors of node_id up to `depth` hops, optionally filtered by edge type."""

    @abstractmethod
    async def vector_search(
        self,
        embedding: list[float],
        node_types: list[NodeType] | None = None,
        top_k: int = 10,
        only_valid: bool = True,
    ) -> list[tuple[AnyNode, float]]:
        """Return top_k nodes ranked by cosine similarity to the query embedding."""

    @abstractmethod
    async def delete_node(self, node_id: str) -> None:
        """Hard-delete a node and all its edges."""

    @abstractmethod
    async def delete_edge(self, edge_id: str) -> None:
        """Hard-delete an edge."""

    @abstractmethod
    async def list_nodes(
        self,
        node_type: NodeType | None = None,
        group_id: str | None = None,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        """List nodes, optionally filtered."""

    @abstractmethod
    async def list_edges(
        self,
        edge_type: EdgeType | None = None,
        group_id: str | None = None,
        only_valid: bool = True,
    ) -> list[Edge]:
        """List edges, optionally filtered."""

    # ------------------------------------------------------------------
    # Convenience helpers (implemented in terms of abstract methods)
    # ------------------------------------------------------------------

    async def expire_node(self, node_id: str) -> None:
        """Soft-delete a node by setting invalid_at to now."""
        node = await self.get_node(node_id)
        if node:
            await self.upsert_node(node.expire())

    async def expire_edge(self, edge_id: str) -> None:
        """Soft-delete an edge by setting invalid_at to now."""
        edge = await self.get_edge(edge_id)
        if edge:
            await self.upsert_edge(edge.expire())

    async def attach_context(
        self,
        agent_id: str,
        ctx_id: str,
        weight: float | None = None,
        **kw: Any,
    ) -> Edge:
        """Create a HAS_CONTEXT edge from agent_id → ctx_id.

        If weight is not provided, it is auto-computed as the cosine similarity
        between the agent and context embeddings (falls back to 1.0 when either
        node has no embedding yet).
        """
        if weight is None:
            agent = await self.get_node(agent_id)
            ctx   = await self.get_node(ctx_id)
            if (
                agent is not None
                and ctx is not None
                and agent.embedding
                and ctx.embedding
            ):
                weight = _cosine(_normalize(agent.embedding), ctx.embedding)
            else:
                weight = 1.0
        edge = Edge.has_context(src_id=agent_id, dst_id=ctx_id, weight=weight, **kw)
        await self.upsert_edge(edge)
        return edge

    async def attach_tool(
        self,
        agent_id: str,
        tool_id: str,
        weight: float | None = None,
        **kw: Any,
    ) -> Edge:
        """Create a HAS_TOOL edge from agent_id → tool_id.

        If weight is not provided, it is auto-computed as the cosine similarity
        between the agent and tool embeddings (falls back to 1.0 when either
        node has no embedding yet). This weight is used by semantic_search() as
        a tool-affinity prior: tools that are semantically central to the agent
        score higher when multiple tools have similar query cosine scores.
        """
        if weight is None:
            agent = await self.get_node(agent_id)
            tool  = await self.get_node(tool_id)
            if (
                agent is not None
                and tool is not None
                and agent.embedding
                and tool.embedding
            ):
                weight = _cosine(_normalize(agent.embedding), tool.embedding)
            else:
                weight = 1.0
        edge = Edge.has_tool(src_id=agent_id, dst_id=tool_id, weight=weight, **kw)
        await self.upsert_edge(edge)
        return edge


# ---------------------------------------------------------------------------
# NetworkX in-memory backend
# ---------------------------------------------------------------------------

class NetworkXGraphStore(GraphStore):
    """In-memory graph store backed by a NetworkX MultiDiGraph.

    - Zero infrastructure — no external services required.
    - Nodes stored as typed Pydantic objects in _nodes dict.
    - Edges stored as typed Pydantic objects in _edges dict.
    - NetworkX graph used for topology queries (neighbors, traversal).
    - Vector search via brute-force cosine similarity (use hnswlib at scale).

    Use this for development, testing, and small workloads.
    Switch to Neo4jGraphStore for production.
    """

    def __init__(self) -> None:
        self._g: nx.MultiDiGraph = nx.MultiDiGraph()
        self._nodes: dict[str, AnyNode] = {}
        self._edges: dict[str, Edge] = {}
        self._metadata: dict[str, Any] = {
            "graph_name": "graph",
            "active_graph_revision_id": "",
            "candidate_graph_revision_id": "",
            "active_graph_version": "v1",
            "revisions": {},
            "revision_history": [],
            "replay_status_by_revision": {},
            "replay_results_by_revision": {},
            "metadata": {},
        }

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def upsert_node(self, node: Node) -> None:
        self._nodes[node.node_id] = node  # type: ignore[assignment]
        self._g.add_node(
            node.node_id,
            node_type=node.node_type,
            name=node.name,
            group_id=node.group_id,
        )

    async def upsert_edge(self, edge: Edge) -> None:
        self._edges[edge.edge_id] = edge
        # NetworkX MultiDiGraph allows parallel edges; key=edge_id disambiguates.
        self._g.add_edge(
            edge.src_id,
            edge.dst_id,
            key=edge.edge_id,
            edge_type=edge.edge_type,
            weight=edge.weight,
        )

    async def delete_node(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)
        if self._g.has_node(node_id):
            self._g.remove_node(node_id)

    async def delete_edge(self, edge_id: str) -> None:
        edge = self._edges.pop(edge_id, None)
        if edge and self._g.has_edge(edge.src_id, edge.dst_id, key=edge_id):
            self._g.remove_edge(edge.src_id, edge.dst_id, key=edge_id)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_node(self, node_id: str) -> AnyNode | None:
        return self._nodes.get(node_id)

    async def get_edge(self, edge_id: str) -> Edge | None:
        return self._edges.get(edge_id)

    async def get_edges(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        direction: str = "out",
        only_valid: bool = True,
    ) -> list[Edge]:
        if direction == "out":
            raw = self._g.out_edges(node_id, keys=True)
        elif direction == "in":
            raw = self._g.in_edges(node_id, keys=True)
        else:
            raw = list(self._g.out_edges(node_id, keys=True)) + \
                  list(self._g.in_edges(node_id, keys=True))

        results: list[Edge] = []
        seen: set[str] = set()
        for _src, _dst, key in raw:
            if key in seen:
                continue
            seen.add(key)
            edge = self._edges.get(key)
            if edge is None:
                continue
            if only_valid and not edge.is_valid:
                continue
            if edge_type is not None and edge.edge_type != edge_type:
                continue
            results.append(edge)
        return results

    async def neighbors(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        depth: int = 1,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        visited: set[str] = set()
        frontier: set[str] = {node_id}

        for _ in range(depth):
            next_frontier: set[str] = set()
            for nid in frontier:
                edges = await self.get_edges(nid, edge_type=edge_type, only_valid=only_valid)
                for e in edges:
                    neighbor = e.dst_id if e.src_id == nid else e.src_id
                    if neighbor not in visited and neighbor != node_id:
                        next_frontier.add(neighbor)
            visited.update(frontier)
            frontier = next_frontier

        nodes = []
        for nid in frontier:
            n = self._nodes.get(nid)
            if n and (not only_valid or n.is_valid):
                nodes.append(n)
        return nodes

    async def list_nodes(
        self,
        node_type: NodeType | None = None,
        group_id: str | None = None,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        results = []
        for node in self._nodes.values():
            if only_valid and not node.is_valid:
                continue
            if node_type is not None and node.node_type != node_type:
                continue
            if group_id is not None and node.group_id != group_id:
                continue
            results.append(node)
        return results

    async def list_edges(
        self,
        edge_type: EdgeType | None = None,
        group_id: str | None = None,
        only_valid: bool = True,
    ) -> list[Edge]:
        results = []
        for edge in self._edges.values():
            if only_valid and not edge.is_valid:
                continue
            if edge_type is not None and edge.edge_type != edge_type:
                continue
            if group_id is not None and edge.group_id != group_id:
                continue
            results.append(edge)
        return results

    async def vector_search(
        self,
        embedding: list[float],
        node_types: list[NodeType] | None = None,
        top_k: int = 10,
        only_valid: bool = True,
    ) -> list[tuple[AnyNode, float]]:
        """Brute-force cosine similarity search over nodes with embeddings."""
        q = _normalize(embedding)
        results: list[tuple[AnyNode, float]] = []

        for node in self._nodes.values():
            if only_valid and not node.is_valid:
                continue
            if node_types and node.node_type not in node_types:
                continue
            if not node.embedding:
                continue
            score = _cosine(q, node.embedding)
            results.append((node, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the full store to a JSON-compatible dict."""
        return {
            "metadata": self._metadata,
            "nodes": [n.model_dump(mode="json") for n in self._nodes.values()],
            "edges": [e.model_dump(mode="json") for e in self._edges.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NetworkXGraphStore":
        """Restore a store from a serialised dict."""
        store = cls()
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            for nd in data.get("nodes", []):
                loop.run_until_complete(store.upsert_node(node_from_dict(nd)))
            for ed in data.get("edges", []):
                loop.run_until_complete(store.upsert_edge(Edge.model_validate(ed)))
            if "metadata" in data and isinstance(data["metadata"], dict):
                store._metadata = dict(data["metadata"])
        finally:
            loop.close()
        return store

    def get_metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        self._metadata = dict(metadata)


# ---------------------------------------------------------------------------
# Vector math helpers
# ---------------------------------------------------------------------------

def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    b_norm = _normalize(b)
    return sum(ai * bi for ai, bi in zip(a, b_norm))
