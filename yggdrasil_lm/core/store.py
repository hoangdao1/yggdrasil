#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xbbf7bceb

# Compiled with Coconut version 3.2.0

"""Graph store abstraction and NetworkX in-memory backend.

GraphStore is the single interface all other components use to read/write the graph.
NetworkXGraphStore is the zero-infrastructure default for development and testing.
Swap it for Neo4jGraphStore (yggdrasil/backends/neo4j.py) in production.
"""

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
_coconut_header_info = ('3.2.0', '311', False)
_coconut_cached__coconut__ = _coconut_sys.modules.get('__coconut__')
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.dirname(_coconut_os.path.abspath(__file__)))
_coconut_pop_path = False
if _coconut_cached__coconut__ is None or getattr(_coconut_cached__coconut__, "_coconut_header_info", None) != _coconut_header_info and _coconut_os.path.dirname(_coconut_cached__coconut__.__file__ or "") != _coconut_file_dir:  # type: ignore
    if _coconut_cached__coconut__ is not None:
        _coconut_sys.modules['_coconut_cached__coconut__'] = _coconut_cached__coconut__
        del _coconut_sys.modules['__coconut__']
    _coconut_sys.path.insert(0, _coconut_file_dir)
    _coconut_pop_path = True
    _coconut_module_name = _coconut_os.path.splitext(_coconut_os.path.basename(_coconut_file_dir))[0]
    if _coconut_module_name and _coconut_module_name[0].isalpha() and all(c.isalpha() or c.isdigit() for c in _coconut_module_name) and "__init__.py" in _coconut_os.listdir(_coconut_file_dir):  # type: ignore
        _coconut_full_module_name = str(_coconut_module_name + ".__coconut__")  # type: ignore
        import __coconut__ as _coconut__coconut__
        _coconut__coconut__.__name__ = _coconut_full_module_name
        for _coconut_v in vars(_coconut__coconut__).values():  # type: ignore
            if getattr(_coconut_v, "__module__", None) == '__coconut__':  # type: ignore
                try:
                    _coconut_v.__module__ = _coconut_full_module_name
                except AttributeError:
                    _coconut_v_type = type(_coconut_v)  # type: ignore
                    if getattr(_coconut_v_type, "__module__", None) == '__coconut__':  # type: ignore
                        _coconut_v_type.__module__ = _coconut_full_module_name
        _coconut_sys.modules[_coconut_full_module_name] = _coconut__coconut__
from __coconut__ import *
from __coconut__ import _coconut_tail_call, _coconut_tco, _namedtuple_of, _coconut, _coconut_Expected, _coconut_MatchError, _coconut_SupportsAdd, _coconut_SupportsMinus, _coconut_SupportsMul, _coconut_SupportsPow, _coconut_SupportsTruediv, _coconut_SupportsFloordiv, _coconut_SupportsMod, _coconut_SupportsAnd, _coconut_SupportsXor, _coconut_SupportsOr, _coconut_SupportsLshift, _coconut_SupportsRshift, _coconut_SupportsMatmul, _coconut_SupportsInv, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_complex_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_arr_concat_op, _coconut_mk_anon_namedtuple, _coconut_matmul, _coconut_py_str, _coconut_flatten, _coconut_multiset, _coconut_back_none_pipe, _coconut_back_none_star_pipe, _coconut_back_none_dubstar_pipe, _coconut_forward_none_compose, _coconut_back_none_compose, _coconut_forward_none_star_compose, _coconut_back_none_star_compose, _coconut_forward_none_dubstar_compose, _coconut_back_none_dubstar_compose, _coconut_call_or_coefficient, _coconut_in, _coconut_not_in, _coconut_attritemgetter, _coconut_if_op, _coconut_CoconutWarning
if _coconut_pop_path:
    _coconut_sys.path.pop(0)
try:
    __file__ = _coconut_os.path.abspath(__file__) if __file__ else __file__
except NameError:
    pass
else:
    if __file__ and '__coconut_cache__' in __file__:
        _coconut_file_comps = []
        while __file__:
            __file__, _coconut_file_comp = _coconut_os.path.split(__file__)
            if not _coconut_file_comp:
                _coconut_file_comps.append(__file__)
                break
            if _coconut_file_comp != '__coconut_cache__':
                _coconut_file_comps.append(_coconut_file_comp)
        __file__ = _coconut_os.path.join(*reversed(_coconut_file_comps))

# Compiled Coconut: -----------------------------------------------------------



import math  #8 (line in Coconut source)
from abc import ABC  #9 (line in Coconut source)
from abc import abstractmethod  #9 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #10 (line in Coconut source)
    from typing import Any  #10 (line in Coconut source)
else:  #10 (line in Coconut source)
    try:  #10 (line in Coconut source)
        Any = _coconut.typing.Any  #10 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #10 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #10 (line in Coconut source)

import networkx as nx  #12 (line in Coconut source)

from yggdrasil_lm.core.edges import Edge  #14 (line in Coconut source)
from yggdrasil_lm.core.edges import EdgeType  #14 (line in Coconut source)
from yggdrasil_lm.core.nodes import AnyNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import Node  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import node_from_dict  #15 (line in Coconut source)


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class GraphStore(ABC):  #22 (line in Coconut source)
    """Async interface for all graph storage backends."""  #23 (line in Coconut source)

    @abstractmethod  #25 (line in Coconut source)
    async def upsert_node(self, node: Node) -> None:  #26 (line in Coconut source)
        """Insert or update a node. Identified by node_id."""  #27 (line in Coconut source)


    @abstractmethod  #29 (line in Coconut source)
    async def upsert_edge(self, edge: Edge) -> None:  #30 (line in Coconut source)
        """Insert or update an edge. Identified by edge_id."""  #31 (line in Coconut source)


    @abstractmethod  #33 (line in Coconut source)
    async def get_node(self, node_id: str) -> AnyNode | None:  #34 (line in Coconut source)
        """Fetch a node by ID, or None if not found."""  #35 (line in Coconut source)


    @abstractmethod  #37 (line in Coconut source)
    async def get_edge(self, edge_id: str) -> Edge | None:  #38 (line in Coconut source)
        """Fetch an edge by ID, or None if not found."""  #39 (line in Coconut source)


    @abstractmethod  #41 (line in Coconut source)
    async def get_edges(self, node_id: str, edge_type: EdgeType | None=None, direction: str="out", only_valid: bool=True,) -> list[Edge]:  # "out" | "in" | "both"  #42 (line in Coconut source)
        """Return edges connected to node_id, optionally filtered by type and direction."""  #49 (line in Coconut source)


    @abstractmethod  #51 (line in Coconut source)
    async def neighbors(self, node_id: str, edge_type: EdgeType | None=None, depth: int=1, only_valid: bool=True,) -> list[AnyNode]:  #52 (line in Coconut source)
        """BFS neighbors of node_id up to `depth` hops, optionally filtered by edge type."""  #59 (line in Coconut source)


    @abstractmethod  #61 (line in Coconut source)
    async def vector_search(self, embedding: list[float], node_types: list[NodeType] | None=None, top_k: int=10, only_valid: bool=True,) -> list[tuple[AnyNode, float]]:  #62 (line in Coconut source)
        """Return top_k nodes ranked by cosine similarity to the query embedding."""  #69 (line in Coconut source)


    @abstractmethod  #71 (line in Coconut source)
    async def delete_node(self, node_id: str) -> None:  #72 (line in Coconut source)
        """Hard-delete a node and all its edges."""  #73 (line in Coconut source)


    @abstractmethod  #75 (line in Coconut source)
    async def delete_edge(self, edge_id: str) -> None:  #76 (line in Coconut source)
        """Hard-delete an edge."""  #77 (line in Coconut source)


    @abstractmethod  #79 (line in Coconut source)
    async def list_nodes(self, node_type: NodeType | None=None, group_id: str | None=None, only_valid: bool=True,) -> list[AnyNode]:  #80 (line in Coconut source)
        """List nodes, optionally filtered."""  #86 (line in Coconut source)


    @abstractmethod  #88 (line in Coconut source)
    async def list_edges(self, edge_type: EdgeType | None=None, group_id: str | None=None, only_valid: bool=True,) -> list[Edge]:  #89 (line in Coconut source)
        """List edges, optionally filtered."""  #95 (line in Coconut source)

# ------------------------------------------------------------------
# Convenience helpers (implemented in terms of abstract methods)
# ------------------------------------------------------------------


    async def expire_node(self, node_id: str) -> None:  #101 (line in Coconut source)
        """Soft-delete a node by setting invalid_at to now."""  #102 (line in Coconut source)
        node = await self.get_node(node_id)  #103 (line in Coconut source)
        if node:  #104 (line in Coconut source)
            await self.upsert_node(node.expire())  #105 (line in Coconut source)


    async def expire_edge(self, edge_id: str) -> None:  #107 (line in Coconut source)
        """Soft-delete an edge by setting invalid_at to now."""  #108 (line in Coconut source)
        edge = await self.get_edge(edge_id)  #109 (line in Coconut source)
        if edge:  #110 (line in Coconut source)
            await self.upsert_edge(edge.expire())  #111 (line in Coconut source)


    async def attach_context(self, agent_id: str, ctx_id: str, weight: float | None=None, **kw: Any,) -> Edge:  #113 (line in Coconut source)
        """Create a HAS_CONTEXT edge from agent_id → ctx_id.

        If weight is not provided, it is auto-computed as the cosine similarity
        between the agent and context embeddings (falls back to 1.0 when either
        node has no embedding yet).
        """  #125 (line in Coconut source)
        if weight is None:  #126 (line in Coconut source)
            agent = await self.get_node(agent_id)  #127 (line in Coconut source)
            ctx = await self.get_node(ctx_id)  #128 (line in Coconut source)
            if (agent is not None and ctx is not None and agent.embedding and ctx.embedding):  #129 (line in Coconut source)
                weight = _cosine(_normalize(agent.embedding), ctx.embedding)  #135 (line in Coconut source)
            else:  #136 (line in Coconut source)
                weight = 1.0  #137 (line in Coconut source)
        edge = Edge.has_context(src_id=agent_id, dst_id=ctx_id, weight=weight, **kw)  #138 (line in Coconut source)
        await self.upsert_edge(edge)  #139 (line in Coconut source)
        return edge  #140 (line in Coconut source)


    async def attach_tool(self, agent_id: str, tool_id: str, weight: float | None=None, **kw: Any,) -> Edge:  #142 (line in Coconut source)
        """Create a HAS_TOOL edge from agent_id → tool_id.

        If weight is not provided, it is auto-computed as the cosine similarity
        between the agent and tool embeddings (falls back to 1.0 when either
        node has no embedding yet). This weight is used by semantic_search() as
        a tool-affinity prior: tools that are semantically central to the agent
        score higher when multiple tools have similar query cosine scores.
        """  #156 (line in Coconut source)
        if weight is None:  #157 (line in Coconut source)
            agent = await self.get_node(agent_id)  #158 (line in Coconut source)
            tool = await self.get_node(tool_id)  #159 (line in Coconut source)
            if (agent is not None and tool is not None and agent.embedding and tool.embedding):  #160 (line in Coconut source)
                weight = _cosine(_normalize(agent.embedding), tool.embedding)  #166 (line in Coconut source)
            else:  #167 (line in Coconut source)
                weight = 1.0  #168 (line in Coconut source)
        edge = Edge.has_tool(src_id=agent_id, dst_id=tool_id, weight=weight, **kw)  #169 (line in Coconut source)
        await self.upsert_edge(edge)  #170 (line in Coconut source)
        return edge  #171 (line in Coconut source)


# ---------------------------------------------------------------------------
# NetworkX in-memory backend
# ---------------------------------------------------------------------------


class NetworkXGraphStore(GraphStore):  #178 (line in Coconut source)
    """In-memory graph store backed by a NetworkX MultiDiGraph.

    - Zero infrastructure — no external services required.
    - Nodes stored as typed Pydantic objects in _nodes dict.
    - Edges stored as typed Pydantic objects in _edges dict.
    - NetworkX graph used for topology queries (neighbors, traversal).
    - Vector search via brute-force cosine similarity (use hnswlib at scale).

    Use this for development, testing, and small workloads.
    Switch to Neo4jGraphStore for production.
    """  #189 (line in Coconut source)

    def __init__(self) -> None:  #191 (line in Coconut source)
        self._g: nx.MultiDiGraph = nx.MultiDiGraph()  #192 (line in Coconut source)
        self._nodes: dict[str, AnyNode] = {}  #193 (line in Coconut source)
        self._edges: dict[str, Edge] = {}  #194 (line in Coconut source)
        self._metadata: dict[str, Any] = {"graph_name": "graph", "active_graph_revision_id": "", "candidate_graph_revision_id": "", "active_graph_version": "v1", "revisions": {}, "revision_history": [], "replay_status_by_revision": {}, "replay_results_by_revision": {}, "metadata": {}}  #195 (line in Coconut source)

# ------------------------------------------------------------------
# Write
# ------------------------------------------------------------------


    async def upsert_node(self, node: Node) -> None:  #211 (line in Coconut source)
        self._nodes[node.node_id] = node  # type: ignore[assignment]  #212 (line in Coconut source)
        self._g.add_node(node.node_id, node_type=node.node_type, name=node.name, group_id=node.group_id)  #213 (line in Coconut source)


    async def upsert_edge(self, edge: Edge) -> None:  #220 (line in Coconut source)
        self._edges[edge.edge_id] = edge  #221 (line in Coconut source)
# NetworkX MultiDiGraph allows parallel edges; key=edge_id disambiguates.
        self._g.add_edge(edge.src_id, edge.dst_id, key=edge.edge_id, edge_type=edge.edge_type, weight=edge.weight)  #223 (line in Coconut source)


    async def delete_node(self, node_id: str) -> None:  #231 (line in Coconut source)
        self._nodes.pop(node_id, None)  #232 (line in Coconut source)
        if self._g.has_node(node_id):  #233 (line in Coconut source)
            self._g.remove_node(node_id)  #234 (line in Coconut source)


    async def delete_edge(self, edge_id: str) -> None:  #236 (line in Coconut source)
        edge = self._edges.pop(edge_id, None)  #237 (line in Coconut source)
        if edge and self._g.has_edge(edge.src_id, edge.dst_id, key=edge_id):  #238 (line in Coconut source)
            self._g.remove_edge(edge.src_id, edge.dst_id, key=edge_id)  #239 (line in Coconut source)

# ------------------------------------------------------------------
# Read
# ------------------------------------------------------------------


    async def get_node(self, node_id: str) -> AnyNode | None:  #245 (line in Coconut source)
        return self._nodes.get(node_id)  #246 (line in Coconut source)


    async def get_edge(self, edge_id: str) -> Edge | None:  #248 (line in Coconut source)
        return self._edges.get(edge_id)  #249 (line in Coconut source)


    async def get_edges(self, node_id: str, edge_type: EdgeType | None=None, direction: str="out", only_valid: bool=True,) -> list[Edge]:  #251 (line in Coconut source)
        _coconut_case_match_to_0 = direction  #258 (line in Coconut source)
        _coconut_case_match_check_0 = False  #258 (line in Coconut source)
        if _coconut_case_match_to_0 == "out":  #258 (line in Coconut source)
            _coconut_case_match_check_0 = True  #258 (line in Coconut source)
        if _coconut_case_match_check_0:  #258 (line in Coconut source)
            raw = self._g.out_edges(node_id, keys=True)  #260 (line in Coconut source)
        if not _coconut_case_match_check_0:  #261 (line in Coconut source)
            if _coconut_case_match_to_0 == "in":  #261 (line in Coconut source)
                _coconut_case_match_check_0 = True  #261 (line in Coconut source)
            if _coconut_case_match_check_0:  #261 (line in Coconut source)
                raw = self._g.in_edges(node_id, keys=True)  #262 (line in Coconut source)
        if not _coconut_case_match_check_0:  #263 (line in Coconut source)
            _coconut_case_match_check_0 = True  #263 (line in Coconut source)
            if _coconut_case_match_check_0:  #263 (line in Coconut source)
                raw = list(self._g.out_edges(node_id, keys=True)) + list(self._g.in_edges(node_id, keys=True))  #264 (line in Coconut source)

        results: list[Edge] = []  #267 (line in Coconut source)
        seen: set[str] = set()  #268 (line in Coconut source)
        for _src, _dst, key in raw:  #269 (line in Coconut source)
            if key in seen:  #270 (line in Coconut source)
                continue  #271 (line in Coconut source)
            seen.add(key)  #272 (line in Coconut source)
            edge = self._edges.get(key)  #273 (line in Coconut source)
            if edge is None:  #274 (line in Coconut source)
                continue  #275 (line in Coconut source)
            if only_valid and not edge.is_valid:  #276 (line in Coconut source)
                continue  #277 (line in Coconut source)
            if edge_type is not None and edge.edge_type != edge_type:  #278 (line in Coconut source)
                continue  #279 (line in Coconut source)
            results.append(edge)  #280 (line in Coconut source)
        return results  #281 (line in Coconut source)


    async def neighbors(self, node_id: str, edge_type: EdgeType | None=None, depth: int=1, only_valid: bool=True,) -> list[AnyNode]:  #283 (line in Coconut source)
        visited: set[str] = set()  #290 (line in Coconut source)
        frontier: set[str] = {node_id}  #291 (line in Coconut source)

        for _ in range(depth):  #293 (line in Coconut source)
            next_frontier: set[str] = set()  #294 (line in Coconut source)
            for nid in frontier:  #295 (line in Coconut source)
                edges = await self.get_edges(nid, edge_type=edge_type, only_valid=only_valid)  #296 (line in Coconut source)
                for e in edges:  #297 (line in Coconut source)
                    neighbor = e.dst_id if e.src_id == nid else e.src_id  #298 (line in Coconut source)
                    if neighbor not in visited and neighbor != node_id:  #299 (line in Coconut source)
                        next_frontier.add(neighbor)  #300 (line in Coconut source)
            visited.update(frontier)  #301 (line in Coconut source)
            frontier = next_frontier  #302 (line in Coconut source)

        nodes = []  #304 (line in Coconut source)
        for nid in frontier:  #305 (line in Coconut source)
            n = self._nodes.get(nid)  #306 (line in Coconut source)
            if n and (not only_valid or n.is_valid):  #307 (line in Coconut source)
                nodes.append(n)  #308 (line in Coconut source)
        return nodes  #309 (line in Coconut source)


    async def list_nodes(self, node_type: NodeType | None=None, group_id: str | None=None, only_valid: bool=True,) -> list[AnyNode]:  #311 (line in Coconut source)
        results = []  #317 (line in Coconut source)
        for node in self._nodes.values():  #318 (line in Coconut source)
            if only_valid and not node.is_valid:  #319 (line in Coconut source)
                continue  #320 (line in Coconut source)
            if node_type is not None and node.node_type != node_type:  #321 (line in Coconut source)
                continue  #322 (line in Coconut source)
            if group_id is not None and node.group_id != group_id:  #323 (line in Coconut source)
                continue  #324 (line in Coconut source)
            results.append(node)  #325 (line in Coconut source)
        return results  #326 (line in Coconut source)


    async def list_edges(self, edge_type: EdgeType | None=None, group_id: str | None=None, only_valid: bool=True,) -> list[Edge]:  #328 (line in Coconut source)
        results = []  #334 (line in Coconut source)
        for edge in self._edges.values():  #335 (line in Coconut source)
            if only_valid and not edge.is_valid:  #336 (line in Coconut source)
                continue  #337 (line in Coconut source)
            if edge_type is not None and edge.edge_type != edge_type:  #338 (line in Coconut source)
                continue  #339 (line in Coconut source)
            if group_id is not None and edge.group_id != group_id:  #340 (line in Coconut source)
                continue  #341 (line in Coconut source)
            results.append(edge)  #342 (line in Coconut source)
        return results  #343 (line in Coconut source)


    async def vector_search(self, embedding: list[float], node_types: list[NodeType] | None=None, top_k: int=10, only_valid: bool=True,) -> list[tuple[AnyNode, float]]:  #345 (line in Coconut source)
        """Brute-force cosine similarity search over nodes with embeddings."""  #352 (line in Coconut source)
        q = _normalize(embedding)  #353 (line in Coconut source)
        results: list[tuple[AnyNode, float]] = []  #354 (line in Coconut source)

        for node in self._nodes.values():  #356 (line in Coconut source)
            if only_valid and not node.is_valid:  #357 (line in Coconut source)
                continue  #358 (line in Coconut source)
            if node_types and node.node_type not in node_types:  #359 (line in Coconut source)
                continue  #360 (line in Coconut source)
            if not node.embedding:  #361 (line in Coconut source)
                continue  #362 (line in Coconut source)
            score = _cosine(q, node.embedding)  #363 (line in Coconut source)
            results.append((node, score))  #364 (line in Coconut source)

        results.sort(key=lambda x: x[1], reverse=True)  #366 (line in Coconut source)
        return results[:top_k]  #367 (line in Coconut source)

# ------------------------------------------------------------------
# Serialisation helpers
# ------------------------------------------------------------------


    def to_dict(self) -> dict[str, Any]:  #373 (line in Coconut source)
        """Serialise the full store to a JSON-compatible dict."""  #374 (line in Coconut source)
        return {"metadata": self._metadata, "nodes": [n.model_dump(mode="json") for n in self._nodes.values()], "edges": [e.model_dump(mode="json") for e in self._edges.values()]}  #375 (line in Coconut source)


    @classmethod  #381 (line in Coconut source)
    def from_dict(cls, data: dict[str, Any]) -> "NetworkXGraphStore":  #382 (line in Coconut source)
        """Restore a store from a serialised dict."""  #383 (line in Coconut source)
        store = cls()  #384 (line in Coconut source)
        import asyncio  #385 (line in Coconut source)
        loop = asyncio.new_event_loop()  #386 (line in Coconut source)
        try:  #387 (line in Coconut source)
            for nd in data.get("nodes", []):  #388 (line in Coconut source)
                loop.run_until_complete(store.upsert_node(node_from_dict(nd)))  #389 (line in Coconut source)
            for ed in data.get("edges", []):  #390 (line in Coconut source)
                loop.run_until_complete(store.upsert_edge(Edge.model_validate(ed)))  #391 (line in Coconut source)
            if "metadata" in data and isinstance(data["metadata"], dict):  #392 (line in Coconut source)
                store._metadata = dict(data["metadata"])  #393 (line in Coconut source)
        finally:  #394 (line in Coconut source)
            loop.close()  #395 (line in Coconut source)
        return store  #396 (line in Coconut source)


    @_coconut_tco  #398 (line in Coconut source)
    def get_metadata(self) -> dict[str, Any]:  #398 (line in Coconut source)
        return _coconut_tail_call(dict, self._metadata)  #399 (line in Coconut source)


    def set_metadata(self, metadata: dict[str, Any]) -> None:  #401 (line in Coconut source)
        self._metadata = dict(metadata)  #402 (line in Coconut source)


# ---------------------------------------------------------------------------
# Vector math helpers
# ---------------------------------------------------------------------------


def _normalize(vec: list[float]) -> list[float]:  #409 (line in Coconut source)
    norm = math.sqrt(sum((x * x for x in vec))) or 1.0  #410 (line in Coconut source)
    return [x / norm for x in vec]  #411 (line in Coconut source)



@_coconut_tco  #414 (line in Coconut source)
def _cosine(a: list[float], b: list[float]) -> float:  #414 (line in Coconut source)
    if len(a) != len(b):  #415 (line in Coconut source)
        return 0.0  #416 (line in Coconut source)
    b_norm = _normalize(b)  #417 (line in Coconut source)
    return _coconut_tail_call(sum, (ai * bi for ai, bi in zip(a, b_norm)))  #418 (line in Coconut source)
