"""Node types for the yggdrasil system.

Every node in the graph is a typed, temporally-valid, embeddable object.
Node type determines execution behavior in the GraphExecutor.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Node type enum
# ---------------------------------------------------------------------------

class NodeType(StrEnum):
    AGENT   = "agent"    # executable — has LLM model + routing table
    TOOL    = "tool"     # callable — has JSON Schema for input/output
    CONTEXT = "context"  # passive knowledge/memory chunk (bi-temporal)
    PROMPT  = "prompt"   # reusable Jinja2 prompt template
    SCHEMA  = "schema"   # JSON Schema contract
    GRAPH   = "graph"    # pointer to a sub-graph (meta-graph pattern)
    APPROVAL = "approval"  # dedicated human approval / inbox step


class ConstraintRule(BaseModel):
    """Declarative constraint evaluated against runtime payloads."""

    name: str = ""
    source: str = "state"  # state | result | input | output
    path: str = ""
    operator: str = "equals"  # equals | not_equals | contains | exists | truthy | in | regex | gt | gte | lt | lte
    value: Any = None
    compare_to_source: str | None = None
    compare_to_path: str = ""
    message: str = ""
    severity: str = "error"


class DecisionRule(BaseModel):
    """Decision-table row for deterministic routing."""

    name: str = ""
    conditions: list[ConstraintRule] = Field(default_factory=list)
    target_node_id: str = "__END__"
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class DecisionTable(BaseModel):
    """Simple decision table evaluated before route_rules."""

    name: str = ""
    rules: list[DecisionRule] = Field(default_factory=list)
    default_target_id: str = "__END__"
    default_intent: str = "decision_table_default"
    strict: bool = False



class RetryPolicy(BaseModel):
    """Retry policy for node execution."""

    max_attempts: int = 1
    backoff_seconds: float = 0.0
    backoff_multiplier: float = 2.0


class ExecutionPolicy(BaseModel):
    """Execution controls for agents and tools."""

    timeout_seconds: float | None = None
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    idempotency_key: str = ""
    transaction_boundary: str = ""  # begin | end | isolated | join


class RouteRule(BaseModel):
    """Deterministic routing rule evaluated before LLM intent routing."""

    name: str = ""
    source: str = "result"  # result | state
    path: str = ""
    operator: str = "equals"  # equals | not_equals | contains | exists | truthy
    value: Any = None
    target_node_id: str = "__END__"
    priority: int = 0
    pause_on_match: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Base node
# ---------------------------------------------------------------------------

class Node(BaseModel):
    """Base class for all graph nodes.

    Fields shared across every node type:
    - Identity: node_id, node_type, name, description
    - Retrieval: embedding (dense vector for similarity search)
    - Temporal validity: valid_at / invalid_at (bi-temporal, from Graphiti)
    - Extensibility: attributes dict
    - Multi-tenancy: group_id
    """

    node_id:     str      = Field(default_factory=_uuid)
    node_type:   NodeType = NodeType.CONTEXT
    name:        str      = ""
    description: str      = ""

    # Dense vector for similarity retrieval (populated by embedder)
    embedding:   list[float] | None = None

    # Temporal validity — when this node is active in the graph.
    # invalid_at=None means "still active".
    valid_at:    datetime = Field(default_factory=_now)
    invalid_at:  datetime | None = None

    # Extensible metadata (any JSON-serialisable values)
    attributes:  dict[str, Any] = Field(default_factory=dict)

    # Graph partition key for multi-tenancy / namespacing
    group_id:    str = "default"

    # Workflow / graph versioning for long-lived deployments
    version: int = 1
    graph_version: str = "v1"

    model_config = {"arbitrary_types_allowed": True}

    @property
    def is_valid(self) -> bool:
        """True if this node is currently active (not expired)."""
        now = _now()
        return self.valid_at <= now and (
            self.invalid_at is None or self.invalid_at > now
        )

    def expire(self) -> "Node":
        """Return a copy of this node marked as expired right now."""
        return self.model_copy(update={"invalid_at": _now()})


# ---------------------------------------------------------------------------
# AgentNode
# ---------------------------------------------------------------------------

class AgentNode(Node):
    """An executable node that runs an LLM with dynamically composed tools and context.

    The agent does NOT declare its tools or context directly — they are discovered
    at runtime by traversing HAS_TOOL and HAS_CONTEXT edges from this node.

    routing_table maps output intent strings to target node_ids (or "__END__").
    """

    node_type:      NodeType = Field(default=NodeType.AGENT, frozen=True)
    model:          str      = "claude-sonnet-4-6"
    system_prompt:  str      = ""
    max_iterations: int      = 10

    # intent → node_id | "__END__"
    routing_table:  dict[str, str] = Field(default_factory=lambda: {"default": "__END__"})
    route_rules: list[RouteRule] = Field(default_factory=list)
    decision_table: DecisionTable | None = None
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)
    state_schema: dict[str, Any] = Field(default_factory=dict)
    constraint_rules: list[ConstraintRule] = Field(default_factory=list)
    pause_before: bool = False
    pause_after: bool = False
    wait_for_input: str | None = None

    @model_validator(mode="after")
    def _enforce_type(self) -> "AgentNode":
        object.__setattr__(self, "node_type", NodeType.AGENT)
        return self


# ---------------------------------------------------------------------------
# ToolNode
# ---------------------------------------------------------------------------

class ToolNode(Node):
    """A callable node with a defined JSON Schema for input and output.

    callable_ref is a dotted "module.function" path registered in the ToolRegistry.
    The graph stores the schema; the registry stores the actual Python callable.
    """

    node_type:     NodeType = Field(default=NodeType.TOOL, frozen=True)

    # JSON Schema objects describing expected I/O
    input_schema:  dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)

    # Dotted import path: "yggdrasil.tools.web_search.search"
    callable_ref:  str  = ""
    is_async:      bool = True

    # Concept tags for structured retrieval boosting (e.g. ["code_execution", "python"])
    # Matched against query_tags in semantic_search() for an overlap bonus.
    tags:          list[str] = Field(default_factory=list)
    execution_policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)

    @model_validator(mode="after")
    def _enforce_type(self) -> "ToolNode":
        object.__setattr__(self, "node_type", NodeType.TOOL)
        return self

    def to_tool_schema(self) -> dict[str, Any]:
        """Render this ToolNode as a tool definition (Anthropic format).

        The LLM backend converts this to its own wire format if needed.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema or {
                "type": "object",
                "properties": {},
            },
        }

    # Backward-compat alias
    def to_anthropic_tool(self) -> dict[str, Any]:
        return self.to_tool_schema()


# ---------------------------------------------------------------------------
# ContextNode
# ---------------------------------------------------------------------------

class ContextNode(Node):
    """A passive knowledge or memory chunk node.

    Supports bi-temporal modelling:
    - valid_at / invalid_at  → when this node is active *in the graph*
    - fact_valid_at / fact_invalid_at → when the underlying fact held *in the world*

    This lets you query: "what did this agent know before the policy changed?"
    """

    node_type:        NodeType         = Field(default=NodeType.CONTEXT, frozen=True)
    content:          str              = ""
    content_type:     str              = "text"  # text | json | code | image_uri
    source:           str              = ""      # provenance URI or description
    token_count:      int              = 0

    # Concept tags for structured filtering and ranking (e.g. ["validation", "show_hide"])
    # Assigned at index time; used alongside cosine similarity for context re-ranking.
    tags:             list[str]        = Field(default_factory=list)

    # Type-based priority bonus for ranking — injected earlier in the system prompt.
    # Suggested values: anti_pattern=3, mapping=2, constraint=1, general=0
    priority:         int              = 0

    # Real-world temporal validity (independent of graph validity)
    fact_valid_at:    datetime | None  = None
    fact_invalid_at:  datetime | None  = None

    @model_validator(mode="after")
    def _enforce_type(self) -> "ContextNode":
        object.__setattr__(self, "node_type", NodeType.CONTEXT)
        return self

    @property
    def is_fact_valid(self) -> bool:
        """True if the underlying fact currently holds in the world."""
        now = _now()
        if self.fact_valid_at and self.fact_valid_at > now:
            return False
        if self.fact_invalid_at and self.fact_invalid_at <= now:
            return False
        return True


# ---------------------------------------------------------------------------
# PromptNode
# ---------------------------------------------------------------------------

class PromptNode(Node):
    """A reusable, parameterised Jinja2 prompt template.

    Stored as a node so it can be versioned, shared across agents,
    retrieved semantically, and swapped without redeploying agent logic.
    """

    node_type:  NodeType   = Field(default=NodeType.PROMPT, frozen=True)
    template:   str        = ""       # Jinja2 template string
    variables:  list[str]  = Field(default_factory=list)  # expected variable names

    @model_validator(mode="after")
    def _enforce_type(self) -> "PromptNode":
        object.__setattr__(self, "node_type", NodeType.PROMPT)
        return self

    def render(self, **kwargs: Any) -> str:
        """Render the template with the given variables."""
        from jinja2 import Template
        return Template(self.template).render(**kwargs)


# ---------------------------------------------------------------------------
# SchemaNode
# ---------------------------------------------------------------------------

class SchemaNode(Node):
    """A JSON Schema contract node.

    Used to validate ToolNode I/O or ContextNode structure.
    Connected via VALIDATES edges.
    """

    node_type:   NodeType       = Field(default=NodeType.SCHEMA, frozen=True)
    json_schema: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _enforce_type(self) -> "SchemaNode":
        object.__setattr__(self, "node_type", NodeType.SCHEMA)
        return self


# ---------------------------------------------------------------------------
# GraphNode
# ---------------------------------------------------------------------------

class GraphNode(Node):
    """A node that represents an entire sub-graph (meta-graph pattern).

    When the executor encounters a GraphNode it transparently descends into
    the sub-graph, starting from entry_node_id and stopping at exit_node_id.
    This enables hierarchical agent compositions where the same sub-graph
    can be reused as a single "step" in multiple parent graphs.
    """

    node_type:     NodeType = Field(default=NodeType.GRAPH, frozen=True)
    entry_node_id: str      = ""   # node to start traversal from
    exit_node_id:  str      = ""   # node whose output is the sub-graph result

    @model_validator(mode="after")
    def _enforce_type(self) -> "GraphNode":
        object.__setattr__(self, "node_type", NodeType.GRAPH)
        return self


class ApprovalNode(Node):
    """A dedicated approval / human-in-the-loop step."""

    node_type: NodeType = Field(default=NodeType.APPROVAL, frozen=True)
    instructions: str = ""
    assignees: list[str] = Field(default_factory=list)
    assignment_mode: str = "any"
    sla_seconds: int | None = None
    escalation_target: str = ""
    input_key: str = "approval"
    approved_target_id: str = "__END__"
    rejected_target_id: str = "__END__"
    require_assignment: bool = False

    @model_validator(mode="after")
    def _enforce_type(self) -> "ApprovalNode":
        object.__setattr__(self, "node_type", NodeType.APPROVAL)
        return self


# ---------------------------------------------------------------------------
# Union for deserialisation
# ---------------------------------------------------------------------------

AnyNode = AgentNode | ToolNode | ContextNode | PromptNode | SchemaNode | GraphNode | ApprovalNode | Node


def node_from_dict(data: dict[str, Any]) -> AnyNode:
    """Deserialise a node dict into the correct typed subclass."""
    _type_map = {
        NodeType.AGENT:   AgentNode,
        NodeType.TOOL:    ToolNode,
        NodeType.CONTEXT: ContextNode,
        NodeType.PROMPT:  PromptNode,
        NodeType.SCHEMA:  SchemaNode,
        NodeType.GRAPH:   GraphNode,
        NodeType.APPROVAL: ApprovalNode,
    }
    node_type = NodeType(data.get("node_type", NodeType.CONTEXT))
    cls = _type_map.get(node_type, Node)
    return cls.model_validate(data)
