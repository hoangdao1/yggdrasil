# Yggdrasil — API Reference

Complete reference for the public `yggdrasil` API.

**Start here:** If you are new to the project, jump to [§1 Quick Start](#1-quick-start)
for a working example in five lines. The rest of the reference covers what `GraphApp`
wraps and how to work directly with the graph primitives.

**Table of Contents**

0. [How To Read This Reference](#0-how-to-read-this-reference)
1. [Quick Start](#1-quick-start)
2. [Builder API](#2-builder-api)
   - [GraphApp](#graphapp)
   - [create_agent](#create_agent)
   - [create_tool](#create_tool)
   - [create_context](#create_context)
   - [create_prompt](#create_prompt)
   - [create_executor](#create_executor)
3. [Package Imports](#3-package-imports)
4. [Node Types](#4-node-types)
   - [NodeType](#nodetype)
   - [Node (base)](#node-base)
   - [AgentNode](#agentnode)
   - [ApprovalNode](#approvalnode)
   - [ToolNode](#toolnode)
   - [ContextNode](#contextnode)
   - [PromptNode](#promptnode)
   - [SchemaNode](#schemanode)
   - [GraphNode](#graphnode)
   - [Utility: node_from_dict](#utility-node_from_dict)
5. [Edge Types](#5-edge-types)
   - [EdgeType](#edgetype)
   - [Edge](#edge)
6. [Graph Store](#6-graph-store)
   - [GraphStore (ABC)](#graphstore-abc)
   - [NetworkXGraphStore](#networkxgraphstore)
7. [Execution Engine](#7-execution-engine)
   - [ExecutionContext](#executioncontext)
   - [ExecutionOptions](#executionoptions)
   - [ContextSelection](#contextselection)
   - [ContextNavigator](#contextnavigator)
   - [TraceEvent](#traceevent)
   - [print_trace](#print_trace)
   - [inspect_trace](#inspect_trace)
   - [get_runtime_nodes](#get_runtime_nodes)
   - [cleanup_session](#cleanup_session)
   - [RoutingDecision](#routingdecision)
   - [AgentResult](#agentresult)
   - [ComposedAgent](#composedagent)
   - [AgentComposer](#agentcomposer)
   - [GraphExecutor](#graphexecutor)
8. [Review And Explainability](#8-review-and-explainability)
   - [Run Explanations](#run-explanations)
9. [LLM Backends](#9-llm-backends)
   - [LLMBackend (ABC)](#llmbackend-abc)
   - [AnthropicBackend](#anthropicbackend)
   - [OpenAIBackend](#openaibackend)
   - [ToolCall / ToolResult / LLMResponse](#toolcall--toolresult--llmresponse)
10. [Batch Execution](#10-batch-execution)
    - [BatchStatus](#batchstatus)
    - [BatchItemResult](#batchitemresult)
    - [BatchRun](#batchrun)
    - [executor.batch()](#executorbatch)
    - [BatchExecutor](#batchexecutor)
11. [Embedder](#11-embedder)
12. [Semantic Search](#12-semantic-search)
    - [RetrievalResult](#retrievalresult)
    - [semantic_search](#semantic_search)
13. [Tool Registry](#13-tool-registry)
    - [ToolRegistry](#toolregistry)
    - [default_registry](#default_registry)
    - [Built-in Tools](#built-in-tools)
14. [End-to-End Tutorial](#14-end-to-end-tutorial)
15. [Claude Code Backend](#15-claude-code-backend)
    - [ClaudeCodeExecutor](#claudecodeexecutor)
16. [OpenTelemetry Exporter](#16-opentelemetry-exporter)
    - [export_trace](#export_trace)
17. [Trace Visualizer](#17-trace-visualizer)
    - [serve_trace](#serve_trace)
    - [live_trace](#live_trace)
    - [VizServer](#vizserver)
    - [HTTP and WebSocket API](#http-and-websocket-api)

---

## 0. How To Read This Reference

If you are new to the project, this reading order tends to work best:

1. `Node`, `Edge`, and `GraphStore`
2. `GraphExecutor` and `ExecutionContext`
3. retrieval, tools, and backends

If you are already building with `yggdrasil`, the most useful sections are usually:

- **Execution Engine** for runtime behavior
- **Claude Code Backend** or **LLM Backends** for provider-specific details

The reference uses a consistent pattern:

- a short description of what the type or API is for
- a signature block
- key fields or methods
- a compact example when behavior is easier to understand in code

---

## 1. Quick Start

90% of use cases fit in five lines:

```python
from yggdrasil_lm.app import GraphApp

app   = GraphApp()
agent = await app.add_agent("Bot", system_prompt="You are a helpful assistant.")
ctx   = await app.run(agent, "What is Python 3.13?")
print(ctx.outputs[agent.node_id]["text"])
```

That is it. `GraphApp` wires up the store, the executor, and the backend automatically.
Jump to [§2 Builder API](#2-builder-api) for the full `GraphApp` surface, or [§4 Node Types](#4-node-types)
to work directly with graph primitives.

---

## 2. Builder API

A beginner-friendly facade over the core primitives. Use `GraphApp` when you want a task-oriented API that handles store setup, executor creation, and edge wiring for you. Import from `yggdrasil.app`.

```python
from yggdrasil_lm.app import (
    GraphApp,
    create_agent,
    create_tool,
    create_context,
    create_prompt,
    create_executor,
)
```

---

### GraphApp

Thin builder facade. Manages a `NetworkXGraphStore` and a lazily-created `GraphExecutor`.

```python
class GraphApp:
    def __init__(
        self,
        *,
        store:         GraphStore | None = None,    # default: new NetworkXGraphStore
        executor:      GraphExecutor | None = None, # default: auto-created on first use
        provider:      str | None = None,           # "anthropic" | "openai" | "compatible"
        backend:       LLMBackend | None = None,
        tool_registry: ToolRegistry | None = None,  # default: default_registry
        **backend_kwargs,
    ) -> None
```

**Properties**

| Property | Type | Description |
|---|---|---|
| `store` | `GraphStore` | The underlying graph store |
| `executor` | `GraphExecutor` | Lazily-created executor (created on first access) |
| `tool_registry` | `ToolRegistry` | Active tool registry |

**Methods**

```python
    async def add_agent(name: str, **kwargs) -> AgentNode
    # Create an AgentNode, upsert it, and return it.

    async def add_tool(
        name: str,
        *,
        fn: Callable | None = None,    # auto-register if provided
        attach: bool = False,          # add HAS_TOOL edge if True
        agent: AgentNode | str | None = None,  # required when attach=True
        **kwargs,
    ) -> ToolNode

    async def add_context(name: str, content: str, **kwargs) -> ContextNode

    async def add_prompt(name: str, template: str, **kwargs) -> PromptNode

    def register_tool(callable_ref: str, fn: Callable) -> None
    # Register a callable with the executor.

    def use_default_tools() -> None
    # Attach the default_registry (web_search, echo, run_python) to the executor.

    async def connect_tool(agent, tool, *, weight=None, **kwargs) -> Edge
    async def connect_context(agent, context, *, weight=None, **kwargs) -> Edge
    async def connect_prompt(agent, prompt, **kwargs) -> Edge
    async def delegate(src_agent, dst_agent, **kwargs) -> Edge

    async def run(
        entry_node: AgentNode | str,
        query: str,
        *,
        strategy: str = "sequential",
        **kwargs,
    ) -> ExecutionContext
```

**Tutorial**

```python
import asyncio
from yggdrasil_lm.app import GraphApp

async def main():
    app = GraphApp()

    agent = await app.add_agent(
        "Researcher",
        system_prompt="You are a technical researcher.",
        model="claude-sonnet-4-6",
    )
    app.use_default_tools()   # register built-in web_search, echo, run_python

    ctx = await app.run(agent, "What changed in Python 3.13?")
    print(ctx.outputs[agent.node_id]["text"])

asyncio.run(main())
```

---

### create_agent

```python
def create_agent(
    name: str,
    *,
    description:    str = "",
    model:          str = "claude-sonnet-4-6",
    system_prompt:  str = "",
    routing_table:  dict[str, str] | None = None,   # default: {"default": "__END__"}
    max_iterations: int = 10,
    **kwargs,
) -> AgentNode
```

Creates an `AgentNode` with beginner-friendly defaults. `routing_table` defaults to `{"default": "__END__"}` when `None`.

---

### create_tool

```python
def create_tool(
    name: str,
    *,
    callable_ref:  str,
    description:   str = "",
    input_schema:  dict[str, Any] | None = None,   # default: {"type": "object", "properties": {}}
    output_schema: dict[str, Any] | None = None,   # default: {}
    is_async:      bool = True,
    **kwargs,
) -> ToolNode
```

---

### create_context

```python
def create_context(
    name: str,
    content: str,
    *,
    description: str = "",
    **kwargs,
) -> ContextNode
```

---

### create_prompt

```python
def create_prompt(
    name: str,
    template: str,
    *,
    description: str = "",
    **kwargs,
) -> PromptNode
```

---

### create_executor

```python
def create_executor(
    store: GraphStore,
    *,
    provider:  str | None = None,
    backend:   LLMBackend | None = None,
    **backend_kwargs,
) -> GraphExecutor
```

Creates a `GraphExecutor` from a small set of backend profiles.

| `provider` value | Backend used |
|---|---|
| `None` | Default `AnthropicBackend()` |
| `"anthropic"` | `AnthropicBackend(**backend_kwargs)` |
| `"openai"` / `"openai-compatible"` / `"compatible"` | `OpenAIBackend(**backend_kwargs)` |

`backend` takes precedence over `provider` when both are supplied.

---

## 3. Package Imports

The top-level `yggdrasil` package exports ~35 symbols covering the happy-path primitives. Everything else lives in a canonical submodule — import from there directly.

```python
# ── Top-level (yggdrasil) — 35 symbols ─────────────────────────────────────

from yggdrasil import (
    # Entry points
    GraphApp, create_agent, create_context, create_executor, create_prompt, create_tool,

    # Core node types
    AgentNode, ApprovalNode, ContextNode, ToolNode, GraphNode,
    RetryPolicy, ExecutionPolicy, RouteRule,

    # Graph primitives
    Edge, EdgeType, END_NODE,
    GraphStore, NetworkXGraphStore,

    # Execution
    GraphExecutor, ExecutionContext, ExecutionOptions,
    RoutingDecision, TraceEvent,

    # Observability
    explain_run, RunExplanation,
    print_trace, inspect_trace,

    # Backends
    AnthropicBackend, OpenAIBackend,

    # Batch
    BatchRun, BatchItemResult, BatchStatus,
)

# ── Submodule imports ────────────────────────────────────────────────────────

# Niche / advanced node types
from yggdrasil_lm.core.nodes import (
    Node, NodeType,
    PromptNode, SchemaNode,
    ConstraintRule, DecisionRule, DecisionTable,
    node_from_dict, AnyNode,
)

# Internal runtime helpers
from yggdrasil_lm.core.executor import (
    WorkflowPause, WorkflowState,
    cleanup_session, get_runtime_nodes,
)

# LLM backends
from yggdrasil_lm.backends.llm import LLMBackend, ToolCall, ToolResult, LLMResponse

# Batch (legacy direct construction)
from yggdrasil_lm.batch import BatchExecutor

# Semantic retrieval
from yggdrasil_lm.retrieval.embedder import Embedder
from yggdrasil_lm.retrieval.wrrf import semantic_search, RetrievalResult

# Tool registry
from yggdrasil_lm.tools.registry import ToolRegistry, default_registry

# Claude Code sub-agent backend (requires pip install 'yggdrasil[claude-code]')
from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

# OpenTelemetry exporter (requires pip install 'yggdrasil[observe]')
from yggdrasil_lm.exporters.otel import export_trace
```

---

## 4. Node Types

All nodes are immutable [Pydantic v2](https://docs.pydantic.dev/) models. Every node type shares the base fields defined on `Node` and adds type-specific fields on top.

---

### NodeType

> Import: `from yggdrasil_lm.core.nodes import NodeType`

```python
class NodeType(StrEnum):
    AGENT   = "agent"
    TOOL    = "tool"
    CONTEXT = "context"
    PROMPT  = "prompt"
    SCHEMA  = "schema"
    GRAPH   = "graph"
    APPROVAL = "approval"
```

`node_type` is **frozen** on every subclass — it cannot be changed after construction.

---

### Node (base)

> Import: `from yggdrasil_lm.core.nodes import Node`

```python
class Node(BaseModel):
    node_id:    str                  # UUID, auto-generated
    node_type:  NodeType             # default: NodeType.CONTEXT
    name:       str                  # default: ""
    description: str                 # default: ""
    embedding:  list[float] | None   # default: None
    valid_at:   datetime             # default: utcnow()
    invalid_at: datetime | None      # default: None  (None = still active)
    attributes: dict[str, Any]       # default: {}
    group_id:   str                  # default: "default"
```

**Properties**

| Property | Type | Description |
|---|---|---|
| `is_valid` | `bool` | `True` when `valid_at <= now < invalid_at` (or `invalid_at is None`) |

**Methods**

| Method | Signature | Description |
|---|---|---|
| `expire` | `() -> Node` | Returns a copy with `invalid_at` set to now |

**Tutorial — creating and expiring a base node**

```python
from yggdrasil_lm.core.nodes import Node

node = Node(name="scratch", description="temporary")
print(node.node_id)    # auto UUID
print(node.is_valid)   # True

dead = node.expire()
print(dead.is_valid)   # False
```

---

### AgentNode

An executable node that runs an LLM. Tools and context are **not** stored on the node itself — they are discovered at traversal time by following `HAS_TOOL` and `HAS_CONTEXT` edges.

At a glance:

- `routing_table` handles intent-to-node mapping
- `route_rules` adds deterministic routing before LLM intent classification
- `decision_table` adds table-driven routing before both route rules and LLM intent classification
- `execution_policy` controls timeout, retry, backoff, idempotency, and transaction boundaries
- `state_schema` validates workflow state for that node
- `constraint_rules` enforce workflow invariants across state and outputs
- `pause_before` / `pause_after` / `wait_for_input` support human-in-the-loop flows

```python
class AgentNode(Node):
    node_type:      NodeType          # frozen = NodeType.AGENT
    model:          str               # default: "claude-sonnet-4-6"
    system_prompt:  str               # default: ""
    max_iterations: int               # default: 10
    routing_table:  dict[str, str]    # default: {}
    route_rules:    list[RouteRule]   # default: []
    decision_table: DecisionTable | None  # default: None
    execution_policy: ExecutionPolicy # default: ExecutionPolicy()
    state_schema:   dict[str, Any]    # default: {}
    constraint_rules: list[ConstraintRule]  # default: []
    pause_before:   bool              # default: False
    pause_after:    bool              # default: False
    wait_for_input: str | None        # default: None
```

**`routing_table`** — maps intent strings to the next `node_id` (or `"__END__"`).
After each LLM response `_infer_intent()` classifies the output via a lightweight LLM call (Haiku-class) and returns the matching key. Falls back to case-insensitive keyword matching when no backend is available. `"default"` fires when nothing else matches.

**`route_rules`** — deterministic routing rules evaluated before LLM intent routing. Use them when workflow state or structured outputs must drive the next hop with no ambiguity.

**`decision_table`** — optional ordered decision table. Use this when auditable table-style routing is easier to review than independent route rules.

**`execution_policy`** — runtime controls for timeout, retry, backoff, idempotency-sensitive execution, and transaction boundaries.

**`state_schema`** — optional JSON Schema used to validate `ExecutionContext.state.data` while the node runs.

**`constraint_rules`** — declarative invariants checked against runtime state, inputs, and outputs.

**`pause_before` / `pause_after` / `wait_for_input`** — enable human-in-the-loop and callback-driven workflows without leaving the core executor.

**Tutorial**

```python
from yggdrasil import AgentNode

researcher = AgentNode(
    name="Researcher",
    description="Finds information on technical topics",
    model="claude-sonnet-4-6",
    system_prompt="You are a technical researcher. Use the tools available.",
    max_iterations=5,
    routing_table={
        "synthesis needed": "<synthesizer_node_id>",
        "default": "__END__",
    },
)
```

---

### ApprovalNode

`ApprovalNode` is a dedicated human-in-the-loop step.

Use it when a workflow must pause for an operator, reviewer, or approver before
continuing to the next branch.

```python
class ApprovalNode(Node):
    node_type: NodeType              # frozen = NodeType.APPROVAL
    instructions: str                # default: ""
    assignees: list[str]             # default: []
    assignment_mode: str             # default: "any"
    sla_seconds: int | None          # default: None
    escalation_target: str           # default: ""
    input_key: str                   # default: "approval"
    approved_target_id: str          # default: "__END__"
    rejected_target_id: str          # default: "__END__"
    require_assignment: bool         # default: False
```

At a glance:

- creates approval/inbox tasks during execution
- pauses the workflow until input is provided
- routes explicitly to approve or reject targets
- supports assignee metadata, SLA timing, and escalation metadata

Typical pattern:

```python
from yggdrasil import ApprovalNode

approval = ApprovalNode(
    name="Manager Approval",
    instructions="Approve or reject this procurement request.",
    assignees=["finance-manager"],
    assignment_mode="any",
    sla_seconds=3600,
    escalation_target="director-on-call",
    input_key="approval",
    approved_target_id="finalize",
    rejected_target_id="reject",
)
```

Runtime notes:

- an `ApprovalNode` emits `approval_task` trace events
- the workflow pauses until the expected input key is populated
- approval and rejection are first-class control-flow branches, not prompt conventions

---

### ToolNode

Describes a callable Python function as a graph object. The graph stores the schema; the actual callable lives in `ToolRegistry`.

At a glance:

- `input_schema` and `output_schema` define contracts
- `execution_policy` controls timeout, retry, backoff, and idempotency

```python
class ToolNode(Node):
    node_type:     NodeType          # frozen = NodeType.TOOL
    callable_ref:  str               # default: ""  — "module.submodule.fn"
    input_schema:  dict[str, Any]    # default: {}  — JSON Schema
    output_schema: dict[str, Any]    # default: {}  — JSON Schema (informational)
    is_async:      bool              # default: True
    tags:          list[str]         # default: []
    execution_policy: ExecutionPolicy # default: ExecutionPolicy()
```

**`tags`** — concept labels matched against `query_tags` in `semantic_search()` for a per-tag score bonus.

**`execution_policy`** — tool-level timeout, retry, backoff, and idempotency settings.

**Methods**

| Method | Signature | Description |
|---|---|---|
| `to_tool_schema` | `() -> dict[str, Any]` | Returns tool definition in Anthropic format |
| `to_anthropic_tool` | `() -> dict[str, Any]` | Backward-compat alias for `to_tool_schema` |

**Tutorial**

```python
from yggdrasil import ToolNode

search_tool = ToolNode(
    name="web_search",
    description="Search the web for current information",
    callable_ref="yggdrasil.tools.web_search.search",
    input_schema={
        "type": "object",
        "properties": {
            "query":       {"type": "string"},
            "num_results": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
    output_schema={"type": "string"},
    is_async=True,
    tags=["web", "search", "information_retrieval"],
)

print(search_tool.to_tool_schema())
# {"name": "web_search", "description": "...", "input_schema": {...}}
```

---

### ContextNode

A passive knowledge or memory chunk injected into an agent's system prompt. Supports **bi-temporal modelling** with two independent timestamp pairs.

```python
class ContextNode(Node):
    node_type:       NodeType          # frozen = NodeType.CONTEXT
    content:         str               # default: ""
    content_type:    str               # default: "text"  ("text"|"json"|"code"|"image_uri")
    source:          str               # default: ""
    token_count:     int               # default: 0
    tags:            list[str]         # default: []
    priority:        int               # default: 0
    fact_valid_at:   datetime | None   # default: None
    fact_invalid_at: datetime | None   # default: None
```

**Bi-temporal fields**

| Pair | Tracks |
|---|---|
| `valid_at` / `invalid_at` (inherited) | When the *node* is active in the graph |
| `fact_valid_at` / `fact_invalid_at` | When the underlying *real-world fact* held |

**Properties**

| Property | Type | Description |
|---|---|---|
| `is_fact_valid` | `bool` | `True` when `now` falls in `[fact_valid_at, fact_invalid_at)` |

**Default navigation signals** (when `AgentComposer` uses the built-in `ContextNavigator`):
```
score =
  semantic_similarity(query, ctx)
  × direct_or_path_affinity
  × path_decay
  + priority_bonus
  + tag_overlap_bonus
  + recency_bonus
  + runtime_provenance_bonus
  - stale_fact_penalty
```

Suggested `priority` values: `anti_pattern=3`, `mapping=2`, `constraint=1`, `general=0`.

**Tutorial**

```python
from datetime import datetime, timezone
from yggdrasil import ContextNode

policy = ContextNode(
    name="Code Review Policy",
    content="All PRs require two approvals before merging.",
    content_type="text",
    source="https://wiki.internal/policy",
    tags=["policy", "git"],
    priority=2,
    fact_valid_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    fact_invalid_at=None,   # still valid
)

print(policy.is_fact_valid)   # True
print(policy.is_valid)        # True (not expired in graph)
```

---

### PromptNode

> Import: `from yggdrasil_lm.core.nodes import PromptNode`

A reusable Jinja2 template stored as a graph node. Storing prompts in the graph allows versioning, semantic search, sharing across agents, and runtime swapping without code changes.

```python
class PromptNode(Node):
    node_type:  NodeType     # frozen = NodeType.PROMPT
    template:   str          # default: ""  — Jinja2 template string
    variables:  list[str]    # default: []  — expected variable names
```

**Methods**

| Method | Signature | Description |
|---|---|---|
| `render` | `(**kwargs: Any) -> str` | Renders the Jinja2 template with the given variables |

**Tutorial**

```python
from yggdrasil_lm.core.nodes import PromptNode

prompt = PromptNode(
    name="ResearcherPrompt",
    template="You are a {{ role }} expert in {{ domain }}. Always cite sources.",
    variables=["role", "domain"],
)

text = prompt.render(role="software engineering", domain="Python")
print(text)
# "You are a software engineering expert in Python. Always cite sources."
```

---

### SchemaNode

> Import: `from yggdrasil_lm.core.nodes import SchemaNode`

Stores a JSON Schema contract as a first-class graph citizen. Connected to `ToolNode` or `ContextNode` via `VALIDATES` edges. Passive — the executor never visits it directly.

```python
class SchemaNode(Node):
    node_type:   NodeType          # frozen = NodeType.SCHEMA
    json_schema: dict[str, Any]    # default: {}
```

**Tutorial**

```python
from yggdrasil_lm.core.nodes import SchemaNode
from yggdrasil import Edge, EdgeType

schema = SchemaNode(
    name="SearchInputSchema",
    description="Input contract for web_search",
    json_schema={
        "type": "object",
        "properties": {
            "query":       {"type": "string", "minLength": 1},
            "num_results": {"type": "integer", "minimum": 1, "maximum": 20},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
)
await store.upsert_node(schema)

# Link to the tool it constrains
await store.upsert_edge(Edge(
    src_id=schema.node_id,
    dst_id=tool.node_id,
    edge_type=EdgeType.VALIDATES,
))

# Validate at call time
import jsonschema
edges = await store.get_edges(tool.node_id, edge_type=EdgeType.VALIDATES, direction="in")
for edge in edges:
    s = await store.get_node(edge.src_id)
    jsonschema.validate(llm_tool_input, s.json_schema)
```

---

### GraphNode

Wraps an entire sub-graph behind a single node interface. When the executor encounters a `GraphNode`, it transparently descends into the sub-graph starting from `entry_node_id` and returns the output of `exit_node_id`.

```python
class GraphNode(Node):
    node_type:     NodeType   # frozen = NodeType.GRAPH
    entry_node_id: str        # default: ""
    exit_node_id:  str        # default: ""
```

**Tutorial**

```python
from yggdrasil import AgentNode, GraphNode, Edge, NetworkXGraphStore, GraphExecutor

store = NetworkXGraphStore()

# Build the inner pipeline
researcher  = AgentNode(name="Researcher",  routing_table={"default": synthesizer.node_id})
synthesizer = AgentNode(name="Synthesizer", routing_table={"default": "__END__"})
await store.upsert_node(researcher)
await store.upsert_node(synthesizer)
await store.upsert_edge(Edge.delegates_to(researcher.node_id, synthesizer.node_id))

# Expose the pipeline as a single reusable node
pipeline = GraphNode(
    name="ResearchPipeline",
    entry_node_id=researcher.node_id,
    exit_node_id=synthesizer.node_id,
)
await store.upsert_node(pipeline)

# Another agent delegates to the whole pipeline as one step
orchestrator = AgentNode(name="Orchestrator", routing_table={"default": pipeline.node_id})
await store.upsert_node(orchestrator)
await store.upsert_edge(Edge.delegates_to(orchestrator.node_id, pipeline.node_id))

ctx = await GraphExecutor(store).run(orchestrator.node_id, "research Python 3.13")
print(ctx.outputs[pipeline.node_id])   # synthesizer's output
```

---

### Utility: node_from_dict

```python
def node_from_dict(data: dict[str, Any]) -> AnyNode
```

Deserializes a plain dict (e.g. from JSON) into the correct typed subclass, keyed on the `"node_type"` field.

```python
from yggdrasil_lm.core.nodes import node_from_dict

data = {"node_type": "agent", "name": "Bot", "model": "claude-sonnet-4-6"}
node = node_from_dict(data)
# → AgentNode(name="Bot", ...)
```

**Type alias**

```python
AnyNode = AgentNode | ToolNode | ContextNode | PromptNode | SchemaNode | GraphNode | Node
```

---

## 5. Edge Types

---

### EdgeType

```python
class EdgeType(StrEnum):
    HAS_TOOL     = "HAS_TOOL"      # agent → tool
    HAS_CONTEXT  = "HAS_CONTEXT"   # agent → context
    HAS_PROMPT   = "HAS_PROMPT"    # agent → prompt
    DELEGATES_TO = "DELEGATES_TO"  # agent → agent
    PRODUCES     = "PRODUCES"      # agent/tool → context  (output materialised)
    COVERS       = "COVERS"        # context → concept tag    [ContextNavigator-internal]
    MENTIONS     = "MENTIONS"      # context → entity         [ContextNavigator-internal]
    NEXT         = "NEXT"          # context → context        [ContextNavigator-internal]
    SIMILAR_TO   = "SIMILAR_TO"    # any → any  (semantic similarity)
    VALIDATES    = "VALIDATES"     # schema → tool/context
    CONTAINS     = "CONTAINS"      # graph-node → node  (sub-graph membership)
```

`COVERS`, `MENTIONS`, and `NEXT` are created and consumed by `ContextNavigator` during context expansion. User code rarely constructs these edges directly — they emerge from `ContextNavigator` traversal and are filtered internally. You can inspect them via `store.get_edges()` but you do not need to create them.

---

### Edge

```python
class Edge(BaseModel):
    edge_id:    str                 # UUID, auto-generated
    edge_type:  EdgeType            # default: HAS_CONTEXT
    src_id:     str                 # source node ID
    dst_id:     str                 # destination node ID
    weight:     float               # default: 1.0
    description: str                # default: ""
    attributes: dict[str, Any]      # default: {}
    valid_at:   datetime            # default: utcnow()
    invalid_at: datetime | None     # default: None
    group_id:   str                 # default: "default"
```

**Properties**

| Property | Type | Description |
|---|---|---|
| `is_valid` | `bool` | `True` when `valid_at <= now < invalid_at` (or `invalid_at is None`) |

**Methods**

| Method | Signature | Description |
|---|---|---|
| `expire` | `() -> Edge` | Returns a copy with `invalid_at` set to now |

**Factory class methods**

| Method | Signature | Creates |
|---|---|---|
| `has_tool` | `(src_id, dst_id, **kw) -> Edge` | `HAS_TOOL` edge |
| `has_context` | `(src_id, dst_id, weight=1.0, **kw) -> Edge` | `HAS_CONTEXT` edge |
| `has_prompt` | `(src_id, dst_id, **kw) -> Edge` | `HAS_PROMPT` edge |
| `delegates_to` | `(src_id, dst_id, **kw) -> Edge` | `DELEGATES_TO` edge |
| `produces` | `(src_id, dst_id, **kw) -> Edge` | `PRODUCES` edge |
| `similar_to` | `(src_id, dst_id, weight=1.0, **kw) -> Edge` | `SIMILAR_TO` edge |

**Tutorial**

```python
from yggdrasil import Edge, EdgeType

# Factory shortcuts
await store.upsert_edge(Edge.has_tool(agent.node_id, tool.node_id))
await store.upsert_edge(Edge.has_context(agent.node_id, ctx.node_id, weight=0.85))
await store.upsert_edge(Edge.has_prompt(agent.node_id, prompt.node_id))
await store.upsert_edge(Edge.delegates_to(agent.node_id, reviewer.node_id))

# Full manual construction
await store.upsert_edge(Edge(
    src_id=tool.node_id,
    dst_id=ctx.node_id,
    edge_type=EdgeType.PRODUCES,
    weight=1.0,
    description="tool output materialised as context chunk",
))

# Soft-delete an edge (preserves history)
edge = (await store.get_edges(agent.node_id, EdgeType.HAS_TOOL))[0]
await store.upsert_edge(edge.expire())
# or:
await store.expire_edge(edge.edge_id)
```

---

## 6. Graph Store

---

### GraphStore (ABC)

Abstract interface every storage backend must implement. All methods are `async`.

```python
class GraphStore(ABC):
    async def upsert_node(node: Node) -> None
    async def upsert_edge(edge: Edge) -> None
    async def get_node(node_id: str) -> AnyNode | None
    async def get_edge(edge_id: str) -> Edge | None

    async def get_edges(
        node_id:    str,
        edge_type:  EdgeType | None = None,
        direction:  str = "out",       # "out" | "in" | "both"
        only_valid: bool = True,
    ) -> list[Edge]

    async def neighbors(
        node_id:    str,
        edge_type:  EdgeType | None = None,
        depth:      int = 1,
        only_valid: bool = True,
    ) -> list[AnyNode]

    async def vector_search(
        embedding:   list[float],
        node_types:  list[NodeType] | None = None,
        top_k:       int = 10,
        only_valid:  bool = True,
    ) -> list[tuple[AnyNode, float]]    # (node, cosine_score)

    async def delete_node(node_id: str) -> None   # hard delete
    async def delete_edge(edge_id: str) -> None   # hard delete

    async def list_nodes(
        node_type: NodeType | None = None,
        group_id:  str | None = None,
        only_valid: bool = True,
    ) -> list[AnyNode]
```

**Convenience methods** (implemented on the ABC using the above)

```python
    async def expire_node(node_id: str) -> None
    async def expire_edge(edge_id: str) -> None

    async def attach_context(
        agent_id: str,
        ctx_id:   str,
        weight:   float | None = None,   # None → cosine(agent.emb, ctx.emb) or 1.0
        **kw,
    ) -> Edge

    async def attach_tool(
        agent_id: str,
        tool_id:  str,
        weight:   float | None = None,   # None → cosine(agent.emb, tool.emb) or 1.0
        **kw,
    ) -> Edge
```

`attach_context` / `attach_tool` auto-compute `weight` as the cosine similarity between the agent's and target's embeddings when both are populated — turning edge weight into a structural relevance prior. Fall back to `1.0` when embeddings are absent.

**Tutorial — graph store operations**

```python
from yggdrasil import NetworkXGraphStore, EdgeType
from yggdrasil_lm.core.nodes import NodeType

store = NetworkXGraphStore()

# Upsert (insert or update by node_id)
await store.upsert_node(agent)
await store.upsert_node(tool)

# Fetch
node = await store.get_node(agent.node_id)

# Get all outbound HAS_TOOL edges from an agent
edges = await store.get_edges(agent.node_id, edge_type=EdgeType.HAS_TOOL)

# BFS 2 hops from an agent
neighbors = await store.neighbors(agent.node_id, depth=2)

# List all active agents
agents = await store.list_nodes(node_type=NodeType.AGENT)

# Vector search — returns (node, score) pairs
hits = await store.vector_search(query_vec, node_types=[NodeType.TOOL], top_k=5)
for node, score in hits:
    print(f"{node.name}: {score:.4f}")

# Soft-delete
await store.expire_node(old_agent.node_id)
await store.expire_edge(stale_edge.edge_id)

# Hard-delete (removes from store entirely)
await store.delete_node(temp_node.node_id)
```

---

### NetworkXGraphStore

In-memory backend backed by [NetworkX](https://networkx.org/). Suitable for development, testing, and single-process workloads.

```python
class NetworkXGraphStore(GraphStore):
    def __init__(self) -> None
```

**Additional methods**

```python
    def to_dict(self) -> dict[str, Any]
    # Returns {"nodes": [<node dicts>], "edges": [<edge dicts>]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NetworkXGraphStore
    # Reconstruct store from a dict produced by to_dict()
```

**Tutorial — serialise and restore a store**

```python
import json
from yggdrasil import NetworkXGraphStore

store = NetworkXGraphStore()
await store.upsert_node(agent)
await store.upsert_edge(Edge.has_tool(agent.node_id, tool.node_id))

# Persist
snapshot = store.to_dict()
with open("graph.json", "w") as f:
    json.dump(snapshot, f)

# Restore
with open("graph.json") as f:
    data = json.load(f)
restored = NetworkXGraphStore.from_dict(data)
```

---

## 7. Execution Engine

---

### ExecutionContext

Mutable shared state threaded through every node during a single `executor.run()` call.

```python
@dataclass
class ExecutionContext:
    query:          str
    session_id:     str                # auto UUID
    outputs:        dict[str, Any]     # node_id → output dict
    trace:          list[TraceEvent]   # structured execution events (see TraceEvent)
    max_hops:       int                # default: 20
    hop_count:      int                # incremented each hop
    extra_messages: list[dict[str, Any]]   # prepended to LLM message history
    state:          WorkflowState      # typed workflow state, pause metadata
    allowed_tools:  set[str] | None    # optional tool allowlist
```

`ExecutionContext` now acts as both the execution envelope and the workflow runtime state carrier.

Key helpers:

- `is_paused() -> bool`
- `snapshot() -> dict[str, Any]`
- `ExecutionContext.from_snapshot(data) -> ExecutionContext`

Access after a run:

```python
from yggdrasil import print_trace

ctx = await executor.run(agent.node_id, "my query")

print(ctx.outputs[agent.node_id])   # {"text": "...", "intent": "..."}
print(ctx.hop_count)                # number of nodes visited
print_trace(ctx)                    # pretty-print full execution tree

# Iterate typed events
for event in ctx.trace:
    print(event.event_type, event.node_name, event.duration_ms)
```

Related runtime types:

```python
@dataclass
class WorkflowState:
    data: dict[str, Any]
    schema: dict[str, Any]
    status: str
    graph_version: str
    pending_pause: WorkflowPause | None
    inbox: dict[str, ApprovalTask]
    idempotency_cache: dict[str, Any]
    metadata: dict[str, Any]

@dataclass
class WorkflowPause:
    reason: str
    node_id: str
    node_name: str
    token: str
    waiting_for: str | None
    metadata: dict[str, Any]

@dataclass
class ApprovalTask:
    task_id: str
    node_id: str
    token: str
    status: str
    assignees: list[str]
    assigned_to: str | None
    waiting_for: str | None
    due_at: datetime | None
    escalation_target: str | None
    metadata: dict[str, Any]
```

---

### ContextSelection

> Import: `from yggdrasil_lm.core.executor import ContextSelection`

One explainable context choice produced by `ContextNavigator`.

```python
@dataclass
class ContextSelection:
    context:     ContextNode
    score:       float
    source:      str
    hops:        int = 0
    path:        list[str] = field(default_factory=list)
    reasons:     list[str] = field(default_factory=list)
    token_count: int = 0
```

---

### ContextNavigator

> Import: `from yggdrasil_lm.core.executor import ContextNavigator`

Graph-native context retrieval with seed, expansion, reranking, and token packing.

```python
@dataclass
class ContextNavigator:
    max_hops: int = 2
    max_context_nodes: int = 8
    max_context_tokens: int = 4000
    semantic_top_k: int = 12
    per_source_limit: int = 2
```

The default navigator can:

- start from direct `HAS_CONTEXT` edges
- seed extra candidates from semantic search when an embedder is present
- include runtime `ContextNode`s from the current session
- expand across `NEXT`, `SIMILAR_TO`, `MENTIONS`, `COVERS`, and `PRODUCES`
- filter stale facts using `ContextNode.is_fact_valid`
- pack the final set to node and token budgets

---

### TraceEvent

A single typed event in the execution trace. Events form a parent-child tree via `parent_event_id`, recording the full agent → tool → result → routing hierarchy with millisecond timing.

In practice, the trace gives you three views at once:

- execution flow: hops, routing, sub-graphs
- agent behavior: prompts, tools, outputs, retries
- workflow runtime: pauses, checkpoints, validation, permissions, transactions
- runtime service: approval tasks, leases, schedules, migrations

```python
EventType = Literal[
    "agent_start",     # LLM loop begins for an AgentNode
    "agent_end",       # LLM loop finishes; carries duration_ms
    "tool_call",       # a tool is about to be invoked
    "tool_result",     # tool returned; carries duration_ms and success flag
    "routing",         # intent classified and next node selected
    "context_inject",  # context nodes assembled into system prompt
    "hop",             # a node was visited in the traversal (top-level container)
    "subgraph_enter",  # GraphNode sub-graph traversal started
    "subgraph_exit",   # GraphNode sub-graph traversal finished
    "pause",           # workflow paused waiting for human or external input
    "resume",          # paused workflow resumed
    "retry",           # retry attempt emitted by execution policy
    "validation",      # schema validation success/failure
    "permission_denied", # role / allowlist enforcement blocked execution
    "checkpoint",      # execution snapshot persisted
    "transaction",     # transactional step tracking
    "approval_task",   # inbox task created by ApprovalNode
    "lease",           # worker lease acquired / released
    "schedule",        # scheduled resume or SLA escalation metadata
    "migration",       # workflow-state migration applied
]

@dataclass
class TraceEvent:
    event_type:      EventType
    session_id:      str
    node_id:         str
    node_name:       str
    timestamp:       datetime
    payload:         dict[str, Any]   # event-type-specific fields (see below)
    event_id:        str              # auto UUID
    parent_event_id: str | None       # links child events to their parent
    duration_ms:     int | None       # set on agent_end and tool_result
```

**Parent-child tree structure**

```
hop                      (parent=None — top-level container per traversal step)
  agent_start            (parent=hop.event_id)
    context_inject       (parent=agent_start.event_id)
    tool_call            (parent=agent_start.event_id)
      tool_result        (parent=tool_call.event_id)
    routing              (parent=agent_start.event_id)  ← only if routing_table set
    agent_end            (parent=agent_start.event_id)  ← carries duration_ms
```

**Payload keys per event_type**

| `event_type` | Payload keys |
|---|---|
| `agent_start` | `query` (str), `model` (str), `tools` (list[str]), `context` (list[str]), `context_scores` (list[dict]) |
| `agent_end` | `text_summary` (str), `intent` (str), `iterations` (int) |
| `tool_call` | `tool_name` (str), `callable_ref` (str), `input` (dict) |
| `tool_result` | `tool_name` (str), `output_summary` (str), `success` (bool) |
| `routing` | `intent` (str), `next_node_id` (str\|None), `confidence` (float\|None), `mode` (`"decision_table"`, `"deterministic"`, or `"llm"`) |
| `context_inject` | `context_names` (list[str]), `count` (int), `selected_contexts` (list[dict]) |
| `pause` | `reason` (str), `token` (str), `waiting_for` (str\|None), `metadata` (dict) |
| `resume` | `token` (str), `waiting_for` (str\|None) |
| `retry` | `attempt` (int), `max_attempts` (int), `error` (str) |
| `validation` | `success` (bool), `error` (str, optional) |
| `permission_denied` | `error` (str) |
| `checkpoint` | `checkpoint_node_id` (str) |
| `transaction` | `transaction_id` (str), `status` (str), additional step payload |
| `approval_task` | `task_id` (str), `assignees` (list[str]), `assigned_to` (str\|None), `due_at` (str\|None), `escalation_target` (str\|None) |
| `lease` | `resource_id` (str), `owner` (str), `expires_at` (str) |
| `schedule` | `task_id` (str, optional), `due_at` or `run_at` (str), metadata fields |
| `migration` | `from_version` (str), `to_version` (str) |
| `hop` | `hop` (int), `node_type` (str), `summary` (str) |
| `subgraph_enter` | `entry_node_id` (str) |
| `subgraph_exit` | `exit_node_id` (str), `summary` (str) |

**Tutorial — programmatic trace inspection**

```python
ctx = await executor.run(entry.node_id, "run pipeline")

# Find slow agents
for event in ctx.trace:
    if event.event_type == "agent_end" and event.duration_ms and event.duration_ms > 5000:
        print(f"Slow: {event.node_name} took {event.duration_ms}ms")

# Find failed tools
for event in ctx.trace:
    if event.event_type == "tool_result" and not event.payload["success"]:
        print(f"Tool failure: {event.node_name} — {event.payload['output_summary']}")

# Audit routing decisions
for event in ctx.trace:
    if event.event_type == "routing":
        intent   = event.payload["intent"]
        next_nid = event.payload["next_node_id"] or "__END__"
        print(f"{event.node_name}: {intent} → {next_nid}")

# Build a timing report
import collections
by_agent: dict[str, list[int]] = collections.defaultdict(list)
for event in ctx.trace:
    if event.event_type == "agent_end" and event.duration_ms:
        by_agent[event.node_name].append(event.duration_ms)
for name, times in by_agent.items():
    print(f"{name}: avg={sum(times)//len(times)}ms over {len(times)} invocations")

# Look up a specific event's children
by_parent: dict[str | None, list[TraceEvent]] = {}
for e in ctx.trace:
    by_parent.setdefault(e.parent_event_id, []).append(e)

hop_events = by_parent.get(None, [])   # top-level hops
for hop in hop_events:
    children = by_parent.get(hop.event_id, [])
    print(f"hop {hop.payload['hop']}: {[c.event_type for c in children]}")
```

---

### print_trace

```python
def print_trace(ctx: ExecutionContext | list[TraceEvent], *, width: int = 72) -> None
```

Renders the execution trace as a human-readable tree to stdout. Groups events by parent-child relationship and shows timings, intents, context injection, and tool outcomes inline.

**Arguments**

| Parameter | Type | Description |
|---|---|---|
| `ctx` | `ExecutionContext` or `list[TraceEvent]` | The trace to render |
| `width` | `int` | Console width for separator lines (default: 72) |

**Example output**

```
Session a1b2c3d4  'research and summarise quantum computing'
════════════════════════════════════════════════════════════════════════
hop 1  AGENT  researcher
  tools: web_search  context: background
  context_inject  background  (1 nodes)
  tool_call  web_search  {"query": "quantum computing 2024"}
    tool_result  web_search  ok  "Results: quantum..."  [120ms]
  routing  synthesis_needed → synthesizer_node_id
  agent_end  'Key facts: ...'  intent=synthesis_needed  iters=2  [340ms]
hop 2  AGENT  synthesizer
  tools: none
  agent_end  'Final summary: ...'  intent=default  [180ms]
════════════════════════════════════════════════════════════════════════
Total: 2 hops · 2 agent_end events · 520ms
```

**Tutorial**

```python
from yggdrasil import print_trace

# From a completed run
ctx = await executor.run(entry.node_id, "my query")
print_trace(ctx)

# From a raw event list (e.g. events loaded from a log)
events: list[TraceEvent] = ctx.trace
print_trace(events)

# Narrow width for terminals
print_trace(ctx, width=60)
```

---

### inspect_trace

```python
def inspect_trace(
    ctx:     ExecutionContext | list[TraceEvent],
    *,
    verbose: bool = True,
    file:    str | None = None,
    format:  Literal["terminal", "html", "text"] = "terminal",
) -> None:
```

Rich terminal UI for inspecting execution traces. Renders a colour-coded tree showing agent configs, tool I/O, routing decisions, timing, and a summary panel.

Falls back to `print_trace()` automatically when `rich` is not installed.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ctx` | `ExecutionContext \| list[TraceEvent]` | required | Trace source |
| `verbose` | `bool` | `True` | Full tool I/O panels and complete output previews |
| `file` | `str \| None` | `None` | Write output to this path |
| `format` | `"terminal" \| "html" \| "text"` | `"terminal"` | Output format |

**Requires:** `pip install 'yggdrasil[dev]'`

**Tutorial**

```python
from yggdrasil import inspect_trace

ctx = await executor.run(agent.node_id, "analyse the codebase")

# Default: verbose tree in terminal
inspect_trace(ctx)

# Compact: one-liner per event
inspect_trace(ctx, verbose=False)

# Export to HTML (preserves colours)
inspect_trace(ctx, file="trace.html", format="html")

# Export to plain text file
inspect_trace(ctx, file="trace.txt", format="text")
```

**Rendered columns in the summary panel**

| Row | Description |
|---|---|
| Hops | Total graph traversal steps |
| Agent calls | Number of `agent_end` events |
| Tool calls | Total tool invocations |
| Tool errors | Failed tool calls (highlighted red when > 0) |
| Context nodes | Total context nodes injected across all agents |
| Routing steps | Number of intent-based routing decisions |
| Low-conf routes | Routes where `confidence < 0.7` (highlighted yellow) |
| Total agent time | Sum of `duration_ms` across all `agent_end` events |
| Agents | Distinct agent names visited |
| Tools used | Distinct tool names called |

---

### get_runtime_nodes

> Import: `from yggdrasil_lm.core.executor import get_runtime_nodes`

```python
async def get_runtime_nodes(
    store:      GraphStore,
    session_id: str | None = None,
    only_valid: bool = True,
) -> list[ContextNode]
```

Returns runtime-materialised `ContextNode`s without graph traversal. Uses `attributes["origin"] == "runtime"` as the discriminator.

**Arguments**

| Parameter | Type | Description |
|---|---|---|
| `store` | `GraphStore` | The store to query |
| `session_id` | `str \| None` | Limit to one session (`ctx.session_id`). `None` returns all sessions. |
| `only_valid` | `bool` | Skip expired nodes (default `True`) |

**Returns** `list[ContextNode]`

**How it works**

When `session_id` is provided, `list_nodes(group_id=session_id)` narrows the scan to O(nodes-in-session) before the attribute check — no edge traversal needed. Without `session_id`, it scans all `CONTEXT` nodes and filters on `attributes["origin"]`.

**Runtime node attributes**

Every materialised `ContextNode` carries:

| Attribute key | Value | Description |
|---|---|---|
| `origin` | `"runtime"` | Discriminates from predefined nodes |
| `session_id` | `ctx.session_id` | The session that produced it |
| `source_node_id` | source node's `node_id` | Provenance without traversal |

The node also has `group_id = ctx.session_id`, enabling fast `list_nodes(group_id=...)` queries directly on the store.

**Tutorial**

```python
from yggdrasil_lm.core.executor import get_runtime_nodes

ctx = await executor.run(agent.node_id, "query")

# Nodes from this session only — fast path
nodes = await get_runtime_nodes(store, session_id=ctx.session_id)
for n in nodes:
    print(n.name)                           # "Output of echo"
    print(n.attributes["source_node_id"])   # tool node's node_id
    print(n.attributes["session_id"])       # == ctx.session_id

# All runtime nodes across all sessions
all_runtime = await get_runtime_nodes(store)

# Including expired nodes (e.g. after cleanup_session)
including_expired = await get_runtime_nodes(store, session_id=ctx.session_id, only_valid=False)

# Filtering without traversal — equivalent fast-path using list_nodes directly
session_nodes = await store.list_nodes(group_id=ctx.session_id)
predefined    = await store.list_nodes(group_id="default")
```

---

### cleanup_session

> Import: `from yggdrasil_lm.core.executor import cleanup_session`

```python
async def cleanup_session(
    store:      GraphStore,
    session_id: str,
    hard:       bool = False,
) -> int
```

Expires or hard-deletes all runtime nodes from `session_id` and their inbound `PRODUCES` edges.

**Arguments**

| Parameter | Type | Description |
|---|---|---|
| `store` | `GraphStore` | The store to clean up |
| `session_id` | `str` | Session to remove; pass `ctx.session_id` |
| `hard` | `bool` | `True` = hard-delete (frees storage). `False` = soft-expire (default, preserves history) |

**Returns** `int` — number of nodes removed or expired.

**Tutorial**

```python
from yggdrasil_lm.core.executor import cleanup_session

ctx = await executor.run(agent.node_id, "query")

# Soft-expire: history preserved, nodes excluded from future queries
n = await cleanup_session(store, ctx.session_id)
print(f"Expired {n} runtime nodes")

# Verify expired nodes are gone from valid queries
after = await get_runtime_nodes(store, session_id=ctx.session_id)
assert len(after) == 0

# Hard-delete: no recovery, frees memory
n = await cleanup_session(store, ctx.session_id, hard=True)
print(f"Deleted {n} runtime nodes")

# Pattern: cleanup after every run in production
try:
    ctx = await executor.run(agent.node_id, query)
    return ctx.outputs[agent.node_id]
finally:
    await cleanup_session(store, ctx.session_id)
```

---

### RoutingDecision

Returned by `GraphExecutor.route()` and `plan()`. Contains the LLM router's selection with explicit reasoning and a confidence score, making agent dispatch fully observable.

```python
@dataclass
class RoutingDecision:
    agent_id:   str    # node_id of the selected AgentNode
    reason:     str    # one-sentence explanation from the LLM router
    confidence: float  # 0.0–1.0
```

**Properties**

| Property | Type | Description |
|---|---|---|
| `low_confidence_warning` | `str \| None` | Non-`None` message when `confidence < 0.7`; use to surface uncertain routing to the caller. |

**Tutorial**

```python
decision = await executor.plan("add a validation rule for SSN format")

print(decision.agent_id)               # "rules-editor"
print(decision.reason)                 # "Task involves writing a Jsonnet validation rule"
print(decision.confidence)             # 0.94
print(decision.low_confidence_warning) # None — confidence is high
```

---

### AgentResult

> Import: `from yggdrasil_lm.core.executor import AgentResult`

Structured execution envelope returned by `GraphExecutor.execute()`. Bundles the agent output with the routing metadata so every dispatch decision is auditable.

```python
@dataclass
class AgentResult:
    routed_to:              str        # agent node_id that was executed
    reason:                 str        # why this agent was chosen
    confidence:             float      # router confidence (1.0 for direct calls)
    context_injected:       list[str]  # ContextNode names in the system prompt
    result:                 str        # agent output text
    low_confidence_warning: str | None # set when confidence < 0.7
```

**Tutorial**

```python
# Two-phase: inspect routing before executing
decision = await executor.plan("add a validation rule for SSN format")
if decision.low_confidence_warning:
    print(decision.low_confidence_warning)  # warn the caller

result = await executor.execute(decision.agent_id, query, routing=decision)
print(result.context_injected)   # ["Rules Editor Guide", "Mixcalc Usage"]
print(result.result)             # agent output text

# One-shot: skip the plan step (confidence defaults to 1.0)
result = await executor.execute("rules-editor", query)
```

---

### ComposedAgent

> Import: `from yggdrasil_lm.core.executor import ComposedAgent`

The fully resolved runtime configuration for one agent invocation. Returned by `AgentComposer.compose()`.

```python
@dataclass
class ComposedAgent:
    agent_node: AgentNode
    tools:      list[ToolNode]
    context:    list[ContextNode]   # selected and packed for prompt injection
    context_selection: list[ContextSelection]
    prompt:     PromptNode | None
    delegates:  list[AgentNode]
```

**Methods**

```python
    def build_system_prompt(**prompt_vars: Any) -> str
    # Render prompt template + inject ranked context into system prompt string.
    # prompt_vars are forwarded to PromptNode.render().

    def build_tool_schemas() -> list[dict[str, Any]]
    # Return list of tool definitions (Anthropic format) for all composed tools.
```

**Tutorial**

```python
from yggdrasil_lm.core.executor import AgentComposer
from yggdrasil_lm.retrieval.embedder import Embedder

composer = AgentComposer(store, embedder=Embedder())
composed = await composer.compose(agent_node, query="search for Python docs")

print([t.name for t in composed.tools])     # ["web_search"]
print([c.name for c in composed.context])   # context sorted by relevance to query
print(composed.context_selection[0].reasons)

system = composed.build_system_prompt(role="researcher", domain="Python")
schemas = composed.build_tool_schemas()
```

---

### AgentComposer

> Import: `from yggdrasil_lm.core.executor import AgentComposer`

Discovers an agent's tools, context, prompt, and delegates by traversing the graph at runtime.

```python
class AgentComposer:
    def __init__(
        self,
        store:             GraphStore,
        embedder:          Embedder | None = None,
        context_navigator: ContextNavigator | None = None,
    ) -> None
```

**Methods**

```python
    async def compose(
        self,
        agent_node: AgentNode,
        query:      str | None = None,
        session_id: str | None = None,
    ) -> ComposedAgent
```

Traversal order:

1. `HAS_TOOL` edges → `ToolNode` list, sorted by `edge.weight` descending
2. `ContextNavigator` → seed, expand, score, and pack `ContextNode` list
3. `HAS_PROMPT` edge → first `PromptNode` found (or `None`)
4. `DELEGATES_TO` edges → `AgentNode` list

The default navigator blends semantic similarity, edge affinity, path decay, priority, tag overlap, recency, and runtime provenance, while filtering stale facts and respecting token budgets.

---

### ExecutionOptions

Optional execution controls for `executor.run()`. Pass as `options=ExecutionOptions(...)`.

```python
@dataclass
class ExecutionOptions:
    allowed_tools: set[str] | None = None   # optional tool allowlist
```

```python
from yggdrasil import ExecutionOptions

ctx = await executor.run(
    agent.node_id,
    "my query",
    options=ExecutionOptions(allowed_tools={"web_search"}),
)
```

---

### GraphExecutor

Executes queries by traversing the agent graph. Dispatches to the correct handler based on `node_type`.

```python
class GraphExecutor:
    def __init__(
        self,
        store:             GraphStore,
        composer:          AgentComposer | None = None,     # auto-created if None
        backend:           LLMBackend | None = None,        # default: AnthropicBackend()
        embedder:          Embedder | None = None,          # enables semantic seeding
        context_navigator: ContextNavigator | None = None,  # custom navigation policy
    ) -> None
```

**Methods**

```python
    def register_tool(callable_ref: str, fn: Callable) -> None
    # Register a Python callable under its dotted ref string.

    def add_event_hook(fn: Callable[[TraceEvent, ExecutionContext], Any]) -> None
    # Subscribe to emitted trace events.

    async def run(
        entry_node_id:     str,
        query:             str,
        strategy:          str = "sequential",   # "sequential" | "parallel" | "topological"
        max_hops:          int = 20,
        extra_messages:    list[dict[str, Any]] | None = None,
        execution_context: ExecutionContext | None = None,
        state:             dict[str, Any] | None = None,
        allowed_tools:     list[str] | None = None,
        options:           ExecutionOptions | None = None,
    ) -> ExecutionContext

    async def resume(
        entry_node_id: str,
        ctx: ExecutionContext,
        *,
        query: str | None = None,
        strategy: str = "sequential",
    ) -> ExecutionContext

    async def checkpoint_context(
        ctx: ExecutionContext,
        *,
        name: str = "Execution checkpoint",
    ) -> ContextNode

    async def load_checkpoint(checkpoint_node_id: str) -> ExecutionContext

    async def resume_from_checkpoint(
        checkpoint_node_id: str,
        entry_node_id: str,
        *,
        query: str | None = None,
        strategy: str = "sequential",
    ) -> ExecutionContext

    # --- White-box routing (two-phase dispatch) ---

    async def route(
        query:      str,
        candidates: list[AgentNode] | None = None,  # default: all valid AgentNodes
    ) -> RoutingDecision
    # LLM-based router: single Haiku call returns {"agent", "reason", "confidence"}.
    # Falls back to the first candidate at confidence 0.5 if JSON parsing fails.

    async def plan(query: str) -> RoutingDecision
    # ⚠️ Deprecated alias for route(). Will be removed in a future release.
    # Use route() instead.

    async def execute(
        agent_id: str,
        query:    str,
        routing:  RoutingDecision | None = None,
    ) -> AgentResult
    # Phase 2: run agent_id and return a structured result envelope.
    # routing is attached to the envelope; if omitted, confidence defaults to 1.0.
```

**Execution strategies**

| Strategy | Behaviour | Use case |
|---|---|---|
| `"sequential"` | DFS: run node → follow `routing_table` → repeat | Agent chains (A → B → C) |
| `"parallel"` | BFS: fan-out to all `DELEGATES_TO` targets via `asyncio.gather` | Supervisor / worker patterns |
| `"topological"` | Waves via `graphlib.TopologicalSorter`; nodes with all deps resolved run in parallel within each wave | Explicit DAG pipelines |

**Node dispatch**

| `node_type` | Behaviour |
|---|---|
| `AGENT` | Compose → build system prompt + tools → run LLM tool-call loop → route |
| `TOOL` | Look up `callable_ref` in registry → execute → return output |
| `CONTEXT` | Return `node.content` directly |
| `GRAPH` | Descend into sub-graph from `entry_node_id`, return `exit_node_id` output |
| `PROMPT` | Render template (no variables injected here) → return string |

**Workflow runtime features**

- deterministic `RouteRule` evaluation before LLM routing
- pause / resume for human-in-the-loop workflows
- resumable execution checkpoints
- tool and state validation against JSON Schema
- retry, timeout, backoff, and idempotency handling from `ExecutionPolicy`
- minimal role and tool allowlist enforcement
- migration hooks for versioned workflow state
- transaction event tracking and optional compensation handlers

**Tutorial — all three strategies**

```python
from yggdrasil import NetworkXGraphStore, GraphExecutor
from yggdrasil_lm.tools.registry import default_registry

store = NetworkXGraphStore()
# ... build your graph ...

executor = GraphExecutor(store)
default_registry.attach(executor)   # register built-in tools

# Sequential chain
ctx = await executor.run(
    entry_node_id=researcher.node_id,
    query="What changed in Python 3.13?",
    strategy="sequential",
    max_hops=10,
)
print(ctx.outputs[synthesizer.node_id]["text"])

# Parallel fan-out
ctx = await executor.run(
    supervisor.node_id,
    "analyse this dataset",
    strategy="parallel",
)
# ctx.outputs[supervisor.node_id] = {
#   "node_result": ...,
#   "delegate_results": {worker1_id: ..., worker2_id: ...}
# }

# Topological DAG
ctx = await executor.run(entry.node_id, "run pipeline", strategy="topological")

# Extra context injected per-call (not stored in graph)
ctx = await executor.run(
    agent.node_id,
    "summarise the document",
    extra_messages=[{"role": "user", "content": "<document text here>"}],
)
```

---

## 8. Review And Explainability

### Run Explanations

Use `explain_run(ctx)` when you want a structured summary of one workflow execution.

```python
from yggdrasil import explain_run

summary = explain_run(ctx)
print(summary.session_id, summary.hop_count, summary.paused)
print(summary.summary.tool_call_count)
for hop in summary.hops:
    print(hop.node_name, hop.summary)
```

`explain_run(...)` returns a `RunExplanation` dataclass with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | The session identifier |
| `query` | `str` | The original query |
| `hop_count` | `int` | Total number of hops executed |
| `paused` | `bool` | Whether the run is paused |
| `hops` | `list[RunHopExplanation]` | Per-hop summaries |
| `routing` | `list[RunRoutingExplanation]` | Routing decisions made |
| `context` | `list[RunContextExplanation]` | Context selections |
| `tool_calls` | `list[RunToolCallExplanation]` | Tool invocations |
| `pauses` | `list[RunPauseExplanation]` | Pause events |
| `summary` | `RunSummary` | Aggregate counts |

---

## 9. LLM Backends

Backends abstract LLM provider differences. `GraphExecutor` accepts any `LLMBackend` implementation.

---

### LLMBackend (ABC)

> Import: `from yggdrasil_lm.backends.llm import LLMBackend`

```python
class LLMBackend(ABC):
    @abstractmethod
    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse: ...

    @abstractmethod
    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]: ...
    # Returns a new list (does not mutate input).
    # Each backend formats assistant turns + tool results differently.
```

---

### AnthropicBackend

Calls the Anthropic Messages API. Default backend used by `GraphExecutor` when none is provided.

```python
class AnthropicBackend(LLMBackend):
    def __init__(self, **kwargs) -> None
    # kwargs forwarded to anthropic.AsyncAnthropic()
    # Requires: pip install anthropic
    # Requires: ANTHROPIC_API_KEY environment variable
```

**Tutorial**

```python
from yggdrasil import AnthropicBackend, GraphExecutor

# Default (reads ANTHROPIC_API_KEY from env)
executor = GraphExecutor(store)

# Explicit with custom client options
backend = AnthropicBackend(timeout=30.0)
executor = GraphExecutor(store, backend=backend)
```

---

### OpenAIBackend

Calls any OpenAI-compatible `/chat/completions` endpoint — Ollama, mlx-lm, LM Studio, vLLM, Together AI, etc.

```python
class OpenAIBackend(LLMBackend):
    def __init__(
        self,
        base_url: str | None = None,   # None → official OpenAI API
        api_key:  str = "local",       # local servers accept any non-empty string
        **kwargs,                       # forwarded to openai.AsyncOpenAI()
    ) -> None
    # Requires: pip install 'yggdrasil[openai]'
```

**Tutorial**

```python
from yggdrasil import OpenAIBackend, GraphExecutor, AgentNode

# Ollama running locally
backend = OpenAIBackend(base_url="http://localhost:11434/v1", api_key="ollama")

# Agent must use a model name the local server recognises
agent = AgentNode(name="Bot", model="llama3.2", routing_table={"default": "__END__"})

executor = GraphExecutor(store, backend=backend)
ctx = await executor.run(agent.node_id, "hello")

# OpenAI API
from yggdrasil import OpenAIBackend
backend = OpenAIBackend(api_key="sk-...")
```

---

### ToolCall / ToolResult / LLMResponse

Internal types that flow between the executor and backends. Exposed for custom backend implementations.

```python
@dataclass
class ToolCall:
    id:    str
    name:  str
    input: dict[str, Any]

@dataclass
class ToolResult:
    tool_call_id: str
    content:      str

@dataclass
class LLMResponse:
    text:        str
    tool_calls:  list[ToolCall]
    stop_reason: str    # "end_turn" | "tool_use"
    _raw:        Any    # backend-native response object (for extend_messages)
```

---

## 10. Batch Execution

---

### BatchStatus

```python
class BatchStatus(StrEnum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    PARTIAL   = "partial"    # at least one success and one failure
```

---

### BatchItemResult

Result for a single item in a batch run.

```python
@dataclass
class BatchItemResult:
    item_id:    str
    status:     BatchStatus          # default: PENDING
    output:     Any                  # default: None
    error:      str | None           # default: None
    started_at: datetime | None      # default: None
    ended_at:   datetime | None      # default: None
```

**Properties**

| Property | Type | Description |
|---|---|---|
| `duration_seconds` | `float \| None` | Wall-clock duration, or `None` if not finished |

---

### BatchRun

Live state of a batch execution, updated after each item.

```python
@dataclass
class BatchRun:
    run_id:         str
    agent_id:       str
    total:          int
    results:        dict[str, BatchItemResult]   # item_id → result
    reduced_output: Any                          # output of reduce_fn, or None
    started_at:     datetime
    ended_at:       datetime | None
```

**Computed properties**

| Property | Type | Description |
|---|---|---|
| `completed` | `int` | Count of `COMPLETED` items |
| `failed` | `int` | Count of `FAILED` items |
| `pending` | `int` | Count of `PENDING` items |
| `running` | `int` | Count of `RUNNING` items |
| `status` | `BatchStatus` | Derived from item statuses |
| `progress` | `float` | `(completed + failed) / total` |

**Methods**

```python
    def successful_outputs(self) -> list[Any]
    # Returns outputs of COMPLETED items in original item order.
```

---

### executor.batch()

The preferred entry point for batch execution. Runs an agent over a list of items with concurrency control, progress tracking, checkpointing, and resume.

```python
async def batch(
    self,
    agent_node_id: str,
    items:         list[Any],
    query_fn:      Callable[[Any], str],
    *,
    context_fn:    Callable[[Any], str | None] | None = None,
    reduce_fn:     Callable[[list[Any]], Any] | None = None,
    on_progress:   Callable[[BatchRun], Any] | None = None,
    concurrency:   int = 5,
    checkpoint:    bool = True,
    strategy:      str = "sequential",
) -> BatchRun
```

| Parameter | Description |
|---|---|
| `agent_node_id` | Node to run for every item |
| `items` | List of items (any type) |
| `query_fn` | `item → query string` |
| `context_fn` | `item → str \| None` — injected as `extra_messages` per item |
| `reduce_fn` | `outputs → Any` — called after the map phase; result in `BatchRun.reduced_output` |
| `on_progress` | Called (sync or async) after each item completes |
| `concurrency` | Max parallel items (default 5) |
| `checkpoint` | Persist `BatchRun` + each `BatchItemResult` as `ContextNode` objects |
| `strategy` | Forwarded to `GraphExecutor.run()` |

**Tutorial**

```python
from yggdrasil import BatchStatus

# Map
run = await executor.batch(
    agent_node_id=agent.node_id,
    items=documents,
    query_fn=lambda doc: f"Summarise: {doc['title']}",
    context_fn=lambda doc: doc["body"],
    on_progress=lambda r: print(f"{r.progress:.0%} — {r.completed}/{r.total}"),
    concurrency=5,
    checkpoint=True,
)

print(run.status)      # "completed" | "partial" | "failed"

for item_id, result in run.results.items():
    if result.status == BatchStatus.FAILED:
        print(f"  {item_id} failed: {result.error}")

# Map + reduce
run = await executor.batch(
    agent.node_id,
    documents,
    query_fn=lambda d: f"Summarise: {d['title']}",
    reduce_fn=lambda outputs: "\n\n---\n\n".join(o["text"] for o in outputs),
)
print(run.reduced_output)   # combined summary
```

**Resume after crash**

Checkpoint nodes persist state across process restarts. Use `BatchExecutor.resume()` directly:

```python
from yggdrasil_lm.batch import BatchExecutor

batch = BatchExecutor(store, executor, concurrency=5)
run = await batch.resume(run_id, documents, query_fn=lambda d: f"Summarise: {d['title']}")
```

Skips `COMPLETED` items. Items that were `RUNNING` when the process died are treated as `PENDING` and retried.

Checkpoint nodes are `ContextNode` objects with `content_type="batch_run"` / `"batch_item"`. Node IDs are deterministic (UUID v5) so the same `run_id` always maps to the same checkpoint nodes.

---

### BatchExecutor

> **Legacy / advanced.** Prefer `executor.batch(...)` for new code. Constructing
> `BatchExecutor` directly emits a `DeprecationWarning`.

```python
from yggdrasil_lm.batch import BatchExecutor

batch = BatchExecutor(store, executor, concurrency=5)
run   = await batch.run(agent.node_id, items, query_fn=lambda x: x)
run2  = await batch.resume(run.run_id, items, query_fn=lambda x: x)
```

`BatchExecutor.run()` and `BatchExecutor.resume()` accept the same parameters as `executor.batch()`. See above for the full parameter table.

---

## 11. Embedder

Generates dense vectors for nodes using [sentence-transformers](https://www.sbert.net/) — no API key required. Requires `pip install 'yggdrasil[embeddings]'`.

```python
class Embedder:
    def __init__(self, model: str = EMBED_MODEL) -> None
    # model defaults to the EMBED_MODEL env var, or "all-MiniLM-L6-v2" if unset.
```

**Environment variables**

| Variable | Default | Description |
|---|---|---|
| `EMBED_MODEL` | `"all-MiniLM-L6-v2"` | sentence-transformers model name. Any model from the [SBERT hub](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html) works. |

**Methods**

```python
    async def embed_text(text: str) -> list[float]
    # Embed a raw string and return a normalised float vector.

    async def embed_node(store: GraphStore, node: AnyNode) -> AnyNode
    # Compute and store embedding for a single node. Returns updated node.

    async def embed_all(
        store:         GraphStore,
        node_types:    list[NodeType] | None = None,
        skip_existing: bool = True,
    ) -> int
    # Embed all matching nodes. Returns count of nodes embedded.
    # skip_existing=True skips nodes that already have an embedding.
```

**Text used for embedding per node type**

| Node type | Text |
|---|---|
| All | `name + " " + description` |
| `ContextNode` | + first 2000 chars of `content` |
| `ToolNode` | + first 500 chars of `input_schema` as JSON |

**Tutorial**

```python
from yggdrasil_lm.retrieval.embedder import Embedder
from yggdrasil_lm.core.nodes import NodeType

embedder = Embedder()

# Embed a single node
tool = await embedder.embed_node(store, tool_node)
print(len(tool.embedding))    # e.g. 384 for all-MiniLM-L6-v2

# Batch-embed all tools and agents
count = await embedder.embed_all(
    store,
    node_types=[NodeType.TOOL, NodeType.AGENT],
    skip_existing=True,
)
print(f"Embedded {count} nodes")

# Embed a query string for vector search
query_vec = await embedder.embed_text("search the web for news")
hits = await store.vector_search(query_vec, node_types=[NodeType.TOOL], top_k=5)

# Use with GraphExecutor for semantic context seeding and ranking
from yggdrasil import GraphExecutor
executor = GraphExecutor(store, embedder=embedder)
```

**Model selection**

```bash
# Via env var (applied at import time)
EMBED_MODEL=BAAI/bge-small-en-v1.5 python3 your_script.py

# Via constructor (takes precedence)
embedder = Embedder(model="BAAI/bge-small-en-v1.5")
```

---

## 12. Semantic Search

Two-stage tool → agent retrieval using weighted Reciprocal Rank Fusion (wRRF).

---

### RetrievalResult

```python
@dataclass
class RetrievalResult:
    agent:       AgentNode
    score:       float
    via_tools:   list[ToolNode]    # default: []
    tool_scores: list[float]       # default: []  — per-tool cosine scores
```

---

### semantic_search

```python
async def semantic_search(
    store:           GraphStore,
    query_embedding: list[float],
    top_k:           int = 5,
    top_k_tools:     int = 20,
    top_k_agents:    int = 10,
    w_tool:          float = 0.7,
    w_agent:         float = 0.3,
    k:               int = 60,
    query_tags:      list[str] | None = None,
    tag_weight:      float = 0.1,
) -> list[RetrievalResult]
```

| Parameter | Description |
|---|---|
| `store` | Graph store to search |
| `query_embedding` | Dense query vector from `Embedder.embed_text()` |
| `top_k` | Final number of agent candidates to return |
| `top_k_tools` | Breadth of tool vector search before walking upstream |
| `top_k_agents` | Breadth of direct agent vector search |
| `w_tool` | Weight for tool-driven score (default `0.7`) |
| `w_agent` | Weight for direct agent score (default `0.3`) |
| `k` | RRF smoothing constant (standard: `60`) |
| `query_tags` | Optional concept tags for structured overlap bonus |
| `tag_weight` | Score bonus per matching tag |

**Scoring formula**
```
tool_score  = w_tool  × cosine(query, tool)  × edge_weight / (rank + k)
agent_score = w_agent × cosine(query, agent)               / (rank + k)
tag_bonus   = len(tool.tags ∩ query_tags) × tag_weight
final_score = tool_score + agent_score + tag_bonus
```

`edge_weight` is the `HAS_TOOL` edge weight set by `attach_tool()` — tools structurally central to their agent receive a prior boost independent of query-time cosine.

**Algorithm**

1. Vector search `ToolNode`s and `AgentNode`s in parallel.
2. Walk `HAS_TOOL` edges upstream from tool hits to find parent `AgentNode`s (capture `edge.weight`).
3. Fuse scores using the formula above.
4. Return top `k` by `final_score`.

**Tutorial**

```python
from yggdrasil_lm.retrieval.embedder import Embedder
from yggdrasil_lm.retrieval.wrrf import semantic_search
from yggdrasil import GraphExecutor
from yggdrasil_lm.core.nodes import NodeType

embedder = Embedder()

# Step 1: embed everything first
await embedder.embed_all(store, node_types=[NodeType.TOOL, NodeType.AGENT])

# Step 2: embed the user query
query_vec = await embedder.embed_text("execute and test Python code")

# Step 3: find the best agent
results = await semantic_search(
    store,
    query_vec,
    top_k=3,
    query_tags=["code_execution"],
    tag_weight=0.15,
)

for r in results:
    print(f"{r.agent.name}  score={r.score:.4f}  via={[t.name for t in r.via_tools]}")

# Step 4: run with the best match
best = results[0].agent
ctx = await GraphExecutor(store, embedder=embedder).run(best.node_id, "run my test suite")
```

---

## 13. Tool Registry

---

### ToolRegistry

Maps `callable_ref` strings to Python callables. Decouples the graph schema from the implementation.

```python
class ToolRegistry:
    def __init__(self) -> None
```

**Methods**

```python
    def register(callable_ref: str, fn: Callable) -> None
    # Register fn under the given dotted ref.

    def tool(callable_ref: str) -> Callable
    # Decorator — registers the decorated function under callable_ref.

    def get(callable_ref: str) -> Callable | None
    # Return the callable or None if not registered.

    def load(callable_ref: str) -> Callable
    # Import callable_ref as a dotted module path and register it.
    # Raises ImportError if the path is invalid.

    def attach(executor: GraphExecutor) -> None
    # Register all tools in this registry with a GraphExecutor.

    def items() -> Iterable[tuple[str, Callable]]
    # Iterate (callable_ref, fn) pairs.

    def __contains__(ref: str) -> bool
    def __len__() -> int
```

**Tutorial**

```python
from yggdrasil_lm.tools.registry import ToolRegistry, default_registry
from yggdrasil import GraphExecutor, ToolNode

# Option 1: decorator on default_registry
@default_registry.tool("myapp.tools.summarise")
async def summarise(input: dict) -> str:
    return input.get("text", "")[:200]

# Option 2: explicit registration on a custom registry
registry = ToolRegistry()
registry.register("myapp.tools.search", my_search_fn)
registry.attach(executor)    # push all to executor

# Option 3: load from dotted path (imports module at call time)
registry.load("myapp.tools.search")

# Check registration
print("myapp.tools.search" in registry)   # True
print(len(registry))                      # number of registered tools

# Tool callable signature — always receives a single dict
async def my_tool(input: dict) -> str:
    query = input["query"]
    # ... do work ...
    return result
```

The `ToolNode.callable_ref` must exactly match the string used in `registry.register()` or `@registry.tool()`.

---

### default_registry

Global singleton `ToolRegistry` instance pre-loaded with the three built-in tools. Attach it to any executor:

```python
from yggdrasil_lm.tools.registry import default_registry

default_registry.attach(executor)
```

---

### Built-in Tools

#### `web_search`

```
callable_ref: "yggdrasil.tools.web_search.search"
```

```python
async def web_search(input: dict) -> str
# input: {"query": str, "num_results": int = 5}
# Uses DuckDuckGo Lite HTML — no API key required.
# Returns formatted string of search results or an error message.
```

#### `run_python`

```
callable_ref: "yggdrasil.tools.code_exec.run_python"
```

```python
async def run_python(input: dict) -> str
# input: {"code": str, "timeout": int = 10}
# Executes code in a subprocess. Returns stdout + stderr.
# WARNING: Only use in trusted / sandboxed environments.
```

#### `echo`

```
callable_ref: "yggdrasil.tools.echo.echo"
```

```python
async def echo(input: dict) -> str
# input: any dict
# Returns a formatted echo of its input. Useful for testing.
```

---

## 14. End-to-End Tutorial

Putting it all together: a two-agent research pipeline with semantic entry-point discovery.

```python
import asyncio
from yggdrasil import AgentNode, ToolNode, ContextNode, Edge, NetworkXGraphStore, GraphExecutor
from yggdrasil_lm.core.nodes import PromptNode, NodeType
from yggdrasil_lm.retrieval.embedder import Embedder
from yggdrasil_lm.retrieval.wrrf import semantic_search
from yggdrasil_lm.tools.registry import default_registry

async def main():
    store = NetworkXGraphStore()

    # 1. Build nodes
    search_tool = ToolNode(
        name="web_search",
        description="Search the web for current information",
        callable_ref="yggdrasil.tools.web_search.search",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        tags=["web", "search"],
    )

    researcher = AgentNode(
        name="Researcher",
        description="Finds factual information using web search",
        system_prompt="You are a technical researcher. Use web_search for every claim.",
        max_iterations=3,
        routing_table={"default": "__END__"},
    )

    synthesizer = AgentNode(
        name="Synthesizer",
        description="Synthesises raw research into a clear report",
        system_prompt="You write clear, structured technical reports.",
        routing_table={"default": "__END__"},
    )

    context = ContextNode(
        name="Output Format",
        content="Always respond in Markdown with a summary, findings, and sources section.",
        priority=1,
    )

    prompt = PromptNode(
        name="SynthPrompt",
        template="You are a {{ role }}. {{ instruction }}",
        variables=["role", "instruction"],
    )

    # 2. Store everything
    for n in [search_tool, researcher, synthesizer, context, prompt]:
        await store.upsert_node(n)

    # 3. Wire the graph
    await store.upsert_edge(Edge.has_tool(researcher.node_id, search_tool.node_id))
    await store.upsert_edge(Edge.has_context(synthesizer.node_id, context.node_id))
    await store.upsert_edge(Edge.has_prompt(synthesizer.node_id, prompt.node_id))
    await store.upsert_edge(Edge.delegates_to(researcher.node_id, synthesizer.node_id))

    # 4. Embed nodes for semantic search
    embedder = Embedder()
    await embedder.embed_all(store, node_types=[NodeType.TOOL, NodeType.AGENT])

    # 5. Discover the entry agent from the query
    query = "What are the major changes in Python 3.13?"
    query_vec = await embedder.embed_text(query)
    results = await semantic_search(store, query_vec, top_k=1)
    entry = results[0].agent
    print(f"Routing to: {entry.name}")   # → "Researcher"

    # 6. Execute
    executor = GraphExecutor(store, embedder=embedder)
    default_registry.attach(executor)

    ctx = await executor.run(entry.node_id, query, strategy="sequential")

    # 7. Inspect results
    print(ctx.outputs[synthesizer.node_id]["text"])
    print(f"\nHops: {ctx.hop_count}")
    for step in ctx.trace:
        print(f"  [{step.event_type}] {step.node_name}")

asyncio.run(main())
```

---

## 15. Claude Code Backend

`ClaudeCodeExecutor` is a `GraphExecutor` subclass that drives each `AgentNode` as a full autonomous Claude Code sub-agent via the [`claude-agent-sdk`](https://pypi.org/project/claude-agent-sdk/). All graph traversal, routing, context composition, and `ToolNode` bridging work identically to `GraphExecutor` — only `_execute_agent` is replaced.

**Installation:**

```bash
pip install 'yggdrasil[claude-code]'
```

---

### ClaudeCodeExecutor

```python
from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

ClaudeCodeExecutor(
    store:              GraphStore,
    composer:           AgentComposer | None = None,
    embedder:           Any = None,
    allowed_tools:      list[str] | None = None,
    extra_mcp_servers:  dict | None = None,
    permission_mode:    str = "default",
    max_budget_usd:     float | None = None,
    cwd:                str | None = None,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `store` | `GraphStore` | — | Graph store instance. |
| `composer` | `AgentComposer \| None` | `None` | Custom composer; auto-created if `None`. |
| `embedder` | `Any` | `None` | Optional `Embedder` for semantic context seeding and ranking. |
| `allowed_tools` | `list[str] \| None` | `["Read","Glob","Grep","Bash","WebSearch"]` | Claude Code built-in tools available to sub-agents. |
| `extra_mcp_servers` | `dict \| None` | `None` | Additional MCP servers merged into every sub-agent invocation. Supports stdio/http format dicts or SDK server objects. |
| `permission_mode` | `str` | `"default"` | How the sub-agent handles permission prompts. One of `"default"`, `"acceptEdits"`, `"bypassPermissions"`. |
| `max_budget_usd` | `float \| None` | `None` | Optional per-invocation USD cost cap. |
| `cwd` | `str \| None` | `None` | Working directory for file operations. |

**Methods:**

`ClaudeCodeExecutor` inherits all methods from `GraphExecutor` (`.run()`, `.plan()`, `.execute()`, `.register_tool()`, etc.) and overrides:

#### `route(query, candidates=None) → RoutingDecision`

Lazily initialises a lightweight `AnthropicBackend` the first time routing is needed (since `ClaudeCodeExecutor` does not use `self._backend` for agent execution — the Claude Code SDK owns that loop). Subsequent routing calls reuse the same backend instance.

```python
# Works identically to GraphExecutor.route() — extra backend init is transparent
decision = await executor.plan("translate this Catala blueprint into Jsonnet rules")
print(decision.agent_id)    # "blueprint-translator"
print(decision.reason)      # "Task requires parsing a Catala file and generating rules"
```

The executor also adds:

#### `register_tool(callable_ref, fn)`

Register a Python callable for a `ToolNode`. The `callable_ref` must match `ToolNode.callable_ref` exactly.

```python
async def my_search(args: dict) -> str:
    return requests.get(f"https://api.example.com?q={args['query']}").text

executor.register_tool("myapp.tools.my_search", my_search)
```

#### `_run_with_query(prompt, options) → str` *(internal)*

Used when no `ToolNode`s are bridged. Calls the Agent SDK `query()` function and returns the final `ResultMessage.result`.

#### `_run_with_sdk_client(prompt, options) → str` *(internal)*

Used when `ToolNode`s are bridged as an in-process MCP server. Uses `ClaudeSDKClient` which supports in-process MCP servers (unlike `query()`). Collects all `AssistantMessage / TextBlock` output and joins them with newlines.

---

**Execution paths:**

```
_execute_agent()
    │
    ├── compose agent (fetch HAS_CONTEXT, HAS_TOOL, HAS_PROMPT edges)
    ├── build_system_prompt()
    ├── _build_mcp_server()   ──→ None (no tools registered)
    │                         ──→ sdk_mcp_server (tools bridged)
    │
    ├── if no MCP server  →  _run_with_query()        (lighter path)
    └── if MCP server     →  _run_with_sdk_client()   (full client required)
```

---

**Example — minimal usage:**

```python
import asyncio
from yggdrasil import AgentNode, NetworkXGraphStore
from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

async def main():
    store = NetworkXGraphStore()

    agent = AgentNode(
        name="Coder",
        system_prompt="You are an expert Python developer.",
        max_iterations=10,
        routing_table={"default": "__END__"},
    )
    await store.upsert_node(agent)

    executor = ClaudeCodeExecutor(
        store,
        allowed_tools=["Read", "Glob", "Grep", "Bash"],
        permission_mode="acceptEdits",
        cwd="/path/to/project",
    )

    ctx = await executor.run(agent.node_id, "Add type annotations to all functions in utils.py")
    print(ctx.outputs[agent.node_id]["text"])

asyncio.run(main())
```

**Example — bridging `ToolNode`s:**

```python
import asyncio
import httpx
from yggdrasil import AgentNode, ToolNode, Edge, NetworkXGraphStore
from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

async def main():
    store = NetworkXGraphStore()

    search_tool = ToolNode(
        name="web_search",
        description="Search the web for a query",
        callable_ref="myapp.tools.web_search",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        is_async=True,
    )

    agent = AgentNode(
        name="Researcher",
        system_prompt="You research topics thoroughly.",
        routing_table={"default": "__END__"},
    )

    await store.upsert_node(search_tool)
    await store.upsert_node(agent)
    await store.upsert_edge(Edge.has_tool(agent.node_id, search_tool.node_id))

    async def web_search(args: dict) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.search.example.com", params={"q": args["query"]})
            return r.text

    executor = ClaudeCodeExecutor(store)
    executor.register_tool("myapp.tools.web_search", web_search)

    ctx = await executor.run(agent.node_id, "What are the highlights of Python 3.13?")
    print(ctx.outputs[agent.node_id]["text"])

asyncio.run(main())
```

**Example — extra MCP servers (Playwright browser):**

```python
executor = ClaudeCodeExecutor(
    store,
    allowed_tools=["Read", "Glob", "Bash"],
    extra_mcp_servers={
        "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
    },
)
```

---

## 16. OpenTelemetry Exporter

Converts an `ExecutionContext` trace into [OpenTelemetry](https://opentelemetry.io/) spans and exports them to any OTLP-compatible backend (Datadog, Signoz, Grafana Tempo, Honeycomb, Jaeger, …).

**Requires:** `pip install 'yggdrasil[observe]'`

---

### export_trace

```python
from yggdrasil_lm.exporters.otel import export_trace

def export_trace(
    ctx:          ExecutionContext,
    tracer:       Any = None,
    service_name: str = "yggdrasil",
) -> None:
```

Exports an `ExecutionContext` trace as a set of nested OTel spans.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ctx` | `ExecutionContext` | required | The context returned by `executor.run()` |
| `tracer` | `opentelemetry.trace.Tracer \| None` | `None` | OTel Tracer instance. When `None`, uses the globally-configured `TracerProvider`. |
| `service_name` | `str` | `"yggdrasil"` | Overrides the `service.name` resource attribute |

**Behaviour**

- No-op (prints a warning to stderr) when `opentelemetry-sdk` is not installed.
- Derives a stable 128-bit OTel `trace_id` from `ctx.session_id` so all spans in a run share the same trace.
- Derives 64-bit `span_id`s deterministically from each `TraceEvent.event_id`.

**Span hierarchy**

```
hop N — <AgentName>          ← root span; one per traversal hop
  agent: <AgentName>         ← child span covering full agent execution
    tool: <ToolName>         ← grandchild span per tool invocation
    [event] context_inject   ← OTel Event on agent span
    [event] routing          ← OTel Event on agent span
```

**Span attributes**

*Hop span*

| Attribute | Description |
|---|---|
| `yggdrasil.hop` | Hop number |
| `yggdrasil.node_type` | Python class of the node |
| `yggdrasil.node_name` | Node display name |
| `yggdrasil.session_id` | Session UUID |
| `yggdrasil.query` | Original query string |
| `yggdrasil.summary` | Hop summary (truncated at 500 chars) |

*Agent span*

| Attribute | Description |
|---|---|
| `yggdrasil.agent.name` | Agent name |
| `yggdrasil.agent.model` | LLM model string |
| `yggdrasil.agent.tools` | JSON array of tool names |
| `yggdrasil.agent.context` | JSON array of context node names |
| `yggdrasil.agent.query` | Query passed to the agent (truncated at 500 chars) |
| `yggdrasil.agent.intent` | Routing intent from `agent_end` event |
| `yggdrasil.agent.iterations` | Tool-use loop iteration count |
| `yggdrasil.agent.summary` | Text summary from `agent_end` (truncated at 500 chars) |
| `llm.system` / `gen_ai.system` | `"anthropic"` (OTel semantic conventions) |
| `llm.request.model` / `gen_ai.request.model` | Model ID |

*Tool span*

| Attribute | Description |
|---|---|
| `yggdrasil.tool.name` | Tool name |
| `yggdrasil.tool.callable_ref` | `callable_ref` string from `ToolNode` |
| `yggdrasil.tool.input` | JSON-serialised tool input (truncated at 1 000 chars) |
| `yggdrasil.tool.output_summary` | Output summary from `tool_result` (truncated at 500 chars) |
| `yggdrasil.tool.success` | Boolean; span status set to `ERROR` on failure |

*OTel Events on agent span*

| Event name | Attribute keys |
|---|---|
| `context_inject` | `context.names` (JSON array), `context.count` |
| `routing` | `routing.intent`, `routing.next_node_id`, `routing.confidence` (optional) |

**Tutorial**

```python
# 1. Configure a backend once at startup (example: local Jaeger / Tempo)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
))
trace.set_tracer_provider(provider)

# 2. Export after every run — same call regardless of backend
from yggdrasil_lm.exporters.otel import export_trace

ctx = await executor.run(entry.node_id, "analyse the codebase")
export_trace(ctx)
```

```python
# Datadog (requires OTLP receiver enabled in the DD Agent)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4317")
))
```

```python
# Signoz cloud
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="https://ingest.signoz.io:443/v1/traces",
        headers={"signoz-access-token": "<token>"},
    )
))
```

```python
# Honeycomb
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="https://api.honeycomb.io/v1/traces",
        headers={
            "x-honeycomb-team": "<api-key>",
            "x-honeycomb-dataset": "yggdrasil",
        },
    )
))
```

```python
# Pass a specific tracer (optional — useful in test environments)
import opentelemetry.trace as otel_trace
my_tracer = otel_trace.get_tracer("my-service")
export_trace(ctx, tracer=my_tracer)
```

---

## 17. Trace Visualizer

The trace visualizer opens a browser tab showing a live or post-run view of an execution trace. It requires no sign-up, cloud account, or API key.

**Installation:**

```bash
pip install 'yggdrasil[viz]'
```

---

### serve_trace

Post-run entry point. Opens a browser tab showing the full trace after a run completes.

```python
from yggdrasil_lm.viz import serve_trace

async def serve_trace(
    ctx:          ExecutionContext,
    *,
    store:        GraphStore | None = None,
    port:         int = 7331,
    open_browser: bool = True,
    wait:         bool = True,
    wait_seconds: int = 0,
) -> None
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ctx` | `ExecutionContext` | required | Context returned by `executor.run()` |
| `store` | `GraphStore \| None` | `None` | When provided, also renders the graph topology panel |
| `port` | `int` | `7331` | Local port to bind |
| `open_browser` | `bool` | `True` | Open the default browser automatically |
| `wait` | `bool` | `True` | Block until Ctrl-C. Set `False` in scripts. |
| `wait_seconds` | `int` | `0` | Auto-stop after N seconds (only when `wait=True` and `> 0`) |

**Tutorial**

```python
import asyncio
from yggdrasil import GraphExecutor, NetworkXGraphStore
from yggdrasil_lm.viz import serve_trace

async def main():
    store = NetworkXGraphStore()
    # ... build graph ...
    executor = GraphExecutor(store)

    ctx = await executor.run(agent.node_id, "analyse the codebase")

    # Open browser and block until Ctrl-C
    await serve_trace(ctx, store=store)

    # Non-blocking (caller manages lifetime)
    await serve_trace(ctx, wait=False)

asyncio.run(main())
```

---

### live_trace

Async context manager. Starts the visualizer before a run so events stream in real-time.

```python
from yggdrasil_lm.viz import live_trace

class live_trace:
    def __init__(
        self,
        executor:     GraphExecutor,
        *,
        port:         int = 7331,
        open_browser: bool = True,
        wait:         bool = True,
        wait_seconds: int = 0,
    ) -> None
```

**Parameters** — same semantics as `serve_trace`.

**Returns** a `_LiveTraceCtx` context object inside the `async with` block. The `executor.run()` method is automatically patched to stream events and finalize the snapshot.

**Properties on the context object**

| Property | Type | Description |
|---|---|---|
| `url` | `str` | URL of the running visualizer (e.g. `http://127.0.0.1:7331`) |

**Tutorial**

```python
import asyncio
from yggdrasil import GraphExecutor, NetworkXGraphStore
from yggdrasil_lm.viz import live_trace

async def main():
    executor = GraphExecutor(store)

    async with live_trace(executor) as viz:
        print(f"Visualizer at {viz.url}")
        ctx = await executor.run(agent.node_id, "my query")
    # Browser stays open after the run; Ctrl-C to exit

asyncio.run(main())
```

---

### VizServer

Low-level server class for custom integration. Use `serve_trace()` or `live_trace()` for the common cases.

```python
from yggdrasil_lm.viz.server import VizServer

class VizServer:
    def __init__(self, port: int = 7331, open_browser: bool = True) -> None
```

**Lifecycle**

```python
server = VizServer(port=7331)
await server.start()          # bind uvicorn in a daemon thread
server.launch_browser()       # open system browser (called automatically if open_browser=True)
server.set_metadata(session_id="...", query="...")  # set session context
server.attach_store(store)    # enable graph topology panel
server.push_event(event, ctx) # called by the GraphExecutor event hook
await server.finalize(ctx)    # send full trace snapshot once run completes
await server.stop()           # signal uvicorn to shut down
```

**Methods**

| Method | Signature | Description |
|---|---|---|
| `start` | `async () -> None` | Start uvicorn in a daemon thread |
| `stop` | `async () -> None` | Signal server to shut down |
| `launch_browser` | `() -> None` | Open system browser to `http://127.0.0.1:{port}` |
| `set_metadata` | `(*, session_id, query) -> None` | Broadcast session/query metadata to connected browsers |
| `attach_store` | `(store) -> None` | Attach a `GraphStore` for the topology panel |
| `refresh_graph_state` | `() -> None` | Trigger an async graph snapshot refresh |
| `push_event` | `(event, ctx) -> None` | Sync hook: broadcast one `TraceEvent` to connected browsers |
| `push_event_async` | `async (event, ctx) -> None` | Async variant of `push_event` |
| `finalize` | `async (ctx, store=None) -> None` | Send full trace snapshot; marks run complete |

---

### HTTP and WebSocket API

The visualizer exposes a small HTTP API on `http://127.0.0.1:{port}`.

#### `GET /`

Returns the single-page HTML application.

**Response:** `text/html`

---

#### `GET /health`

Liveness check.

**Response:** `application/json`

```json
{"status": "ok"}
```

---

#### `POST /explain`

Returns a structured `RunExplanation` for the active session.

**Request body:** `application/json`

```json
{"session_id": "<optional — if provided, must match active session>"}
```

**Response:** `application/json` — a serialized `RunExplanation` object.

**Error responses:**

| Status | Body | Condition |
|---|---|---|
| `404` | `{"error": "session_id '...' not found; active session is '...'"}` | `session_id` mismatch |
| `404` | `{"error": "No explanation available yet; run has not been finalized"}` | Run not yet complete |

---

#### `WebSocket /ws`

Real-time event stream. Connect before or after the run starts — late-joining clients receive a full replay of all buffered events.

**Message format:** Each message is a JSON object with a `type` field:

| `type` | Description |
|---|---|
| `"meta"` | `{"type": "meta", "data": {"session_id": "...", "query": "..."}}` — session context |
| `"summary"` | `{"type": "summary", "data": {...}}` — live execution summary (see below) |
| `"event"` | `{"type": "event", "data": <TraceEvent dict>}` — one trace event |
| `"graph_state"` | `{"type": "graph_state", "data": {...}}` — full graph topology snapshot |
| `"finalize"` | `{"type": "finalize", "data": {...}}` — full trace snapshot once complete |

**Summary object fields:**

| Field | Type | Description |
|---|---|---|
| `status` | `str` | `"waiting"`, `"running"`, `"paused"`, `"completed"`, `"completed_with_issues"`, or `"error"` |
| `finalized` | `bool` | `True` after the run completes |
| `session_id` | `str` | Active session ID |
| `query` | `str` | Original query string |
| `current_node_id` | `str` | Node ID of the most recent event |
| `current_node_name` | `str` | Node name of the most recent event |
| `counts` | `dict[str, int]` | Event type → count |
| `event_count` | `int` | Total events emitted |
| `error_count` | `int` | Tool errors + validation failures + permission denials + fatal errors |
| `fatal_error_count` | `int` | `error`-type events only |
| `warning_count` | `int` | Low-confidence route count |
| `low_confidence_route_count` | `int` | Routes where `confidence < 0.7` |
| `pause_count` | `int` | Number of `pause` events |
| `approval_count` | `int` | Number of `approval_task` events |
| `checkpoint_count` | `int` | Number of `checkpoint` events |
| `runtime_event_count` | `int` | All pause/resume/retry/validation/checkpoint/approval events |
| `latest_pause` | `dict \| None` | Most recent `pause` event dict |
| `latest_approval_task` | `dict \| None` | Most recent `approval_task` event dict |
| `latest_permission_denied` | `dict \| None` | Most recent `permission_denied` event dict |
| `latest_checkpoint` | `dict \| None` | Most recent `checkpoint` event dict |

---

### TraceView

`TraceView` and `extract_trace_view` are internal implementation details used by
`explain_run(ctx)` and `inspect_trace(ctx)`. They are not part of the public API.

Use `explain_run(ctx)` to get a structured summary of a completed run.

---

