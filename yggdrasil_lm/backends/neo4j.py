#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x51c1a87c

# Compiled with Coconut version 3.2.0

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



import json  #18 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #19 (line in Coconut source)
    from typing import Any  #19 (line in Coconut source)
else:  #19 (line in Coconut source)
    try:  #19 (line in Coconut source)
        Any = _coconut.typing.Any  #19 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #19 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #19 (line in Coconut source)

from yggdrasil_lm.core.edges import Edge  #21 (line in Coconut source)
from yggdrasil_lm.core.edges import EdgeType  #21 (line in Coconut source)
from yggdrasil_lm.core.nodes import AnyNode  #22 (line in Coconut source)
from yggdrasil_lm.core.nodes import Node  #22 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #22 (line in Coconut source)
from yggdrasil_lm.core.nodes import node_from_dict  #22 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #23 (line in Coconut source)


class Neo4jGraphStore(GraphStore):  #26 (line in Coconut source)
    """Neo4j-backed graph store using the official async Python driver."""  #27 (line in Coconut source)

    def __init__(self, uri: str, user: str, password: str, database: str="neo4j") -> None:  #29 (line in Coconut source)
        try:  #30 (line in Coconut source)
            from neo4j import AsyncGraphDatabase  #31 (line in Coconut source)
        except ImportError:  #32 (line in Coconut source)
            raise ImportError("neo4j package required: pip install 'yggdrasil[neo4j]'")  #33 (line in Coconut source)
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))  #36 (line in Coconut source)
        self._db = database  #37 (line in Coconut source)


    async def close(self) -> None:  #39 (line in Coconut source)
        await self._driver.close()  #40 (line in Coconut source)


    async def upsert_node(self, node: Node) -> None:  #42 (line in Coconut source)
        data = node.model_dump(mode="json")  #43 (line in Coconut source)
        data["embedding_json"] = json.dumps(data.pop("embedding", None) or [])  #44 (line in Coconut source)
        data["attributes_json"] = json.dumps(data.pop("attributes", {}))  #45 (line in Coconut source)

        cypher = """
        MERGE (n:Node {node_id: $node_id})
        SET n += $props
        SET n:%(label)s
        """ % {"label": node.node_type.upper()}  #51 (line in Coconut source)

        async with self._driver.session(database=self._db) as session:  #53 (line in Coconut source)
            await session.run(cypher, node_id=node.node_id, props=data)  #54 (line in Coconut source)


    async def upsert_edge(self, edge: Edge) -> None:  #56 (line in Coconut source)
        cypher = """
        MATCH (src:Node {node_id: $src_id})
        MATCH (dst:Node {node_id: $dst_id})
        MERGE (src)-[r:%(rel)s {edge_id: $edge_id}]->(dst)
        SET r += $props
        """ % {"rel": edge.edge_type.upper().replace("-", "_")}  #62 (line in Coconut source)

        props = edge.model_dump(mode="json")  #64 (line in Coconut source)
        props["attributes_json"] = json.dumps(props.pop("attributes", {}))  #65 (line in Coconut source)

        async with self._driver.session(database=self._db) as session:  #67 (line in Coconut source)
            await session.run(cypher, src_id=edge.src_id, dst_id=edge.dst_id, edge_id=edge.edge_id, props=props)  #68 (line in Coconut source)


    async def get_node(self, node_id: str) -> AnyNode | None:  #76 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #77 (line in Coconut source)
            result = await session.run("MATCH (n:Node {node_id: $node_id}) RETURN properties(n) AS props", node_id=node_id)  #78 (line in Coconut source)
            record = await result.single()  #82 (line in Coconut source)
            if record is None:  #83 (line in Coconut source)
                return None  #84 (line in Coconut source)
            return (self._deserialise_node)((dict)(record["props"]))  #85 (line in Coconut source)


    async def get_edge(self, edge_id: str) -> Edge | None:  #87 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #88 (line in Coconut source)
            result = await session.run("MATCH ()-[r {edge_id: $edge_id}]->() RETURN properties(r) AS props", edge_id=edge_id)  #89 (line in Coconut source)
            record = await result.single()  #93 (line in Coconut source)
            if record is None:  #94 (line in Coconut source)
                return None  #95 (line in Coconut source)
            return (Edge.model_validate)((dict)(record["props"]))  #96 (line in Coconut source)


    async def get_edges(self, node_id: str, edge_type: EdgeType | None=None, direction: str="out", only_valid: bool=True,) -> list[Edge]:  #98 (line in Coconut source)
        rel = ":{_coconut_format_0}".format(_coconut_format_0=(edge_type.upper())) if edge_type else ""  #105 (line in Coconut source)

        _coconut_case_match_to_0 = direction  #107 (line in Coconut source)
        _coconut_case_match_check_0 = False  #107 (line in Coconut source)
        if _coconut_case_match_to_0 == "out":  #107 (line in Coconut source)
            _coconut_case_match_check_0 = True  #107 (line in Coconut source)
        if _coconut_case_match_check_0:  #107 (line in Coconut source)
            pattern = "(n:Node {{node_id: $node_id}})-[r{_coconut_format_0}]->()".format(_coconut_format_0=(rel))  #109 (line in Coconut source)
        if not _coconut_case_match_check_0:  #110 (line in Coconut source)
            if _coconut_case_match_to_0 == "in":  #110 (line in Coconut source)
                _coconut_case_match_check_0 = True  #110 (line in Coconut source)
            if _coconut_case_match_check_0:  #110 (line in Coconut source)
                pattern = "()-[r{_coconut_format_0}]->(n:Node {{node_id: $node_id}})".format(_coconut_format_0=(rel))  #111 (line in Coconut source)
        if not _coconut_case_match_check_0:  #112 (line in Coconut source)
            _coconut_case_match_check_0 = True  #112 (line in Coconut source)
            if _coconut_case_match_check_0:  #112 (line in Coconut source)
                pattern = "(n:Node {{node_id: $node_id}})-[r{_coconut_format_0}]-()".format(_coconut_format_0=(rel))  #113 (line in Coconut source)

        cypher = "MATCH {_coconut_format_0} RETURN properties(r) AS props".format(_coconut_format_0=(pattern))  #115 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #116 (line in Coconut source)
            result = await session.run(cypher, node_id=node_id)  #117 (line in Coconut source)
            edges = []  #118 (line in Coconut source)
            async for record in result:  #119 (line in Coconut source)
                edge = (Edge.model_validate)((dict)(record["props"]))  #120 (line in Coconut source)
                if only_valid and not edge.is_valid:  #121 (line in Coconut source)
                    continue  #122 (line in Coconut source)
                edges.append(edge)  #123 (line in Coconut source)
            return edges  #124 (line in Coconut source)


    async def neighbors(self, node_id: str, edge_type: EdgeType | None=None, depth: int=1, only_valid: bool=True,) -> list[AnyNode]:  #126 (line in Coconut source)
        rel = ":{_coconut_format_0}".format(_coconut_format_0=(edge_type.upper())) if edge_type else ""  #133 (line in Coconut source)
        cypher = (("MATCH (n:Node {{node_id: $node_id}})-[r{_coconut_format_0}*1..{_coconut_format_1}]->(m:Node) ".format(_coconut_format_0=(rel), _coconut_format_1=(depth)) + "RETURN DISTINCT properties(m) AS props"))  #134 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #138 (line in Coconut source)
            result = await session.run(cypher, node_id=node_id)  #139 (line in Coconut source)
            nodes = []  #140 (line in Coconut source)
            async for record in result:  #141 (line in Coconut source)
                node = (self._deserialise_node)((dict)(record["props"]))  #142 (line in Coconut source)
                if only_valid and not node.is_valid:  #143 (line in Coconut source)
                    continue  #144 (line in Coconut source)
                nodes.append(node)  #145 (line in Coconut source)
            return nodes  #146 (line in Coconut source)


    async def vector_search(self, embedding: list[float], node_types: list[NodeType] | None=None, top_k: int=10, only_valid: bool=True,) -> list[tuple[AnyNode, float]]:  #148 (line in Coconut source)
# Requires Neo4j 5.x vector index.
# Create index: CREATE VECTOR INDEX nodeEmbeddings
#   FOR (n:Node) ON n.embedding OPTIONS {indexConfig: {`vector.dimensions`: 1024}}
        where = ""  #158 (line in Coconut source)
        if node_types:  #159 (line in Coconut source)
            types_list = "['" + "','".join((t.value for t in node_types)) + "']"  #160 (line in Coconut source)
            where = "WHERE n.node_type IN {_coconut_format_0}".format(_coconut_format_0=(types_list))  #161 (line in Coconut source)

        cypher = """
        CALL db.index.vector.queryNodes('nodeEmbeddings', $top_k, $embedding)
        YIELD node AS n, score
        {_coconut_format_0}
        RETURN properties(n) AS props, score
        ORDER BY score DESC
        LIMIT $top_k
        """.format(_coconut_format_0=(where))  #170 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #171 (line in Coconut source)
            result = await session.run(cypher, top_k=top_k, embedding=embedding)  #172 (line in Coconut source)
            results = []  #173 (line in Coconut source)
            async for record in result:  #174 (line in Coconut source)
                node = (self._deserialise_node)((dict)(record["props"]))  #175 (line in Coconut source)
                if only_valid and not node.is_valid:  #176 (line in Coconut source)
                    continue  #177 (line in Coconut source)
                results.append((node, float(record["score"])))  #178 (line in Coconut source)
            return results  #179 (line in Coconut source)


    async def delete_node(self, node_id: str) -> None:  #181 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #182 (line in Coconut source)
            await session.run("MATCH (n:Node {node_id: $node_id}) DETACH DELETE n", node_id=node_id)  #183 (line in Coconut source)


    async def delete_edge(self, edge_id: str) -> None:  #188 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #189 (line in Coconut source)
            await session.run("MATCH ()-[r {edge_id: $edge_id}]->() DELETE r", edge_id=edge_id)  #190 (line in Coconut source)


    async def list_nodes(self, node_type: NodeType | None=None, group_id: str | None=None, only_valid: bool=True,) -> list[AnyNode]:  #195 (line in Coconut source)
        filters = []  #201 (line in Coconut source)
        if node_type:  #202 (line in Coconut source)
            filters.append("n.node_type = '{_coconut_format_0}'".format(_coconut_format_0=(node_type.value)))  #203 (line in Coconut source)
        if group_id:  #204 (line in Coconut source)
            filters.append("n.group_id = '{_coconut_format_0}'".format(_coconut_format_0=(group_id)))  #205 (line in Coconut source)
        where = "WHERE " + " AND ".join(filters) if filters else ""  #206 (line in Coconut source)

        cypher = "MATCH (n:Node) {_coconut_format_0} RETURN properties(n) AS props".format(_coconut_format_0=(where))  #208 (line in Coconut source)
        async with self._driver.session(database=self._db) as session:  #209 (line in Coconut source)
            result = await session.run(cypher)  #210 (line in Coconut source)
            nodes = []  #211 (line in Coconut source)
            async for record in result:  #212 (line in Coconut source)
                node = (self._deserialise_node)((dict)(record["props"]))  #213 (line in Coconut source)
                if only_valid and not node.is_valid:  #214 (line in Coconut source)
                    continue  #215 (line in Coconut source)
                nodes.append(node)  #216 (line in Coconut source)
            return nodes  #217 (line in Coconut source)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


    @_coconut_tco  #223 (line in Coconut source)
    def _deserialise_node(self, props: dict[str, Any]) -> AnyNode:  #223 (line in Coconut source)
        if "embedding_json" in props:  #224 (line in Coconut source)
            props["embedding"] = json.loads(props.pop("embedding_json") or "null")  #225 (line in Coconut source)
        if "attributes_json" in props:  #226 (line in Coconut source)
            props["attributes"] = json.loads(props.pop("attributes_json") or "{}")  #227 (line in Coconut source)
        return _coconut_tail_call(node_from_dict, props)  #228 (line in Coconut source)
