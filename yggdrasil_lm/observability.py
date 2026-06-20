#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x46b9d09a

# Compiled with Coconut version 3.2.0

"""Data API for structured trace inspection.

This module is the canonical home for functions that return typed objects
from an execution trace. It does NOT render to a terminal or start a server.
"""

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
_coconut_header_info = ('3.2.0', '311', False)
_coconut_cached__coconut__ = _coconut_sys.modules.get('__coconut__')
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.abspath(__file__))
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



from dataclasses import dataclass  #7 (line in Coconut source)
from dataclasses import field  #7 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #8 (line in Coconut source)
    from typing import Any  #8 (line in Coconut source)
else:  #8 (line in Coconut source)
    try:  #8 (line in Coconut source)
        Any = _coconut.typing.Any  #8 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #8 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #8 (line in Coconut source)

from yggdrasil_lm.core.executor import ExecutionContext  #10 (line in Coconut source)
from yggdrasil_lm.core.executor import TraceEvent  #10 (line in Coconut source)
from yggdrasil_lm.core.executor import cleanup_session  #10 (line in Coconut source)
from yggdrasil_lm.core.executor import get_runtime_nodes  #10 (line in Coconut source)
from yggdrasil_lm.core.executor import print_trace  #10 (line in Coconut source)
from yggdrasil_lm.exporters.otel import export_trace  #17 (line in Coconut source)
from yggdrasil_lm.trace_ui import inspect_trace  #18 (line in Coconut source)


@dataclass  #21 (line in Coconut source)
class RunHopExplanation():  #22 (line in Coconut source)
    node_id: str  #23 (line in Coconut source)
    node_name: str  #24 (line in Coconut source)
    hop: int | None  #25 (line in Coconut source)
    summary: str = ""  #26 (line in Coconut source)


@dataclass  #29 (line in Coconut source)
class RunRoutingExplanation():  #30 (line in Coconut source)
    node_id: str  #31 (line in Coconut source)
    node_name: str  #32 (line in Coconut source)
    intent: str | None  #33 (line in Coconut source)
    next_node_id: str | None  #34 (line in Coconut source)
    confidence: float | None  #35 (line in Coconut source)
    mode: str = "llm"  #36 (line in Coconut source)


@dataclass  #39 (line in Coconut source)
class RunContextExplanation():  #40 (line in Coconut source)
    node_id: str  #41 (line in Coconut source)
    node_name: str  #42 (line in Coconut source)
    selected_contexts: list[dict[str, Any]] = field(default_factory=list)  #43 (line in Coconut source)


@dataclass  #46 (line in Coconut source)
class RunToolCallExplanation():  #47 (line in Coconut source)
    node_id: str  #48 (line in Coconut source)
    tool_name: str  #49 (line in Coconut source)
    callable_ref: str  #50 (line in Coconut source)
    input: dict[str, Any] = field(default_factory=dict)  #51 (line in Coconut source)


@dataclass  #54 (line in Coconut source)
class RunPauseExplanation():  #55 (line in Coconut source)
    node_id: str  #56 (line in Coconut source)
    node_name: str  #57 (line in Coconut source)
    waiting_for: Any = None  #58 (line in Coconut source)
    reason: str = ""  #59 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #60 (line in Coconut source)


@dataclass  #63 (line in Coconut source)
class RunSummary():  #64 (line in Coconut source)
    routing_decision_count: int = 0  #65 (line in Coconut source)
    tool_call_count: int = 0  #66 (line in Coconut source)
    context_injection_count: int = 0  #67 (line in Coconut source)
    pause_event_count: int = 0  #68 (line in Coconut source)


@dataclass  #71 (line in Coconut source)
class RunExplanation():  #72 (line in Coconut source)
    session_id: str  #73 (line in Coconut source)
    query: str  #74 (line in Coconut source)
    hop_count: int  #75 (line in Coconut source)
    paused: bool  #76 (line in Coconut source)
    hops: list[RunHopExplanation] = field(default_factory=list)  #77 (line in Coconut source)
    routing: list[RunRoutingExplanation] = field(default_factory=list)  #78 (line in Coconut source)
    context: list[RunContextExplanation] = field(default_factory=list)  #79 (line in Coconut source)
    tool_calls: list[RunToolCallExplanation] = field(default_factory=list)  #80 (line in Coconut source)
    pauses: list[RunPauseExplanation] = field(default_factory=list)  #81 (line in Coconut source)
    summary: RunSummary = field(default_factory=RunSummary)  #82 (line in Coconut source)


@dataclass  #85 (line in Coconut source)
class TraceView():  #86 (line in Coconut source)
    hops: list[TraceEvent] = field(default_factory=list)  #87 (line in Coconut source)
    agent_starts: list[TraceEvent] = field(default_factory=list)  #88 (line in Coconut source)
    agent_ends: list[TraceEvent] = field(default_factory=list)  #89 (line in Coconut source)
    tool_calls: list[TraceEvent] = field(default_factory=list)  #90 (line in Coconut source)
    tool_results: list[TraceEvent] = field(default_factory=list)  #91 (line in Coconut source)
    context_inject: list[TraceEvent] = field(default_factory=list)  #92 (line in Coconut source)
    routing: list[TraceEvent] = field(default_factory=list)  #93 (line in Coconut source)
    pauses: list[TraceEvent] = field(default_factory=list)  #94 (line in Coconut source)


def extract_trace_view(events: list[TraceEvent]) -> TraceView:  #97 (line in Coconut source)
    view = TraceView()  #98 (line in Coconut source)
    for event in events:  #99 (line in Coconut source)
        _coconut_case_match_to_0 = event.event_type  #100 (line in Coconut source)
        _coconut_case_match_check_0 = False  #100 (line in Coconut source)
        if _coconut_case_match_to_0 == "hop":  #100 (line in Coconut source)
            _coconut_case_match_check_0 = True  #100 (line in Coconut source)
        if _coconut_case_match_check_0:  #100 (line in Coconut source)
            view.hops.append(event)  #102 (line in Coconut source)
        if not _coconut_case_match_check_0:  #103 (line in Coconut source)
            if _coconut_case_match_to_0 == "agent_start":  #103 (line in Coconut source)
                _coconut_case_match_check_0 = True  #103 (line in Coconut source)
            if _coconut_case_match_check_0:  #103 (line in Coconut source)
                view.agent_starts.append(event)  #104 (line in Coconut source)
        if not _coconut_case_match_check_0:  #105 (line in Coconut source)
            if _coconut_case_match_to_0 == "agent_end":  #105 (line in Coconut source)
                _coconut_case_match_check_0 = True  #105 (line in Coconut source)
            if _coconut_case_match_check_0:  #105 (line in Coconut source)
                view.agent_ends.append(event)  #106 (line in Coconut source)
        if not _coconut_case_match_check_0:  #107 (line in Coconut source)
            if _coconut_case_match_to_0 == "tool_call":  #107 (line in Coconut source)
                _coconut_case_match_check_0 = True  #107 (line in Coconut source)
            if _coconut_case_match_check_0:  #107 (line in Coconut source)
                view.tool_calls.append(event)  #108 (line in Coconut source)
        if not _coconut_case_match_check_0:  #109 (line in Coconut source)
            if _coconut_case_match_to_0 == "tool_result":  #109 (line in Coconut source)
                _coconut_case_match_check_0 = True  #109 (line in Coconut source)
            if _coconut_case_match_check_0:  #109 (line in Coconut source)
                view.tool_results.append(event)  #110 (line in Coconut source)
        if not _coconut_case_match_check_0:  #111 (line in Coconut source)
            if _coconut_case_match_to_0 == "context_inject":  #111 (line in Coconut source)
                _coconut_case_match_check_0 = True  #111 (line in Coconut source)
            if _coconut_case_match_check_0:  #111 (line in Coconut source)
                view.context_inject.append(event)  #112 (line in Coconut source)
        if not _coconut_case_match_check_0:  #113 (line in Coconut source)
            if _coconut_case_match_to_0 == "routing":  #113 (line in Coconut source)
                _coconut_case_match_check_0 = True  #113 (line in Coconut source)
            if _coconut_case_match_check_0:  #113 (line in Coconut source)
                view.routing.append(event)  #114 (line in Coconut source)
        if not _coconut_case_match_check_0:  #115 (line in Coconut source)
            if _coconut_case_match_to_0 == "pause":  #115 (line in Coconut source)
                _coconut_case_match_check_0 = True  #115 (line in Coconut source)
            if _coconut_case_match_check_0:  #115 (line in Coconut source)
                view.pauses.append(event)  #116 (line in Coconut source)
    return view  #117 (line in Coconut source)



@_coconut_tco  #120 (line in Coconut source)
def explain_run(ctx: ExecutionContext) -> RunExplanation:  #120 (line in Coconut source)
    """Summarize why a run behaved the way it did."""  #121 (line in Coconut source)
    view = extract_trace_view(ctx.trace)  #122 (line in Coconut source)
    paused = ctx.is_paused() or bool(view.pauses)  #123 (line in Coconut source)

    return _coconut_tail_call(RunExplanation, session_id=ctx.session_id, query=ctx.query, hop_count=ctx.hop_count, paused=paused, hops=[RunHopExplanation(node_id=e.node_id, node_name=e.node_name, hop=e.payload.get("hop"), summary=e.payload.get("summary", "")) for e in view.hops], routing=[RunRoutingExplanation(node_id=e.node_id, node_name=e.node_name, intent=e.payload.get("intent"), next_node_id=e.payload.get("next_node_id"), confidence=e.payload.get("confidence"), mode=e.payload.get("mode", "llm")) for e in view.routing], context=[RunContextExplanation(node_id=e.node_id, node_name=e.node_name, selected_contexts=e.payload.get("selected_contexts", [])) for e in view.context_inject], tool_calls=[RunToolCallExplanation(node_id=e.node_id, tool_name=e.payload.get("tool_name", e.node_name), callable_ref=e.payload.get("callable_ref", ""), input=e.payload.get("input", {})) for e in view.tool_calls], pauses=[RunPauseExplanation(node_id=e.node_id, node_name=e.node_name, waiting_for=e.payload.get("waiting_for"), reason=e.payload.get("reason", ""), metadata=e.payload.get("metadata", {})) for e in view.pauses], summary=RunSummary(routing_decision_count=len(view.routing), tool_call_count=len(view.tool_calls), context_injection_count=len(view.context_inject), pause_event_count=len(view.pauses)))  #125 (line in Coconut source)



__all__ = ["explain_run", "export_trace", "RunExplanation", "cleanup_session", "get_runtime_nodes", "inspect_trace", "print_trace"]  #186 (line in Coconut source)
