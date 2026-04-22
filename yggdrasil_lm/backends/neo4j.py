"""Neo4j production backend for GraphStore.

Requires: pip install yggdrasil[neo4j]
Environment: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

Drop-in replacement for NetworkXGraphStore:
    store = Neo4jGraphStore(uri=..., user=..., password=...)
    # All GraphStore methods work identically.

Features over NetworkXGraphStore:
- Persistent across process restarts
- Concurrent write-safe
- Cypher traversal for complex multi-hop queries
- GDS (Graph Data Science) for community detection
- Native vector index (Neo4j 5.x+) for fast ANN search
"""

from __future__ import annotations

import json
from typing import Any

from yggdrasil_lm.core.edges import Edge, EdgeType
from yggdrasil_lm.core.nodes import AnyNode, Node, NodeType, node_from_dict
from yggdrasil_lm.core.store import GraphStore


class Neo4jGraphStore(GraphStore):
    """Neo4j-backed graph store using the official async Python driver."""

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j") -> None:
        try:
            from neo4j import AsyncGraphDatabase
        except ImportError:
            raise ImportError(
                "neo4j package required: pip install 'yggdrasil[neo4j]'"
            )
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        self._db = database

    async def close(self) -> None:
        await self._driver.close()

    async def upsert_node(self, node: Node) -> None:
        data = node.model_dump(mode="json")
        data["embedding_json"] = json.dumps(data.pop("embedding", None) or [])
        data["attributes_json"] = json.dumps(data.pop("attributes", {}))

        cypher = """
        MERGE (n:Node {node_id: $node_id})
        SET n += $props
        SET n:%(label)s
        """ % {"label": node.node_type.upper()}

        async with self._driver.session(database=self._db) as session:
            await session.run(cypher, node_id=node.node_id, props=data)

    async def upsert_edge(self, edge: Edge) -> None:
        cypher = """
        MATCH (src:Node {node_id: $src_id})
        MATCH (dst:Node {node_id: $dst_id})
        MERGE (src)-[r:%(rel)s {edge_id: $edge_id}]->(dst)
        SET r += $props
        """ % {"rel": edge.edge_type.upper().replace("-", "_")}

        props = edge.model_dump(mode="json")
        props["attributes_json"] = json.dumps(props.pop("attributes", {}))

        async with self._driver.session(database=self._db) as session:
            await session.run(
                cypher,
                src_id=edge.src_id,
                dst_id=edge.dst_id,
                edge_id=edge.edge_id,
                props=props,
            )

    async def get_node(self, node_id: str) -> AnyNode | None:
        async with self._driver.session(database=self._db) as session:
            result = await session.run(
                "MATCH (n:Node {node_id: $node_id}) RETURN properties(n) AS props",
                node_id=node_id,
            )
            record = await result.single()
            if record is None:
                return None
            return self._deserialise_node(dict(record["props"]))

    async def get_edge(self, edge_id: str) -> Edge | None:
        async with self._driver.session(database=self._db) as session:
            result = await session.run(
                "MATCH ()-[r {edge_id: $edge_id}]->() RETURN properties(r) AS props",
                edge_id=edge_id,
            )
            record = await result.single()
            if record is None:
                return None
            return Edge.model_validate(dict(record["props"]))

    async def get_edges(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        direction: str = "out",
        only_valid: bool = True,
    ) -> list[Edge]:
        rel = f":{edge_type.upper()}" if edge_type else ""

        if direction == "out":
            pattern = f"(n:Node {{node_id: $node_id}})-[r{rel}]->()"
        elif direction == "in":
            pattern = f"()-[r{rel}]->(n:Node {{node_id: $node_id}})"
        else:
            pattern = f"(n:Node {{node_id: $node_id}})-[r{rel}]-()"

        cypher = f"MATCH {pattern} RETURN properties(r) AS props"
        async with self._driver.session(database=self._db) as session:
            result = await session.run(cypher, node_id=node_id)
            edges = []
            async for record in result:
                edge = Edge.model_validate(dict(record["props"]))
                if only_valid and not edge.is_valid:
                    continue
                edges.append(edge)
            return edges

    async def neighbors(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        depth: int = 1,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        rel = f":{edge_type.upper()}" if edge_type else ""
        cypher = (
            f"MATCH (n:Node {{node_id: $node_id}})-[r{rel}*1..{depth}]->(m:Node) "
            "RETURN DISTINCT properties(m) AS props"
        )
        async with self._driver.session(database=self._db) as session:
            result = await session.run(cypher, node_id=node_id)
            nodes = []
            async for record in result:
                node = self._deserialise_node(dict(record["props"]))
                if only_valid and not node.is_valid:
                    continue
                nodes.append(node)
            return nodes

    async def vector_search(
        self,
        embedding: list[float],
        node_types: list[NodeType] | None = None,
        top_k: int = 10,
        only_valid: bool = True,
    ) -> list[tuple[AnyNode, float]]:
        # Requires Neo4j 5.x vector index.
        # Create index: CREATE VECTOR INDEX nodeEmbeddings
        #   FOR (n:Node) ON n.embedding OPTIONS {indexConfig: {`vector.dimensions`: 1024}}
        where = ""
        if node_types:
            types_list = "['" + "','".join(t.value for t in node_types) + "']"
            where = f"WHERE n.node_type IN {types_list}"

        cypher = f"""
        CALL db.index.vector.queryNodes('nodeEmbeddings', $top_k, $embedding)
        YIELD node AS n, score
        {where}
        RETURN properties(n) AS props, score
        ORDER BY score DESC
        LIMIT $top_k
        """
        async with self._driver.session(database=self._db) as session:
            result = await session.run(cypher, top_k=top_k, embedding=embedding)
            results = []
            async for record in result:
                node = self._deserialise_node(dict(record["props"]))
                if only_valid and not node.is_valid:
                    continue
                results.append((node, float(record["score"])))
            return results

    async def delete_node(self, node_id: str) -> None:
        async with self._driver.session(database=self._db) as session:
            await session.run(
                "MATCH (n:Node {node_id: $node_id}) DETACH DELETE n",
                node_id=node_id,
            )

    async def delete_edge(self, edge_id: str) -> None:
        async with self._driver.session(database=self._db) as session:
            await session.run(
                "MATCH ()-[r {edge_id: $edge_id}]->() DELETE r",
                edge_id=edge_id,
            )

    async def list_nodes(
        self,
        node_type: NodeType | None = None,
        group_id: str | None = None,
        only_valid: bool = True,
    ) -> list[AnyNode]:
        filters = []
        if node_type:
            filters.append(f"n.node_type = '{node_type.value}'")
        if group_id:
            filters.append(f"n.group_id = '{group_id}'")
        where = "WHERE " + " AND ".join(filters) if filters else ""

        cypher = f"MATCH (n:Node) {where} RETURN properties(n) AS props"
        async with self._driver.session(database=self._db) as session:
            result = await session.run(cypher)
            nodes = []
            async for record in result:
                node = self._deserialise_node(dict(record["props"]))
                if only_valid and not node.is_valid:
                    continue
                nodes.append(node)
            return nodes

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _deserialise_node(self, props: dict[str, Any]) -> AnyNode:
        if "embedding_json" in props:
            props["embedding"] = json.loads(props.pop("embedding_json") or "null")
        if "attributes_json" in props:
            props["attributes"] = json.loads(props.pop("attributes_json") or "{}")
        return node_from_dict(props)
