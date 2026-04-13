---
title: Explainable Systems
parent: Docs
nav_order: 11
---

# Explainable Agent Systems

`yggdrasil` makes agent runs explainable at run-time: after a run you can ask what happened, why routing chose a specific branch, which tools were called, and which context was injected.

## Run-Time Explainability

After running the system, use `explain_run(ctx)` to get a structured summary:

- which hop ran first?
- which tool was called?
- which context was injected and why?
- what route moved the workflow forward?

```python
from yggdrasil import explain_run

ctx = await executor.run(entry_node_id=agent.node_id, query="...")
summary = explain_run(ctx)
```

`explain_run(ctx)` returns a typed `RunExplanation` dataclass:

```python
print(summary.hop_count)
print(summary.summary.tool_call_count)
print(summary.routing)      # list[RunRoutingExplanation]
print(summary.tool_calls)   # list[RunToolCallExplanation]
print(summary.context)      # list of context injection details
```

Fields include:

- session id and query
- hop count and per-hop summaries
- routing decisions (intent, next node, confidence, mode)
- selected context nodes and injection reasons
- tool calls and their inputs
- pause points and approval tasks

Serialize to JSON:

```python
import dataclasses, json
print(json.dumps(dataclasses.asdict(summary), default=str))
```

## Routing Stack

Understanding the four routing layers helps interpret `explain_run` output:

1. `decision_table` — policy-driven routing (evaluates multi-condition rows)
2. `route_rules` — deterministic workflow shortcuts or pauses
3. LLM or keyword intent inference — interprets agent output into an intent label
4. `routing_table` — maps intent label to next node

In other words:

- `decision_table` explains policy-driven routing
- `route_rules` explain deterministic workflow shortcuts or pauses
- intent inference explains how the system interpreted the agent result
- `routing_table` explains why that interpreted intent led to a specific next node

This lets a team answer both:

- why did the system choose this branch?
- was that branch caused by policy, a deterministic rule, or model interpretation?

## Terminal And Browser Views

For event-by-event trace inspection beyond `explain_run`:

```python
from yggdrasil.trace_ui import inspect_trace, print_trace
from yggdrasil.viz import serve_trace

# Rich terminal tree
inspect_trace(ctx)

# Plain text (CI-friendly)
print_trace(ctx)

# Interactive browser UI
await serve_trace(ctx, store=executor.store)
```

## Why This Matters

Explainability is not only about model outputs.

For real agent systems, teams also need to explain:

- workflow transitions
- context selection
- routing behavior
- behavior changes over time

That is why `yggdrasil` focuses on graph-native explainability, not only prompt/response inspection.

## Related APIs

- `explain_run(ctx)` — returns `RunExplanation`
- `inspect_trace(ctx)` — Rich terminal tree view
- `print_trace(ctx)` — plain-text trace
- `serve_trace(ctx, store=...)` — interactive browser UI
- `export_trace(ctx.trace, ...)` — OpenTelemetry export

See also:

- [Observability](observability.md)
