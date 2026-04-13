---
title: Advanced Configuration
parent: Docs
nav_order: 10
---

# Advanced Configuration

This page collects the setup choices that are useful after your first successful run.

## LLM Backends

Yggdrasil supports:

- `AnthropicBackend`
- `OpenAIBackend` for OpenAI-compatible APIs

### Anthropic

```python
from yggdrasil import GraphExecutor

executor = GraphExecutor(store)
```

This uses the default backend path, which expects `yggdrasil[anthropic]` to be installed and `ANTHROPIC_API_KEY` to be set.

Install:

```bash
pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...
```

### OpenAI API

```python
from yggdrasil import GraphExecutor, OpenAIBackend

executor = GraphExecutor(
    store,
    backend=OpenAIBackend(api_key="sk-..."),
)
```

Install:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY=sk-...
```

### Local OpenAI-Compatible Servers

Ollama example:

```python
from yggdrasil import GraphExecutor, OpenAIBackend

executor = GraphExecutor(
    store,
    backend=OpenAIBackend(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
)
```

## Neo4j Graph Store

If you want a production graph database instead of the in-memory `NetworkXGraphStore`, install the Neo4j extra:

```bash
pip install -e ".[neo4j]"
```

Then use `Neo4jGraphStore` from `yggdrasil.backends.neo4j`.

## Claude Code Backend

Install:

```bash
pip install -e ".[claude-code]"
```

This backend is useful when you want each graph hop to run as a Claude Code sub-agent rather than a direct API call.

See the API reference for the `ClaudeCodeExecutor` details:

- [API reference](../API_REFERENCE.md)

## Embeddings And Retrieval

Install the embeddings extra before using `sentence-transformers`-based retrieval:

```bash
pip install -e ".[embeddings]"
```

If you pass an embedder into `AgentComposer` or `GraphExecutor`, the default `ContextNavigator` can seed semantic candidates and score them alongside graph-native traversal signals instead of relying only on static edge weights.

This is useful when:

- many context nodes are attached to the same agent
- the most relevant context changes by query
- you want graph structure plus semantic ranking
- you want runtime-produced session context to participate in selection

You can also provide a custom `ContextNavigator` to tune:

- traversal depth
- context node and token budgets
- per-source diversity limits
- edge types used during expansion
- stale-fact filtering behavior

## Batch Execution

Use `BatchExecutor` when the same workflow should run over many inputs.

See:

- [Batch execution](batch-execution.md)
- [API reference](../API_REFERENCE.md)

## Workflow Controls

Yggdrasil supports a richer execution model for business workflows. The settings below are the ones most likely to matter once you move beyond simple agent chains.

### Execution Policies

`AgentNode` and `ToolNode` can carry an `execution_policy` with:

- `timeout_seconds`
- `retry_policy.max_attempts`
- `retry_policy.backoff_seconds`
- `retry_policy.backoff_multiplier`
- `idempotency_key`
- `transaction_boundary`

Use this when:

- a tool must be retried safely
- a step should fail fast
- duplicate requests must not execute the same side effect twice

### Deterministic Routing

`AgentNode.route_rules` and `decision_table` let you evaluate deterministic rules before LLM intent routing.

This is useful when:

- approvals must always route to a review node
- compliance branches must not depend on model phrasing
- workflow state should drive the next step directly
The routing stack runs in this order:

1. `decision_table`
2. `route_rules`
3. LLM or keyword intent inference
4. `routing_table`

That order matters. The earlier layers are more deterministic and policy-like. The later layers are more flexible.

#### Routing Layers

`decision_table`

- evaluates a table of multi-condition rows
- returns the first matching `DecisionRule`
- can be marked `strict=True` to force the table's default target when no row matches
- is the best fit for reviewable business policy and compliance routing

Use this when:

- routing depends on several conditions together
- the next step should be explainable as policy, not phrasing
- a team wants to code-review routing behavior over time

`route_rules`

- evaluates simpler deterministic rules in priority order
- is lighter-weight than a full decision table
- can pause execution on match with `pause_on_match=True`
- is a good fit for local overrides and workflow guardrails

Use this when:

- one condition should short-circuit normal routing
- a step should pause for input or approval before continuing
- you want a simple deterministic branch without building a full table

LLM or keyword intent inference

- runs only if no `decision_table` row or `route_rule` has already chosen a target
- interprets the agent output into an intent label such as `billing` or `technical`
- uses a cheap keyword pass first, then the backend when needed
- is the most flexible and least policy-stable layer

Use this when:

- the model output must be interpreted semantically
- exact workflow state does not already determine the next step
- routing should stay adaptive to natural-language results

`routing_table`

- maps an intent label to a target node id
- does not reason about the route by itself
- is the final dispatch map after an intent has been selected
- should usually include a `default` entry

Use this when:

- the intent names are already known
- different intents should fan out to different graph paths
- you want a stable contract between "intent classification" and "next node"

#### Mental Model

Think of the four layers like this:

- `decision_table` = policy table
- `route_rules` = deterministic guardrails
- intent inference = semantic interpretation
- `routing_table` = dispatch map

If a `decision_table` row matches, the executor does not continue to later routing layers. If no deterministic rule matches, the executor infers an intent and then looks it up in `routing_table`.

#### Example

```python
from yggdrasil import AgentNode, ConstraintRule, DecisionRule, DecisionTable, RouteRule

agent = AgentNode(
    name="SupportIntake",
    routing_table={
        "billing": "billing-agent-id",
        "technical": "technical-agent-id",
        "default": "__END__",
    },
    decision_table=DecisionTable(
        strict=False,
        rules=[
            DecisionRule(
                name="vip-billing-review",
                priority=100,
                target_node_id="senior-review-id",
                conditions=[
                    ConstraintRule(source="state", path="ticket.type", operator="equals", value="billing"),
                    ConstraintRule(source="state", path="ticket.priority", operator="equals", value="vip"),
                ],
            ),
        ],
    ),
    route_rules=[
        RouteRule(
            name="pause-for-missing-account-id",
            priority=50,
            source="state",
            path="ticket.account_id",
            operator="truthy",
            value=False,
            target_node_id="__END__",
            pause_on_match=True,
        )
    ],
)
```

How this executes:

- if the VIP billing row matches, route directly to `senior-review-id`
- otherwise, if the account id is missing, pause the workflow
- otherwise, infer an intent such as `billing`
- then look up that intent in `routing_table`

### Pause / Resume And Checkpoints

`ExecutionContext.state` carries workflow state and pause metadata.

Main APIs:

- `GraphExecutor.checkpoint_context(ctx)` to persist a resumable checkpoint
- `GraphExecutor.load_checkpoint(node_id)` to restore it
- `GraphExecutor.resume(...)` or `resume_from_checkpoint(...)` to continue execution
- `ApprovalNode` to create inbox-style approval tasks inside the runtime

This is useful for:

- human approvals
- external callbacks
- long-running cases that span multiple requests or workers

See also:

- [Long-running workflows](long-running-workflows.md)
- [Workflow patterns](workflow-patterns.md)

### Validation

The executor can validate:

- tool input against `ToolNode.input_schema`
- tool output against `ToolNode.output_schema`
- workflow state against `AgentNode.state_schema`
- additional contracts linked through `VALIDATES` edges
- workflow invariants through `AgentNode.constraint_rules`

Use `allowed_tools` on `ExecutionOptions` to restrict which tools may be called during a run.

### Event Hooks

`add_event_hook(fn)` subscribes to emitted `TraceEvent` objects during execution. Use it to feed external systems, trigger integrations, or build custom dashboards on top of trace data.

## Suggested Documentation Split

If you continue expanding the project docs, this split tends to work well:

- `README.md`: value proposition, install, first run
- `docs/start-here.md`: shortest guided learning path
- `docs/first-graph.md`: beginner tutorial
- `docs/choose-backend.md`: provider selection and setup
- `docs/workflow-patterns.md`: runnable orchestration examples
- `docs/observability.md`: traces, cleanup, export
- `API_REFERENCE.md`: exhaustive reference
- `COMPARISONS.md`: positioning against other frameworks

## Related Docs

- [README](../README.md)
- [Start Here](start-here.md)
- [Choose a Backend](choose-backend.md)
- [Workflow patterns](workflow-patterns.md)
- [Observability](observability.md)
- [API reference](../API_REFERENCE.md)
