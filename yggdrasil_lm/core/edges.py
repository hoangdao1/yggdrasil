#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xc76ae8ef

# Compiled with Coconut version 3.2.0

"""Edge types for the yggdrasil system.

Edges are typed, weighted, and temporally valid.
Multiple edge types can exist between the same two nodes (multi-relational graph).
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



import uuid  #7 (line in Coconut source)
from datetime import datetime  #8 (line in Coconut source)
from datetime import timezone  #8 (line in Coconut source)
from enum import StrEnum  #9 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #10 (line in Coconut source)
    from typing import Any  #10 (line in Coconut source)
else:  #10 (line in Coconut source)
    try:  #10 (line in Coconut source)
        Any = _coconut.typing.Any  #10 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #10 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #10 (line in Coconut source)

from pydantic import BaseModel  #12 (line in Coconut source)
from pydantic import Field  #12 (line in Coconut source)


@_coconut_tco  #15 (line in Coconut source)
def _now() -> datetime:  #15 (line in Coconut source)
    return _coconut_tail_call(datetime.now, timezone.utc)  #16 (line in Coconut source)



@_coconut_tco  #19 (line in Coconut source)
def _uuid() -> str:  #19 (line in Coconut source)
    return _coconut_tail_call(str, uuid.uuid4())  #20 (line in Coconut source)


# ---------------------------------------------------------------------------
# Edge type enum
# ---------------------------------------------------------------------------


class EdgeType(StrEnum):  #27 (line in Coconut source)
# Composition edges — define what an agent IS made of
    HAS_TOOL = "HAS_TOOL"  # agent → tool  #29 (line in Coconut source)
    HAS_CONTEXT = "HAS_CONTEXT"  # agent → context  #30 (line in Coconut source)
    HAS_PROMPT = "HAS_PROMPT"  # agent → prompt  #31 (line in Coconut source)

# Control-flow edges
    DELEGATES_TO = "DELEGATES_TO"  # agent → agent (routing / delegation)  #34 (line in Coconut source)

# Provenance edges — track execution history in the graph
    PRODUCES = "PRODUCES"  # agent/tool → context (output materialised as node)  #37 (line in Coconut source)

# Knowledge edges — document/entity relationships
    MENTIONS = "MENTIONS"  # context → entity  #40 (line in Coconut source)
    NEXT = "NEXT"  # context → context (sequence within a doc)  #41 (line in Coconut source)

# Knowledge edges — concept taxonomy
    COVERS = "COVERS"  # context → concept tag (for structured filtering)  #44 (line in Coconut source)

# Retrieval edges — populated by the embedder / indexer
    SIMILAR_TO = "SIMILAR_TO"  # any → any (semantic similarity)  #47 (line in Coconut source)

# Validation edges
    VALIDATES = "VALIDATES"  # schema → tool/context  #50 (line in Coconut source)

# Meta-graph edges
    CONTAINS = "CONTAINS"  # graph-node → node (sub-graph membership)  #53 (line in Coconut source)


# ---------------------------------------------------------------------------
# Edge model
# ---------------------------------------------------------------------------

class Edge(BaseModel):  #60 (line in Coconut source)
    """A typed, weighted, temporally-valid directed edge between two nodes.

    Temporal validity:
    - valid_at / invalid_at control when this relationship is active.
    - Setting invalid_at=now() retires an edge without deleting it,
      preserving history for point-in-time queries.
    """  #67 (line in Coconut source)

    edge_id: str = Field(default_factory=_uuid)  #69 (line in Coconut source)
    edge_type: EdgeType = EdgeType.HAS_CONTEXT  #70 (line in Coconut source)
    src_id: str = ""  #71 (line in Coconut source)
    dst_id: str = ""  #72 (line in Coconut source)

# Relationship strength — used to rank context nodes when composing agents.
# Higher weight = more relevant context injected first.
    weight: float = 1.0  #76 (line in Coconut source)

# Optional LLM-generated or human-written relationship summary.
    description: str = ""  #79 (line in Coconut source)

# Extensible metadata
    attributes: dict[str, Any] = Field(default_factory=dict)  #82 (line in Coconut source)

# Temporal validity
    valid_at: datetime = Field(default_factory=_now)  #85 (line in Coconut source)
    invalid_at: datetime | None = None  #86 (line in Coconut source)

# Partition key (same as nodes)
    group_id: str = "default"  #89 (line in Coconut source)

# Workflow / graph versioning
    version: int = 1  #92 (line in Coconut source)
    graph_version: str = "v1"  #93 (line in Coconut source)
    graph_revision_id: str = ""  #94 (line in Coconut source)

# Minimal role-based access control for traversals that rely on edges
    required_roles: list[str] = Field(default_factory=list)  #97 (line in Coconut source)

    @property  #99 (line in Coconut source)
    def is_valid(self) -> bool:  #100 (line in Coconut source)
        """True if this edge is currently active."""  #101 (line in Coconut source)
        now = _now()  #102 (line in Coconut source)
        return self.valid_at <= now and (self.invalid_at is None or self.invalid_at > now)  #103 (line in Coconut source)


    @_coconut_tco  #107 (line in Coconut source)
    def expire(self) -> "Edge":  #107 (line in Coconut source)
        """Return a copy of this edge marked as expired right now."""  #108 (line in Coconut source)
        return _coconut_tail_call(self.model_copy, update={"invalid_at": _now()})  #109 (line in Coconut source)


    @classmethod  #111 (line in Coconut source)
    @_coconut_tco  #112 (line in Coconut source)
    def has_tool(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":  #112 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.HAS_TOOL, src_id=src_id, dst_id=dst_id, **kw)  #113 (line in Coconut source)


    @classmethod  #115 (line in Coconut source)
    @_coconut_tco  #116 (line in Coconut source)
    def has_context(cls, src_id: str, dst_id: str, weight: float=1.0, **kw: Any) -> "Edge":  #116 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.HAS_CONTEXT, src_id=src_id, dst_id=dst_id, weight=weight, **kw)  #117 (line in Coconut source)


    @classmethod  #119 (line in Coconut source)
    @_coconut_tco  #120 (line in Coconut source)
    def has_prompt(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":  #120 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.HAS_PROMPT, src_id=src_id, dst_id=dst_id, **kw)  #121 (line in Coconut source)


    @classmethod  #123 (line in Coconut source)
    @_coconut_tco  #124 (line in Coconut source)
    def delegates_to(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":  #124 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.DELEGATES_TO, src_id=src_id, dst_id=dst_id, **kw)  #125 (line in Coconut source)


    @classmethod  #127 (line in Coconut source)
    @_coconut_tco  #128 (line in Coconut source)
    def produces(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":  #128 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.PRODUCES, src_id=src_id, dst_id=dst_id, **kw)  #129 (line in Coconut source)


    @classmethod  #131 (line in Coconut source)
    @_coconut_tco  #132 (line in Coconut source)
    def similar_to(cls, src_id: str, dst_id: str, weight: float=1.0, **kw: Any) -> "Edge":  #132 (line in Coconut source)
        return _coconut_tail_call(cls, edge_type=EdgeType.SIMILAR_TO, src_id=src_id, dst_id=dst_id, weight=weight, **kw)  #133 (line in Coconut source)
