# Why Behavior Changed

Use this workflow when a team asks:

- why did this route change?
- why did this tool disappear?
- why was this context selected now but not before?

`yggdrasil` is designed to answer those questions from run traces and structured observability output rather than ad hoc log reading.

## Explain One Run

Use `explain_run(ctx)` to get a structured summary of why a specific run behaved the way it did. It returns a typed `RunExplanation` — no terminal output, no server.

```python
from yggdrasil_lm.observability import explain_run

ctx = await executor.run(entry_node_id=agent.node_id, query="...")
summary = explain_run(ctx)
```

The run summary includes:

- hops, routing decisions, context injection, and tool calls
- approval task and pause details for human-in-the-loop workflows

Serialize to JSON for storage or dashboards:

```python
import dataclasses, json
print(json.dumps(dataclasses.asdict(summary), default=str))
```

## Then View It — Terminal Or Browser

Once you have the `ctx`, choose how to view the full event-by-event trace:

**Terminal (Rich tree UI):**

```python
from yggdrasil_lm.trace_ui import inspect_trace

inspect_trace(ctx)

# Export as a shareable artifact
inspect_trace(ctx, file="trace.html", format="html")
inspect_trace(ctx, file="trace.txt", format="text")
```

**Browser (interactive, with graph store snapshot):**

```python
from yggdrasil_lm.viz import serve_trace

await serve_trace(ctx, store=executor.store)
```

**Browser (live streaming during the run):**

```python
from yggdrasil_lm.viz import live_trace

async with live_trace(executor) as viz:
    ctx = await executor.run(entry_node_id=agent.node_id, query="...")
```

Use `inspect_trace(ctx)` when working in a terminal or exporting a shareable file. Use `serve_trace(ctx, store=executor.store)` when you want an interactive browser session with the graph store snapshot alongside the trace. `live_trace(executor)` is for watching a run in progress.

See [Observability](observability.md) for the full mode-selector and API reference.

## Understand Routing Decisions

The routing stack runs in this order:

1. `decision_table` — policy-driven routing (multi-condition rows)
2. `route_rules` — deterministic guardrails and pauses
3. LLM or keyword intent inference — interprets agent output
4. `routing_table` — maps intent to next node

`explain_run(ctx).routing` gives you the routing decision for each hop, including the mode (`decision_table`, `route_rules`, `intent`, or `default`) and which node was chosen.

## Practical Investigation Sequence

For a real incident or confusing run:

1. run `explain_run(ctx)` and check `routing` and `tool_calls`
2. use `inspect_trace(ctx)` or `serve_trace(ctx, store=executor.store)` to walk through the full event-by-event trace
3. compare `ctx.outputs` before and after the change to isolate the hop where behavior diverged

That sequence usually answers both:

- what the agent did
- why it chose that path

**Terminal view** — `inspect_trace(ctx)` from `yggdrasil.trace_ui`. Use when working in a terminal or exporting a shareable file.

**Browser view** — `serve_trace(ctx, store=executor.store)` from `yggdrasil.viz`. Use when you want an interactive browser session with the graph store snapshot alongside the trace.
