#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x1ea89948

# Compiled with Coconut version 3.2.0

"""Agent composition and graph execution engine.

Key components:
- AgentComposer  — discovers an agent's tools/context/prompt by traversing edges
- ComposedAgent  — assembled runtime configuration for a single agent invocation
- ExecutionContext — shared mutable state that flows through the graph during a run
- GraphExecutor  — dispatches nodes and follows routing edges to traverse the graph
- TraceEvent     — structured, typed execution event for full observability
- print_trace()  — render a session trace as a human-readable execution tree

Execution strategies:
- sequential  : DFS — run node, route to next, repeat (default for chains)
- parallel    : BFS fan-out — gather all DELEGATES_TO targets concurrently
- topological : DAG waves — graphlib.TopologicalSorter for explicit pipelines
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



import asyncio  #17 (line in Coconut source)
import graphlib  #18 (line in Coconut source)
import inspect  #19 (line in Coconut source)
import json  #20 (line in Coconut source)
import logging  #21 (line in Coconut source)
import re  #22 (line in Coconut source)
import time  #23 (line in Coconut source)
import uuid  #24 (line in Coconut source)
from collections import deque  #25 (line in Coconut source)
from dataclasses import dataclass  #26 (line in Coconut source)
from dataclasses import field  #26 (line in Coconut source)
from datetime import datetime  #27 (line in Coconut source)
from datetime import timedelta  #27 (line in Coconut source)
from datetime import timezone  #27 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Any  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Any = _coconut.typing.Any  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Callable  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Callable = _coconut.typing.Callable  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Literal  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Literal = _coconut.typing.Literal  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)

from yggdrasil_lm.backends.llm import LLMBackend  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import ToolResult  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import default_backend  #30 (line in Coconut source)
from yggdrasil_lm.core.edges import Edge  #31 (line in Coconut source)
from yggdrasil_lm.core.edges import EdgeType  #31 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ApprovalNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import AnyNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ConstraintRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ContextNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import DecisionRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import DecisionTable  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ExecutionPolicy  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import GraphNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import PromptNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ReasonerNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import RouteRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import SchemaNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import TransformNode  #32 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #50 (line in Coconut source)
from yggdrasil_lm.core.store import _cosine  #50 (line in Coconut source)
from yggdrasil_lm.core.store import _normalize  #50 (line in Coconut source)


# ---------------------------------------------------------------------------
# TraceEvent — structured, typed execution event
# ---------------------------------------------------------------------------

EventType = Literal["agent_start", "agent_end", "tool_call", "tool_result", "routing", "context_inject", "hop", "subgraph_enter", "subgraph_exit", "pause", "resume", "retry", "validation", "permission_denied", "checkpoint", "transaction", "approval_task", "lease", "schedule", "migration", "error",]  #57 (line in Coconut source)

_log = logging.getLogger(__name__)  #81 (line in Coconut source)

# Type alias for multimodal query content (mirrors the Anthropic Messages API).
# A plain str is treated as a single text block.  A list follows the Anthropic
# content-block schema: {"type": "text", "text": "..."} or
# {"type": "image", "source": {"type": "base64"|"url", ...}}.
QueryContent = str | list[dict[str, Any]]  #87 (line in Coconut source)


@_coconut_tco  #90 (line in Coconut source)
def _query_text(query: QueryContent) -> str:  #90 (line in Coconut source)
    """Extract the plain-text portion of a query for routing and context scoring."""  #91 (line in Coconut source)
    _coconut_case_match_to_0 = query  #92 (line in Coconut source)
    _coconut_case_match_check_0 = False  #92 (line in Coconut source)
    _coconut_match_temp_0 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #92 (line in Coconut source)
    _coconut_case_match_check_0 = True  #92 (line in Coconut source)
    if _coconut_case_match_check_0:  #92 (line in Coconut source)
        _coconut_case_match_check_0 = False  #92 (line in Coconut source)
        if not _coconut_case_match_check_0:  #92 (line in Coconut source)
            if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #92 (line in Coconut source)
                _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #92 (line in Coconut source)
                if _coconut_match_temp_1:  #92 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #92 (line in Coconut source)

        if not _coconut_case_match_check_0:  #92 (line in Coconut source)
            if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #92 (line in Coconut source)
                _coconut_case_match_check_0 = True  #92 (line in Coconut source)
            if _coconut_case_match_check_0:  #92 (line in Coconut source)
                _coconut_case_match_check_0 = False  #92 (line in Coconut source)
                if not _coconut_case_match_check_0:  #92 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #92 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #92 (line in Coconut source)

                if not _coconut_case_match_check_0:  #92 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #92 (line in Coconut source)
                        _coconut_match_temp_2 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #92 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #92 (line in Coconut source)
                            raise _coconut.TypeError("str.__match_args__ must be a tuple")  #92 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_2) < 0:  #92 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #92 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #92 (line in Coconut source)




    if _coconut_case_match_check_0:  #92 (line in Coconut source)
        return query  #94 (line in Coconut source)
    if not _coconut_case_match_check_0:  #95 (line in Coconut source)
        _coconut_case_match_check_0 = True  #95 (line in Coconut source)
        if _coconut_case_match_check_0:  #95 (line in Coconut source)
            return _coconut_tail_call(" ".join, (block.get("text", "") for block in query if block.get("type") == "text"))  #96 (line in Coconut source)



@dataclass  #99 (line in Coconut source)
class TraceEvent():  #100 (line in Coconut source)
    """A single typed event in the execution trace.

    Events form a tree via parent_event_id:
    - agent_start spawns child events (context_inject, tool_call, tool_result, routing)
    - agent_end closes the agent_start span with duration_ms
    - hop records sequential graph traversal steps

    Payload keys per event_type:
    - agent_start:     model, tools (list[str]), context (list[str]), query
    - agent_end:       text_summary (str), intent (str), iterations (int)
    - tool_call:       tool_name (str), callable_ref (str), input (dict)
    - tool_result:     tool_name (str), output_summary (str), success (bool)
    - routing:         intent (str), next_node_id (str|None), confidence (float|None)
    - context_inject:  context_names (list[str]), count (int)
    - hop:             hop (int), node_type (str), summary (str)
    - subgraph_enter:  entry_node_id (str)
    - subgraph_exit:   exit_node_id (str), summary (str)
    """  #118 (line in Coconut source)

    event_type: EventType  #120 (line in Coconut source)
    session_id: str  #121 (line in Coconut source)
    node_id: str  #122 (line in Coconut source)
    node_name: str  #123 (line in Coconut source)
    timestamp: datetime  #124 (line in Coconut source)
    payload: dict[str, Any]  #125 (line in Coconut source)
    event_id: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #126 (line in Coconut source)
    parent_event_id: str | None = None  #127 (line in Coconut source)
    duration_ms: int | None = None  #128 (line in Coconut source)


# ---------------------------------------------------------------------------
# RoutingDecision — white-box routing result
# ---------------------------------------------------------------------------

class RoutingDecision(_coconut.collections.namedtuple("RoutingDecision", ('agent_id', 'reason', 'confidence'))):  #135 (line in Coconut source)
    """LLM routing decision with explicit reasoning and confidence.

    Returned by GraphExecutor.route() / plan() so callers can inspect and
    debug every dispatch choice before (or instead of) executing.
    """  #140 (line in Coconut source)

    __slots__ = ()  #142 (line in Coconut source)
    _coconut_is_data = True  #142 (line in Coconut source)
    __match_args__ = ('agent_id', 'reason', 'confidence')  #142 (line in Coconut source)
    def __add__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    def __mul__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    def __rmul__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    __ne__ = _coconut.object.__ne__  #142 (line in Coconut source)
    def __eq__(self, other):  #142 (line in Coconut source)
        return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)  #142 (line in Coconut source)
    def __hash__(self):  #142 (line in Coconut source)
        return _coconut.tuple.__hash__(self) ^ _coconut.hash(self.__class__)  #142 (line in Coconut source)
    @property  #142 (line in Coconut source)
    def low_confidence_warning(self) -> str | None:  #143 (line in Coconut source)
        """Non-None when confidence is below 0.7."""  #144 (line in Coconut source)
        if self.confidence < 0.7:  #145 (line in Coconut source)
            return (("Low-confidence routing ({_coconut_format_0:.0%}) — ".format(_coconut_format_0=(self.confidence)) + "consider specifying the agent explicitly."))  #146 (line in Coconut source)
        return None  #150 (line in Coconut source)


# ---------------------------------------------------------------------------
# AgentResult — structured execution envelope
# ---------------------------------------------------------------------------


@dataclass  #157 (line in Coconut source)
class AgentResult():  #158 (line in Coconut source)
    """Execution envelope returned by GraphExecutor.execute()."""  #159 (line in Coconut source)

    routed_to: str  #161 (line in Coconut source)
    reason: str  #162 (line in Coconut source)
    confidence: float  #163 (line in Coconut source)
    context_injected: list[str]  #164 (line in Coconut source)
    result: str  #165 (line in Coconut source)
    low_confidence_warning: str | None = None  #166 (line in Coconut source)


@dataclass  #169 (line in Coconut source)
class WorkflowPause():  #170 (line in Coconut source)
    """Represents a paused workflow waiting for external input or approval."""  #171 (line in Coconut source)

    reason: str  #173 (line in Coconut source)
    node_id: str  #174 (line in Coconut source)
    node_name: str = ""  #175 (line in Coconut source)
    token: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #176 (line in Coconut source)
    waiting_for: str | None = None  #177 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #178 (line in Coconut source)


@dataclass  #181 (line in Coconut source)
class ApprovalTask():  #182 (line in Coconut source)
    """Inbox item created by an ApprovalNode."""  #183 (line in Coconut source)

    task_id: str  #185 (line in Coconut source)
    node_id: str  #186 (line in Coconut source)
    token: str  #187 (line in Coconut source)
    status: str = "pending"  #188 (line in Coconut source)
    assignees: list[str] = field(default_factory=list)  #189 (line in Coconut source)
    assigned_to: str | None = None  #190 (line in Coconut source)
    waiting_for: str | None = None  #191 (line in Coconut source)
    due_at: datetime | None = None  #192 (line in Coconut source)
    escalation_target: str | None = None  #193 (line in Coconut source)
    created_at: datetime = field(default_factory=lambda _=None: datetime.now(timezone.utc))  #194 (line in Coconut source)
    resolved_at: datetime | None = None  #195 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #196 (line in Coconut source)


@dataclass  #199 (line in Coconut source)
class WorkflowState():  #200 (line in Coconut source)
    """Typed workflow state carried between nodes."""  #201 (line in Coconut source)

    data: dict[str, Any] = field(default_factory=dict)  #203 (line in Coconut source)
    schema: dict[str, Any] = field(default_factory=dict)  #204 (line in Coconut source)
    status: str = "running"  #205 (line in Coconut source)
    graph_version: str = "v1"  #206 (line in Coconut source)
    pending_pause: WorkflowPause | None = None  #207 (line in Coconut source)
    inbox: dict[str, ApprovalTask] = field(default_factory=dict)  #208 (line in Coconut source)
    idempotency_cache: dict[str, Any] = field(default_factory=dict)  #209 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #210 (line in Coconut source)


# ---------------------------------------------------------------------------
# ExecutionContext — flows through the graph during a run
# ---------------------------------------------------------------------------

@dataclass  #217 (line in Coconut source)
class ExecutionContext():  #218 (line in Coconut source)
    """Shared mutable state for a single graph traversal.

    Every node reads from and writes to this object.
    The trace list records the full execution history as structured TraceEvent
    objects so callers can inspect, render, or replay exactly what happened.
    """  #224 (line in Coconut source)

    query: QueryContent  #226 (line in Coconut source)
    session_id: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #227 (line in Coconut source)
    outputs: dict[str, Any] = field(default_factory=dict)  #228 (line in Coconut source)
    trace: list[TraceEvent] = field(default_factory=list)  #229 (line in Coconut source)
    max_hops: int = 20  #230 (line in Coconut source)
    hop_count: int = 0  #231 (line in Coconut source)

    extra_messages: list[dict[str, Any]] = field(default_factory=list)  #233 (line in Coconut source)
    state: WorkflowState = field(default_factory=WorkflowState)  #234 (line in Coconut source)
    allowed_tools: set[str] | None = None  #235 (line in Coconut source)
    _active_subgraphs: list[str] = field(default_factory=list)  #236 (line in Coconut source)

    def is_paused(self) -> bool:  #238 (line in Coconut source)
        return self.state.status == "paused"  #239 (line in Coconut source)


    def snapshot(self) -> dict[str, Any]:  #241 (line in Coconut source)
        """Serialize the execution context for durable checkpointing."""  #242 (line in Coconut source)
        return {"query": self.query, "session_id": self.session_id, "outputs": self.outputs, "trace": [{"event_type": event.event_type, "session_id": event.session_id, "node_id": event.node_id, "node_name": event.node_name, "timestamp": event.timestamp.isoformat(), "payload": event.payload, "event_id": event.event_id, "parent_event_id": event.parent_event_id, "duration_ms": event.duration_ms} for event in self.trace], "max_hops": self.max_hops, "hop_count": self.hop_count, "extra_messages": self.extra_messages, "state": {"data": self.state.data, "schema": self.state.schema, "status": self.state.status, "graph_version": self.state.graph_version, "pending_pause": None if self.state.pending_pause is None else {"reason": self.state.pending_pause.reason, "node_id": self.state.pending_pause.node_id, "node_name": self.state.pending_pause.node_name, "token": self.state.pending_pause.token, "waiting_for": self.state.pending_pause.waiting_for, "metadata": self.state.pending_pause.metadata}, "inbox": {task_id: {"task_id": task.task_id, "node_id": task.node_id, "token": task.token, "status": task.status, "assignees": task.assignees, "assigned_to": task.assigned_to, "waiting_for": task.waiting_for, "due_at": task.due_at.isoformat() if task.due_at else None, "escalation_target": task.escalation_target, "created_at": task.created_at.isoformat(), "resolved_at": task.resolved_at.isoformat() if task.resolved_at else None, "metadata": task.metadata} for task_id, task in self.state.inbox.items()}, "idempotency_cache": self.state.idempotency_cache, "metadata": self.state.metadata}, "allowed_tools": sorted(self.allowed_tools) if self.allowed_tools is not None else None}  #243 (line in Coconut source)


    @classmethod  #300 (line in Coconut source)
    @_coconut_tco  #301 (line in Coconut source)
    def from_snapshot(cls, data: dict[str, Any]) -> "ExecutionContext":  #301 (line in Coconut source)
        """Restore an execution context from snapshot data."""  #302 (line in Coconut source)
        raw_state = data.get("state", {})  #303 (line in Coconut source)
        pending_pause = raw_state.get("pending_pause")  #304 (line in Coconut source)
        state = WorkflowState(data=raw_state.get("data", {}), schema=raw_state.get("schema", {}), status=raw_state.get("status", "running"), graph_version=raw_state.get("graph_version", "v1"), pending_pause=(WorkflowPause(reason=pending_pause.get("reason", ""), node_id=pending_pause.get("node_id", ""), node_name=pending_pause.get("node_name", ""), token=pending_pause.get("token", str(uuid.uuid4())), waiting_for=pending_pause.get("waiting_for"), metadata=pending_pause.get("metadata", {})) if pending_pause else None), inbox={task_id: ApprovalTask(task_id=item.get("task_id", task_id), node_id=item.get("node_id", ""), token=item.get("token", str(uuid.uuid4())), status=item.get("status", "pending"), assignees=item.get("assignees", []), assigned_to=item.get("assigned_to"), waiting_for=item.get("waiting_for"), due_at=(datetime.fromisoformat(item["due_at"]) if item.get("due_at") else None), escalation_target=item.get("escalation_target"), created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.now(timezone.utc), resolved_at=(datetime.fromisoformat(item["resolved_at"]) if item.get("resolved_at") else None), metadata=item.get("metadata", {})) for task_id, item in raw_state.get("inbox", {}).items()}, idempotency_cache=raw_state.get("idempotency_cache", {}), metadata=raw_state.get("metadata", {}))  #305 (line in Coconut source)
        return _coconut_tail_call(cls, query=data.get("query", ""), session_id=data.get("session_id", str(uuid.uuid4())), outputs=data.get("outputs", {}), trace=[TraceEvent(event_type=item["event_type"], session_id=item.get("session_id", data.get("session_id", "")), node_id=item.get("node_id", ""), node_name=item.get("node_name", ""), timestamp=datetime.fromisoformat(item["timestamp"]), payload=item.get("payload", {}), event_id=item.get("event_id", str(uuid.uuid4())), parent_event_id=item.get("parent_event_id"), duration_ms=item.get("duration_ms")) for item in data.get("trace", [])], max_hops=data.get("max_hops", 20), hop_count=data.get("hop_count", 0), extra_messages=data.get("extra_messages", []), state=state, allowed_tools=set(data["allowed_tools"]) if data.get("allowed_tools") is not None else None)  #347 (line in Coconut source)


# ---------------------------------------------------------------------------
# Context navigation
# ---------------------------------------------------------------------------


@dataclass  #377 (line in Coconut source)
class ContextSelection():  #378 (line in Coconut source)
    """A scored, explainable context selection produced by ContextNavigator."""  #379 (line in Coconut source)

    context: ContextNode  #381 (line in Coconut source)
    score: float  #382 (line in Coconut source)
    source: str  #383 (line in Coconut source)
    hops: int = 0  #384 (line in Coconut source)
    path: list[str] = field(default_factory=list)  #385 (line in Coconut source)
    reasons: list[str] = field(default_factory=list)  #386 (line in Coconut source)
    token_count: int = 0  #387 (line in Coconut source)


@dataclass  #390 (line in Coconut source)
class ContextNavigator():  #391 (line in Coconut source)
    """Graph-native context retrieval with expansion, reranking, and budgeting."""  #392 (line in Coconut source)

    max_hops: int = 2  #394 (line in Coconut source)
    max_context_nodes: int = 8  #395 (line in Coconut source)
    max_context_tokens: int = 4000  #396 (line in Coconut source)
    semantic_top_k: int = 12  #397 (line in Coconut source)
    per_source_limit: int = 2  #398 (line in Coconut source)
    expansion_edge_types: tuple[EdgeType, ...] = (EdgeType.NEXT, EdgeType.SIMILAR_TO, EdgeType.MENTIONS, EdgeType.COVERS, EdgeType.PRODUCES)  #399 (line in Coconut source)
    path_decay: float = 0.85  #406 (line in Coconut source)
    tag_weight: float = 0.15  #407 (line in Coconut source)
    priority_weight: float = 0.1  #408 (line in Coconut source)
    recency_weight: float = 0.1  #409 (line in Coconut source)
    provenance_weight: float = 0.15  #410 (line in Coconut source)
    stale_fact_penalty: float = 0.4  #411 (line in Coconut source)
    exclude_stale_facts: bool = True  #412 (line in Coconut source)

    async def navigate(self, store: GraphStore, agent_node: AgentNode, *, query: str | None=None, embedder: Any=None, session_id: str | None=None,) -> list[ContextSelection]:  #414 (line in Coconut source)
        """Select context for an agent using graph traversal and token budgeting."""  #423 (line in Coconut source)
        direct_edges = await store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_CONTEXT)  #424 (line in Coconut source)
        direct_context_edges: dict[str, Edge] = {}  #425 (line in Coconut source)
        seed_map: dict[str, ContextSelection] = {}  #426 (line in Coconut source)

        query_vec: list[float] | None = None  #428 (line in Coconut source)
        if query and embedder:  #429 (line in Coconut source)
            query_vec = _normalize(await embedder.embed_text(query))  #430 (line in Coconut source)

        for edge in direct_edges:  #432 (line in Coconut source)
            node = await store.get_node(edge.dst_id)  #433 (line in Coconut source)
            if not isinstance(node, ContextNode) or not node.is_valid:  #434 (line in Coconut source)
                continue  #435 (line in Coconut source)
            if self.exclude_stale_facts and not node.is_fact_valid:  #436 (line in Coconut source)
                continue  #437 (line in Coconut source)
            direct_context_edges[node.node_id] = edge  #438 (line in Coconut source)
            selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=edge, source="attached", hops=0, path=[agent_node.node_id, node.node_id], path_weight=edge.weight, session_id=session_id)  #439 (line in Coconut source)
            seed_map[node.node_id] = selection  #450 (line in Coconut source)

        if query_vec is not None:  #452 (line in Coconut source)
            semantic_hits = await store.vector_search(query_vec, node_types=[NodeType.CONTEXT,], top_k=self.semantic_top_k)  #453 (line in Coconut source)
            for rank, (node, _score) in enumerate(semantic_hits):  #458 (line in Coconut source)
                if not isinstance(node, ContextNode) or node.node_id in seed_map or not node.is_valid:  #459 (line in Coconut source)
                    continue  #460 (line in Coconut source)
                if self.exclude_stale_facts and not node.is_fact_valid:  #461 (line in Coconut source)
                    continue  #462 (line in Coconut source)
                selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(node.node_id), source="semantic", hops=0, path=[node.node_id,], path_weight=max(0.5, 1.0 - rank * 0.03), session_id=session_id)  #463 (line in Coconut source)
                seed_map[node.node_id] = selection  #474 (line in Coconut source)

        if session_id:  #476 (line in Coconut source)
            runtime_nodes = await store.list_nodes(node_type=NodeType.CONTEXT, group_id=session_id)  #477 (line in Coconut source)
            for node in runtime_nodes:  #478 (line in Coconut source)
                if not isinstance(node, ContextNode):  #479 (line in Coconut source)
                    continue  #480 (line in Coconut source)
                if node.attributes.get("origin") != "runtime":  #481 (line in Coconut source)
                    continue  #482 (line in Coconut source)
                selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(node.node_id), source="runtime", hops=0, path=[node.node_id,], path_weight=1.0, session_id=session_id)  #483 (line in Coconut source)
                existing = seed_map.get(node.node_id)  #494 (line in Coconut source)
                if existing is None or selection.score > existing.score:  #495 (line in Coconut source)
                    seed_map[node.node_id] = selection  #496 (line in Coconut source)

        expanded = await self._expand_contexts(store, list(seed_map.values()), query=query, query_vec=query_vec, direct_context_edges=direct_context_edges, session_id=session_id)  #498 (line in Coconut source)

        ranked = sorted(expanded.values(), key=lambda s: s.score, reverse=True)  #507 (line in Coconut source)
        return self._pack_contexts(ranked)  #508 (line in Coconut source)


    async def _expand_contexts(self, store: GraphStore, seeds: list[ContextSelection], *, query: str | None, query_vec: list[float] | None, direct_context_edges: dict[str, Edge], session_id: str | None,) -> dict[str, ContextSelection]:  #510 (line in Coconut source)
        candidates: dict[str, ContextSelection] = {seed.context.node_id: seed for seed in seeds}  #520 (line in Coconut source)
        frontier: deque[tuple[AnyNode, int, list[str], float, str]] = deque(((seed.context, 0, list(seed.path), 1.0, seed.source) for seed in seeds))  #521 (line in Coconut source)
        seen_paths: set[tuple[str, int]] = set()  #525 (line in Coconut source)

        while frontier:  #527 (line in Coconut source)
            current, hops, path, path_weight, origin = frontier.popleft()  #528 (line in Coconut source)
            if hops >= self.max_hops:  #529 (line in Coconut source)
                continue  #530 (line in Coconut source)
            key = (current.node_id, hops)  #531 (line in Coconut source)
            if key in seen_paths:  #532 (line in Coconut source)
                continue  #533 (line in Coconut source)
            seen_paths.add(key)  #534 (line in Coconut source)

            for edge in await store.get_edges(current.node_id, direction="both"):  #536 (line in Coconut source)
                if edge.edge_type not in self.expansion_edge_types:  #537 (line in Coconut source)
                    continue  #538 (line in Coconut source)
                neighbor_id = edge.dst_id if edge.src_id == current.node_id else edge.src_id  #539 (line in Coconut source)
                neighbor = await store.get_node(neighbor_id)  #540 (line in Coconut source)
                if neighbor is None or not neighbor.is_valid:  #541 (line in Coconut source)
                    continue  #542 (line in Coconut source)

                next_path = path + [neighbor_id,]  #544 (line in Coconut source)
                next_weight = path_weight * max(edge.weight, 0.1)  #545 (line in Coconut source)
                next_hops = hops + 1  #546 (line in Coconut source)

                if isinstance(neighbor, ContextNode):  #548 (line in Coconut source)
                    if self.exclude_stale_facts and not neighbor.is_fact_valid:  #549 (line in Coconut source)
                        continue  #550 (line in Coconut source)
                    selection = self._score_context(neighbor, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(neighbor.node_id), source="{_coconut_format_0}+graph".format(_coconut_format_0=(origin)), hops=next_hops, path=next_path, path_weight=next_weight, session_id=session_id)  #551 (line in Coconut source)
                    existing = candidates.get(neighbor.node_id)  #562 (line in Coconut source)
                    if existing is None or selection.score > existing.score:  #563 (line in Coconut source)
                        candidates[neighbor.node_id] = selection  #564 (line in Coconut source)

                frontier.append((neighbor, next_hops, next_path, next_weight, origin))  #566 (line in Coconut source)

        return candidates  #568 (line in Coconut source)


    def _pack_contexts(self, ranked: list[ContextSelection]) -> list[ContextSelection]:  #570 (line in Coconut source)
        packed: list[ContextSelection] = []  #571 (line in Coconut source)
        total_tokens = 0  #572 (line in Coconut source)
        per_source: dict[str, int] = {}  #573 (line in Coconut source)

        for selection in ranked:  #575 (line in Coconut source)
            source_key = selection.context.source or selection.source or "unknown"  #576 (line in Coconut source)
            if per_source.get(source_key, 0) >= self.per_source_limit:  #577 (line in Coconut source)
                continue  #578 (line in Coconut source)
            if len(packed) >= self.max_context_nodes:  #579 (line in Coconut source)
                break  #580 (line in Coconut source)
            if packed and total_tokens + selection.token_count > self.max_context_tokens:  #581 (line in Coconut source)
                continue  #582 (line in Coconut source)

            packed.append(selection)  #584 (line in Coconut source)
            total_tokens += selection.token_count  #585 (line in Coconut source)
            per_source[source_key] = per_source.get(source_key, 0) + 1  #586 (line in Coconut source)

        return packed  #588 (line in Coconut source)


    @_coconut_tco  #590 (line in Coconut source)
    def _score_context(self, ctx: ContextNode, *, query: str | None, query_vec: list[float] | None, direct_edge: Edge | None, source: str, hops: int, path: list[str], path_weight: float, session_id: str | None,) -> ContextSelection:  #590 (line in Coconut source)
        semantic = 0.5  #603 (line in Coconut source)
        if query_vec is not None and ctx.embedding:  #604 (line in Coconut source)
            semantic = max(0.0, _cosine(query_vec, ctx.embedding))  #605 (line in Coconut source)

        direct_affinity = direct_edge.weight if direct_edge is not None else 0.5  #607 (line in Coconut source)
        path_bonus = (self.path_decay**hops) * max(path_weight, 0.1)  #608 (line in Coconut source)
        priority_bonus = ctx.priority * self.priority_weight  #609 (line in Coconut source)
        tag_bonus = self._tag_overlap_bonus(query, ctx)  #610 (line in Coconut source)
        recency_bonus = self._recency_bonus(ctx)  #611 (line in Coconut source)
        provenance_bonus = self.provenance_weight if ctx.attributes.get("origin") == "runtime" else 0.0  #612 (line in Coconut source)
        if session_id and ctx.group_id == session_id:  #613 (line in Coconut source)
            provenance_bonus += self.provenance_weight  #614 (line in Coconut source)

        score = semantic * direct_affinity * path_bonus  #616 (line in Coconut source)
        score += priority_bonus + tag_bonus + recency_bonus + provenance_bonus  #617 (line in Coconut source)
        if not ctx.is_fact_valid:  #618 (line in Coconut source)
            score -= self.stale_fact_penalty  #619 (line in Coconut source)

        reasons = ["semantic={_coconut_format_0:.2f}".format(_coconut_format_0=(semantic)), "affinity={_coconut_format_0:.2f}".format(_coconut_format_0=(direct_affinity)), "hops={_coconut_format_0}".format(_coconut_format_0=(hops))]  #621 (line in Coconut source)
        if priority_bonus:  #626 (line in Coconut source)
            reasons.append("priority+={_coconut_format_0:.2f}".format(_coconut_format_0=(priority_bonus)))  #627 (line in Coconut source)
        if tag_bonus:  #628 (line in Coconut source)
            reasons.append("tags+={_coconut_format_0:.2f}".format(_coconut_format_0=(tag_bonus)))  #629 (line in Coconut source)
        if recency_bonus:  #630 (line in Coconut source)
            reasons.append("recent+={_coconut_format_0:.2f}".format(_coconut_format_0=(recency_bonus)))  #631 (line in Coconut source)
        if provenance_bonus:  #632 (line in Coconut source)
            reasons.append("runtime+={_coconut_format_0:.2f}".format(_coconut_format_0=(provenance_bonus)))  #633 (line in Coconut source)
        if not ctx.is_fact_valid:  #634 (line in Coconut source)
            reasons.append("stale-={_coconut_format_0:.2f}".format(_coconut_format_0=(self.stale_fact_penalty)))  #635 (line in Coconut source)

        return _coconut_tail_call(ContextSelection, context=ctx, score=score, source=source, hops=hops, path=path, reasons=reasons, token_count=self._estimate_tokens(ctx))  #637 (line in Coconut source)


    @_coconut_tco  #647 (line in Coconut source)
    def _estimate_tokens(self, ctx: ContextNode) -> int:  #647 (line in Coconut source)
        if ctx.token_count > 0:  #648 (line in Coconut source)
            return ctx.token_count  #649 (line in Coconut source)
        content = ctx.content or ""  #650 (line in Coconut source)
        return _coconut_tail_call(max, 1, len(content.split()) + len(content) // 12)  #651 (line in Coconut source)


    def _tag_overlap_bonus(self, query: str | None, ctx: ContextNode) -> float:  #653 (line in Coconut source)
        if not query or not ctx.tags:  #654 (line in Coconut source)
            return 0.0  #655 (line in Coconut source)
        query_lower = query.lower()  #656 (line in Coconut source)
        overlap = sum((1 for tag in ctx.tags if tag.lower() in query_lower))  #657 (line in Coconut source)
        return overlap * self.tag_weight  #658 (line in Coconut source)


    def _recency_bonus(self, ctx: ContextNode) -> float:  #660 (line in Coconut source)
        age_s = (datetime.now(timezone.utc) - ctx.valid_at).total_seconds()  #661 (line in Coconut source)
        if age_s <= 3600:  #662 (line in Coconut source)
            return self.recency_weight  #663 (line in Coconut source)
        if age_s <= 86400:  #664 (line in Coconut source)
            return self.recency_weight / 2  #665 (line in Coconut source)
        return 0.0  #666 (line in Coconut source)


# ---------------------------------------------------------------------------
# ComposedAgent — runtime snapshot of an agent's composition
# ---------------------------------------------------------------------------


@dataclass  #673 (line in Coconut source)
class ComposedAgent():  #674 (line in Coconut source)
    """The fully-resolved runtime configuration for one AgentNode invocation.

    Built by AgentComposer.compose() via graph traversal — not hardcoded.
    """  #678 (line in Coconut source)

    agent_node: AgentNode  #680 (line in Coconut source)
    tools: list[ToolNode]  #681 (line in Coconut source)
    context: list[ContextNode]  #682 (line in Coconut source)
    context_selection: list[ContextSelection]  #683 (line in Coconut source)
    prompt: PromptNode | None  #684 (line in Coconut source)
    delegates: list[AgentNode]  #685 (line in Coconut source)

    @_coconut_tco  #687 (line in Coconut source)
    def build_system_prompt(self, **prompt_vars: Any) -> str:  #687 (line in Coconut source)
        """Assemble the system prompt from the prompt template + context nodes.

        Image context nodes (content_type == "image") are excluded here — they
        are injected as multimodal content blocks in the user message instead.
        """  #692 (line in Coconut source)
        parts: list[str] = []  #693 (line in Coconut source)

        if self.prompt:  #695 (line in Coconut source)
            parts.append(self.prompt.render(**prompt_vars))  #696 (line in Coconut source)
        elif self.agent_node.system_prompt:  #697 (line in Coconut source)
            parts.append(self.agent_node.system_prompt)  #698 (line in Coconut source)

        text_context = [ctx for ctx in self.context if ctx.content_type != "image"]  #700 (line in Coconut source)
        if text_context:  #701 (line in Coconut source)
            parts.append("\n\n## Relevant Context\n")  #702 (line in Coconut source)
            for ctx in text_context:  #703 (line in Coconut source)
                header = "### {_coconut_format_0}".format(_coconut_format_0=(ctx.name)) if ctx.name else "###"  #704 (line in Coconut source)
                if ctx.source:  #705 (line in Coconut source)
                    header += " (source: {_coconut_format_0})".format(_coconut_format_0=(ctx.source))  #706 (line in Coconut source)
                parts.append("{_coconut_format_0}\n{_coconut_format_1}".format(_coconut_format_0=(header), _coconut_format_1=(ctx.content)))  #707 (line in Coconut source)

        return _coconut_tail_call("\n".join, parts)  #709 (line in Coconut source)


    def build_image_context_blocks(self) -> list[dict[str, Any]]:  #711 (line in Coconut source)
        """Return Anthropic-format image blocks for image context nodes."""  #712 (line in Coconut source)
        blocks: list[dict[str, Any]] = []  #713 (line in Coconut source)
        for ctx in self.context:  #714 (line in Coconut source)
            if ctx.content_type != "image":  #715 (line in Coconut source)
                continue  #716 (line in Coconut source)
            source_type = ctx.attributes.get("image_source", "url")  #717 (line in Coconut source)
            if source_type == "base64":  #718 (line in Coconut source)
                media_type = ctx.attributes.get("media_type", "image/jpeg")  #719 (line in Coconut source)
                blocks.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": ctx.content}})  #720 (line in Coconut source)
            else:  #724 (line in Coconut source)
                blocks.append({"type": "image", "source": {"type": "url", "url": ctx.content}})  #725 (line in Coconut source)
        return blocks  #729 (line in Coconut source)


    def build_tool_schemas(self) -> list[dict[str, Any]]:  #731 (line in Coconut source)
        """Return tool definitions for all composed tools (backend-agnostic format)."""  #732 (line in Coconut source)
        return [t.to_tool_schema() for t in self.tools]  #733 (line in Coconut source)


    def explain(self) -> dict[str, Any]:  #735 (line in Coconut source)
        """Return a structured explanation of the composed runtime agent."""  #736 (line in Coconut source)
        prompt_source = "none"  #737 (line in Coconut source)
        prompt_name = ""  #738 (line in Coconut source)
        if self.prompt is not None:  #739 (line in Coconut source)
            prompt_source = "prompt_node"  #740 (line in Coconut source)
            prompt_name = self.prompt.name  #741 (line in Coconut source)
        elif self.agent_node.system_prompt:  #742 (line in Coconut source)
            prompt_source = "agent_node"  #743 (line in Coconut source)

        return {"agent": {"node_id": self.agent_node.node_id, "name": self.agent_node.name, "model": self.agent_node.model}, "prompt": {"source": prompt_source, "name": prompt_name}, "tools": [{"node_id": tool.node_id, "name": tool.name, "callable_ref": tool.callable_ref, "description": tool.description} for tool in self.tools], "context": [{"node_id": selection.context.node_id, "name": selection.context.name, "source": selection.source, "score": round(selection.score, 4), "hops": selection.hops, "path": selection.path, "reasons": selection.reasons, "token_count": selection.token_count} for selection in self.context_selection], "delegates": [{"node_id": delegate.node_id, "name": delegate.name} for delegate in self.delegates]}  #745 (line in Coconut source)


# ---------------------------------------------------------------------------
# AgentComposer — discovers composition from the graph
# ---------------------------------------------------------------------------


class AgentComposer():  #791 (line in Coconut source)
    """Assembles an agent's runtime configuration by traversing graph edges.

    This is the architectural core: composition IS traversal.
    Adding a tool to an agent = upsert_edge(HAS_TOOL, agent, tool). No code change.

    Pass an Embedder instance to enable query-time context re-ranking: context nodes
    are scored by edge.weight * cosine(query, ctx) + priority_bonus instead of
    static edge weight alone.
    """  #800 (line in Coconut source)

    def __init__(self, store: GraphStore, embedder: Any=None, context_navigator: ContextNavigator | None=None,) -> None:  #802 (line in Coconut source)
        self.store = store  #808 (line in Coconut source)
        self._embedder = embedder  #809 (line in Coconut source)
        self._context_navigator = context_navigator or ContextNavigator()  #810 (line in Coconut source)


    async def compose(self, agent_node: AgentNode, query: str | None=None, session_id: str | None=None,) -> ComposedAgent:  #812 (line in Coconut source)
        node_id = agent_node.node_id  #818 (line in Coconut source)

        tool_edges = await self.store.get_edges(node_id, edge_type=EdgeType.HAS_TOOL)  #820 (line in Coconut source)
        tool_edges.sort(key=lambda e: e.weight, reverse=True)  #821 (line in Coconut source)
        raw_tool_nodes = await asyncio.gather(*[self.store.get_node(e.dst_id) for e in tool_edges])  #822 (line in Coconut source)
        tools: list[ToolNode] = [n for n in raw_tool_nodes if isinstance(n, ToolNode) and n.is_valid]  #823 (line in Coconut source)

        context_selection = await self._context_navigator.navigate(self.store, agent_node, query=query, embedder=self._embedder, session_id=session_id)  #827 (line in Coconut source)
        context = [selection.context for selection in context_selection]  #834 (line in Coconut source)

        prompt_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.HAS_PROMPT)  #836 (line in Coconut source)
        prompt = next((n for n in prompt_nodes if isinstance(n, PromptNode)), None)  #837 (line in Coconut source)

        delegate_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.DELEGATES_TO)  #839 (line in Coconut source)
        delegates = [n for n in delegate_nodes if isinstance(n, AgentNode) and n.is_valid]  #840 (line in Coconut source)

        return ComposedAgent(agent_node=agent_node, tools=tools, context=context, context_selection=context_selection, prompt=prompt, delegates=delegates)  #842 (line in Coconut source)


# ---------------------------------------------------------------------------
# Router prompt templates
# ---------------------------------------------------------------------------


_ROUTER_SYSTEM = ('You are a routing classifier. Respond with a single valid JSON object and nothing else.')  #856 (line in Coconut source)

_ROUTER_TEMPLATE = """\
Select the best agent for this task.

Available agents:
{agent_list}

Task: {query}

Respond with JSON only:
{{"agent": "<id>", "reason": "<one sentence explaining why>", "confidence": <0.0-1.0>}}"""  #870 (line in Coconut source)

_INTENT_TEMPLATE = """\
Given this agent output, select the best routing intent.

Available intents:
{intents}
- default

Agent output:
{text}

Respond with JSON only:
{{"intent": "<selected>", "reason": "<brief reason>"}}"""  #883 (line in Coconut source)


# ---------------------------------------------------------------------------
# ExecutionOptions — security and tenancy controls for run()
# ---------------------------------------------------------------------------

class ExecutionOptions(_coconut.collections.namedtuple("ExecutionOptions", ('allowed_tools',))):  #890 (line in Coconut source)
    """Runtime controls for GraphExecutor.run()."""  #891 (line in Coconut source)


    __slots__ = ()  #894 (line in Coconut source)
    _coconut_is_data = True  #894 (line in Coconut source)
    __match_args__ = ('allowed_tools',)  #894 (line in Coconut source)
    def __add__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    def __mul__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    def __rmul__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    __ne__ = _coconut.object.__ne__  #894 (line in Coconut source)
    def __eq__(self, other):  #894 (line in Coconut source)
        return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)  #894 (line in Coconut source)
    def __hash__(self):  #894 (line in Coconut source)
        return _coconut.tuple.__hash__(self) ^ _coconut.hash(self.__class__)  #894 (line in Coconut source)
    def __new__(_coconut_cls, allowed_tools=None):  #894 (line in Coconut source)
        return _coconut.tuple.__new__(_coconut_cls, (allowed_tools,))  #894 (line in Coconut source)
    _coconut_data_defaults = {0: __new__.__defaults__[0]}  # type: ignore  #894 (line in Coconut source)
@dataclass  #894 (line in Coconut source)
class ResumeReadiness():  #895 (line in Coconut source)
    """Diagnosis of whether a checkpointed/paused context is safe to resume."""  #896 (line in Coconut source)

    status: str  #898 (line in Coconut source)
    is_paused: bool  #899 (line in Coconut source)
    is_stale: bool  #900 (line in Coconut source)
    last_event_at: datetime | None  #901 (line in Coconut source)
    seconds_since_last_event: float | None  #902 (line in Coconut source)
    available: list[str]  #903 (line in Coconut source)
    unrecoverable: list[str]  #904 (line in Coconut source)

    @property  #906 (line in Coconut source)
    def ok(self) -> bool:  #907 (line in Coconut source)
        """True when nothing blocks an automatic resume."""  #908 (line in Coconut source)
        return not self.is_stale and not self.unrecoverable  #909 (line in Coconut source)


# ---------------------------------------------------------------------------
# GraphExecutor — dispatches nodes and traverses the graph
# ---------------------------------------------------------------------------


class GraphExecutor():  #916 (line in Coconut source)
    """Executes a query by traversing the agent graph.

    Node dispatch is based on node_type:
    - AGENT   → compose + LLM call + tool handling + routing
    - TOOL    → call registered Python callable
    - CONTEXT → return content (passive)
    - GRAPH   → recursive sub-graph execution
    - PROMPT  → render template (usually consumed by AGENT, not executed directly)
    """  #925 (line in Coconut source)

    def __init__(self, store: GraphStore, composer: AgentComposer | None=None, backend: LLMBackend | None=None, embedder: Any=None, context_navigator: ContextNavigator | None=None, router_model: str="claude-haiku-4-5-20251001",) -> None:  #927 (line in Coconut source)
        self.store = store  #936 (line in Coconut source)
        self.composer = composer or AgentComposer(store, embedder=embedder, context_navigator=context_navigator)  #937 (line in Coconut source)
        self._backend = backend or default_backend()  #940 (line in Coconut source)
        self._router_model = router_model  #941 (line in Coconut source)

        self._tool_fns: dict[str, Any] = {}  #943 (line in Coconut source)
        self._event_hooks: list[Callable[[TraceEvent, ExecutionContext], Any]] = []  #944 (line in Coconut source)


    def register_tool(self, callable_ref: str, fn: Any) -> None:  #946 (line in Coconut source)
        """Register a callable under its dotted ref string."""  #947 (line in Coconut source)
        self._tool_fns[callable_ref] = fn  #948 (line in Coconut source)


    def add_event_hook(self, fn: Callable[[TraceEvent, ExecutionContext], Any]) -> None:  #950 (line in Coconut source)
        """Register a callback invoked for every emitted event."""  #951 (line in Coconut source)
        self._event_hooks.append(fn)  #952 (line in Coconut source)

# ------------------------------------------------------------------
# Trace emission helper
# ------------------------------------------------------------------


    def _emit(self, ctx: ExecutionContext, event_type: EventType, node_id: str, node_name: str, payload: dict[str, Any], event_id: str | None=None, parent_event_id: str | None=None, duration_ms: int | None=None,) -> TraceEvent:  #958 (line in Coconut source)
        """Create and append a TraceEvent to ctx.trace. Returns the event."""  #969 (line in Coconut source)
        event = TraceEvent(event_type=event_type, session_id=ctx.session_id, node_id=node_id, node_name=node_name, timestamp=datetime.now(timezone.utc), payload=payload, event_id=event_id or str(uuid.uuid4()), parent_event_id=parent_event_id, duration_ms=duration_ms)  #970 (line in Coconut source)
        ctx.trace.append(event)  #981 (line in Coconut source)
        for hook in getattr(self, "_event_hooks", []):  #982 (line in Coconut source)
            hook_result = hook(event, ctx)  #983 (line in Coconut source)
            if asyncio.iscoroutine(hook_result):  #984 (line in Coconut source)
                asyncio.create_task(hook_result)  #985 (line in Coconut source)
        return event  #986 (line in Coconut source)

# ------------------------------------------------------------------
# Public entry points
# ------------------------------------------------------------------


    async def run(self, entry_node_id: str, query: QueryContent, strategy: str="sequential", max_hops: int=20, extra_messages: list[dict[str, Any]] | None=None, execution_context: ExecutionContext | None=None, state: dict[str, Any] | None=None, allowed_tools: list[str] | None=None, options: ExecutionOptions | None=None, **kwargs: Any,) -> ExecutionContext:  #992 (line in Coconut source)
        """Execute a query starting from entry_node_id."""  #1005 (line in Coconut source)
        ctx = execution_context or ExecutionContext(query=query, max_hops=max_hops)  #1006 (line in Coconut source)
        ctx.query = query  #1007 (line in Coconut source)
        ctx.max_hops = max_hops  #1008 (line in Coconut source)
        if extra_messages:  #1009 (line in Coconut source)
            ctx.extra_messages = list(extra_messages)  #1010 (line in Coconut source)
        if state:  #1011 (line in Coconut source)
            ctx.state.data.update(state)  #1012 (line in Coconut source)
        if allowed_tools is not None:  #1013 (line in Coconut source)
            ctx.allowed_tools = set(allowed_tools)  #1014 (line in Coconut source)
        if options is not None and options.allowed_tools is not None:  #1015 (line in Coconut source)
            ctx.allowed_tools = options.allowed_tools  #1016 (line in Coconut source)
        try:  #1017 (line in Coconut source)
            entry = await self.store.get_node(entry_node_id)  #1018 (line in Coconut source)
            if entry is None:  #1019 (line in Coconut source)
                raise ValueError(("Entry node {_coconut_format_0!r} not found in graph store.\n".format(_coconut_format_0=(entry_node_id)) + "Hint: use `agent.node_id` (not `agent.name`) as the entry_node_id,\n" + "or call `await store.list_nodes()` to inspect what is in the store."))  #1020 (line in Coconut source)
            _coconut_case_match_to_1 = strategy  #1025 (line in Coconut source)
            _coconut_case_match_check_1 = False  #1025 (line in Coconut source)
            if _coconut_case_match_to_1 == "sequential":  #1025 (line in Coconut source)
                _coconut_case_match_check_1 = True  #1025 (line in Coconut source)
            if _coconut_case_match_check_1:  #1025 (line in Coconut source)
                await self._run_sequential(entry, ctx)  #1027 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1028 (line in Coconut source)
                if _coconut_case_match_to_1 == "parallel":  #1028 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #1028 (line in Coconut source)
                if _coconut_case_match_check_1:  #1028 (line in Coconut source)
                    await self._run_parallel(entry, ctx)  #1029 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1030 (line in Coconut source)
                if _coconut_case_match_to_1 == "topological":  #1030 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #1030 (line in Coconut source)
                if _coconut_case_match_check_1:  #1030 (line in Coconut source)
                    await self._run_topological(entry_node_id, ctx)  #1031 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1032 (line in Coconut source)
                _coconut_case_match_check_1 = True  #1032 (line in Coconut source)
                if _coconut_case_match_check_1:  #1032 (line in Coconut source)
                    raise ValueError("Unknown strategy: {_coconut_format_0!r}".format(_coconut_format_0=(strategy)))  #1033 (line in Coconut source)
        except Exception as exc:  #1034 (line in Coconut source)
            _log.error("Executor fatal error [session=%s node=%s]: %s", ctx.session_id, entry_node_id, exc, exc_info=True)  #1035 (line in Coconut source)
            self._emit(ctx, "error", entry_node_id, "", payload={"error": str(exc), "error_type": type(exc).__name__})  #1039 (line in Coconut source)
            raise  #1049 (line in Coconut source)

        return ctx  #1051 (line in Coconut source)


    async def resume(self, entry_node_id: str, ctx: ExecutionContext, *, query: QueryContent | None=None, strategy: str="sequential",) -> ExecutionContext:  #1053 (line in Coconut source)
        """Resume a paused workflow context."""  #1061 (line in Coconut source)
        if query is not None:  #1062 (line in Coconut source)
            ctx.query = query  #1063 (line in Coconut source)
        ctx.state.status = "running"  #1064 (line in Coconut source)
        pause = ctx.state.pending_pause  #1065 (line in Coconut source)
        ctx.state.pending_pause = None  #1066 (line in Coconut source)
        if pause is not None:  #1067 (line in Coconut source)
            self._emit(ctx, "resume", pause.node_id, pause.node_name, payload={"token": pause.token, "waiting_for": pause.waiting_for})  #1068 (line in Coconut source)
        return await self.run(entry_node_id, ctx.query, strategy=strategy, max_hops=ctx.max_hops, execution_context=ctx)  #1075 (line in Coconut source)


    @_coconut_tco  #1083 (line in Coconut source)
    def inspect_resume(self, ctx: ExecutionContext, *, stale_after_seconds: float=1200.0, required_outputs: list[str] | None=None, now: datetime | None=None,) -> ResumeReadiness:  #1083 (line in Coconut source)
        """Diagnose whether ``ctx`` is safe to resume — no side effects."""  #1091 (line in Coconut source)
        last_event_at = max((e.timestamp for e in ctx.trace), default=None)  #1092 (line in Coconut source)
        if last_event_at is None:  #1093 (line in Coconut source)
            seconds_since: float | None = None  #1094 (line in Coconut source)
            is_stale = False  #1095 (line in Coconut source)
        else:  #1096 (line in Coconut source)
            current = now or datetime.now(timezone.utc)  #1097 (line in Coconut source)
            seconds_since = (current - last_event_at).total_seconds()  #1098 (line in Coconut source)
            is_stale = seconds_since > stale_after_seconds  #1099 (line in Coconut source)

        available: list[str] = []  #1101 (line in Coconut source)
        unrecoverable: list[str] = []  #1102 (line in Coconut source)
        for key in required_outputs or []:  #1103 (line in Coconut source)
            if key in ctx.outputs or key in ctx.state.data:  #1104 (line in Coconut source)
                available.append(key)  #1105 (line in Coconut source)
            else:  #1106 (line in Coconut source)
                unrecoverable.append(key)  #1107 (line in Coconut source)

        return _coconut_tail_call(ResumeReadiness, status=ctx.state.status, is_paused=ctx.is_paused(), is_stale=is_stale, last_event_at=last_event_at, seconds_since_last_event=seconds_since, available=available, unrecoverable=unrecoverable)  #1109 (line in Coconut source)


    async def batch(self, agent_node_id: str, items: list[Any], query_fn: Callable[[Any,], str], *, context_fn: Callable[[Any,], str | None] | None=None, reduce_fn: Callable[[list[Any],], Any] | None=None, on_progress: Callable[[Any,], Any] | None=None, concurrency: int=5, checkpoint: bool=True, strategy: str="sequential",) -> Any:  #1119 (line in Coconut source)
        """Run an agent over a list of items with concurrency control."""  #1132 (line in Coconut source)
        import warnings  #1133 (line in Coconut source)
        from yggdrasil_lm.batch import BatchExecutor  #1134 (line in Coconut source)
        with warnings.catch_warnings():  #1135 (line in Coconut source)
            warnings.simplefilter("ignore", DeprecationWarning)  #1136 (line in Coconut source)
            _batch = BatchExecutor(self.store, self, concurrency=concurrency)  #1137 (line in Coconut source)
        return await _batch.run(agent_node_id, items, query_fn, context_fn=context_fn, reduce_fn=reduce_fn, on_progress=on_progress, checkpoint=checkpoint, strategy=strategy)  #1138 (line in Coconut source)


    async def checkpoint_context(self, ctx: ExecutionContext, *, name: str="Execution checkpoint", max_inline_chars: int | None=None,) -> ContextNode:  #1149 (line in Coconut source)
        """Persist a resumable execution snapshot as a runtime context node."""  #1156 (line in Coconut source)
        snap = ctx.snapshot()  #1157 (line in Coconut source)
        if max_inline_chars is not None:  #1158 (line in Coconut source)
            snap = await self._offload_snapshot_blobs(ctx, snap, max_inline_chars)  #1159 (line in Coconut source)
        checkpoint = ContextNode(name=name, description="Serialized execution checkpoint", content=json.dumps(snap, default=str), content_type="json", source="checkpoint", group_id=ctx.session_id, attributes={"origin": "checkpoint", "session_id": ctx.session_id, "graph_version": ctx.state.graph_version})  #1160 (line in Coconut source)
        await self.store.upsert_node(checkpoint)  #1173 (line in Coconut source)
        self._emit(ctx, "checkpoint", checkpoint.node_id, checkpoint.name, payload={"checkpoint_node_id": checkpoint.node_id})  #1174 (line in Coconut source)
        return checkpoint  #1181 (line in Coconut source)


    async def _offload_snapshot_blobs(self, ctx: ExecutionContext, snap: dict[str, Any], max_inline_chars: int,) -> dict[str, Any]:  #1183 (line in Coconut source)
        """Replace oversized top-level snapshot values with blob node refs."""  #1189 (line in Coconut source)
        async def offload(value: Any) -> Any:  #1190 (line in Coconut source)
            try:  #1191 (line in Coconut source)
                encoded = json.dumps(value, default=str)  #1192 (line in Coconut source)
            except (TypeError, ValueError):  #1193 (line in Coconut source)
                return value  #1194 (line in Coconut source)
            if len(encoded) <= max_inline_chars:  #1195 (line in Coconut source)
                return value  #1196 (line in Coconut source)
            blob = ContextNode(name="Checkpoint blob", description="Offloaded checkpoint payload", content=encoded, content_type="json", source="checkpoint", group_id=ctx.session_id, attributes={"origin": "checkpoint_blob", "session_id": ctx.session_id})  #1197 (line in Coconut source)
            await self.store.upsert_node(blob)  #1206 (line in Coconut source)
            return {"$ygg_blob": blob.node_id}  #1207 (line in Coconut source)


        outputs = snap.get("outputs")  #1209 (line in Coconut source)
        if isinstance(outputs, dict):  #1210 (line in Coconut source)
            for key, value in list(outputs.items()):  #1211 (line in Coconut source)
                outputs[key] = await offload(value)  #1212 (line in Coconut source)
        state_data = snap.get("state", {}).get("data")  #1213 (line in Coconut source)
        if isinstance(state_data, dict):  #1214 (line in Coconut source)
            for key, value in list(state_data.items()):  #1215 (line in Coconut source)
                state_data[key] = await offload(value)  #1216 (line in Coconut source)
        return snap  #1217 (line in Coconut source)


    async def load_checkpoint(self, checkpoint_node_id: str) -> ExecutionContext:  #1219 (line in Coconut source)
        """Restore an execution context from a checkpoint node."""  #1220 (line in Coconut source)
        node = await self.store.get_node(checkpoint_node_id)  #1221 (line in Coconut source)
        if not isinstance(node, ContextNode):  #1222 (line in Coconut source)
            raise ValueError("Checkpoint node not found: {_coconut_format_0}".format(_coconut_format_0=(checkpoint_node_id)))  #1223 (line in Coconut source)
        snap = json.loads(node.content)  #1224 (line in Coconut source)
        await self._rehydrate_snapshot_blobs(snap)  #1225 (line in Coconut source)
        return ExecutionContext.from_snapshot(snap)  #1226 (line in Coconut source)


    async def _rehydrate_snapshot_blobs(self, snap: dict[str, Any]) -> None:  #1228 (line in Coconut source)
        """Inverse of ``_offload_snapshot_blobs`` — resolve ``$ygg_blob`` refs."""  #1229 (line in Coconut source)
        async def resolve(value: Any) -> Any:  #1230 (line in Coconut source)
            if isinstance(value, dict) and set(value) == {"$ygg_blob"}:  #1231 (line in Coconut source)
                blob = await self.store.get_node(value["$ygg_blob"])  #1232 (line in Coconut source)
                if not isinstance(blob, ContextNode):  #1233 (line in Coconut source)
                    raise ValueError("Checkpoint blob node missing: {_coconut_format_0}".format(_coconut_format_0=(value['$ygg_blob'])))  #1234 (line in Coconut source)
                return json.loads(blob.content)  #1237 (line in Coconut source)
            return value  #1238 (line in Coconut source)


        outputs = snap.get("outputs")  #1240 (line in Coconut source)
        if isinstance(outputs, dict):  #1241 (line in Coconut source)
            for key, value in list(outputs.items()):  #1242 (line in Coconut source)
                outputs[key] = await resolve(value)  #1243 (line in Coconut source)
        state_data = snap.get("state", {}).get("data")  #1244 (line in Coconut source)
        if isinstance(state_data, dict):  #1245 (line in Coconut source)
            for key, value in list(state_data.items()):  #1246 (line in Coconut source)
                state_data[key] = await resolve(value)  #1247 (line in Coconut source)


    async def resume_from_checkpoint(self, checkpoint_node_id: str, entry_node_id: str, *, query: QueryContent | None=None, strategy: str="sequential",) -> ExecutionContext:  #1249 (line in Coconut source)
        """Load a checkpointed context and resume execution."""  #1257 (line in Coconut source)
        ctx = await self.load_checkpoint(checkpoint_node_id)  #1258 (line in Coconut source)
        return await self.resume(entry_node_id, ctx, query=query, strategy=strategy)  #1259 (line in Coconut source)


    def _resolve_json_path(self, payload: Any, path: str) -> Any:  #1261 (line in Coconut source)
        """Resolve a dotted JSON path against a payload dict."""  #1262 (line in Coconut source)
        current: Any = payload  #1263 (line in Coconut source)
        for part in [p for p in path.split(".") if p]:  #1264 (line in Coconut source)
            _coconut_case_match_to_2 = current  #1265 (line in Coconut source)
            _coconut_case_match_check_2 = False  #1265 (line in Coconut source)
            if _coconut.isinstance(_coconut_case_match_to_2, _coconut.abc.Mapping):  #1265 (line in Coconut source)
                _coconut_case_match_check_2 = True  #1265 (line in Coconut source)
            if _coconut_case_match_check_2 and not (part in current):  #1265 (line in Coconut source)
                _coconut_case_match_check_2 = False  #1265 (line in Coconut source)
            if _coconut_case_match_check_2:  #1265 (line in Coconut source)
                current = current[part]  #1267 (line in Coconut source)
            if not _coconut_case_match_check_2:  #1268 (line in Coconut source)
                _coconut_case_match_check_2 = True  #1268 (line in Coconut source)
                if _coconut_case_match_check_2:  #1268 (line in Coconut source)
                    return None  #1269 (line in Coconut source)
        return current  #1270 (line in Coconut source)


    def _payload_for_source(self, source: str, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> Any:  #1272 (line in Coconut source)
        _coconut_case_match_to_3 = source  #1281 (line in Coconut source)
        _coconut_case_match_check_3 = False  #1281 (line in Coconut source)
        if _coconut_case_match_to_3 == "result":  #1281 (line in Coconut source)
            _coconut_case_match_check_3 = True  #1281 (line in Coconut source)
        if _coconut_case_match_check_3:  #1281 (line in Coconut source)
            return result  #1283 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1284 (line in Coconut source)
            if _coconut_case_match_to_3 == "input":  #1284 (line in Coconut source)
                _coconut_case_match_check_3 = True  #1284 (line in Coconut source)
            if _coconut_case_match_check_3:  #1284 (line in Coconut source)
                return input_payload  #1285 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1286 (line in Coconut source)
            if _coconut_case_match_to_3 == "output":  #1286 (line in Coconut source)
                _coconut_case_match_check_3 = True  #1286 (line in Coconut source)
            if _coconut_case_match_check_3:  #1286 (line in Coconut source)
                return output_payload  #1287 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1288 (line in Coconut source)
            _coconut_case_match_check_3 = True  #1288 (line in Coconut source)
            if _coconut_case_match_check_3:  #1288 (line in Coconut source)
                return state.data  #1289 (line in Coconut source)


    @_coconut_tco  #1291 (line in Coconut source)
    def _compare_values(self, operator: str, left: Any, right: Any) -> bool:  #1291 (line in Coconut source)
        _coconut_case_match_to_4 = operator  #1292 (line in Coconut source)
        _coconut_case_match_check_4 = False  #1292 (line in Coconut source)
        if _coconut_case_match_to_4 == "exists":  #1292 (line in Coconut source)
            _coconut_case_match_check_4 = True  #1292 (line in Coconut source)
        if _coconut_case_match_check_4:  #1292 (line in Coconut source)
            return left is not None  #1294 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1295 (line in Coconut source)
            if _coconut_case_match_to_4 == "truthy":  #1295 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1295 (line in Coconut source)
            if _coconut_case_match_check_4:  #1295 (line in Coconut source)
                return _coconut_tail_call(bool, left)  #1296 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1297 (line in Coconut source)
            if _coconut_case_match_to_4 == "contains":  #1297 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1297 (line in Coconut source)
            if _coconut_case_match_check_4:  #1297 (line in Coconut source)
                return left is not None and right in left  #1298 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1299 (line in Coconut source)
            if _coconut_case_match_to_4 == "not_equals":  #1299 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1299 (line in Coconut source)
            if _coconut_case_match_check_4:  #1299 (line in Coconut source)
                return left != right  #1300 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1301 (line in Coconut source)
            if _coconut_case_match_to_4 == "in":  #1301 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1301 (line in Coconut source)
            if _coconut_case_match_check_4:  #1301 (line in Coconut source)
                return left in right if right is not None else False  #1302 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1303 (line in Coconut source)
            if _coconut_case_match_to_4 == "regex":  #1303 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1303 (line in Coconut source)
            if _coconut_case_match_check_4:  #1303 (line in Coconut source)
                return isinstance(left, str) and isinstance(right, str) and re.search(right, left) is not None  #1304 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1305 (line in Coconut source)
            if _coconut_case_match_to_4 == "gt":  #1305 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1305 (line in Coconut source)
            if _coconut_case_match_check_4:  #1305 (line in Coconut source)
                return left > right  #1306 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1307 (line in Coconut source)
            if _coconut_case_match_to_4 == "gte":  #1307 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1307 (line in Coconut source)
            if _coconut_case_match_check_4:  #1307 (line in Coconut source)
                return left >= right  #1308 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1309 (line in Coconut source)
            if _coconut_case_match_to_4 == "lt":  #1309 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1309 (line in Coconut source)
            if _coconut_case_match_check_4:  #1309 (line in Coconut source)
                return left < right  #1310 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1311 (line in Coconut source)
            if _coconut_case_match_to_4 == "lte":  #1311 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1311 (line in Coconut source)
            if _coconut_case_match_check_4:  #1311 (line in Coconut source)
                return left <= right  #1312 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1313 (line in Coconut source)
            _coconut_case_match_check_4 = True  #1313 (line in Coconut source)
            if _coconut_case_match_check_4:  #1313 (line in Coconut source)
                return left == right  #1314 (line in Coconut source)


    @_coconut_tco  #1316 (line in Coconut source)
    def _evaluate_constraint_rule(self, rule: ConstraintRule, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> bool:  #1316 (line in Coconut source)
        source_data = self._payload_for_source(rule.source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1325 (line in Coconut source)
        left = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1332 (line in Coconut source)
        right = rule.value  #1333 (line in Coconut source)
        if rule.compare_to_source:  #1334 (line in Coconut source)
            compare_data = self._payload_for_source(rule.compare_to_source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1335 (line in Coconut source)
            right = self._resolve_json_path(compare_data, rule.compare_to_path) if rule.compare_to_path else compare_data  #1342 (line in Coconut source)
        return _coconut_tail_call(self._compare_values, rule.operator, left, right)  #1343 (line in Coconut source)


    @_coconut_tco  #1345 (line in Coconut source)
    def _evaluate_route_rule(self, rule: RouteRule, *, result: dict[str, Any], state: WorkflowState,) -> bool:  #1345 (line in Coconut source)
        source_data = state.data if rule.source == "state" else result  #1352 (line in Coconut source)
        return _coconut_tail_call(self._compare_values, rule.operator, self._resolve_json_path(source_data, rule.path) if rule.path else source_data, rule.value)  #1353 (line in Coconut source)


    def _describe_constraint_rule(self, rule: ConstraintRule, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> dict[str, Any]:  #1359 (line in Coconut source)
        source_data = self._payload_for_source(rule.source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1368 (line in Coconut source)
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1375 (line in Coconut source)
        expected = rule.value  #1376 (line in Coconut source)
        if rule.compare_to_source:  #1377 (line in Coconut source)
            compare_data = self._payload_for_source(rule.compare_to_source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1378 (line in Coconut source)
            expected = (self._resolve_json_path(compare_data, rule.compare_to_path) if rule.compare_to_path else compare_data)  #1385 (line in Coconut source)
        matched = self._compare_values(rule.operator, actual, expected)  #1389 (line in Coconut source)
        return {"name": rule.name, "source": rule.source, "path": rule.path, "operator": rule.operator, "actual": actual, "expected": expected, "matched": matched, "compare_to_source": rule.compare_to_source, "compare_to_path": rule.compare_to_path, "message": rule.message}  #1390 (line in Coconut source)


    def _describe_route_rule(self, rule: RouteRule, *, state: WorkflowState, result: dict[str, Any],) -> dict[str, Any]:  #1403 (line in Coconut source)
        source_data = state.data if rule.source == "state" else result  #1410 (line in Coconut source)
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1411 (line in Coconut source)
        matched = self._compare_values(rule.operator, actual, rule.value)  #1412 (line in Coconut source)
        return {"name": rule.name, "source": rule.source, "path": rule.path, "operator": rule.operator, "actual": actual, "expected": rule.value, "matched": matched, "priority": rule.priority, "target_node_id": rule.target_node_id, "pause_on_match": rule.pause_on_match}  #1413 (line in Coconut source)


    async def _validate_constraint_rules(self, node: AgentNode, *, ctx: ExecutionContext, result: Any=None, input_payload: Any=None, output_payload: Any=None, parent_event_id: str | None=None,) -> None:  #1426 (line in Coconut source)
        for rule in node.constraint_rules:  #1436 (line in Coconut source)
            if rule.source in {"result", "output"} and result is None and output_payload is None:  #1437 (line in Coconut source)
                continue  #1438 (line in Coconut source)
            if self._evaluate_constraint_rule(rule, state=ctx.state, result=result, input_payload=input_payload, output_payload=output_payload):  #1439 (line in Coconut source)
                continue  #1446 (line in Coconut source)
            message = rule.message or "Constraint {_coconut_format_0!r} failed".format(_coconut_format_0=(rule.name or rule.path or rule.operator))  #1447 (line in Coconut source)
            self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": False, "error": message, "constraint": rule.name}, parent_event_id=parent_event_id)  #1448 (line in Coconut source)
            raise ValueError(message)  #1456 (line in Coconut source)


    def _evaluate_decision_table(self, table: DecisionTable, *, state: WorkflowState, result: dict[str, Any],) -> DecisionRule | None:  #1458 (line in Coconut source)
        for rule in sorted(table.rules, key=lambda item: item.priority, reverse=True):  #1465 (line in Coconut source)
            if all((self._evaluate_constraint_rule(condition, state=state, result=result) for condition in rule.conditions)):  #1466 (line in Coconut source)
                return rule  #1470 (line in Coconut source)
        return None  #1471 (line in Coconut source)


    async def _pause_execution(self, ctx: ExecutionContext, node: AnyNode, *, reason: str, waiting_for: str | None=None, metadata: dict[str, Any] | None=None,) -> None:  #1473 (line in Coconut source)
        pause = WorkflowPause(reason=reason, node_id=node.node_id, node_name=node.name or "", waiting_for=waiting_for, metadata=metadata or {})  #1482 (line in Coconut source)
        ctx.state.pending_pause = pause  #1489 (line in Coconut source)
        ctx.state.status = "paused"  #1490 (line in Coconut source)
        self._emit(ctx, "pause", node.node_id, node.name or "", payload={"reason": reason, "token": pause.token, "waiting_for": waiting_for, "metadata": pause.metadata})  #1491 (line in Coconut source)


    def _validate_against_schema(self, payload: Any, schema: dict[str, Any], *, label: str,) -> None:  #1504 (line in Coconut source)
        if not schema:  #1511 (line in Coconut source)
            return  #1512 (line in Coconut source)
        schema_type = schema.get("type")  #1513 (line in Coconut source)
        _coconut_case_match_to_5 = schema_type  #1514 (line in Coconut source)
        _coconut_case_match_check_5 = False  #1514 (line in Coconut source)
        if _coconut_case_match_to_5 == "object":  #1514 (line in Coconut source)
            _coconut_case_match_check_5 = True  #1514 (line in Coconut source)
        if _coconut_case_match_check_5:  #1514 (line in Coconut source)
            if not isinstance(payload, dict):  #1516 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be an object".format(_coconut_format_0=(label)))  #1517 (line in Coconut source)
            required = schema.get("required", [])  #1518 (line in Coconut source)
            for key in required:  #1519 (line in Coconut source)
                if key not in payload:  #1520 (line in Coconut source)
                    raise ValueError("{_coconut_format_0} missing required field {_coconut_format_1!r}".format(_coconut_format_0=(label), _coconut_format_1=(key)))  #1521 (line in Coconut source)
            for key, subschema in schema.get("properties", {}).items():  #1522 (line in Coconut source)
                if key in payload:  #1523 (line in Coconut source)
                    self._validate_against_schema(payload[key], subschema, label="{_coconut_format_0}.{_coconut_format_1}".format(_coconut_format_0=(label), _coconut_format_1=(key)))  #1524 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1525 (line in Coconut source)
            if _coconut_case_match_to_5 == "array":  #1525 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1525 (line in Coconut source)
            if _coconut_case_match_check_5:  #1525 (line in Coconut source)
                if not isinstance(payload, list):  #1526 (line in Coconut source)
                    raise ValueError("{_coconut_format_0} must be an array".format(_coconut_format_0=(label)))  #1527 (line in Coconut source)
                for idx, item in enumerate(payload):  #1528 (line in Coconut source)
                    self._validate_against_schema(item, schema.get("items", {}), label="{_coconut_format_0}[{_coconut_format_1}]".format(_coconut_format_0=(label), _coconut_format_1=(idx)))  #1529 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1530 (line in Coconut source)
            if _coconut_case_match_to_5 == "string":  #1530 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1530 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, str)):  #1530 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1530 (line in Coconut source)
            if _coconut_case_match_check_5:  #1530 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a string".format(_coconut_format_0=(label)))  #1531 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1532 (line in Coconut source)
            if _coconut_case_match_to_5 == "integer":  #1532 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1532 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, int)):  #1532 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1532 (line in Coconut source)
            if _coconut_case_match_check_5:  #1532 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be an integer".format(_coconut_format_0=(label)))  #1533 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1534 (line in Coconut source)
            if _coconut_case_match_to_5 == "number":  #1534 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1534 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, (int, float))):  #1534 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1534 (line in Coconut source)
            if _coconut_case_match_check_5:  #1534 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a number".format(_coconut_format_0=(label)))  #1535 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1536 (line in Coconut source)
            if _coconut_case_match_to_5 == "boolean":  #1536 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1536 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, bool)):  #1536 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1536 (line in Coconut source)
            if _coconut_case_match_check_5:  #1536 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a boolean".format(_coconut_format_0=(label)))  #1537 (line in Coconut source)


    async def _validate_node_schemas(self, node: AnyNode, *, input_payload: Any=None, output_payload: Any=None, ctx: ExecutionContext, parent_event_id: str | None=None,) -> None:  #1539 (line in Coconut source)
        try:  #1548 (line in Coconut source)
            _coconut_case_match_to_6 = node  #1549 (line in Coconut source)
            _coconut_case_match_check_6 = False  #1549 (line in Coconut source)
            _coconut_match_temp_3 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #1549 (line in Coconut source)
            _coconut_case_match_check_6 = True  #1549 (line in Coconut source)
            if _coconut_case_match_check_6:  #1549 (line in Coconut source)
                _coconut_case_match_check_6 = False  #1549 (line in Coconut source)
                if not _coconut_case_match_check_6:  #1549 (line in Coconut source)
                    if (_coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_6, ToolNode)):  #1549 (line in Coconut source)
                        _coconut_match_temp_4 = _coconut.len(_coconut_case_match_to_6) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_6.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {}) and _coconut_case_match_to_6[i] == _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_6.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_6, "__match_args__") else _coconut.len(_coconut_case_match_to_6) == 0  # type: ignore  #1549 (line in Coconut source)
                        if _coconut_match_temp_4:  #1549 (line in Coconut source)
                            _coconut_case_match_check_6 = True  #1549 (line in Coconut source)

                if not _coconut_case_match_check_6:  #1549 (line in Coconut source)
                    if (not _coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_6, ToolNode)):  #1549 (line in Coconut source)
                        _coconut_case_match_check_6 = True  #1549 (line in Coconut source)
                    if _coconut_case_match_check_6:  #1549 (line in Coconut source)
                        _coconut_case_match_check_6 = False  #1549 (line in Coconut source)
                        if not _coconut_case_match_check_6:  #1549 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1549 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1549 (line in Coconut source)

                        if not _coconut_case_match_check_6:  #1549 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1549 (line in Coconut source)
                                _coconut_match_temp_5 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1549 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_5, _coconut.tuple):  #1549 (line in Coconut source)
                                    raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #1549 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_5) < 0:  #1549 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_5),))  #1549 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1549 (line in Coconut source)




            if _coconut_case_match_check_6:  #1549 (line in Coconut source)
                if input_payload is not None:  #1551 (line in Coconut source)
                    self._validate_against_schema(input_payload, node.input_schema, label="tool_input")  #1552 (line in Coconut source)
                if output_payload is not None:  #1553 (line in Coconut source)
                    self._validate_against_schema(output_payload, node.output_schema, label="tool_output")  #1554 (line in Coconut source)
            if not _coconut_case_match_check_6:  #1555 (line in Coconut source)
                _coconut_match_temp_6 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1555 (line in Coconut source)
                _coconut_case_match_check_6 = True  #1555 (line in Coconut source)
                if _coconut_case_match_check_6:  #1555 (line in Coconut source)
                    _coconut_case_match_check_6 = False  #1555 (line in Coconut source)
                    if not _coconut_case_match_check_6:  #1555 (line in Coconut source)
                        if (_coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_6, AgentNode)):  #1555 (line in Coconut source)
                            _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_6) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_6.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {}) and _coconut_case_match_to_6[i] == _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_6.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_6, "__match_args__") else _coconut.len(_coconut_case_match_to_6) == 0  # type: ignore  #1555 (line in Coconut source)
                            if _coconut_match_temp_7:  #1555 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1555 (line in Coconut source)

                    if not _coconut_case_match_check_6:  #1555 (line in Coconut source)
                        if (not _coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_6, AgentNode)):  #1555 (line in Coconut source)
                            _coconut_case_match_check_6 = True  #1555 (line in Coconut source)
                        if _coconut_case_match_check_6:  #1555 (line in Coconut source)
                            _coconut_case_match_check_6 = False  #1555 (line in Coconut source)
                            if not _coconut_case_match_check_6:  #1555 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1555 (line in Coconut source)
                                    _coconut_case_match_check_6 = True  #1555 (line in Coconut source)

                            if not _coconut_case_match_check_6:  #1555 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1555 (line in Coconut source)
                                    _coconut_match_temp_8 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1555 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #1555 (line in Coconut source)
                                        raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1555 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_8) < 0:  #1555 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #1555 (line in Coconut source)
                                    _coconut_case_match_check_6 = True  #1555 (line in Coconut source)




                if _coconut_case_match_check_6:  #1555 (line in Coconut source)
                    state_schema = node.state_schema or ctx.state.schema  #1556 (line in Coconut source)
                    if state_schema:  #1557 (line in Coconut source)
                        self._validate_against_schema(ctx.state.data, state_schema, label="state")  #1558 (line in Coconut source)
                    await self._validate_constraint_rules(node, ctx=ctx, result=output_payload, input_payload=input_payload, output_payload=output_payload, parent_event_id=parent_event_id)  #1559 (line in Coconut source)
            validates = await self.store.get_edges(node.node_id, edge_type=EdgeType.VALIDATES, direction="in")  #1567 (line in Coconut source)
            for edge in validates:  #1568 (line in Coconut source)
                schema_node = await self.store.get_node(edge.src_id)  #1569 (line in Coconut source)
                if not isinstance(schema_node, SchemaNode):  #1570 (line in Coconut source)
                    continue  #1571 (line in Coconut source)
                phase = edge.attributes.get("phase", "output")  #1572 (line in Coconut source)
                payload = output_payload if phase == "output" else input_payload  #1573 (line in Coconut source)
                if payload is not None:  #1574 (line in Coconut source)
                    self._validate_against_schema(payload, schema_node.json_schema, label="{_coconut_format_0}_payload".format(_coconut_format_0=(phase)))  #1575 (line in Coconut source)
        except Exception as exc:  #1576 (line in Coconut source)
            self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": False, "error": str(exc)}, parent_event_id=parent_event_id)  #1577 (line in Coconut source)
            raise  #1585 (line in Coconut source)
        self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": True}, parent_event_id=parent_event_id)  #1586 (line in Coconut source)

# ------------------------------------------------------------------
# Sequential (DFS)
# ------------------------------------------------------------------


    async def _run_sequential(self, node: AnyNode, ctx: ExecutionContext) -> Any:  #1599 (line in Coconut source)
        if ctx.is_paused():  #1600 (line in Coconut source)
            return None  #1601 (line in Coconut source)
        if ctx.hop_count >= ctx.max_hops:  #1602 (line in Coconut source)
            return None  #1603 (line in Coconut source)
        ctx.hop_count += 1  #1604 (line in Coconut source)

        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={"hop": ctx.hop_count, "node_type": str(node.node_type), "summary": ""})  #1606 (line in Coconut source)

        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)  #1612 (line in Coconut source)
        ctx.outputs[node.node_id] = result  #1613 (line in Coconut source)
        ctx.state.data["_last_node_id"] = node.node_id  #1614 (line in Coconut source)
        ctx.state.data["_last_output"] = result  #1615 (line in Coconut source)

        hop_event.payload["summary"] = _summarise(result)  #1617 (line in Coconut source)

        if ctx.is_paused():  #1619 (line in Coconut source)
            return result  #1620 (line in Coconut source)

        _coconut_case_match_to_7 = node  #1622 (line in Coconut source)
        _coconut_case_match_check_7 = False  #1622 (line in Coconut source)
        _coconut_match_temp_9 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1622 (line in Coconut source)
        _coconut_case_match_check_7 = True  #1622 (line in Coconut source)
        if _coconut_case_match_check_7:  #1622 (line in Coconut source)
            _coconut_case_match_check_7 = False  #1622 (line in Coconut source)
            if not _coconut_case_match_check_7:  #1622 (line in Coconut source)
                _coconut_match_set_name_rt = _coconut_sentinel  #1622 (line in Coconut source)
                if (_coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_7, AgentNode)):  #1622 (line in Coconut source)
                    _coconut_match_temp_10 = _coconut.getattr(_coconut_case_match_to_7, 'routing_table', _coconut_sentinel)  #1622 (line in Coconut source)
                    _coconut_match_temp_11 = _coconut.len(_coconut_case_match_to_7) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {}) and _coconut_case_match_to_7[i] == _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) if _coconut_case_match_to_7.__match_args__[i] not in ('routing_table',)) if _coconut.hasattr(_coconut_case_match_to_7, "__match_args__") else _coconut.len(_coconut_case_match_to_7) == 0  # type: ignore  #1622 (line in Coconut source)
                    if (_coconut_match_temp_10 is not _coconut_sentinel) and (_coconut_match_temp_11):  #1622 (line in Coconut source)
                        _coconut_match_set_name_rt = _coconut_match_temp_10  #1622 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1622 (line in Coconut source)
                if _coconut_case_match_check_7:  #1622 (line in Coconut source)
                    if _coconut_match_set_name_rt is not _coconut_sentinel:  #1622 (line in Coconut source)
                        rt = _coconut_match_set_name_rt  #1622 (line in Coconut source)

            if not _coconut_case_match_check_7:  #1622 (line in Coconut source)
                _coconut_match_set_name_rt = _coconut_sentinel  #1622 (line in Coconut source)
                if (not _coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_7, AgentNode)):  #1622 (line in Coconut source)
                    _coconut_match_temp_13 = _coconut.getattr(_coconut_case_match_to_7, 'routing_table', _coconut_sentinel)  #1622 (line in Coconut source)
                    if _coconut_match_temp_13 is not _coconut_sentinel:  #1622 (line in Coconut source)
                        _coconut_match_set_name_rt = _coconut_match_temp_13  #1622 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1622 (line in Coconut source)
                if _coconut_case_match_check_7:  #1622 (line in Coconut source)
                    _coconut_case_match_check_7 = False  #1622 (line in Coconut source)
                    if not _coconut_case_match_check_7:  #1622 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1622 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1622 (line in Coconut source)

                    if not _coconut_case_match_check_7:  #1622 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1622 (line in Coconut source)
                            _coconut_match_temp_12 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1622 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_12, _coconut.tuple):  #1622 (line in Coconut source)
                                raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1622 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_12) < 0:  #1622 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_12),))  #1622 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1622 (line in Coconut source)


                if _coconut_case_match_check_7:  #1622 (line in Coconut source)
                    if _coconut_match_set_name_rt is not _coconut_sentinel:  #1622 (line in Coconut source)
                        rt = _coconut_match_set_name_rt  #1622 (line in Coconut source)


        if _coconut_case_match_check_7 and not (rt):  #1622 (line in Coconut source)
            _coconut_case_match_check_7 = False  #1622 (line in Coconut source)
        if _coconut_case_match_check_7:  #1622 (line in Coconut source)
            next_id = await self._route(node, result, ctx, parent_event_id=hop_event.event_id)  #1624 (line in Coconut source)
            if next_id and next_id != "__END__":  #1625 (line in Coconut source)
                next_node = await self.store.get_node(next_id)  #1626 (line in Coconut source)
                if next_node:  #1627 (line in Coconut source)
                    return await self._run_sequential(next_node, ctx)  #1628 (line in Coconut source)
        if not _coconut_case_match_check_7:  #1629 (line in Coconut source)
            _coconut_match_temp_14 = _coconut.getattr(ApprovalNode, "_coconut_is_data", False) or _coconut.isinstance(ApprovalNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ApprovalNode)  # type: ignore  #1629 (line in Coconut source)
            _coconut_case_match_check_7 = True  #1629 (line in Coconut source)
            if _coconut_case_match_check_7:  #1629 (line in Coconut source)
                _coconut_case_match_check_7 = False  #1629 (line in Coconut source)
                if not _coconut_case_match_check_7:  #1629 (line in Coconut source)
                    if (_coconut_match_temp_14) and (_coconut.isinstance(_coconut_case_match_to_7, ApprovalNode)):  #1629 (line in Coconut source)
                        _coconut_match_temp_15 = _coconut.len(_coconut_case_match_to_7) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {}) and _coconut_case_match_to_7[i] == _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_7.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_7, "__match_args__") else _coconut.len(_coconut_case_match_to_7) == 0  # type: ignore  #1629 (line in Coconut source)
                        if _coconut_match_temp_15:  #1629 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1629 (line in Coconut source)

                if not _coconut_case_match_check_7:  #1629 (line in Coconut source)
                    if (not _coconut_match_temp_14) and (_coconut.isinstance(_coconut_case_match_to_7, ApprovalNode)):  #1629 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1629 (line in Coconut source)
                    if _coconut_case_match_check_7:  #1629 (line in Coconut source)
                        _coconut_case_match_check_7 = False  #1629 (line in Coconut source)
                        if not _coconut_case_match_check_7:  #1629 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1629 (line in Coconut source)
                                _coconut_case_match_check_7 = True  #1629 (line in Coconut source)

                        if not _coconut_case_match_check_7:  #1629 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1629 (line in Coconut source)
                                _coconut_match_temp_16 = _coconut.getattr(ApprovalNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1629 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_16, _coconut.tuple):  #1629 (line in Coconut source)
                                    raise _coconut.TypeError("ApprovalNode.__match_args__ must be a tuple")  #1629 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_16) < 0:  #1629 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ApprovalNode' only supports %s)" % (_coconut.len(_coconut_match_temp_16),))  #1629 (line in Coconut source)
                                _coconut_case_match_check_7 = True  #1629 (line in Coconut source)




            if _coconut_case_match_check_7:  #1629 (line in Coconut source)
                next_id = result.get("next_node_id") if isinstance(result, dict) else None  #1630 (line in Coconut source)
                if next_id and next_id != "__END__":  #1631 (line in Coconut source)
                    next_node = await self.store.get_node(next_id)  #1632 (line in Coconut source)
                    if next_node:  #1633 (line in Coconut source)
                        return await self._run_sequential(next_node, ctx)  #1634 (line in Coconut source)

        return result  #1636 (line in Coconut source)

# ------------------------------------------------------------------
# Parallel (BFS fan-out)
# ------------------------------------------------------------------


    async def _run_parallel(self, node: AnyNode, ctx: ExecutionContext) -> Any:  #1642 (line in Coconut source)
        if ctx.is_paused():  #1643 (line in Coconut source)
            return None  #1644 (line in Coconut source)
        if ctx.hop_count >= ctx.max_hops:  #1645 (line in Coconut source)
            return None  #1646 (line in Coconut source)
        ctx.hop_count += 1  #1647 (line in Coconut source)
        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={"hop": ctx.hop_count, "node_type": str(node.node_type), "summary": ""})  #1648 (line in Coconut source)
        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)  #1653 (line in Coconut source)
        ctx.outputs[node.node_id] = result  #1654 (line in Coconut source)
        ctx.state.data["_last_node_id"] = node.node_id  #1655 (line in Coconut source)
        ctx.state.data["_last_output"] = result  #1656 (line in Coconut source)
        hop_event.payload["summary"] = _summarise(result)  #1657 (line in Coconut source)

        delegate_edges = await self.store.get_edges(node.node_id, edge_type=EdgeType.DELEGATES_TO)  #1659 (line in Coconut source)
        if not delegate_edges:  #1662 (line in Coconut source)
            return result  #1663 (line in Coconut source)

        delegate_nodes = []  #1665 (line in Coconut source)
        for edge in delegate_edges:  #1666 (line in Coconut source)
            n = await self.store.get_node(edge.dst_id)  #1667 (line in Coconut source)
            if n:  #1668 (line in Coconut source)
                delegate_nodes.append(n)  #1669 (line in Coconut source)

        sub_results = await asyncio.gather(*[self._run_parallel(d, ctx) for d in delegate_nodes])  #1671 (line in Coconut source)

        merged = {"node_result": result, "delegate_results": {d.node_id: r for d, r in zip(delegate_nodes, sub_results)}}  #1675 (line in Coconut source)
        ctx.outputs[node.node_id] = merged  #1681 (line in Coconut source)
        return merged  #1682 (line in Coconut source)

# ------------------------------------------------------------------
# Topological (DAG waves)
# ------------------------------------------------------------------


    async def _run_topological(self, entry_node_id: str, ctx: ExecutionContext) -> None:  #1688 (line in Coconut source)
        """Execute a DAG in topological order using stdlib graphlib."""  #1689 (line in Coconut source)
        dep_map: dict[str, set[str]] = {}  #1690 (line in Coconut source)
        visited: set[str] = set()  #1691 (line in Coconut source)
        queue = [entry_node_id,]  #1692 (line in Coconut source)

        while queue:  #1694 (line in Coconut source)
            nid = queue.pop()  #1695 (line in Coconut source)
            if nid in visited:  #1696 (line in Coconut source)
                continue  #1697 (line in Coconut source)
            visited.add(nid)  #1698 (line in Coconut source)
            edges = await self.store.get_edges(nid, edge_type=EdgeType.DELEGATES_TO)  #1699 (line in Coconut source)
            dep_map.setdefault(nid, set())  #1700 (line in Coconut source)
            for e in edges:  #1701 (line in Coconut source)
                dep_map.setdefault(e.dst_id, set()).add(nid)  #1702 (line in Coconut source)
                if e.dst_id not in visited:  #1703 (line in Coconut source)
                    queue.append(e.dst_id)  #1704 (line in Coconut source)

        for nid in list(dep_map):  #1706 (line in Coconut source)
            node = await self.store.get_node(nid)  #1707 (line in Coconut source)
            if isinstance(node, TransformNode) and node.input_keys:  #1708 (line in Coconut source)
                for key in node.input_keys:  #1709 (line in Coconut source)
                    if key in dep_map:  #1710 (line in Coconut source)
                        dep_map[nid].add(key)  #1711 (line in Coconut source)

        sorter = graphlib.TopologicalSorter(dep_map)  #1713 (line in Coconut source)
        sorter.prepare()  #1714 (line in Coconut source)

        wave = 0  #1716 (line in Coconut source)
        while sorter.is_active():  #1717 (line in Coconut source)
            if ctx.is_paused():  #1718 (line in Coconut source)
                return  #1719 (line in Coconut source)
            if ctx.hop_count >= ctx.max_hops:  #1720 (line in Coconut source)
                return  #1721 (line in Coconut source)
            wave += 1  #1722 (line in Coconut source)
            ready = list(sorter.get_ready())  #1723 (line in Coconut source)
            remaining = max(ctx.max_hops - ctx.hop_count, 0)  #1724 (line in Coconut source)
            if remaining == 0:  #1725 (line in Coconut source)
                return  #1726 (line in Coconut source)
            if len(ready) > remaining:  #1727 (line in Coconut source)
                ready = ready[:remaining]  #1728 (line in Coconut source)
            nodes = list(await asyncio.gather(*[self.store.get_node(nid) for nid in ready]))  #1729 (line in Coconut source)

            hop_events = []  #1731 (line in Coconut source)
            valid_nodes = [(nid, n) for nid, n in zip(ready, nodes) if n is not None]  #1732 (line in Coconut source)
            for nid, n in valid_nodes:  #1733 (line in Coconut source)
                ctx.hop_count += 1  #1734 (line in Coconut source)
                hop_event = self._emit(ctx, "hop", nid, n.name or "", payload={"hop": ctx.hop_count, "node_type": str(n.node_type), "summary": "", "wave": wave})  #1735 (line in Coconut source)
                hop_events.append(hop_event)  #1741 (line in Coconut source)

            t0 = time.monotonic()  #1743 (line in Coconut source)
            results = await asyncio.gather(*[self._execute_node(n, ctx, parent_event_id=he.event_id) for (_, n), he in zip(valid_nodes, hop_events)])  #1744 (line in Coconut source)
            wave_ms = int((time.monotonic() - t0) * 1000)  #1748 (line in Coconut source)

            for (nid, _), result, hop_event in zip(valid_nodes, results, hop_events):  #1750 (line in Coconut source)
                ctx.outputs[nid] = result  #1751 (line in Coconut source)
                ctx.state.data["_last_node_id"] = nid  #1752 (line in Coconut source)
                ctx.state.data["_last_output"] = result  #1753 (line in Coconut source)
                hop_event.payload["summary"] = _summarise(result)  #1754 (line in Coconut source)
                hop_event.payload["wave_ms"] = wave_ms  #1755 (line in Coconut source)
                sorter.done(nid)  #1756 (line in Coconut source)

# ------------------------------------------------------------------
# Node dispatch
# ------------------------------------------------------------------


    async def _execute_node(self, node: AnyNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #1762 (line in Coconut source)
        _coconut_case_match_to_8 = node  #1768 (line in Coconut source)
        _coconut_case_match_check_8 = False  #1768 (line in Coconut source)
        _coconut_match_temp_17 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1768 (line in Coconut source)
        _coconut_case_match_check_8 = True  #1768 (line in Coconut source)
        if _coconut_case_match_check_8:  #1768 (line in Coconut source)
            _coconut_case_match_check_8 = False  #1768 (line in Coconut source)
            if not _coconut_case_match_check_8:  #1768 (line in Coconut source)
                if (_coconut_match_temp_17) and (_coconut.isinstance(_coconut_case_match_to_8, AgentNode)):  #1768 (line in Coconut source)
                    _coconut_match_temp_18 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1768 (line in Coconut source)
                    if _coconut_match_temp_18:  #1768 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1768 (line in Coconut source)

            if not _coconut_case_match_check_8:  #1768 (line in Coconut source)
                if (not _coconut_match_temp_17) and (_coconut.isinstance(_coconut_case_match_to_8, AgentNode)):  #1768 (line in Coconut source)
                    _coconut_case_match_check_8 = True  #1768 (line in Coconut source)
                if _coconut_case_match_check_8:  #1768 (line in Coconut source)
                    _coconut_case_match_check_8 = False  #1768 (line in Coconut source)
                    if not _coconut_case_match_check_8:  #1768 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1768 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1768 (line in Coconut source)

                    if not _coconut_case_match_check_8:  #1768 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1768 (line in Coconut source)
                            _coconut_match_temp_19 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1768 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_19, _coconut.tuple):  #1768 (line in Coconut source)
                                raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1768 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_19) < 0:  #1768 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_19),))  #1768 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1768 (line in Coconut source)




        if _coconut_case_match_check_8:  #1768 (line in Coconut source)
            return await self._execute_agent(node, ctx, parent_event_id=parent_event_id)  #1770 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1771 (line in Coconut source)
            _coconut_match_temp_20 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #1771 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1771 (line in Coconut source)
            if _coconut_case_match_check_8:  #1771 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1771 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1771 (line in Coconut source)
                    if (_coconut_match_temp_20) and (_coconut.isinstance(_coconut_case_match_to_8, ToolNode)):  #1771 (line in Coconut source)
                        _coconut_match_temp_21 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1771 (line in Coconut source)
                        if _coconut_match_temp_21:  #1771 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1771 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1771 (line in Coconut source)
                    if (not _coconut_match_temp_20) and (_coconut.isinstance(_coconut_case_match_to_8, ToolNode)):  #1771 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1771 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1771 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1771 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1771 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1771 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1771 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1771 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1771 (line in Coconut source)
                                _coconut_match_temp_22 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1771 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_22, _coconut.tuple):  #1771 (line in Coconut source)
                                    raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #1771 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_22) < 0:  #1771 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_22),))  #1771 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1771 (line in Coconut source)




            if _coconut_case_match_check_8:  #1771 (line in Coconut source)
                t0 = time.monotonic()  #1772 (line in Coconut source)
                result = await self._execute_tool(node, ctx)  #1773 (line in Coconut source)
                duration_ms = int((time.monotonic() - t0) * 1000)  #1774 (line in Coconut source)
                self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name, "callable_ref": node.callable_ref, "output_summary": _summarise(result), "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #1775 (line in Coconut source)
                return result  #1786 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1787 (line in Coconut source)
            _coconut_match_temp_23 = _coconut.getattr(ApprovalNode, "_coconut_is_data", False) or _coconut.isinstance(ApprovalNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ApprovalNode)  # type: ignore  #1787 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1787 (line in Coconut source)
            if _coconut_case_match_check_8:  #1787 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1787 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1787 (line in Coconut source)
                    if (_coconut_match_temp_23) and (_coconut.isinstance(_coconut_case_match_to_8, ApprovalNode)):  #1787 (line in Coconut source)
                        _coconut_match_temp_24 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1787 (line in Coconut source)
                        if _coconut_match_temp_24:  #1787 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1787 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1787 (line in Coconut source)
                    if (not _coconut_match_temp_23) and (_coconut.isinstance(_coconut_case_match_to_8, ApprovalNode)):  #1787 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1787 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1787 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1787 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1787 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1787 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1787 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1787 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1787 (line in Coconut source)
                                _coconut_match_temp_25 = _coconut.getattr(ApprovalNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1787 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_25, _coconut.tuple):  #1787 (line in Coconut source)
                                    raise _coconut.TypeError("ApprovalNode.__match_args__ must be a tuple")  #1787 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_25) < 0:  #1787 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ApprovalNode' only supports %s)" % (_coconut.len(_coconut_match_temp_25),))  #1787 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1787 (line in Coconut source)




            if _coconut_case_match_check_8:  #1787 (line in Coconut source)
                return await self._execute_approval(node, ctx, parent_event_id=parent_event_id)  #1788 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1789 (line in Coconut source)
            _coconut_match_temp_26 = _coconut.getattr(ContextNode, "_coconut_is_data", False) or _coconut.isinstance(ContextNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ContextNode)  # type: ignore  #1789 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1789 (line in Coconut source)
            if _coconut_case_match_check_8:  #1789 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1789 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1789 (line in Coconut source)
                    if (_coconut_match_temp_26) and (_coconut.isinstance(_coconut_case_match_to_8, ContextNode)):  #1789 (line in Coconut source)
                        _coconut_match_temp_27 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1789 (line in Coconut source)
                        if _coconut_match_temp_27:  #1789 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1789 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1789 (line in Coconut source)
                    if (not _coconut_match_temp_26) and (_coconut.isinstance(_coconut_case_match_to_8, ContextNode)):  #1789 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1789 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1789 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1789 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1789 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1789 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1789 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1789 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1789 (line in Coconut source)
                                _coconut_match_temp_28 = _coconut.getattr(ContextNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1789 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_28, _coconut.tuple):  #1789 (line in Coconut source)
                                    raise _coconut.TypeError("ContextNode.__match_args__ must be a tuple")  #1789 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_28) < 0:  #1789 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ContextNode' only supports %s)" % (_coconut.len(_coconut_match_temp_28),))  #1789 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1789 (line in Coconut source)




            if _coconut_case_match_check_8:  #1789 (line in Coconut source)
                return node.content  #1790 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
            _coconut_match_temp_29 = _coconut.getattr(GraphNode, "_coconut_is_data", False) or _coconut.isinstance(GraphNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in GraphNode)  # type: ignore  #1791 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1791 (line in Coconut source)
            if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1791 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                    if (_coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_8, GraphNode)):  #1791 (line in Coconut source)
                        _coconut_match_temp_30 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1791 (line in Coconut source)
                        if _coconut_match_temp_30:  #1791 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1791 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                    if (not _coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_8, GraphNode)):  #1791 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1791 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1791 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1791 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1791 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1791 (line in Coconut source)
                                _coconut_match_temp_31 = _coconut.getattr(GraphNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1791 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_31, _coconut.tuple):  #1791 (line in Coconut source)
                                    raise _coconut.TypeError("GraphNode.__match_args__ must be a tuple")  #1791 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_31) < 0:  #1791 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'GraphNode' only supports %s)" % (_coconut.len(_coconut_match_temp_31),))  #1791 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1791 (line in Coconut source)




            if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                return await self._execute_subgraph(node, ctx, parent_event_id=parent_event_id)  #1792 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1793 (line in Coconut source)
            _coconut_match_temp_32 = _coconut.getattr(TransformNode, "_coconut_is_data", False) or _coconut.isinstance(TransformNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in TransformNode)  # type: ignore  #1793 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1793 (line in Coconut source)
            if _coconut_case_match_check_8:  #1793 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1793 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1793 (line in Coconut source)
                    if (_coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_8, TransformNode)):  #1793 (line in Coconut source)
                        _coconut_match_temp_33 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1793 (line in Coconut source)
                        if _coconut_match_temp_33:  #1793 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1793 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1793 (line in Coconut source)
                    if (not _coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_8, TransformNode)):  #1793 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1793 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1793 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1793 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1793 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1793 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1793 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1793 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1793 (line in Coconut source)
                                _coconut_match_temp_34 = _coconut.getattr(TransformNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1793 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_34, _coconut.tuple):  #1793 (line in Coconut source)
                                    raise _coconut.TypeError("TransformNode.__match_args__ must be a tuple")  #1793 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_34) < 0:  #1793 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'TransformNode' only supports %s)" % (_coconut.len(_coconut_match_temp_34),))  #1793 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1793 (line in Coconut source)




            if _coconut_case_match_check_8:  #1793 (line in Coconut source)
                return await self._execute_transform(node, ctx, parent_event_id=parent_event_id)  #1794 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1795 (line in Coconut source)
            _coconut_match_temp_35 = _coconut.getattr(ReasonerNode, "_coconut_is_data", False) or _coconut.isinstance(ReasonerNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ReasonerNode)  # type: ignore  #1795 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1795 (line in Coconut source)
            if _coconut_case_match_check_8:  #1795 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1795 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1795 (line in Coconut source)
                    if (_coconut_match_temp_35) and (_coconut.isinstance(_coconut_case_match_to_8, ReasonerNode)):  #1795 (line in Coconut source)
                        _coconut_match_temp_36 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1795 (line in Coconut source)
                        if _coconut_match_temp_36:  #1795 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1795 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1795 (line in Coconut source)
                    if (not _coconut_match_temp_35) and (_coconut.isinstance(_coconut_case_match_to_8, ReasonerNode)):  #1795 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1795 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1795 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1795 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1795 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1795 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1795 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1795 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1795 (line in Coconut source)
                                _coconut_match_temp_37 = _coconut.getattr(ReasonerNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1795 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_37, _coconut.tuple):  #1795 (line in Coconut source)
                                    raise _coconut.TypeError("ReasonerNode.__match_args__ must be a tuple")  #1795 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_37) < 0:  #1795 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ReasonerNode' only supports %s)" % (_coconut.len(_coconut_match_temp_37),))  #1795 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1795 (line in Coconut source)




            if _coconut_case_match_check_8:  #1795 (line in Coconut source)
                return await self._execute_reasoner(node, ctx, parent_event_id=parent_event_id)  #1796 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1797 (line in Coconut source)
            _coconut_match_temp_38 = _coconut.getattr(PromptNode, "_coconut_is_data", False) or _coconut.isinstance(PromptNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in PromptNode)  # type: ignore  #1797 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1797 (line in Coconut source)
            if _coconut_case_match_check_8:  #1797 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1797 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1797 (line in Coconut source)
                    if (_coconut_match_temp_38) and (_coconut.isinstance(_coconut_case_match_to_8, PromptNode)):  #1797 (line in Coconut source)
                        _coconut_match_temp_39 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1797 (line in Coconut source)
                        if _coconut_match_temp_39:  #1797 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1797 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1797 (line in Coconut source)
                    if (not _coconut_match_temp_38) and (_coconut.isinstance(_coconut_case_match_to_8, PromptNode)):  #1797 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1797 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1797 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1797 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1797 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1797 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1797 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1797 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1797 (line in Coconut source)
                                _coconut_match_temp_40 = _coconut.getattr(PromptNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1797 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_40, _coconut.tuple):  #1797 (line in Coconut source)
                                    raise _coconut.TypeError("PromptNode.__match_args__ must be a tuple")  #1797 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_40) < 0:  #1797 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'PromptNode' only supports %s)" % (_coconut.len(_coconut_match_temp_40),))  #1797 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1797 (line in Coconut source)




            if _coconut_case_match_check_8:  #1797 (line in Coconut source)
                return node.render()  #1798 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1799 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1799 (line in Coconut source)
            if _coconut_case_match_check_8:  #1799 (line in Coconut source)
                return None  #1800 (line in Coconut source)

# ------------------------------------------------------------------
# Sub-graph execution
# ------------------------------------------------------------------


    _MAX_SUBGRAPH_DEPTH = 16  #1806 (line in Coconut source)

    async def _execute_subgraph(self, node: GraphNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #1808 (line in Coconut source)
        """Run a GraphNode: descend, route to exit, surface result."""  #1814 (line in Coconut source)
        if node.node_id in ctx._active_subgraphs:  #1815 (line in Coconut source)
            chain = " → ".join(ctx._active_subgraphs + [node.node_id,])  #1816 (line in Coconut source)
            raise ValueError("GraphNode cycle detected: {_coconut_format_0}".format(_coconut_format_0=(chain)))  #1817 (line in Coconut source)
        if len(ctx._active_subgraphs) >= self._MAX_SUBGRAPH_DEPTH:  #1818 (line in Coconut source)
            raise ValueError(("GraphNode recursion depth exceeded ".format() + "({_coconut_format_0}) at {_coconut_format_1!r}".format(_coconut_format_0=(self._MAX_SUBGRAPH_DEPTH), _coconut_format_1=(node.name or node.node_id))))  #1819 (line in Coconut source)

        if not node.entry_node_id:  #1824 (line in Coconut source)
            raise ValueError("GraphNode {_coconut_format_0!r} has no entry_node_id.".format(_coconut_format_0=(node.name or node.node_id)))  #1825 (line in Coconut source)
        sub_entry = await self.store.get_node(node.entry_node_id)  #1828 (line in Coconut source)
        if sub_entry is None:  #1829 (line in Coconut source)
            raise ValueError(("GraphNode {_coconut_format_0!r} entry_node_id ".format(_coconut_format_0=(node.name or node.node_id)) + "{_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node.entry_node_id))))  #1830 (line in Coconut source)

        exit_id = node.exit_node_id or node.entry_node_id  #1835 (line in Coconut source)
        sub_query = self._resolve_subgraph_query(node, ctx)  #1836 (line in Coconut source)
        sub_state_overlay = self._resolve_subgraph_state(node, ctx)  #1837 (line in Coconut source)

        self._emit(ctx, "subgraph_enter", node.node_id, node.name or "", payload={"entry_node_id": node.entry_node_id, "exit_node_id": exit_id, "strategy": node.strategy, "scoped": node.scope_outputs}, parent_event_id=parent_event_id)  #1839 (line in Coconut source)

        async def _run_subgraph() -> Any:  #1850 (line in Coconut source)
            if node.scope_outputs:  #1851 (line in Coconut source)
                child = ExecutionContext(query=sub_query, session_id=ctx.session_id, max_hops=max(ctx.max_hops - ctx.hop_count, 1), state=ctx.state, allowed_tools=ctx.allowed_tools, extra_messages=list(ctx.extra_messages), _active_subgraphs=ctx._active_subgraphs + [node.node_id,])  #1852 (line in Coconut source)
                if sub_state_overlay:  #1861 (line in Coconut source)
                    ctx.state.data.update(sub_state_overlay)  #1862 (line in Coconut source)
                await self._dispatch_strategy(node.strategy, sub_entry, child)  #1863 (line in Coconut source)
                ctx.trace.extend(child.trace)  #1864 (line in Coconut source)
                ctx.hop_count += child.hop_count  #1865 (line in Coconut source)
                return child.outputs.get(exit_id)  #1866 (line in Coconut source)
            else:  #1867 (line in Coconut source)
                ctx._active_subgraphs.append(node.node_id)  #1868 (line in Coconut source)
                try:  #1869 (line in Coconut source)
                    if sub_state_overlay:  #1870 (line in Coconut source)
                        ctx.state.data.update(sub_state_overlay)  #1871 (line in Coconut source)
                    if sub_query is not None:  #1872 (line in Coconut source)
                        prev_query = ctx.query  #1873 (line in Coconut source)
                        ctx.query = sub_query  #1874 (line in Coconut source)
                        try:  #1875 (line in Coconut source)
                            await self._dispatch_strategy(node.strategy, sub_entry, ctx)  #1876 (line in Coconut source)
                        finally:  #1877 (line in Coconut source)
                            ctx.query = prev_query  #1878 (line in Coconut source)
                    else:  #1879 (line in Coconut source)
                        await self._dispatch_strategy(node.strategy, sub_entry, ctx)  #1880 (line in Coconut source)
                    return ctx.outputs.get(exit_id)  #1881 (line in Coconut source)
                finally:  #1882 (line in Coconut source)
                    ctx._active_subgraphs.pop()  #1883 (line in Coconut source)


        try:  #1885 (line in Coconut source)
            result = await self._call_with_retry(_run_subgraph, ctx, node=node, policy=node.execution_policy, parent_event_id=parent_event_id)  #1886 (line in Coconut source)
        except Exception as exc:  #1893 (line in Coconut source)
            self._emit(ctx, "subgraph_exit", node.node_id, node.name or "", payload={"exit_node_id": exit_id, "summary": "", "error": str(exc), "error_type": type(exc).__name__}, parent_event_id=parent_event_id)  #1894 (line in Coconut source)
            raise  #1904 (line in Coconut source)

        self._emit(ctx, "subgraph_exit", node.node_id, node.name or "", payload={"exit_node_id": exit_id, "summary": _summarise(result)}, parent_event_id=parent_event_id)  #1906 (line in Coconut source)
        return result  #1911 (line in Coconut source)


    async def _dispatch_strategy(self, strategy: str, entry: AnyNode, ctx: ExecutionContext,) -> None:  #1913 (line in Coconut source)
        _coconut_case_match_to_9 = strategy  #1919 (line in Coconut source)
        _coconut_case_match_check_9 = False  #1919 (line in Coconut source)
        if _coconut_case_match_to_9 == "sequential":  #1919 (line in Coconut source)
            _coconut_case_match_check_9 = True  #1919 (line in Coconut source)
        if _coconut_case_match_check_9:  #1919 (line in Coconut source)
            await self._run_sequential(entry, ctx)  #1921 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1922 (line in Coconut source)
            if _coconut_case_match_to_9 == "parallel":  #1922 (line in Coconut source)
                _coconut_case_match_check_9 = True  #1922 (line in Coconut source)
            if _coconut_case_match_check_9:  #1922 (line in Coconut source)
                await self._run_parallel(entry, ctx)  #1923 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1924 (line in Coconut source)
            if _coconut_case_match_to_9 == "topological":  #1924 (line in Coconut source)
                _coconut_case_match_check_9 = True  #1924 (line in Coconut source)
            if _coconut_case_match_check_9:  #1924 (line in Coconut source)
                await self._run_topological(entry.node_id, ctx)  #1925 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1926 (line in Coconut source)
            _coconut_case_match_check_9 = True  #1926 (line in Coconut source)
            if _coconut_case_match_check_9:  #1926 (line in Coconut source)
                raise ValueError("Unknown sub-graph strategy: {_coconut_format_0!r}".format(_coconut_format_0=(strategy)))  #1927 (line in Coconut source)


    async def resolve_subgraph_inputs(self, node: GraphNode | str, ctx: ExecutionContext | None=None,) -> dict[str, Any]:  #1929 (line in Coconut source)
        """Dry-run a GraphNode's input wiring without executing anything."""  #1934 (line in Coconut source)
        if isinstance(node, str):  #1935 (line in Coconut source)
            resolved = await self.store.get_node(node)  #1936 (line in Coconut source)
            if resolved is None:  #1937 (line in Coconut source)
                raise ValueError("Node {_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node)))  #1938 (line in Coconut source)
            node = resolved  #1939 (line in Coconut source)
        if not isinstance(node, GraphNode):  #1940 (line in Coconut source)
            raise ValueError("resolve_subgraph_inputs expected GraphNode, got {_coconut_format_0}".format(_coconut_format_0=(type(node).__name__)))  #1941 (line in Coconut source)
        if not node.entry_node_id:  #1944 (line in Coconut source)
            raise ValueError("GraphNode {_coconut_format_0!r} has no entry_node_id.".format(_coconut_format_0=(node.name or node.node_id)))  #1945 (line in Coconut source)
        sub_entry = await self.store.get_node(node.entry_node_id)  #1948 (line in Coconut source)
        if sub_entry is None:  #1949 (line in Coconut source)
            raise ValueError(("GraphNode {_coconut_format_0!r} entry_node_id ".format(_coconut_format_0=(node.name or node.node_id)) + "{_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node.entry_node_id))))  #1950 (line in Coconut source)
        ctx = ctx or ExecutionContext(query="")  #1954 (line in Coconut source)
        return {"entry_node_id": node.entry_node_id, "exit_node_id": node.exit_node_id or node.entry_node_id, "strategy": node.strategy, "scope_outputs": node.scope_outputs, "query": self._resolve_subgraph_query(node, ctx), "state_overlay": self._resolve_subgraph_state(node, ctx)}  #1955 (line in Coconut source)


    def _resolve_subgraph_query(self, node: GraphNode, ctx: ExecutionContext,) -> QueryContent:  #1964 (line in Coconut source)
        """Build the sub-graph's initial query from input_keys."""  #1969 (line in Coconut source)
        if not node.input_keys:  #1970 (line in Coconut source)
            return ctx.query  #1971 (line in Coconut source)
        parts = [_text_of(ctx.outputs[key]) if key in ctx.outputs else _text_of(ctx.state.data[key]) if key in ctx.state.data else None for key in node.input_keys]  #1972 (line in Coconut source)
        return "\n\n".join((p for p in parts if p)) or _query_text(ctx.query)  #1978 (line in Coconut source)


    def _resolve_subgraph_state(self, node: GraphNode, ctx: ExecutionContext,) -> dict[str, Any]:  #1980 (line in Coconut source)
        """Resolve input_map aliases against parent outputs / state."""  #1985 (line in Coconut source)
        if not node.input_map:  #1986 (line in Coconut source)
            return {}  #1987 (line in Coconut source)
        return {alias: ctx.outputs[source] if source in ctx.outputs else ctx.state.data[source] for alias, source in node.input_map.items() if source in ctx.outputs or source in ctx.state.data}  #1988 (line in Coconut source)

# ------------------------------------------------------------------
# Agent execution
# ------------------------------------------------------------------


    async def _execute_agent(self, node: AgentNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #1998 (line in Coconut source)
        if node.pause_before:  #2004 (line in Coconut source)
            await self._pause_execution(ctx, node, reason="pause_before", waiting_for=node.wait_for_input)  #2005 (line in Coconut source)
            return {"text": "", "intent": "default", "status": "paused"}  #2011 (line in Coconut source)
        t0 = time.monotonic()  #2012 (line in Coconut source)
        composed = await self.composer.compose(node, query=_query_text(ctx.query), session_id=ctx.session_id)  #2013 (line in Coconut source)
        system = composed.build_system_prompt()  #2014 (line in Coconut source)
        tool_defs = composed.build_tool_schemas()  #2015 (line in Coconut source)
        if node.state_schema:  #2016 (line in Coconut source)
            ctx.state.schema = node.state_schema  #2017 (line in Coconut source)
        await self._validate_node_schemas(node, ctx=ctx, parent_event_id=parent_event_id)  #2018 (line in Coconut source)

        agent_event_id = str(uuid.uuid4())  #2024 (line in Coconut source)
        self._emit(ctx, "agent_start", node.node_id, node.name or "", payload={"query": ctx.query, "system": system, "model": node.model, "tools": [t.name for t in composed.tools], "context": [c.name for c in composed.context if c.name], "context_scores": [{"name": s.context.name, "score": round(s.score, 4), "source": s.source, "hops": s.hops} for s in composed.context_selection]}, event_id=agent_event_id, parent_event_id=parent_event_id)  #2025 (line in Coconut source)

        if composed.context:  #2047 (line in Coconut source)
            self._emit(ctx, "context_inject", node.node_id, node.name or "", payload={"context_names": [c.name for c in composed.context if c.name], "count": len(composed.context), "selected_contexts": [{"node_id": s.context.node_id, "name": s.context.name, "score": round(s.score, 4), "source": s.source, "hops": s.hops, "token_count": s.token_count, "path": s.path, "reasons": s.reasons} for s in composed.context_selection]}, parent_event_id=agent_event_id)  #2048 (line in Coconut source)

        messages: list[dict[str, Any]] = list(ctx.extra_messages)  #2070 (line in Coconut source)
        if ctx.state.data:  #2071 (line in Coconut source)
            messages.append({"role": "assistant", "content": "Workflow state:\n{_coconut_format_0}".format(_coconut_format_0=(json.dumps(ctx.state.data, sort_keys=True, default=str)))})  #2072 (line in Coconut source)

        image_ctx_blocks = composed.build_image_context_blocks()  #2077 (line in Coconut source)
        if image_ctx_blocks:  #2078 (line in Coconut source)
            user_content: QueryContent = (list(ctx.query) + image_ctx_blocks if isinstance(ctx.query, list) else [{"type": "text", "text": ctx.query},] + image_ctx_blocks)  #2079 (line in Coconut source)
        else:  #2083 (line in Coconut source)
            user_content = ctx.query  #2084 (line in Coconut source)
        messages.append({"role": "user", "content": user_content})  #2085 (line in Coconut source)

        last_response = None  #2087 (line in Coconut source)
        iterations = 0  #2088 (line in Coconut source)

        for _iteration in range(node.max_iterations):  #2090 (line in Coconut source)
            iterations += 1  #2091 (line in Coconut source)
            policy = node.execution_policy  #2092 (line in Coconut source)
            try:  #2093 (line in Coconut source)
                last_response = await self._call_with_retry(lambda _=None: self._chat_once(node, system, messages, tool_defs), ctx, node=node, policy=policy, parent_event_id=agent_event_id)  #2094 (line in Coconut source)
            except Exception:  #2101 (line in Coconut source)
                raise  #2102 (line in Coconut source)

            if last_response.stop_reason == "end_turn":  #2104 (line in Coconut source)
                intent = await self._infer_intent(last_response.text, node)  #2105 (line in Coconut source)
                result = {"text": last_response.text, "intent": intent}  #2106 (line in Coconut source)
                await self._validate_node_schemas(node, output_payload=result, ctx=ctx, parent_event_id=agent_event_id)  #2107 (line in Coconut source)
                if node.pause_after:  #2113 (line in Coconut source)
                    await self._pause_execution(ctx, node, reason="pause_after", waiting_for=node.wait_for_input, metadata={"result": result})  #2114 (line in Coconut source)
                duration_ms = int((time.monotonic() - t0) * 1000)  #2121 (line in Coconut source)
                self._emit(ctx, "agent_end", node.node_id, node.name or "", payload={"text_summary": _summarise(last_response.text), "full_response": last_response.text, "intent": intent, "iterations": iterations}, parent_event_id=agent_event_id, duration_ms=duration_ms)  #2122 (line in Coconut source)
                return result  #2133 (line in Coconut source)

            if last_response.stop_reason == "tool_use":  #2135 (line in Coconut source)
                tool_results = await self._handle_tool_calls(last_response, node, ctx, parent_event_id=agent_event_id)  #2136 (line in Coconut source)
                messages = self._backend.extend_messages(messages, last_response, tool_results)  #2139 (line in Coconut source)
                continue  #2140 (line in Coconut source)

            break  #2142 (line in Coconut source)

        text = last_response.text if last_response else ""  #2144 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2145 (line in Coconut source)
        self._emit(ctx, "agent_end", node.node_id, node.name or "", payload={"text_summary": _summarise(text), "full_response": text, "intent": "default", "iterations": iterations}, parent_event_id=agent_event_id, duration_ms=duration_ms)  #2146 (line in Coconut source)
        result = {"text": text, "intent": "default"}  #2157 (line in Coconut source)
        await self._validate_node_schemas(node, output_payload=result, ctx=ctx, parent_event_id=agent_event_id)  #2158 (line in Coconut source)
        return result  #2164 (line in Coconut source)


    async def _execute_approval(self, node: ApprovalNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #2166 (line in Coconut source)
        payload = ctx.state.data.get(node.input_key, {})  #2172 (line in Coconut source)
        if isinstance(payload, dict) and "approved" in payload:  #2173 (line in Coconut source)
            approved = bool(payload.get("approved"))  #2174 (line in Coconut source)
            assigned_to = payload.get("assigned_to")  #2175 (line in Coconut source)
            task = next((item for item in ctx.state.inbox.values() if item.node_id == node.node_id and item.status == "pending"), None)  #2176 (line in Coconut source)
            if task is not None:  #2180 (line in Coconut source)
                task.status = "approved" if approved else "rejected"  #2181 (line in Coconut source)
                task.assigned_to = assigned_to or task.assigned_to  #2182 (line in Coconut source)
                task.resolved_at = datetime.now(timezone.utc)  #2183 (line in Coconut source)
            return {"approved": approved, "next_node_id": node.approved_target_id if approved else node.rejected_target_id, "assigned_to": assigned_to}  #2184 (line in Coconut source)

        assigned_to = node.assignees[0] if node.assignees and node.require_assignment else None  #2190 (line in Coconut source)
        task = ApprovalTask(task_id=str(uuid.uuid4()), node_id=node.node_id, token=str(uuid.uuid4()), assignees=list(node.assignees), assigned_to=assigned_to, waiting_for=node.instructions or node.name, due_at=(datetime.now(timezone.utc) + timedelta(seconds=node.sla_seconds) if node.sla_seconds else None), escalation_target=node.escalation_target or None, metadata={"assignment_mode": node.assignment_mode, "input_key": node.input_key})  #2191 (line in Coconut source)
        ctx.state.inbox[task.task_id] = task  #2205 (line in Coconut source)
        self._emit(ctx, "approval_task", node.node_id, node.name or "", payload={"task_id": task.task_id, "assignees": task.assignees, "assigned_to": task.assigned_to, "due_at": task.due_at.isoformat() if task.due_at else None, "escalation_target": task.escalation_target}, parent_event_id=parent_event_id)  #2206 (line in Coconut source)
        if task.due_at and task.escalation_target:  #2220 (line in Coconut source)
            self._emit(ctx, "schedule", node.node_id, node.name or "", payload={"task_id": task.task_id, "due_at": task.due_at.isoformat(), "escalation_target": task.escalation_target}, parent_event_id=parent_event_id)  #2221 (line in Coconut source)
        await self._pause_execution(ctx, node, reason="approval_wait", waiting_for=node.instructions or node.name, metadata={"task_id": task.task_id, "token": task.token})  #2233 (line in Coconut source)
        return {"status": "paused", "task_id": task.task_id, "next_node_id": None}  #2240 (line in Coconut source)


    async def _handle_tool_calls(self, response: Any, agent_node: AgentNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> list[ToolResult]:  #2242 (line in Coconut source)
        """Execute all tool calls in the response and return normalised results."""  #2249 (line in Coconut source)
        tool_edges = await self.store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_TOOL)  #2250 (line in Coconut source)
        tool_map: dict[str, ToolNode] = {}  #2251 (line in Coconut source)
        for edge in tool_edges:  #2252 (line in Coconut source)
            tn = await self.store.get_node(edge.dst_id)  #2253 (line in Coconut source)
            if tn and isinstance(tn, ToolNode):  #2254 (line in Coconut source)
                tool_map[tn.name] = tn  #2255 (line in Coconut source)

        results: list[ToolResult] = []  #2257 (line in Coconut source)
        for tc in response.tool_calls:  #2258 (line in Coconut source)
            tool_node = tool_map.get(tc.name)  #2259 (line in Coconut source)
            callable_ref = tool_node.callable_ref if tool_node else ""  #2260 (line in Coconut source)

            call_event = self._emit(ctx, "tool_call", tool_node.node_id if tool_node else agent_node.node_id, tc.name, payload={"tool_name": tc.name, "callable_ref": callable_ref, "input": tc.input}, parent_event_id=parent_event_id)  #2262 (line in Coconut source)

            t0 = time.monotonic()  #2274 (line in Coconut source)
            if tool_node is None:  #2275 (line in Coconut source)
                content = "Tool {_coconut_format_0!r} not found.".format(_coconut_format_0=(tc.name))  #2276 (line in Coconut source)
                success = False  #2277 (line in Coconut source)
            else:  #2278 (line in Coconut source)
                try:  #2279 (line in Coconut source)
                    raw = await self._execute_tool(tool_node, ctx, input_data=tc.input)  #2280 (line in Coconut source)
                    await self._materialise_output(tool_node, raw, ctx)  #2281 (line in Coconut source)
                    content = raw if isinstance(raw, str) else str(raw)  #2282 (line in Coconut source)
                    success = True  #2283 (line in Coconut source)
                except Exception as exc:  #2284 (line in Coconut source)
                    content = "Tool error: {_coconut_format_0}".format(_coconut_format_0=(exc))  #2285 (line in Coconut source)
                    success = False  #2286 (line in Coconut source)

            duration_ms = int((time.monotonic() - t0) * 1000)  #2288 (line in Coconut source)

            self._emit(ctx, "tool_result", tool_node.node_id if tool_node else agent_node.node_id, tc.name, payload={"tool_name": tc.name, "output_summary": _summarise(content), "success": success}, parent_event_id=call_event.event_id, duration_ms=duration_ms)  #2290 (line in Coconut source)

            results.append(ToolResult(tool_call_id=tc.id, content=content))  #2303 (line in Coconut source)

        return results  #2305 (line in Coconut source)

# ------------------------------------------------------------------
# Tool execution
# ------------------------------------------------------------------


    def _callable_injection_kwargs(self, fn: Any, ctx: ExecutionContext) -> dict[str, Any]:  #2311 (line in Coconut source)
        """Extra keyword arguments to pass to a tool/transform callable."""  #2312 (line in Coconut source)
        try:  #2313 (line in Coconut source)
            params = inspect.signature(fn).parameters  #2314 (line in Coconut source)
        except (TypeError, ValueError):  #2315 (line in Coconut source)
            return {}  #2316 (line in Coconut source)
        kwargs: dict[str, Any] = {}  #2317 (line in Coconut source)
        if "session_id" in params:  #2318 (line in Coconut source)
            kwargs["session_id"] = ctx.session_id  #2319 (line in Coconut source)
        if "ctx" in params:  #2320 (line in Coconut source)
            kwargs["ctx"] = ctx  #2321 (line in Coconut source)
        if "store" in params:  #2322 (line in Coconut source)
            kwargs["store"] = self.store  #2323 (line in Coconut source)
        return kwargs  #2324 (line in Coconut source)


    async def _execute_tool(self, node: ToolNode, ctx: ExecutionContext, input_data: dict[str, Any] | None=None,) -> Any:  #2326 (line in Coconut source)
        fn = self._tool_fns.get(node.callable_ref)  #2332 (line in Coconut source)
        if fn is None:  #2333 (line in Coconut source)
            raise RuntimeError(("Tool callable not registered: {_coconut_format_0!r}. ".format(_coconut_format_0=(node.callable_ref)) + "Call executor.register_tool(ref, fn) before running."))  #2334 (line in Coconut source)

        payload = input_data or (list(ctx.outputs.values())[-1] if ctx.outputs else {})  #2339 (line in Coconut source)
        runtime_payload = dict(payload) if isinstance(payload, dict) else {"input": payload}  #2340 (line in Coconut source)
        await self._validate_node_schemas(node, input_payload=payload, ctx=ctx)  #2341 (line in Coconut source)
        idempotency_key = self._idempotency_key(node, payload)  #2342 (line in Coconut source)
        if idempotency_key:  #2343 (line in Coconut source)
            if idempotency_key in ctx.state.idempotency_cache:  #2344 (line in Coconut source)
                return ctx.state.idempotency_cache[idempotency_key]  #2345 (line in Coconut source)

        injected = self._callable_injection_kwargs(fn, ctx)  #2347 (line in Coconut source)

        async def invoke() -> Any:  #2349 (line in Coconut source)
            if node.is_async:  #2350 (line in Coconut source)
                return await fn(runtime_payload, **injected)  #2351 (line in Coconut source)
            return await asyncio.to_thread(fn, runtime_payload, **injected)  #2352 (line in Coconut source)


        result = await self._call_with_retry(invoke, ctx, node=node, policy=node.execution_policy)  #2354 (line in Coconut source)
        await self._validate_node_schemas(node, output_payload=result, ctx=ctx)  #2360 (line in Coconut source)
        if idempotency_key:  #2361 (line in Coconut source)
            ctx.state.idempotency_cache[idempotency_key] = result  #2362 (line in Coconut source)
        return result  #2363 (line in Coconut source)


    async def _execute_transform(self, node: TransformNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #2365 (line in Coconut source)
        fn = self._tool_fns.get(node.callable_ref)  #2371 (line in Coconut source)
        if fn is None:  #2372 (line in Coconut source)
            raise RuntimeError(("Transform callable not registered: {_coconut_format_0!r}. ".format(_coconut_format_0=(node.callable_ref)) + "Call executor.register_tool(ref, fn) before running."))  #2373 (line in Coconut source)

        if node.input_keys:  #2378 (line in Coconut source)
            input_data: dict[str, Any] = {key: ctx.outputs[key] if key in ctx.outputs else ctx.state.data[key] for key in node.input_keys if key in ctx.outputs or key in ctx.state.data}  #2379 (line in Coconut source)
        elif ctx.outputs:  #2384 (line in Coconut source)
            last = list(ctx.outputs.values())[-1]  #2385 (line in Coconut source)
            input_data = dict(last) if isinstance(last, dict) else {"input": last}  #2386 (line in Coconut source)
        else:  #2387 (line in Coconut source)
            input_data = dict(ctx.state.data)  #2388 (line in Coconut source)

        idempotency_key = self._idempotency_key(node, input_data)  #2390 (line in Coconut source)
        if idempotency_key and idempotency_key in ctx.state.idempotency_cache:  #2391 (line in Coconut source)
            return ctx.state.idempotency_cache[idempotency_key]  #2392 (line in Coconut source)

        t0 = time.monotonic()  #2394 (line in Coconut source)
        injected = self._callable_injection_kwargs(fn, ctx)  #2395 (line in Coconut source)

        async def invoke() -> Any:  #2397 (line in Coconut source)
            if node.is_async:  #2398 (line in Coconut source)
                return await fn(input_data, **injected)  #2399 (line in Coconut source)
            return await asyncio.to_thread(fn, input_data, **injected)  #2400 (line in Coconut source)


        result = await self._call_with_retry(invoke, ctx, node=node, policy=node.execution_policy)  #2402 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2403 (line in Coconut source)

        if node.output_key:  #2405 (line in Coconut source)
            ctx.state.data[node.output_key] = result  #2406 (line in Coconut source)

        self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name, "callable_ref": node.callable_ref, "output_summary": _summarise(result), "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #2408 (line in Coconut source)

        if idempotency_key:  #2423 (line in Coconut source)
            ctx.state.idempotency_cache[idempotency_key] = result  #2424 (line in Coconut source)
        return result  #2425 (line in Coconut source)


    async def _execute_reasoner(self, node: ReasonerNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #2427 (line in Coconut source)
        """Run the symbolic Datalog reasoner over facts from state + the KG."""  #2433 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import Program  #2434 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import Rule  #2434 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import fact_to_dict  #2434 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import parse_program  #2434 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import rule_from_obj  #2434 (line in Coconut source)

        rules: list[Rule] = list(parse_program(node.program)) if node.program else []  #2442 (line in Coconut source)
        for raw in node.rules:  #2443 (line in Coconut source)
            rules.extend(rule_from_obj(raw))  #2444 (line in Coconut source)
        program = Program(rules)  #2445 (line in Coconut source)

        facts = await self._gather_reasoner_facts(node, ctx)  #2447 (line in Coconut source)

        t0 = time.monotonic()  #2449 (line in Coconut source)

        @_coconut_tco  #2451 (line in Coconut source)
        def _solve() -> Any:  #2451 (line in Coconut source)
            return _coconut_tail_call(program.solve, facts, with_proof=node.with_proof)  #2452 (line in Coconut source)


        solution = await self._call_with_retry(lambda _=None: asyncio.to_thread(_solve), ctx, node=node, policy=node.execution_policy, parent_event_id=parent_event_id)  #2454 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2461 (line in Coconut source)

        emitted = solution.derived if node.emit_derived_only else solution.facts  #2463 (line in Coconut source)
        if node.query:  #2464 (line in Coconut source)
            wanted = set(node.query)  #2465 (line in Coconut source)
            emitted = {f for f in emitted if f[0] in wanted}  #2466 (line in Coconut source)

        if node.fail_on_empty and not emitted:  #2468 (line in Coconut source)
            raise RuntimeError(("ReasonerNode {_coconut_format_0!r} derived no facts ".format(_coconut_format_0=(node.name or node.node_id)) + "for query {_coconut_format_0}".format(_coconut_format_0=(node.query or '*'))))  #2469 (line in Coconut source)

        result: dict[str, Any] = {"facts": [fact_to_dict(f) for f in sorted(emitted, key=repr)], "fact_count": len(emitted), "input_count": len(facts), "predicates": sorted({f[0] for f in emitted})}  #2474 (line in Coconut source)
        if node.with_proof:  #2480 (line in Coconut source)
            result["proofs"] = [{"fact": fact_to_dict(f), "explanation": solution.explain(f)} for f in sorted(emitted, key=repr) if f in solution.justifications]  #2481 (line in Coconut source)

        if node.output_key:  #2487 (line in Coconut source)
            ctx.state.data[node.output_key] = result  #2488 (line in Coconut source)

        self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name or "reasoner", "node_type": str(node.node_type), "output_summary": _summarise(result), "fact_count": result["fact_count"], "input_count": result["input_count"], "predicates": result["predicates"], "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #2490 (line in Coconut source)
        return result  #2507 (line in Coconut source)


    async def _gather_reasoner_facts(self, node: ReasonerNode, ctx: ExecutionContext,) -> list[Any]:  #2509 (line in Coconut source)
        """Collect ground facts for a reasoner from state and the knowledge graph."""  #2514 (line in Coconut source)
        src = node.fact_source  #2515 (line in Coconut source)
        facts: list[Any] = []  #2516 (line in Coconut source)

        if src.state_keys:  #2518 (line in Coconut source)
            for key in src.state_keys:  #2519 (line in Coconut source)
                val = ctx.state.data.get(key)  #2520 (line in Coconut source)
                if isinstance(val, list):  #2521 (line in Coconut source)
                    facts.extend(val)  #2522 (line in Coconut source)
                elif val is not None:  #2523 (line in Coconut source)
                    facts.append(val)  #2524 (line in Coconut source)
        else:  #2525 (line in Coconut source)
            if ctx.outputs:  #2526 (line in Coconut source)
                last = list(ctx.outputs.values())[-1]  #2527 (line in Coconut source)
                if isinstance(last, list):  #2528 (line in Coconut source)
                    facts.extend(last)  #2529 (line in Coconut source)
                elif isinstance(last, dict) and isinstance(last.get("facts"), list):  #2530 (line in Coconut source)
                    facts.extend(last["facts"])  #2531 (line in Coconut source)
            if isinstance(ctx.state.data.get("facts"), list):  #2532 (line in Coconut source)
                facts.extend(ctx.state.data["facts"])  #2533 (line in Coconut source)

        if src.edge_types:  #2535 (line in Coconut source)
            name_cache: dict[str, str] = {}  #2536 (line in Coconut source)

            async def _label(node_id: str) -> str:  #2538 (line in Coconut source)
                if node_id in name_cache:  #2539 (line in Coconut source)
                    return name_cache[node_id]  #2540 (line in Coconut source)
                if not src.use_node_names:  #2541 (line in Coconut source)
                    name_cache[node_id] = node_id  #2542 (line in Coconut source)
                    return node_id  #2543 (line in Coconut source)
                n = await self.store.get_node(node_id)  #2544 (line in Coconut source)
                label = (n.name if n and n.name else node_id)  #2545 (line in Coconut source)
                name_cache[node_id] = label  #2546 (line in Coconut source)
                return label  #2547 (line in Coconut source)


            for etype in src.edge_types:  #2549 (line in Coconut source)
                try:  #2550 (line in Coconut source)
                    edge_type = EdgeType(etype)  #2551 (line in Coconut source)
                except ValueError:  #2552 (line in Coconut source)
                    edge_type = None  #2553 (line in Coconut source)
                edges = await self.store.list_edges(edge_type=edge_type) if edge_type else []  #2554 (line in Coconut source)
                if edge_type is None:  #2555 (line in Coconut source)
                    edges = [e for e in await self.store.list_edges() if str(e.edge_type) == etype]  #2556 (line in Coconut source)
                pred = etype.lower()  #2557 (line in Coconut source)
                for e in edges:  #2558 (line in Coconut source)
                    facts.append((pred, await _label(e.src_id), await _label(e.dst_id)))  #2559 (line in Coconut source)

        if src.include_node_facts:  #2561 (line in Coconut source)
            for n in await self.store.list_nodes():  #2562 (line in Coconut source)
                label = n.name if (src.use_node_names and n.name) else n.node_id  #2563 (line in Coconut source)
                facts.append((str(n.node_type), label))  #2564 (line in Coconut source)

        return facts  #2566 (line in Coconut source)


    async def _chat_once(self, node: AgentNode, system: str, messages: list[dict[str, Any]], tool_defs: list[dict[str, Any]],) -> Any:  #2568 (line in Coconut source)
        return await self._backend.chat(model=node.model, system=system, messages=messages, tools=tool_defs)  #2575 (line in Coconut source)


    async def _call_with_retry(self, fn: Callable[[], Any], ctx: ExecutionContext, *, node: AnyNode, policy: ExecutionPolicy, parent_event_id: str | None=None,) -> Any:  #2582 (line in Coconut source)
        attempts = max(1, policy.retry_policy.max_attempts)  #2591 (line in Coconut source)
        delay = max(0.0, policy.retry_policy.backoff_seconds)  #2592 (line in Coconut source)
        last_exc: Exception | None = None  #2593 (line in Coconut source)
        for attempt in range(1, attempts + 1):  #2594 (line in Coconut source)
            try:  #2595 (line in Coconut source)
                if policy.timeout_seconds:  #2596 (line in Coconut source)
                    return await asyncio.wait_for(fn(), timeout=policy.timeout_seconds)  #2597 (line in Coconut source)
                return await fn()  #2598 (line in Coconut source)
            except Exception as exc:  #2599 (line in Coconut source)
                last_exc = exc  #2600 (line in Coconut source)
                if attempt >= attempts:  #2601 (line in Coconut source)
                    break  #2602 (line in Coconut source)
                self._emit(ctx, "retry", node.node_id, node.name or "", payload={"attempt": attempt, "max_attempts": attempts, "error": str(exc)}, parent_event_id=parent_event_id)  #2603 (line in Coconut source)
                if delay > 0:  #2611 (line in Coconut source)
                    await asyncio.sleep(delay)  #2612 (line in Coconut source)
                    delay *= max(policy.retry_policy.backoff_multiplier, 1.0)  #2613 (line in Coconut source)
        assert last_exc is not None  #2614 (line in Coconut source)
        raise last_exc  #2615 (line in Coconut source)


    @_coconut_tco  #2617 (line in Coconut source)
    def _idempotency_key(self, node: ToolNode, payload: Any) -> str:  #2617 (line in Coconut source)
        template = node.execution_policy.idempotency_key  #2618 (line in Coconut source)
        if template == "":  #2619 (line in Coconut source)
            return ""  #2620 (line in Coconut source)
        if template == "auto":  #2621 (line in Coconut source)
            return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(json.dumps(payload, sort_keys=True, default=str)))  #2622 (line in Coconut source)
        if isinstance(payload, dict) and template in payload:  #2623 (line in Coconut source)
            return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(payload[template]))  #2624 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(template))  #2625 (line in Coconut source)

# ------------------------------------------------------------------
# Output materialisation
# ------------------------------------------------------------------


    async def _materialise_output(self, source_node: AnyNode, output: Any, ctx: ExecutionContext,) -> ContextNode:  #2631 (line in Coconut source)
        """Write execution output back into the graph as a ContextNode."""  #2637 (line in Coconut source)
        from yggdrasil_lm.core.nodes import ContextNode  #2638 (line in Coconut source)
        from yggdrasil_lm.core.edges import Edge  #2639 (line in Coconut source)

        content = output if isinstance(output, str) else str(output)  #2641 (line in Coconut source)
        ctx_node = ContextNode(name="Output of {_coconut_format_0}".format(_coconut_format_0=(source_node.name)), description="Auto-materialised output from {_coconut_format_0} node".format(_coconut_format_0=(source_node.node_type)), content=content, source="node:{_coconut_format_0}".format(_coconut_format_0=(source_node.node_id)), group_id=ctx.session_id, attributes={"origin": "runtime", "session_id": ctx.session_id, "source_node_id": source_node.node_id})  #2642 (line in Coconut source)
        await self.store.upsert_node(ctx_node)  #2654 (line in Coconut source)
        await self.store.upsert_edge(Edge.produces(src_id=source_node.node_id, dst_id=ctx_node.node_id))  #2655 (line in Coconut source)
        ctx.outputs[ctx_node.node_id] = content  #2658 (line in Coconut source)
        return ctx_node  #2659 (line in Coconut source)

# ------------------------------------------------------------------
# Routing
# ------------------------------------------------------------------


    async def _route(self, node: AgentNode, result: dict[str, Any], ctx: ExecutionContext, parent_event_id: str | None=None,) -> str | None:  #2665 (line in Coconut source)
        if node.decision_table is not None:  #2672 (line in Coconut source)
            decision = self._evaluate_decision_table(node.decision_table, state=ctx.state, result=result)  #2673 (line in Coconut source)
            if decision is not None:  #2674 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": decision.name or "decision_table", "next_node_id": None if decision.target_node_id == "__END__" else decision.target_node_id, "confidence": 1.0, "mode": "decision_table"}, parent_event_id=parent_event_id)  #2675 (line in Coconut source)
                return decision.target_node_id  #2688 (line in Coconut source)
            if node.decision_table.strict:  #2689 (line in Coconut source)
                target = node.decision_table.default_target_id  #2690 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": node.decision_table.default_intent, "next_node_id": None if target == "__END__" else target, "confidence": 1.0, "mode": "decision_table"}, parent_event_id=parent_event_id)  #2691 (line in Coconut source)
                return target  #2704 (line in Coconut source)
        for rule in sorted(node.route_rules, key=lambda r: r.priority, reverse=True):  #2705 (line in Coconut source)
            if self._evaluate_route_rule(rule, result=result, state=ctx.state):  #2706 (line in Coconut source)
                if rule.pause_on_match:  #2707 (line in Coconut source)
                    await self._pause_execution(ctx, node, reason=rule.name or "route_rule_pause", waiting_for=node.wait_for_input, metadata={"rule": rule.name, "target": rule.target_node_id})  #2708 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": rule.name or "route_rule", "next_node_id": None if rule.target_node_id == "__END__" else rule.target_node_id, "confidence": 1.0, "mode": "deterministic"}, parent_event_id=parent_event_id)  #2715 (line in Coconut source)
                return rule.target_node_id  #2728 (line in Coconut source)
        intent = result.get("intent", "default")  #2729 (line in Coconut source)
        next_id = node.routing_table.get(intent) or node.routing_table.get("default", "__END__")  #2730 (line in Coconut source)

        self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": intent, "next_node_id": next_id if next_id != "__END__" else None, "confidence": None, "mode": "llm"}, parent_event_id=parent_event_id)  #2732 (line in Coconut source)

        return next_id  #2741 (line in Coconut source)


    async def _infer_intent(self, text: str, node: AgentNode) -> str:  #2743 (line in Coconut source)
        """Classify routing intent from agent output text."""  #2744 (line in Coconut source)
        if not node.routing_table:  #2745 (line in Coconut source)
            return "default"  #2746 (line in Coconut source)
        intents = [intent for intent in node.routing_table if intent != "default"]  #2747 (line in Coconut source)
        if not intents:  #2748 (line in Coconut source)
            return "default"  #2749 (line in Coconut source)

        keyword_intent = self._infer_intent_keywords(text, node)  #2751 (line in Coconut source)
        if keyword_intent != "default":  #2752 (line in Coconut source)
            return keyword_intent  #2753 (line in Coconut source)

        if self._backend is None:  #2755 (line in Coconut source)
            return "default"  #2756 (line in Coconut source)

        prompt = _INTENT_TEMPLATE.format(intents="\n".join(("- {_coconut_format_0}".format(_coconut_format_0=(intent)) for intent in intents)), text=text[:2000])  #2758 (line in Coconut source)
        try:  #2762 (line in Coconut source)
            response = await self._backend.chat(model=self._router_model, system=_ROUTER_SYSTEM, messages=[{"role": "user", "content": prompt},], tools=[])  #2763 (line in Coconut source)
            data = json.loads(response.text.strip())  #2769 (line in Coconut source)
            return str(data.get("intent", "default"))  #2770 (line in Coconut source)
        except Exception:  #2771 (line in Coconut source)
            return "default"  #2772 (line in Coconut source)


    def _infer_intent_keywords(self, text: str, node: AgentNode) -> str:  #2774 (line in Coconut source)
        """Keyword-based intent fallback (no LLM call)."""  #2775 (line in Coconut source)
        text_lower = text.lower()  #2776 (line in Coconut source)
        for intent in node.routing_table:  #2777 (line in Coconut source)
            if intent != "default" and intent.lower() in text_lower:  #2778 (line in Coconut source)
                return intent  #2779 (line in Coconut source)
        return "default"  #2780 (line in Coconut source)

# ------------------------------------------------------------------
# White-box routing: plan + execute (two-phase dispatch)
# ------------------------------------------------------------------


    async def route(self, query: str, candidates: list[AgentNode] | None=None,) -> RoutingDecision:  #2786 (line in Coconut source)
        """LLM-based router: pick the best AgentNode for *query*."""  #2791 (line in Coconut source)
        if candidates is None:  #2792 (line in Coconut source)
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)  #2793 (line in Coconut source)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]  #2794 (line in Coconut source)

        if not candidates:  #2796 (line in Coconut source)
            raise ValueError("No valid AgentNode candidates found in the store.")  #2797 (line in Coconut source)

        if len(candidates) == 1:  #2799 (line in Coconut source)
            return RoutingDecision(candidates[0].node_id, "Only one agent available.", 1.0)  #2800 (line in Coconut source)

        agent_list = "\n".join(("- {_coconut_format_0}: {_coconut_format_1}".format(_coconut_format_0=(n.node_id), _coconut_format_1=(n.description)) for n in candidates))  #2802 (line in Coconut source)
        prompt = _ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)  #2803 (line in Coconut source)

        try:  #2805 (line in Coconut source)
            response = await self._backend.chat(model=self._router_model, system=_ROUTER_SYSTEM, messages=[{"role": "user", "content": prompt},], tools=[])  #2806 (line in Coconut source)
            data = json.loads(response.text.strip())  #2812 (line in Coconut source)
            return RoutingDecision(str(data["agent"]), str(data.get("reason", "")), float(data.get("confidence", 0.5)))  #2813 (line in Coconut source)
        except Exception:  #2818 (line in Coconut source)
            return RoutingDecision(candidates[0].node_id, "Fallback: router response could not be parsed.", 0.5)  #2819 (line in Coconut source)


    async def plan(self, query: str) -> RoutingDecision:  #2825 (line in Coconut source)
        """Deprecated alias for route()."""  #2826 (line in Coconut source)
        import warnings  #2827 (line in Coconut source)
        warnings.warn('GraphExecutor.plan() is deprecated and will be removed in a future release. Use GraphExecutor.route() instead.', DeprecationWarning, stacklevel=2)  #2828 (line in Coconut source)
        return await self.route(query)  #2834 (line in Coconut source)


    async def execute(self, agent_id: str, query: QueryContent, routing: RoutingDecision | None=None,) -> AgentResult:  #2836 (line in Coconut source)
        """Phase 2 of two-phase dispatch: run *agent_id* and return a structured envelope."""  #2842 (line in Coconut source)
        node = await self.store.get_node(agent_id)  #2843 (line in Coconut source)
        if node is None or not isinstance(node, AgentNode):  #2844 (line in Coconut source)
            raise ValueError("Agent node not found or not an AgentNode: {_coconut_format_0!r}".format(_coconut_format_0=(agent_id)))  #2845 (line in Coconut source)

        composed = await self.composer.compose(node, query=_query_text(query))  #2847 (line in Coconut source)
        context_names = [c.name for c in composed.context if c.name]  #2848 (line in Coconut source)

        ctx = ExecutionContext(query=query)  #2850 (line in Coconut source)
        raw = await self._execute_agent(node, ctx)  #2851 (line in Coconut source)
        text = raw.get("text", "") if isinstance(raw, dict) else str(raw)  #2852 (line in Coconut source)

        decision = routing or RoutingDecision(agent_id, "Direct execution (no routing phase).", 1.0)  #2854 (line in Coconut source)

        return AgentResult(routed_to=agent_id, reason=decision.reason, confidence=decision.confidence, context_injected=context_names, result=text, low_confidence_warning=decision.low_confidence_warning)  #2856 (line in Coconut source)


# ---------------------------------------------------------------------------
# print_trace() — render a session trace as a human-readable execution tree
# ---------------------------------------------------------------------------


def print_trace(ctx: ExecutionContext | list[TraceEvent], *, width: int=72) -> None:  #2870 (line in Coconut source)
    """Print the execution trace as a human-readable tree."""  #2871 (line in Coconut source)
    _coconut_case_match_to_10 = ctx  #2872 (line in Coconut source)
    _coconut_case_match_check_10 = False  #2872 (line in Coconut source)
    _coconut_match_temp_41 = _coconut.getattr(ExecutionContext, "_coconut_is_data", False) or _coconut.isinstance(ExecutionContext, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ExecutionContext)  # type: ignore  #2872 (line in Coconut source)
    _coconut_case_match_check_10 = True  #2872 (line in Coconut source)
    if _coconut_case_match_check_10:  #2872 (line in Coconut source)
        _coconut_case_match_check_10 = False  #2872 (line in Coconut source)
        if not _coconut_case_match_check_10:  #2872 (line in Coconut source)
            if (_coconut_match_temp_41) and (_coconut.isinstance(_coconut_case_match_to_10, ExecutionContext)):  #2872 (line in Coconut source)
                _coconut_match_temp_42 = _coconut.len(_coconut_case_match_to_10) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_10.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_10, "_coconut_data_defaults", {}) and _coconut_case_match_to_10[i] == _coconut.getattr(_coconut_case_match_to_10, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_10.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_10, "__match_args__") else _coconut.len(_coconut_case_match_to_10) == 0  # type: ignore  #2872 (line in Coconut source)
                if _coconut_match_temp_42:  #2872 (line in Coconut source)
                    _coconut_case_match_check_10 = True  #2872 (line in Coconut source)

        if not _coconut_case_match_check_10:  #2872 (line in Coconut source)
            if (not _coconut_match_temp_41) and (_coconut.isinstance(_coconut_case_match_to_10, ExecutionContext)):  #2872 (line in Coconut source)
                _coconut_case_match_check_10 = True  #2872 (line in Coconut source)
            if _coconut_case_match_check_10:  #2872 (line in Coconut source)
                _coconut_case_match_check_10 = False  #2872 (line in Coconut source)
                if not _coconut_case_match_check_10:  #2872 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_10) in _coconut_self_match_types:  #2872 (line in Coconut source)
                        _coconut_case_match_check_10 = True  #2872 (line in Coconut source)

                if not _coconut_case_match_check_10:  #2872 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_10) in _coconut_self_match_types:  #2872 (line in Coconut source)
                        _coconut_match_temp_43 = _coconut.getattr(ExecutionContext, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #2872 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_43, _coconut.tuple):  #2872 (line in Coconut source)
                            raise _coconut.TypeError("ExecutionContext.__match_args__ must be a tuple")  #2872 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_43) < 0:  #2872 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ExecutionContext' only supports %s)" % (_coconut.len(_coconut_match_temp_43),))  #2872 (line in Coconut source)
                        _coconut_case_match_check_10 = True  #2872 (line in Coconut source)




    if _coconut_case_match_check_10:  #2872 (line in Coconut source)
        events = ctx.trace  #2874 (line in Coconut source)
        session_id = ctx.session_id[:8]  #2875 (line in Coconut source)
        query = _query_text(ctx.query)  #2876 (line in Coconut source)
    if not _coconut_case_match_check_10:  #2877 (line in Coconut source)
        _coconut_case_match_check_10 = True  #2877 (line in Coconut source)
        if _coconut_case_match_check_10:  #2877 (line in Coconut source)
            events = ctx  #2878 (line in Coconut source)
            session_id = events[0].session_id[:8] if events else "?"  #2879 (line in Coconut source)
            query = ""  #2880 (line in Coconut source)

    sep = "═" * width  #2882 (line in Coconut source)
    print("\nSession {_coconut_format_0}  {_coconut_format_1!r}".format(_coconut_format_0=(session_id), _coconut_format_1=(query)))  #2883 (line in Coconut source)
    print(sep)  #2884 (line in Coconut source)

    by_id: dict[str, TraceEvent] = {e.event_id: e for e in events}  #2886 (line in Coconut source)
    children: dict[str | None, list[TraceEvent]] = {}  #2887 (line in Coconut source)
    for e in events:  #2888 (line in Coconut source)
        children.setdefault(e.parent_event_id, []).append(e)  #2889 (line in Coconut source)

    def _fmt_ms(ms: int | None) -> str:  #2891 (line in Coconut source)
        return "[{_coconut_format_0}ms]".format(_coconut_format_0=(ms)) if ms is not None else ""  #2892 (line in Coconut source)


    def _render(event: TraceEvent, indent: int) -> None:  #2894 (line in Coconut source)
        pad = "  " * indent  #2895 (line in Coconut source)
        t = event.event_type  #2896 (line in Coconut source)
        p = event.payload  #2897 (line in Coconut source)
        ms = _fmt_ms(event.duration_ms)  #2898 (line in Coconut source)

        _coconut_case_match_to_11 = t  #2900 (line in Coconut source)
        _coconut_case_match_check_11 = False  #2900 (line in Coconut source)
        if _coconut_case_match_to_11 == "hop":  #2900 (line in Coconut source)
            _coconut_case_match_check_11 = True  #2900 (line in Coconut source)
        if _coconut_case_match_check_11:  #2900 (line in Coconut source)
            node_type = p.get("node_type", "").split(".")[-1].upper()  #2902 (line in Coconut source)
            hop_num = p.get("hop", "")  #2903 (line in Coconut source)
            hop_label = "hop {_coconut_format_0}  ".format(_coconut_format_0=(hop_num)) if hop_num else ""  #2904 (line in Coconut source)
            print("{_coconut_format_0}{_coconut_format_1}{_coconut_format_2}  {_coconut_format_3}".format(_coconut_format_0=(pad), _coconut_format_1=(hop_label), _coconut_format_2=(node_type), _coconut_format_3=(event.node_name)))  #2905 (line in Coconut source)
            for child in children.get(event.event_id, []):  #2906 (line in Coconut source)
                _render(child, indent + 1)  #2907 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2909 (line in Coconut source)
            if _coconut_case_match_to_11 == "agent_start":  #2909 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2909 (line in Coconut source)
            if _coconut_case_match_check_11:  #2909 (line in Coconut source)
                tools = ", ".join(p.get("tools", [])) or "none"  #2910 (line in Coconut source)
                ctx_l = p.get("context", [])  #2911 (line in Coconut source)
                ctx_s = "  context: {_coconut_format_0}".format(_coconut_format_0=(', '.join(ctx_l))) if ctx_l else ""  #2912 (line in Coconut source)
                print("{_coconut_format_0}tools: {_coconut_format_1}{_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(tools), _coconut_format_2=(ctx_s)))  #2913 (line in Coconut source)
                if p.get("context_scores"):  #2914 (line in Coconut source)
                    ranked = ["{_coconut_format_0}[{_coconut_format_1}, {_coconut_format_2}, hops={_coconut_format_3}]".format(_coconut_format_0=(item.get('name')), _coconut_format_1=(item.get('score')), _coconut_format_2=(item.get('source')), _coconut_format_3=(item.get('hops'))) for item in p["context_scores"]]  #2915 (line in Coconut source)
                    print("{_coconut_format_0}ranked_context: {_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(' | '.join(ranked))))  #2919 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2920 (line in Coconut source)
                    _render(child, indent)  #2921 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2923 (line in Coconut source)
            if _coconut_case_match_to_11 == "context_inject":  #2923 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2923 (line in Coconut source)
            if _coconut_case_match_check_11:  #2923 (line in Coconut source)
                names = ", ".join(p.get("context_names", [])) or "—"  #2924 (line in Coconut source)
                count = p.get("count", 0)  #2925 (line in Coconut source)
                print("{_coconut_format_0}context_inject  {_coconut_format_1}  ({_coconut_format_2} nodes)".format(_coconut_format_0=(pad), _coconut_format_1=(names), _coconut_format_2=(count)))  #2926 (line in Coconut source)
                for item in p.get("selected_contexts", []):  #2927 (line in Coconut source)
                    reasons = ", ".join(item.get("reasons", []))  #2928 (line in Coconut source)
                    print(("{_coconut_format_0}  selected  {_coconut_format_1}  score={_coconut_format_2}  ".format(_coconut_format_0=(pad), _coconut_format_1=(item.get('name')), _coconut_format_2=(item.get('score'))) + "source={_coconut_format_0}  hops={_coconut_format_1}  ".format(_coconut_format_0=(item.get('source')), _coconut_format_1=(item.get('hops'))) + "tokens={_coconut_format_0}".format(_coconut_format_0=(item.get('token_count')))))  #2929 (line in Coconut source)
                    if reasons:  #2934 (line in Coconut source)
                        print("{_coconut_format_0}    reasons  {_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(reasons)))  #2935 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2937 (line in Coconut source)
            if _coconut_case_match_to_11 == "agent_end":  #2937 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2937 (line in Coconut source)
            if _coconut_case_match_check_11:  #2937 (line in Coconut source)
                summary = p.get("text_summary", "")  #2938 (line in Coconut source)
                intent = p.get("intent", "default")  #2939 (line in Coconut source)
                iters = p.get("iterations", 1)  #2940 (line in Coconut source)
                iter_s = "  iters={_coconut_format_0}".format(_coconut_format_0=(iters)) if iters > 1 else ""  #2941 (line in Coconut source)
                print("{_coconut_format_0}agent_end  {_coconut_format_1!r}  intent={_coconut_format_2}{_coconut_format_3}  {_coconut_format_4}".format(_coconut_format_0=(pad), _coconut_format_1=(summary), _coconut_format_2=(intent), _coconut_format_3=(iter_s), _coconut_format_4=(ms)))  #2942 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2944 (line in Coconut source)
            if _coconut_case_match_to_11 == "tool_call":  #2944 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2944 (line in Coconut source)
            if _coconut_case_match_check_11:  #2944 (line in Coconut source)
                inp = json.dumps(p.get("input", {}), ensure_ascii=False)  #2945 (line in Coconut source)
                inp = inp[:60] + "…" if len(inp) > 60 else inp  #2946 (line in Coconut source)
                print("{_coconut_format_0}tool_call  {_coconut_format_1}  {_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(inp)))  #2947 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2948 (line in Coconut source)
                    _render(child, indent + 1)  #2949 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2951 (line in Coconut source)
            if _coconut_case_match_to_11 == "tool_result":  #2951 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2951 (line in Coconut source)
            if _coconut_case_match_check_11:  #2951 (line in Coconut source)
                status = "ok" if p.get("success") else "err"  #2952 (line in Coconut source)
                summary = p.get("output_summary", "")  #2953 (line in Coconut source)
                print("{_coconut_format_0}tool_result  {_coconut_format_1}  {_coconut_format_2}  {_coconut_format_3!r}  {_coconut_format_4}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(status), _coconut_format_3=(summary), _coconut_format_4=(ms)))  #2954 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2956 (line in Coconut source)
            if _coconut_case_match_to_11 == "routing":  #2956 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2956 (line in Coconut source)
            if _coconut_case_match_check_11:  #2956 (line in Coconut source)
                intent = p.get("intent", "default")  #2957 (line in Coconut source)
                next_id = p.get("next_node_id") or "__END__"  #2958 (line in Coconut source)
                conf = p.get("confidence")  #2959 (line in Coconut source)
                conf_s = "  conf={_coconut_format_0:.0%}".format(_coconut_format_0=(conf)) if conf is not None else ""  #2960 (line in Coconut source)
                print("{_coconut_format_0}routing  {_coconut_format_1} → {_coconut_format_2}{_coconut_format_3}".format(_coconut_format_0=(pad), _coconut_format_1=(intent), _coconut_format_2=(next_id), _coconut_format_3=(conf_s)))  #2961 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2963 (line in Coconut source)
            if _coconut_case_match_to_11 == "subgraph_enter":  #2963 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2963 (line in Coconut source)
            if _coconut_case_match_check_11:  #2963 (line in Coconut source)
                print("{_coconut_format_0}subgraph_enter  {_coconut_format_1}  entry={_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(p.get('entry_node_id', ''))))  #2964 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2965 (line in Coconut source)
                    _render(child, indent + 1)  #2966 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2968 (line in Coconut source)
            if _coconut_case_match_to_11 == "subgraph_exit":  #2968 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2968 (line in Coconut source)
            if _coconut_case_match_check_11:  #2968 (line in Coconut source)
                print("{_coconut_format_0}subgraph_exit   {_coconut_format_1}  {_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(ms)))  #2969 (line in Coconut source)


    total_ms = 0  #2971 (line in Coconut source)
    hops = 0  #2972 (line in Coconut source)
    ends = 0  #2973 (line in Coconut source)
    for event in children.get(None, []):  #2974 (line in Coconut source)
        _render(event, indent=0)  #2975 (line in Coconut source)
        if event.event_type == "hop":  #2976 (line in Coconut source)
            hops += 1  #2977 (line in Coconut source)

    for event in events:  #2979 (line in Coconut source)
        if event.event_type == "agent_end":  #2980 (line in Coconut source)
            ends += 1  #2981 (line in Coconut source)
            if event.duration_ms:  #2982 (line in Coconut source)
                total_ms += event.duration_ms  #2983 (line in Coconut source)

    print(sep)  #2985 (line in Coconut source)
    ms_s = " · {_coconut_format_0}ms".format(_coconut_format_0=(total_ms)) if total_ms else ""  #2986 (line in Coconut source)
    print("Total: {_coconut_format_0} hops · {_coconut_format_1} agent_end events{_coconut_format_2}\n".format(_coconut_format_0=(hops), _coconut_format_1=(ends), _coconut_format_2=(ms_s)))  #2987 (line in Coconut source)


# ---------------------------------------------------------------------------
# Runtime node utilities
# ---------------------------------------------------------------------------


async def get_runtime_nodes(store: GraphStore, session_id: str | None=None, only_valid: bool=True,) -> list[ContextNode]:  #2994 (line in Coconut source)
    """Return runtime-materialised ContextNodes without graph traversal."""  #2999 (line in Coconut source)
    candidates = await store.list_nodes(node_type=NodeType.CONTEXT, group_id=session_id, only_valid=only_valid)  #3000 (line in Coconut source)
    return [n for n in candidates if isinstance(n, ContextNode) and n.attributes.get("origin") == "runtime"]  #3005 (line in Coconut source)



async def cleanup_session(store: GraphStore, session_id: str, hard: bool=False,) -> int:  #3011 (line in Coconut source)
    """Expire (or hard-delete) all runtime nodes from *session_id*."""  #3016 (line in Coconut source)
    nodes = await store.list_nodes(group_id=session_id, only_valid=False)  #3017 (line in Coconut source)
    count = 0  #3018 (line in Coconut source)
    for node in nodes:  #3019 (line in Coconut source)
        in_edges = await store.get_edges(node.node_id, edge_type=EdgeType.PRODUCES, direction="in", only_valid=False)  #3020 (line in Coconut source)
        for edge in in_edges:  #3023 (line in Coconut source)
            if hard:  #3024 (line in Coconut source)
                await store.delete_edge(edge.edge_id)  #3025 (line in Coconut source)
            else:  #3026 (line in Coconut source)
                await store.expire_edge(edge.edge_id)  #3027 (line in Coconut source)

        if hard:  #3029 (line in Coconut source)
            await store.delete_node(node.node_id)  #3030 (line in Coconut source)
        else:  #3031 (line in Coconut source)
            await store.expire_node(node.node_id)  #3032 (line in Coconut source)
        count += 1  #3033 (line in Coconut source)

    return count  #3035 (line in Coconut source)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _summarise(value: Any, max_len: int=200) -> str:  #3042 (line in Coconut source)
    s = value if isinstance(value, str) else str(value)  #3043 (line in Coconut source)
    return s[:max_len] + "…" if len(s) > max_len else s  #3044 (line in Coconut source)



@_coconut_tco  #3047 (line in Coconut source)
def _text_of(value: Any) -> str:  #3047 (line in Coconut source)
    """Best-effort extraction of a string payload from a node output."""  #3048 (line in Coconut source)
    _coconut_case_match_to_12 = value  #3049 (line in Coconut source)
    _coconut_case_match_check_12 = False  #3049 (line in Coconut source)
    if _coconut_case_match_to_12 is None:  #3049 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3049 (line in Coconut source)
    if _coconut_case_match_check_12:  #3049 (line in Coconut source)
        return ""  #3051 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3052 (line in Coconut source)
        _coconut_match_temp_44 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #3052 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3052 (line in Coconut source)
        if _coconut_case_match_check_12:  #3052 (line in Coconut source)
            _coconut_case_match_check_12 = False  #3052 (line in Coconut source)
            if not _coconut_case_match_check_12:  #3052 (line in Coconut source)
                if (_coconut_match_temp_44) and (_coconut.isinstance(_coconut_case_match_to_12, str)):  #3052 (line in Coconut source)
                    _coconut_match_temp_45 = _coconut.len(_coconut_case_match_to_12) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_12.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_12, "_coconut_data_defaults", {}) and _coconut_case_match_to_12[i] == _coconut.getattr(_coconut_case_match_to_12, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_12.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_12, "__match_args__") else _coconut.len(_coconut_case_match_to_12) == 0  # type: ignore  #3052 (line in Coconut source)
                    if _coconut_match_temp_45:  #3052 (line in Coconut source)
                        _coconut_case_match_check_12 = True  #3052 (line in Coconut source)

            if not _coconut_case_match_check_12:  #3052 (line in Coconut source)
                if (not _coconut_match_temp_44) and (_coconut.isinstance(_coconut_case_match_to_12, str)):  #3052 (line in Coconut source)
                    _coconut_case_match_check_12 = True  #3052 (line in Coconut source)
                if _coconut_case_match_check_12:  #3052 (line in Coconut source)
                    _coconut_case_match_check_12 = False  #3052 (line in Coconut source)
                    if not _coconut_case_match_check_12:  #3052 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_12) in _coconut_self_match_types:  #3052 (line in Coconut source)
                            _coconut_case_match_check_12 = True  #3052 (line in Coconut source)

                    if not _coconut_case_match_check_12:  #3052 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_12) in _coconut_self_match_types:  #3052 (line in Coconut source)
                            _coconut_match_temp_46 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #3052 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_46, _coconut.tuple):  #3052 (line in Coconut source)
                                raise _coconut.TypeError("str.__match_args__ must be a tuple")  #3052 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_46) < 0:  #3052 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_46),))  #3052 (line in Coconut source)
                            _coconut_case_match_check_12 = True  #3052 (line in Coconut source)




        if _coconut_case_match_check_12:  #3052 (line in Coconut source)
            return value  #3053 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3054 (line in Coconut source)
        if _coconut.isinstance(_coconut_case_match_to_12, _coconut.abc.Mapping):  #3054 (line in Coconut source)
            _coconut_case_match_check_12 = True  #3054 (line in Coconut source)
        if _coconut_case_match_check_12:  #3054 (line in Coconut source)
            for key in ("text", "output", "result", "content"):  #3055 (line in Coconut source)
                v = value.get(key)  #3056 (line in Coconut source)
                if isinstance(v, str):  #3057 (line in Coconut source)
                    return v  #3058 (line in Coconut source)
            return _coconut_tail_call(str, value)  #3059 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3060 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3060 (line in Coconut source)
        if _coconut_case_match_check_12:  #3060 (line in Coconut source)
            return _coconut_tail_call(str, value)  #3061 (line in Coconut source)
