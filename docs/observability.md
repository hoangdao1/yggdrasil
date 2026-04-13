---
title: Observability
parent: Docs
nav_order: 6
---

# Observability

Yggdrasil emits a structured trace for every run. That trace makes the system easier to debug than a single opaque agent loop.

## Quick Mode Selector

Pick based on what you're trying to do:

| I want to...                            | Use                              | Returns       |
|-----------------------------------------|----------------------------------|---------------|
| Debug a run in the terminal (rich UI)   | `inspect_trace(ctx)`             | None (prints) |
| Debug a run in the terminal (plain CI)  | `print_trace(ctx)`               | None (prints) |
| Open an interactive browser view        | `await serve_trace(ctx, store=…)`| None (server) |
| Stream events live while a run executes | `async with live_trace(executor)`| None (server) |
| Get a structured summary of a run       | `explain_run(ctx)`               | `RunExplanation` |
| Export to Datadog / Jaeger / Honeycomb  | `export_trace(ctx.trace, …)`     | None (exports) |
| Access raw events directly              | `ctx.trace`                      | `list[TraceEvent]` |

Install extras first based on what you need:

```bash
pip install -e ".[dev]"   # for inspect_trace (Rich terminal UI)
pip install -e ".[viz]"   # for serve_trace and live_trace (browser UI)
pip install -e ".[observe]" # for export_trace (OpenTelemetry)
```

---

## Terminal Mode

Use terminal mode when you want a trace view without starting a server. No extra setup beyond the `dev` extra.

### inspect_trace — Rich tree UI

```python
from yggdrasil.trace_ui import inspect_trace

ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
inspect_trace(ctx)
```

What you get:
- Readable tree view grouped by hop
- Agent configs, context scores, tool inputs/outputs
- Routing decisions with confidence scores
- Timing and summary statistics panel

Options:

```python
# Compact mode — one-line summaries instead of full panels
inspect_trace(ctx, verbose=False)

# Export to file
inspect_trace(ctx, file="trace.html", format="html")
inspect_trace(ctx, file="trace.txt",  format="text")
```

Falls back to `print_trace()` automatically when `rich` is not installed.

### print_trace — Plain-text fallback

```python
from yggdrasil.trace_ui import print_trace

print_trace(ctx)
```

Use this for:
- CI logs
- Quick debugging
- Environments where Rich output is not wanted

No extra dependencies. Ships with the core package.

---

## Browser Mode

Use browser mode when you want an interactive UI with a graph store snapshot alongside the trace. Requires `pip install -e ".[viz]"`.

### serve_trace — Interactive post-run view

```python
from yggdrasil.viz import serve_trace

ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
await serve_trace(ctx, store=executor.store)
```

Opens `http://127.0.0.1:7331` in your default browser. Pass `store=executor.store` to include a live graph store snapshot next to the trace.

The browser UI lets you:
- Step through each hop and agent turn
- Inspect tool inputs and outputs
- See which context was selected and why
- Compare routing decisions with confidence scores
- View the graph store snapshot alongside the trace

### live_trace — Stream events during a run

```python
from yggdrasil.viz import live_trace

async with live_trace(executor) as viz:
    ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
```

Events stream into the browser in real time as the graph executes. Use this when you want to watch the run in progress rather than inspecting it after the fact.

---

## Data API

Use the data API when you want structured objects you can inspect, serialize, pass to dashboards, or build tooling on top of.

### explain_run — Summarize a completed run

```python
from yggdrasil.observability import explain_run

ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
summary = explain_run(ctx)
```

Returns a `RunExplanation` dataclass with:
- Hop order and per-hop summaries
- Routing decisions (intent, next node, confidence, mode)
- Selected context nodes and injection reasons
- Tool calls and their inputs
- Pause points and approval task details

Serialize to JSON:

```python
import dataclasses, json
print(json.dumps(dataclasses.asdict(summary), default=str))
```

---

## Raw Event Access

Because the trace is a plain list, you can inspect it directly:

```python
for event in ctx.trace:
    print(event.event_type, event.node_name, event.payload)
```

Common cases:
- Find which tools were called
- Inspect routing choices and confidence
- Review injected context
- Inspect pause tokens and resume points
- Audit retries and validation failures
- Build your own dashboards or exporters

`context_inject` events include richer context-navigation metadata:
- Ranked selected contexts
- Scores and source types (`attached`, `semantic`, `runtime`)
- Hop counts and traversal paths
- Ranking reasons

### Event types

Each `TraceEvent` has an `event_type` string. The most common types are:

- `agent_start`, `agent_end`
- `tool_call`, `tool_result`
- `routing`
- `context_inject`
- `hop`
- `subgraph_enter`, `subgraph_exit`
- `pause`, `resume`
- `retry`, `validation`
- `checkpoint`
- `approval_task`

---

## Export to OpenTelemetry

```bash
pip install -e ".[observe]"
```

```python
from yggdrasil.observability import export_trace

export_trace(ctx.trace, service_name="yggdrasil")
```

This lets you send execution data to systems like Datadog, Jaeger, SigNoz, and Honeycomb.

---

## Runtime Node Management

Tool results and generated context can become runtime nodes during execution:

```python
from yggdrasil import cleanup_session, get_runtime_nodes

runtime_nodes = await get_runtime_nodes(store, ctx.session_id)
await cleanup_session(store, ctx.session_id)
```

Use this when:
- You materialize per-run outputs into the graph
- You want to inspect artifacts from a session
- You want to remove temporary runtime state afterward

---

## What to Look at First

When debugging a failed or confusing run, check in this order:

1. Which `AgentNode` actually ran
2. Which tools were composed into that run
3. Which context nodes were injected
4. Why those context nodes were selected and what path surfaced them
5. Whether the model tried to call the expected tool
6. Which route was chosen next

---

## Related Docs

- [README](../README.md)
- [Start Here](start-here.md)
- [Visualizer Web UI](visualizer-web-ui.md)
- [Workflow patterns](workflow-patterns.md)
- [Advanced configuration](advanced-configuration.md)
- [Architecture](architecture.md)
- [API reference](../API_REFERENCE.md)
