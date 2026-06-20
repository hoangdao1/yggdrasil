#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x9b411656

# Compiled with Coconut version 3.2.0

"""Weighted Reciprocal Rank Fusion (wRRF) for two-stage tool→agent retrieval.

Algorithm (from arXiv:2511.18194), extended with score-weighted fusion:
1. Embed query → q_vec
2. vector_search(TOOL nodes) → tool_hits ranked by cosine score
3. vector_search(AGENT nodes) → agent_hits ranked by cosine score
4. Walk HAS_TOOL edges upstream from tool hits → find parent AgentNodes,
   capturing each edge's weight as a tool-affinity prior.
5. Score fusion per candidate agent:
     tool_score  = w_tool  * cosine_score * edge_weight / (rank + k)
     agent_score = w_agent * cosine_score / (rank + k)
     tag_bonus   = len(tool.tags ∩ query_tags) * tag_weight   [optional]
     final_score = tool_score + agent_score + tag_bonus
6. Return top_k agents by final_score.

Improvements over pure rank-based RRF:
- Cosine score magnitude is preserved: a tool at rank 1 with cosine 0.95
  scores much higher than one at rank 1 with cosine 0.51.
- HAS_TOOL edge weight acts as a structural affinity prior: tools that are
  semantically central to their agent (set via attach_tool()) are boosted
  independently of query-time similarity.
- Optional query_tags enable concept-overlap bonuses for tools tagged with
  matching concepts, providing a structured signal on top of embeddings.
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



from dataclasses import dataclass  #26 (line in Coconut source)
from dataclasses import field  #26 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #27 (line in Coconut source)
    from typing import Any  #27 (line in Coconut source)
else:  #27 (line in Coconut source)
    try:  #27 (line in Coconut source)
        Any = _coconut.typing.Any  #27 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #27 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #27 (line in Coconut source)

from yggdrasil_lm.core.edges import EdgeType  #29 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #30 (line in Coconut source)
from yggdrasil_lm.core.nodes import AnyNode  #30 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #30 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #30 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #31 (line in Coconut source)


@dataclass  #34 (line in Coconut source)
class RetrievalResult():  #35 (line in Coconut source)
    """A ranked agent retrieval result."""  #36 (line in Coconut source)

    agent: AgentNode  #38 (line in Coconut source)
    score: float  #39 (line in Coconut source)
    via_tools: list[ToolNode] = field(default_factory=list)  # tools that surfaced this agent  #40 (line in Coconut source)
    tool_scores: list[float] = field(default_factory=list)  # cosine scores of those tools  #41 (line in Coconut source)


async def semantic_search(store: GraphStore, query_embedding: list[float], top_k: int=5, top_k_tools: int=20, top_k_agents: int=10, w_tool: float=0.7, w_agent: float=0.3, k: int=60, query_tags: list[str] | None=None, tag_weight: float=0.1,) -> list[RetrievalResult]:  # score bonus per matching tag  # concept tags extracted from the query  # RRF smoothing constant  #44 (line in Coconut source)
    """Find the best AgentNodes for a query via score-weighted wRRF.

    Args:
        store:           The graph store to search.
        query_embedding: Dense vector of the user query.
        top_k:           Number of final agent results to return.
        top_k_tools:     How many tool nodes to retrieve before walking upstream.
        top_k_agents:    How many agent nodes to retrieve directly.
        w_tool:          Weight for tool-driven score (higher = tools drive the result).
        w_agent:         Weight for direct agent score.
        k:               RRF smoothing constant (60 is the standard default).
        query_tags:      Optional concept tags (e.g. ["code_execution", "python"]).
                         Tools whose tags overlap with these receive a bonus per match.
        tag_weight:      Bonus added per matching tag.
    """  #70 (line in Coconut source)
    import asyncio  #71 (line in Coconut source)

# Step 1: Search ToolNodes and AgentNodes in parallel
    tool_coro = store.vector_search(query_embedding, node_types=[NodeType.TOOL,], top_k=top_k_tools)  #74 (line in Coconut source)
    agent_coro = store.vector_search(query_embedding, node_types=[NodeType.AGENT,], top_k=top_k_agents)  #75 (line in Coconut source)
    tool_hits, agent_hits = await asyncio.gather(tool_coro, agent_coro)  #76 (line in Coconut source)

# Build fast lookup: tool_node_id → (rank, cosine_score)
    tool_rank_score: dict[str, tuple[int, float]] = {node.node_id: (rank, score) for rank, (node, score) in enumerate(tool_hits) if isinstance(node, ToolNode)}  #79 (line in Coconut source)

# Step 2: Walk HAS_TOOL edges upstream from tool hits → find parent AgentNodes.
# Also capture edge.weight as the tool-affinity prior set at attach time.
# tool_to_agents: agent_id → list of (AgentNode, ToolNode, cosine_score, edge_weight)
    tool_to_agents: dict[str, list[tuple[AgentNode, ToolNode, float, float]]] = {}  #88 (line in Coconut source)
    for tool_node, tool_score in tool_hits:  #89 (line in Coconut source)
        _coconut_case_match_to_1 = tool_node  #90 (line in Coconut source)
        _coconut_case_match_check_1 = False  #90 (line in Coconut source)
        _coconut_match_temp_3 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #90 (line in Coconut source)
        _coconut_case_match_check_1 = True  #90 (line in Coconut source)
        if _coconut_case_match_check_1:  #90 (line in Coconut source)
            _coconut_case_match_check_1 = False  #90 (line in Coconut source)
            if not _coconut_case_match_check_1:  #90 (line in Coconut source)
                if (_coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_1, ToolNode)):  #90 (line in Coconut source)
                    _coconut_match_temp_4 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #90 (line in Coconut source)
                    if _coconut_match_temp_4:  #90 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #90 (line in Coconut source)

            if not _coconut_case_match_check_1:  #90 (line in Coconut source)
                if (not _coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_1, ToolNode)):  #90 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #90 (line in Coconut source)
                if _coconut_case_match_check_1:  #90 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #90 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #90 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #90 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #90 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #90 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #90 (line in Coconut source)
                            _coconut_match_temp_5 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #90 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_5, _coconut.tuple):  #90 (line in Coconut source)
                                raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #90 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_5) < 0:  #90 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_5),))  #90 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #90 (line in Coconut source)




        if _coconut_case_match_check_1:  #90 (line in Coconut source)
            parent_edges = await store.get_edges(tool_node.node_id, edge_type=EdgeType.HAS_TOOL, direction="in")  #92 (line in Coconut source)
            for edge in parent_edges:  #95 (line in Coconut source)
                parent = await store.get_node(edge.src_id)  #96 (line in Coconut source)
                _coconut_case_match_to_0 = parent  #97 (line in Coconut source)
                _coconut_case_match_check_0 = False  #97 (line in Coconut source)
                _coconut_match_temp_0 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #97 (line in Coconut source)
                _coconut_case_match_check_0 = True  #97 (line in Coconut source)
                if _coconut_case_match_check_0:  #97 (line in Coconut source)
                    _coconut_case_match_check_0 = False  #97 (line in Coconut source)
                    if not _coconut_case_match_check_0:  #97 (line in Coconut source)
                        if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, AgentNode)):  #97 (line in Coconut source)
                            _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #97 (line in Coconut source)
                            if _coconut_match_temp_1:  #97 (line in Coconut source)
                                _coconut_case_match_check_0 = True  #97 (line in Coconut source)

                    if not _coconut_case_match_check_0:  #97 (line in Coconut source)
                        if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, AgentNode)):  #97 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #97 (line in Coconut source)
                        if _coconut_case_match_check_0:  #97 (line in Coconut source)
                            _coconut_case_match_check_0 = False  #97 (line in Coconut source)
                            if not _coconut_case_match_check_0:  #97 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #97 (line in Coconut source)
                                    _coconut_case_match_check_0 = True  #97 (line in Coconut source)

                            if not _coconut_case_match_check_0:  #97 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #97 (line in Coconut source)
                                    _coconut_match_temp_2 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #97 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #97 (line in Coconut source)
                                        raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #97 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_2) < 0:  #97 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #97 (line in Coconut source)
                                    _coconut_case_match_check_0 = True  #97 (line in Coconut source)




                if _coconut_case_match_check_0 and not (parent.is_valid):  #97 (line in Coconut source)
                    _coconut_case_match_check_0 = False  #97 (line in Coconut source)
                if _coconut_case_match_check_0:  #97 (line in Coconut source)
                    agent_id = parent.node_id  #99 (line in Coconut source)
                    if agent_id not in tool_to_agents:  #100 (line in Coconut source)
                        tool_to_agents[agent_id] = []  #101 (line in Coconut source)
                    tool_to_agents[agent_id].append((parent, tool_node, tool_score, edge.weight))  #102 (line in Coconut source)

# Step 3: Build rank lookup for direct agent hits
    agent_rank_score: dict[str, tuple[int, float]] = {node.node_id: (rank, score) for rank, (node, score) in enumerate(agent_hits) if isinstance(node, AgentNode)}  #107 (line in Coconut source)

# Step 4: Build fused score for every candidate agent
    candidates: dict[str, dict[str, Any]] = {}  #114 (line in Coconut source)

# From direct agent hits — score = w_agent * cosine / (rank + k)
    for rank, (node, cosine) in enumerate(agent_hits):  #117 (line in Coconut source)
        _coconut_case_match_to_2 = node  #118 (line in Coconut source)
        _coconut_case_match_check_2 = False  #118 (line in Coconut source)
        _coconut_match_temp_6 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #118 (line in Coconut source)
        _coconut_case_match_check_2 = True  #118 (line in Coconut source)
        if _coconut_case_match_check_2:  #118 (line in Coconut source)
            _coconut_case_match_check_2 = False  #118 (line in Coconut source)
            if not _coconut_case_match_check_2:  #118 (line in Coconut source)
                if (_coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_2, AgentNode)):  #118 (line in Coconut source)
                    _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #118 (line in Coconut source)
                    if _coconut_match_temp_7:  #118 (line in Coconut source)
                        _coconut_case_match_check_2 = True  #118 (line in Coconut source)

            if not _coconut_case_match_check_2:  #118 (line in Coconut source)
                if (not _coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_2, AgentNode)):  #118 (line in Coconut source)
                    _coconut_case_match_check_2 = True  #118 (line in Coconut source)
                if _coconut_case_match_check_2:  #118 (line in Coconut source)
                    _coconut_case_match_check_2 = False  #118 (line in Coconut source)
                    if not _coconut_case_match_check_2:  #118 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #118 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #118 (line in Coconut source)

                    if not _coconut_case_match_check_2:  #118 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #118 (line in Coconut source)
                            _coconut_match_temp_8 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #118 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #118 (line in Coconut source)
                                raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #118 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_8) < 0:  #118 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #118 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #118 (line in Coconut source)




        if _coconut_case_match_check_2:  #118 (line in Coconut source)
            candidates[node.node_id] = {"agent": node, "agent_score": w_agent * cosine / (rank + k), "tool_score": 0.0, "via_tools": [], "tool_scores": []}  #120 (line in Coconut source)

# From tool-inferred agents — score = w_tool * cosine * edge_weight / (rank + k)
    for agent_id, entries in tool_to_agents.items():  #129 (line in Coconut source)
# Pick the entry whose tool has the best (lowest) rank
        best_entry = min(entries, key=lambda e: tool_rank_score.get(e[1].node_id, (top_k_tools, 0.0))[0])  #131 (line in Coconut source)
        best_rank, best_cosine = tool_rank_score.get(best_entry[1].node_id, (top_k_tools, 0.0))  #135 (line in Coconut source)
        best_edge_weight = best_entry[3]  #138 (line in Coconut source)
        tool_score = w_tool * best_cosine * best_edge_weight / (best_rank + k)  #139 (line in Coconut source)

# Tag overlap bonus: score boost per concept tag shared between the
# best-ranked tool and the caller-supplied query_tags.
        if query_tags:  #143 (line in Coconut source)
            best_tool = best_entry[1]  #144 (line in Coconut source)
            overlap = len(set(best_tool.tags) & set(query_tags))  #145 (line in Coconut source)
            tool_score += overlap * tag_weight  #146 (line in Coconut source)

        a_rank, a_cosine = agent_rank_score.get(agent_id, (top_k_agents, 0.0))  #148 (line in Coconut source)
        agent_score = w_agent * a_cosine / (a_rank + k)  #149 (line in Coconut source)

        if agent_id not in candidates:  #151 (line in Coconut source)
            candidates[agent_id] = {"agent": best_entry[0], "agent_score": agent_score, "tool_score": tool_score, "via_tools": [e[1] for e in entries], "tool_scores": [e[2] for e in entries]}  #152 (line in Coconut source)
        else:  #159 (line in Coconut source)
            candidates[agent_id]["tool_score"] += tool_score  #160 (line in Coconut source)
            candidates[agent_id]["via_tools"] += [e[1] for e in entries]  #161 (line in Coconut source)
            candidates[agent_id]["tool_scores"] += [e[2] for e in entries]  #162 (line in Coconut source)

# Step 5: Rank by fused score
    ranked = sorted(candidates.values(), key=lambda c: c["agent_score"] + c["tool_score"], reverse=True)  #165 (line in Coconut source)

    return [RetrievalResult(agent=c["agent"], score=c["agent_score"] + c["tool_score"], via_tools=c["via_tools"], tool_scores=c["tool_scores"]) for c in ranked[:top_k]]  #171 (line in Coconut source)
