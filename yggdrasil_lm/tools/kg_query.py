#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x5a379f3e

# Compiled with Coconut version 3.2.0

"""Knowledge-graph-as-factbase tools.

These let an ``AgentNode`` (the neural side) query the typed, temporal knowledge
graph (the symbolic side) at runtime — neighbours, reachability, and a dump of
edges/nodes as ground Datalog facts that can be fed straight into a
:class:`~yggdrasil_lm.core.nodes.ReasonerNode`.

Every callable opts into the live ``GraphStore`` by declaring a ``store``
keyword parameter; the executor injects it automatically (see
``GraphExecutor._callable_injection_kwargs``). Register them with
``app.use_default_tools()`` or ``executor.register_tool(ref, fn)``.
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



if _coconut.typing.TYPE_CHECKING:  #14 (line in Coconut source)
    from typing import Any  #14 (line in Coconut source)
else:  #14 (line in Coconut source)
    try:  #14 (line in Coconut source)
        Any = _coconut.typing.Any  #14 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #14 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #14 (line in Coconut source)

from yggdrasil_lm.core.edges import EdgeType  #16 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #17 (line in Coconut source)


def _label(node: Any, use_names: bool) -> str:  #20 (line in Coconut source)
    if node is None:  #21 (line in Coconut source)
        return ""  #22 (line in Coconut source)
    return node.name if (use_names and getattr(node, "name", "")) else node.node_id  #23 (line in Coconut source)



async def neighbors(input: dict[str, Any], *, store: GraphStore) -> dict[str, Any]:  #26 (line in Coconut source)
    """Return neighbours of a node, optionally filtered by edge type.

    Input: ``{"node_id": str, "edge_type": str|None, "depth": int=1,
              "use_names": bool=True}``
    """  #31 (line in Coconut source)
    node_id = input.get("node_id", "")  #32 (line in Coconut source)
    if not node_id:  #33 (line in Coconut source)
        return {"error": "node_id required", "neighbors": []}  #34 (line in Coconut source)
    etype = _coerce_edge_type(input.get("edge_type"))  #35 (line in Coconut source)
    depth = int(input.get("depth", 1))  #36 (line in Coconut source)
    use_names = bool(input.get("use_names", True))  #37 (line in Coconut source)
    nodes = await store.neighbors(node_id, edge_type=etype, depth=depth)  #38 (line in Coconut source)
    return {"neighbors": [{"node_id": n.node_id, "name": n.name, "node_type": str(n.node_type)} for n in nodes], "labels": [_label(n, use_names) for n in nodes], "count": len(nodes)}  #39 (line in Coconut source)



async def reachable(input: dict[str, Any], *, store: GraphStore) -> dict[str, Any]:  #49 (line in Coconut source)
    """Transitive reachability from a node along one edge type (BFS closure).

    Input: ``{"node_id": str, "edge_type": str, "max_depth": int=16,
              "use_names": bool=True}``
    Returns the set of reachable node labels and whether ``target`` (optional)
    is reachable.
    """  #56 (line in Coconut source)
    node_id = input.get("node_id", "")  #57 (line in Coconut source)
    if not node_id:  #58 (line in Coconut source)
        return {"error": "node_id required", "reachable": []}  #59 (line in Coconut source)
    etype = _coerce_edge_type(input.get("edge_type"))  #60 (line in Coconut source)
    max_depth = int(input.get("max_depth", 16))  #61 (line in Coconut source)
    use_names = bool(input.get("use_names", True))  #62 (line in Coconut source)

    visited: set[str] = set()  #64 (line in Coconut source)
    frontier = {node_id}  #65 (line in Coconut source)
    for _ in range(max_depth):  #66 (line in Coconut source)
        nxt: set[str] = set()  #67 (line in Coconut source)
        for nid in frontier:  #68 (line in Coconut source)
            for e in await store.get_edges(nid, edge_type=etype, direction="out"):  #69 (line in Coconut source)
                if e.dst_id not in visited and e.dst_id != node_id:  #70 (line in Coconut source)
                    nxt.add(e.dst_id)  #71 (line in Coconut source)
        visited |= frontier  #72 (line in Coconut source)
        frontier = nxt - visited  #73 (line in Coconut source)
        if not frontier:  #74 (line in Coconut source)
            break  #75 (line in Coconut source)
    visited.discard(node_id)  #76 (line in Coconut source)

    labels = []  #78 (line in Coconut source)
    for nid in visited:  #79 (line in Coconut source)
        n = await store.get_node(nid)  #80 (line in Coconut source)
        if n:  #81 (line in Coconut source)
            labels.append(_label(n, use_names))  #82 (line in Coconut source)

    target = input.get("target")  #84 (line in Coconut source)
    result: dict[str, Any] = {"reachable": sorted(labels), "count": len(labels)}  #85 (line in Coconut source)
    if target is not None:  #86 (line in Coconut source)
        result["target_reachable"] = target in set(labels) or target in visited  #87 (line in Coconut source)
    return result  #88 (line in Coconut source)



async def facts(input: dict[str, Any], *, store: GraphStore) -> dict[str, Any]:  #91 (line in Coconut source)
    """Dump the graph as ground Datalog facts ready for a ReasonerNode.

    Edges become binary facts ``edge_type(src, dst)``; when ``include_nodes`` is
    set, each node becomes a unary fact ``node_type(label)``.

    Input: ``{"edge_types": [str]|None, "include_nodes": bool=False,
              "use_names": bool=True}``  (``edge_types=None`` ⟹ all edge types)
    Returns ``{"facts": [["edge_type","src","dst"], ...]}`` — list form, which
    ``normalise_fact`` accepts directly.
    """  #101 (line in Coconut source)
    use_names = bool(input.get("use_names", True))  #102 (line in Coconut source)
    requested = input.get("edge_types")  #103 (line in Coconut source)
    wanted = {str(t) for t in requested} if requested else None  #104 (line in Coconut source)

    out: list[list[Any]] = []  #106 (line in Coconut source)
    label_cache: dict[str, str] = {}  #107 (line in Coconut source)

    async def lbl(nid: str) -> str:  #109 (line in Coconut source)
        if nid not in label_cache:  #110 (line in Coconut source)
            label_cache[nid] = _label(await store.get_node(nid), use_names)  #111 (line in Coconut source)
        return label_cache[nid]  #112 (line in Coconut source)


    for e in await store.list_edges():  #114 (line in Coconut source)
        etype = str(e.edge_type)  #115 (line in Coconut source)
        if wanted is not None and etype not in wanted:  #116 (line in Coconut source)
            continue  #117 (line in Coconut source)
        out.append([etype.lower(), await lbl(e.src_id), await lbl(e.dst_id)])  #118 (line in Coconut source)

    if input.get("include_nodes"):  #120 (line in Coconut source)
        for n in await store.list_nodes():  #121 (line in Coconut source)
            out.append([str(n.node_type), _label(n, use_names)])  #122 (line in Coconut source)

    return {"facts": out, "count": len(out)}  #124 (line in Coconut source)



def _coerce_edge_type(value: Any) -> EdgeType | None:  #127 (line in Coconut source)
    if not value:  #128 (line in Coconut source)
        return None  #129 (line in Coconut source)
    try:  #130 (line in Coconut source)
        return EdgeType(value)  #131 (line in Coconut source)
    except ValueError:  #132 (line in Coconut source)
        return None  #133 (line in Coconut source)
