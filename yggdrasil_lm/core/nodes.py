#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x3175f19d

# Compiled with Coconut version 3.2.0

"""Node types for the yggdrasil system.

Every node in the graph is a typed, temporally-valid, embeddable object.
Node type determines execution behavior in the GraphExecutor.
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
from pydantic import model_validator  #12 (line in Coconut source)


@_coconut_tco  #15 (line in Coconut source)
def _now() -> datetime:  #15 (line in Coconut source)
    return _coconut_tail_call(datetime.now, timezone.utc)  #16 (line in Coconut source)



@_coconut_tco  #19 (line in Coconut source)
def _uuid() -> str:  #19 (line in Coconut source)
    return _coconut_tail_call(str, uuid.uuid4())  #20 (line in Coconut source)


# ---------------------------------------------------------------------------
# Node type enum
# ---------------------------------------------------------------------------


class NodeType(StrEnum):  #27 (line in Coconut source)
    AGENT = "agent"  # executable — has LLM model + routing table  #28 (line in Coconut source)
    TOOL = "tool"  # callable — has JSON Schema for input/output  #29 (line in Coconut source)
    CONTEXT = "context"  # passive knowledge/memory chunk (bi-temporal)  #30 (line in Coconut source)
    PROMPT = "prompt"  # reusable Jinja2 prompt template  #31 (line in Coconut source)
    SCHEMA = "schema"  # JSON Schema contract  #32 (line in Coconut source)
    GRAPH = "graph"  # pointer to a sub-graph (meta-graph pattern)  #33 (line in Coconut source)
    APPROVAL = "approval"  # dedicated human approval / inbox step  #34 (line in Coconut source)
    TRANSFORM = "transform"  # pure-Python data reshaping step (no LLM)  #35 (line in Coconut source)
    REASONER = "reasoner"  # symbolic inference step (Datalog) — no LLM  #36 (line in Coconut source)


class ConstraintRule(BaseModel):  #39 (line in Coconut source)
    """Declarative constraint evaluated against runtime payloads."""  #40 (line in Coconut source)

    name: str = ""  #42 (line in Coconut source)
    source: str = "state"  # state | result | input | output  #43 (line in Coconut source)
    path: str = ""  #44 (line in Coconut source)
    operator: str = "equals"  # equals | not_equals | contains | exists | truthy | in | regex | gt | gte | lt | lte  #45 (line in Coconut source)
    value: Any = None  #46 (line in Coconut source)
    compare_to_source: str | None = None  #47 (line in Coconut source)
    compare_to_path: str = ""  #48 (line in Coconut source)
    message: str = ""  #49 (line in Coconut source)
    severity: str = "error"  #50 (line in Coconut source)


class DecisionRule(BaseModel):  #53 (line in Coconut source)
    """Decision-table row for deterministic routing."""  #54 (line in Coconut source)

    name: str = ""  #56 (line in Coconut source)
    conditions: list[ConstraintRule] = Field(default_factory=list)  #57 (line in Coconut source)
    target_node_id: str = "__END__"  #58 (line in Coconut source)
    priority: int = 0  #59 (line in Coconut source)
    metadata: dict[str, Any] = Field(default_factory=dict)  #60 (line in Coconut source)


class DecisionTable(BaseModel):  #63 (line in Coconut source)
    """Simple decision table evaluated before route_rules."""  #64 (line in Coconut source)

    name: str = ""  #66 (line in Coconut source)
    rules: list[DecisionRule] = Field(default_factory=list)  #67 (line in Coconut source)
    default_target_id: str = "__END__"  #68 (line in Coconut source)
    default_intent: str = "decision_table_default"  #69 (line in Coconut source)
    strict: bool = False  #70 (line in Coconut source)



class RetryPolicy(BaseModel):  #74 (line in Coconut source)
    """Retry policy for node execution."""  #75 (line in Coconut source)

    max_attempts: int = 1  #77 (line in Coconut source)
    backoff_seconds: float = 0.0  #78 (line in Coconut source)
    backoff_multiplier: float = 2.0  #79 (line in Coconut source)


class ExecutionPolicy(BaseModel):  #82 (line in Coconut source)
    """Execution controls for agents and tools."""  #83 (line in Coconut source)

    timeout_seconds: float | None = None  #85 (line in Coconut source)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)  #86 (line in Coconut source)
    idempotency_key: str = ""  #87 (line in Coconut source)
    transaction_boundary: str = ""  # begin | end | isolated | join  #88 (line in Coconut source)


class RouteRule(BaseModel):  #91 (line in Coconut source)
    """Deterministic routing rule evaluated before LLM intent routing."""  #92 (line in Coconut source)

    name: str = ""  #94 (line in Coconut source)
    source: str = "result"  # result | state  #95 (line in Coconut source)
    path: str = ""  #96 (line in Coconut source)
    operator: str = "equals"  # equals | not_equals | contains | exists | truthy  #97 (line in Coconut source)
    value: Any = None  #98 (line in Coconut source)
    target_node_id: str = "__END__"  #99 (line in Coconut source)
    priority: int = 0  #100 (line in Coconut source)
    pause_on_match: bool = False  #101 (line in Coconut source)
    metadata: dict[str, Any] = Field(default_factory=dict)  #102 (line in Coconut source)


# ---------------------------------------------------------------------------
# Base node
# ---------------------------------------------------------------------------

class Node(BaseModel):  #109 (line in Coconut source)
    """Base class for all graph nodes.

    Fields shared across every node type:
    - Identity: node_id, node_type, name, description
    - Retrieval: embedding (dense vector for similarity search)
    - Temporal validity: valid_at / invalid_at (bi-temporal, from Graphiti)
    - Extensibility: attributes dict
    - Multi-tenancy: group_id
    """  #118 (line in Coconut source)

    node_id: str = Field(default_factory=_uuid)  #120 (line in Coconut source)
    node_type: NodeType = NodeType.CONTEXT  #121 (line in Coconut source)
    name: str = ""  #122 (line in Coconut source)
    description: str = ""  #123 (line in Coconut source)

# Dense vector for similarity retrieval (populated by embedder)
    embedding: list[float] | None = None  #126 (line in Coconut source)

# Temporal validity — when this node is active in the graph.
# invalid_at=None means "still active".
    valid_at: datetime = Field(default_factory=_now)  #130 (line in Coconut source)
    invalid_at: datetime | None = None  #131 (line in Coconut source)

# Extensible metadata (any JSON-serialisable values)
    attributes: dict[str, Any] = Field(default_factory=dict)  #134 (line in Coconut source)

# Graph partition key for multi-tenancy / namespacing
    group_id: str = "default"  #137 (line in Coconut source)

# Workflow / graph versioning for long-lived deployments
    version: int = 1  #140 (line in Coconut source)
    graph_version: str = "v1"  #141 (line in Coconut source)

    model_config = {"arbitrary_types_allowed": True}  #143 (line in Coconut source)

    @property  #145 (line in Coconut source)
    def is_valid(self) -> bool:  #146 (line in Coconut source)
        """True if this node is currently active (not expired)."""  #147 (line in Coconut source)
        now = _now()  #148 (line in Coconut source)
        return self.valid_at <= now and (self.invalid_at is None or self.invalid_at > now)  #149 (line in Coconut source)


    @_coconut_tco  #153 (line in Coconut source)
    def expire(self) -> "Node":  #153 (line in Coconut source)
        """Return a copy of this node marked as expired right now."""  #154 (line in Coconut source)
        return _coconut_tail_call(self.model_copy, update={"invalid_at": _now()})  #155 (line in Coconut source)


# ---------------------------------------------------------------------------
# AgentNode
# ---------------------------------------------------------------------------


class AgentNode(Node):  #162 (line in Coconut source)
    """An executable node that runs an LLM with dynamically composed tools and context.

    The agent does NOT declare its tools or context directly — they are discovered
    at runtime by traversing HAS_TOOL and HAS_CONTEXT edges from this node.

    routing_table maps output intent strings to target node_ids (or "__END__").
    """  #169 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.AGENT, frozen=True)  #171 (line in Coconut source)
    model: str = "claude-sonnet-4-6"  #172 (line in Coconut source)
    system_prompt: str = ""  #173 (line in Coconut source)
    max_iterations: int = 10  #174 (line in Coconut source)

# intent → node_id | "__END__"
    routing_table: dict[str, str] = Field(default_factory=lambda _=None: {"default": "__END__"})  #177 (line in Coconut source)
    route_rules: list[RouteRule] = Field(default_factory=list)  #178 (line in Coconut source)
    decision_table: DecisionTable | None = None  #179 (line in Coconut source)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)  #180 (line in Coconut source)
    state_schema: dict[str, Any] = Field(default_factory=dict)  #181 (line in Coconut source)
    constraint_rules: list[ConstraintRule] = Field(default_factory=list)  #182 (line in Coconut source)
    pause_before: bool = False  #183 (line in Coconut source)
    pause_after: bool = False  #184 (line in Coconut source)
    wait_for_input: str | None = None  #185 (line in Coconut source)

    @model_validator(mode="after")  #187 (line in Coconut source)
    def _enforce_type(self) -> "AgentNode":  #188 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.AGENT)  #189 (line in Coconut source)
        return self  #190 (line in Coconut source)


# ---------------------------------------------------------------------------
# ToolNode
# ---------------------------------------------------------------------------


class ToolNode(Node):  #197 (line in Coconut source)
    """A callable node with a defined JSON Schema for input and output.

    callable_ref is a dotted "module.function" path registered in the ToolRegistry.
    The graph stores the schema; the registry stores the actual Python callable.
    """  #202 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.TOOL, frozen=True)  #204 (line in Coconut source)

# JSON Schema objects describing expected I/O
    input_schema: dict[str, Any] = Field(default_factory=dict)  #207 (line in Coconut source)
    output_schema: dict[str, Any] = Field(default_factory=dict)  #208 (line in Coconut source)

# Dotted import path: "tools.web_search.search"
    callable_ref: str = ""  #211 (line in Coconut source)
    is_async: bool = True  #212 (line in Coconut source)

# Concept tags for structured retrieval boosting (e.g. ["code_execution", "python"])
# Matched against query_tags in semantic_search() for an overlap bonus.
    tags: list[str] = Field(default_factory=list)  #216 (line in Coconut source)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)  #217 (line in Coconut source)

    @model_validator(mode="after")  #219 (line in Coconut source)
    def _enforce_type(self) -> "ToolNode":  #220 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.TOOL)  #221 (line in Coconut source)
        return self  #222 (line in Coconut source)


    def to_tool_schema(self) -> dict[str, Any]:  #224 (line in Coconut source)
        """Render this ToolNode as a tool definition (Anthropic format).

        The LLM backend converts this to its own wire format if needed.
        """  #228 (line in Coconut source)
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema or {"type": "object", "properties": {}}}  #229 (line in Coconut source)

# Backward-compat alias

    @_coconut_tco  #239 (line in Coconut source)
    def to_anthropic_tool(self) -> dict[str, Any]:  #239 (line in Coconut source)
        return _coconut_tail_call(self.to_tool_schema)  #240 (line in Coconut source)


# ---------------------------------------------------------------------------
# ContextNode
# ---------------------------------------------------------------------------


class ContextNode(Node):  #247 (line in Coconut source)
    """A passive knowledge or memory chunk node.

    Supports bi-temporal modelling:
    - valid_at / invalid_at  → when this node is active *in the graph*
    - fact_valid_at / fact_invalid_at → when the underlying fact held *in the world*

    This lets you query: "what did this agent know before the policy changed?"
    """  #255 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.CONTEXT, frozen=True)  #257 (line in Coconut source)
    content: str = ""  #258 (line in Coconut source)
    content_type: str = "text"  # text | json | code | image_uri  #259 (line in Coconut source)
    source: str = ""  # provenance URI or description  #260 (line in Coconut source)
    token_count: int = 0  #261 (line in Coconut source)

# Concept tags for structured filtering and ranking (e.g. ["validation", "show_hide"])
# Assigned at index time; used alongside cosine similarity for context re-ranking.
    tags: list[str] = Field(default_factory=list)  #265 (line in Coconut source)

# Type-based priority bonus for ranking — injected earlier in the system prompt.
# Suggested values: anti_pattern=3, mapping=2, constraint=1, general=0
    priority: int = 0  #269 (line in Coconut source)

# Real-world temporal validity (independent of graph validity)
    fact_valid_at: datetime | None = None  #272 (line in Coconut source)
    fact_invalid_at: datetime | None = None  #273 (line in Coconut source)

    @model_validator(mode="after")  #275 (line in Coconut source)
    def _enforce_type(self) -> "ContextNode":  #276 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.CONTEXT)  #277 (line in Coconut source)
        return self  #278 (line in Coconut source)


    @property  #280 (line in Coconut source)
    def is_fact_valid(self) -> bool:  #281 (line in Coconut source)
        """True if the underlying fact currently holds in the world."""  #282 (line in Coconut source)
        now = _now()  #283 (line in Coconut source)
        if self.fact_valid_at and self.fact_valid_at > now:  #284 (line in Coconut source)
            return False  #285 (line in Coconut source)
        if self.fact_invalid_at and self.fact_invalid_at <= now:  #286 (line in Coconut source)
            return False  #287 (line in Coconut source)
        return True  #288 (line in Coconut source)


# ---------------------------------------------------------------------------
# PromptNode
# ---------------------------------------------------------------------------


class PromptNode(Node):  #295 (line in Coconut source)
    """A reusable, parameterised Jinja2 prompt template.

    Stored as a node so it can be versioned, shared across agents,
    retrieved semantically, and swapped without redeploying agent logic.
    """  #300 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.PROMPT, frozen=True)  #302 (line in Coconut source)
    template: str = ""  # Jinja2 template string  #303 (line in Coconut source)
    variables: list[str] = Field(default_factory=list)  # expected variable names  #304 (line in Coconut source)

    @model_validator(mode="after")  #306 (line in Coconut source)
    def _enforce_type(self) -> "PromptNode":  #307 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.PROMPT)  #308 (line in Coconut source)
        return self  #309 (line in Coconut source)


    @_coconut_tco  #311 (line in Coconut source)
    def render(self, **kwargs: Any) -> str:  #311 (line in Coconut source)
        """Render the template with the given variables."""  #312 (line in Coconut source)
        from jinja2 import Template  #313 (line in Coconut source)
        return _coconut_tail_call(Template(self.template).render, **kwargs)  #314 (line in Coconut source)


# ---------------------------------------------------------------------------
# SchemaNode
# ---------------------------------------------------------------------------


class SchemaNode(Node):  #321 (line in Coconut source)
    """A JSON Schema contract node.

    Used to validate ToolNode I/O or ContextNode structure.
    Connected via VALIDATES edges.
    """  #326 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.SCHEMA, frozen=True)  #328 (line in Coconut source)
    json_schema: dict[str, Any] = Field(default_factory=dict)  #329 (line in Coconut source)

    @model_validator(mode="after")  #331 (line in Coconut source)
    def _enforce_type(self) -> "SchemaNode":  #332 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.SCHEMA)  #333 (line in Coconut source)
        return self  #334 (line in Coconut source)


# ---------------------------------------------------------------------------
# GraphNode
# ---------------------------------------------------------------------------


class GraphNode(Node):  #341 (line in Coconut source)
    """A node that represents an entire sub-graph (meta-graph pattern).

    When the executor encounters a GraphNode it transparently descends into
    the sub-graph, starting from entry_node_id, traverses it under the chosen
    strategy, and exposes only the exit node's output to the parent graph.
    This enables hierarchical agent compositions where the same sub-graph
    can be reused as a single "step" in multiple parent graphs.

    Fields:
        entry_node_id    — node to start traversal from
        exit_node_id     — node whose output is the sub-graph result.
                           If empty, falls back to entry_node_id.
        strategy         — "sequential" | "parallel" | "topological"
        input_keys       — parent node_ids (or state.data keys) collected and
                           passed as the sub-graph's initial query (text join).
        input_map        — explicit {alias: source_key} mapping. The sub-graph
                           sees these aliases under its state.data.
        scope_outputs    — if True (default), inner outputs are kept scoped to
                           the sub-graph and only the exit node's output is
                           surfaced to the parent ctx.outputs. If False, all
                           inner outputs are merged into the parent (legacy).
        execution_policy — retry / timeout policy applied to the whole sub-run.
    """  #364 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.GRAPH, frozen=True)  #366 (line in Coconut source)
    entry_node_id: str = ""  #367 (line in Coconut source)
    exit_node_id: str = ""  #368 (line in Coconut source)
    strategy: str = "sequential"  #369 (line in Coconut source)
    input_keys: list[str] = Field(default_factory=list)  #370 (line in Coconut source)
    input_map: dict[str, str] = Field(default_factory=dict)  #371 (line in Coconut source)
    scope_outputs: bool = True  #372 (line in Coconut source)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)  #373 (line in Coconut source)

    @model_validator(mode="after")  #375 (line in Coconut source)
    def _enforce_type(self) -> "GraphNode":  #376 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.GRAPH)  #377 (line in Coconut source)
        return self  #378 (line in Coconut source)



class TransformNode(Node):  #381 (line in Coconut source)
    """A pure-Python data reshaping step with no LLM invocation.

    Sits between nodes in a pipeline to split, join, filter, or reformat
    data without burning tokens. The callable receives a dict of collected
    inputs and returns any value that flows into ctx.outputs and optionally
    ctx.state.data[output_key].

    input_keys — node_ids or state.data keys to collect before running.
        When non-empty the topological executor treats them as hard
        dependencies (fan-in), guaranteeing all listed branches are done
        before this node fires.
    output_key — if set, also writes the result to ctx.state.data[output_key]
        so downstream agents can read it from workflow state.
    """  #395 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.TRANSFORM, frozen=True)  #397 (line in Coconut source)
    callable_ref: str = ""  #398 (line in Coconut source)
    input_keys: list[str] = Field(default_factory=list)  #399 (line in Coconut source)
    output_key: str = ""  #400 (line in Coconut source)
    is_async: bool = True  #401 (line in Coconut source)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)  #402 (line in Coconut source)

    @model_validator(mode="after")  #404 (line in Coconut source)
    def _enforce_type(self) -> "TransformNode":  #405 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.TRANSFORM)  #406 (line in Coconut source)
        return self  #407 (line in Coconut source)



class FactSource(BaseModel):  #410 (line in Coconut source)
    """Declares where a :class:`ReasonerNode` pulls ground facts from.

    A reasoner is the *symbolic* half of a neurosymbolic pipeline: an upstream
    neural ``AgentNode`` extracts structured facts, this node loads them and runs
    a sound rule program over them.

    state_keys
        Keys in ``ctx.state.data`` whose values are lists of facts (tuples,
        dicts ``{"predicate", "args"}``, lists, or atom-syntax strings). When
        empty the reasoner falls back to the previous node's output (if it is a
        list of facts) and to ``state.data["facts"]``.
    edge_types
        Knowledge-graph edge types (e.g. ``["MENTIONS", "COVERS"]``) to load as
        binary facts of the form ``edge_type(src_name, dst_name)``. This turns
        the typed graph into a logic fact base the rules can reason over.
    include_node_facts
        When True, every currently-valid node is emitted as a unary fact
        ``node_type(node_name)`` so rules can reason about graph membership.
    use_node_names
        When True (default) edge/node facts use the node ``name``; otherwise the
        ``node_id``. Names are friendlier for hand-written rules.
    """  #432 (line in Coconut source)

    state_keys: list[str] = Field(default_factory=list)  #434 (line in Coconut source)
    edge_types: list[str] = Field(default_factory=list)  #435 (line in Coconut source)
    include_node_facts: bool = False  #436 (line in Coconut source)
    use_node_names: bool = True  #437 (line in Coconut source)


class ReasonerNode(Node):  #440 (line in Coconut source)
    """A symbolic inference step backed by the built-in Datalog engine.

    The reasoner runs a deterministic, sound rule ``program`` over ground facts
    gathered from workflow state and/or the knowledge graph (see
    :class:`FactSource`), computes the deductive closure, and writes the result
    back so a downstream agent can verbalise or act on it. No LLM is invoked —
    this is the verifiable, explainable half of neurosymbolic AI.

    Fields:
        program       — Datalog source (string DSL). See
                        ``yggdrasil_lm.symbolic.datalog`` for the syntax.
        rules         — optional pre-parsed rules (list of dicts or Rule objects)
                        merged with ``program`` if both are given.
        fact_source   — where ground facts come from.
        query         — predicate names to surface in the output. Empty = all
                        derived facts.
        emit_derived_only — if True (default) the output ``facts`` list contains
                        only newly inferred facts, not the input facts.
        with_proof    — record a justification for each derived fact (adds a
                        ``proofs`` list to the output, one per derived fact).
        output_key    — if set, the result dict is also written to
                        ``ctx.state.data[output_key]`` for downstream nodes.
        fail_on_empty — raise if the closure derives nothing (useful as a guard).
    """  #464 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.REASONER, frozen=True)  #466 (line in Coconut source)
    program: str = ""  #467 (line in Coconut source)
    rules: list[dict[str, Any]] = Field(default_factory=list)  #468 (line in Coconut source)
    fact_source: FactSource = Field(default_factory=FactSource)  #469 (line in Coconut source)
    query: list[str] = Field(default_factory=list)  #470 (line in Coconut source)
    emit_derived_only: bool = True  #471 (line in Coconut source)
    with_proof: bool = False  #472 (line in Coconut source)
    output_key: str = "inferred"  #473 (line in Coconut source)
    fail_on_empty: bool = False  #474 (line in Coconut source)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)  #475 (line in Coconut source)

    @model_validator(mode="after")  #477 (line in Coconut source)
    def _enforce_type(self) -> "ReasonerNode":  #478 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.REASONER)  #479 (line in Coconut source)
        return self  #480 (line in Coconut source)



class ApprovalNode(Node):  #483 (line in Coconut source)
    """A dedicated approval / human-in-the-loop step."""  #484 (line in Coconut source)

    node_type: NodeType = Field(default=NodeType.APPROVAL, frozen=True)  #486 (line in Coconut source)
    instructions: str = ""  #487 (line in Coconut source)
    assignees: list[str] = Field(default_factory=list)  #488 (line in Coconut source)
    assignment_mode: str = "any"  #489 (line in Coconut source)
    sla_seconds: int | None = None  #490 (line in Coconut source)
    escalation_target: str = ""  #491 (line in Coconut source)
    input_key: str = "approval"  #492 (line in Coconut source)
    approved_target_id: str = "__END__"  #493 (line in Coconut source)
    rejected_target_id: str = "__END__"  #494 (line in Coconut source)
    require_assignment: bool = False  #495 (line in Coconut source)

    @model_validator(mode="after")  #497 (line in Coconut source)
    def _enforce_type(self) -> "ApprovalNode":  #498 (line in Coconut source)
        object.__setattr__(self, "node_type", NodeType.APPROVAL)  #499 (line in Coconut source)
        return self  #500 (line in Coconut source)


# ---------------------------------------------------------------------------
# Union for deserialisation
# ---------------------------------------------------------------------------


AnyNode = AgentNode | ToolNode | ContextNode | PromptNode | SchemaNode | GraphNode | ApprovalNode | TransformNode | ReasonerNode | Node  #507 (line in Coconut source)


@_coconut_tco  #510 (line in Coconut source)
def node_from_dict(data: dict[str, Any]) -> AnyNode:  #510 (line in Coconut source)
    """Deserialise a node dict into the correct typed subclass."""  #511 (line in Coconut source)
    _type_map = {NodeType.AGENT: AgentNode, NodeType.TOOL: ToolNode, NodeType.CONTEXT: ContextNode, NodeType.PROMPT: PromptNode, NodeType.SCHEMA: SchemaNode, NodeType.GRAPH: GraphNode, NodeType.APPROVAL: ApprovalNode, NodeType.TRANSFORM: TransformNode, NodeType.REASONER: ReasonerNode}  #512 (line in Coconut source)
    node_type = NodeType(data.get("node_type", NodeType.CONTEXT))  #523 (line in Coconut source)
    cls = _type_map.get(node_type, Node)  #524 (line in Coconut source)
    return _coconut_tail_call(cls.model_validate, data)  #525 (line in Coconut source)
