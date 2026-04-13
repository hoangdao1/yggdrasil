---
title: Visualizer Web UI
parent: Docs
nav_order: 15
---

# Visualizer Web UI

Yggdrasil includes a local browser UI for inspecting execution traces.

Use it when you want:

- a live view of events while a graph is running
- a post-run browser view you can keep open while debugging
- a graph store snapshot alongside the trace

This UI is separate from `inspect_trace()`.

- `inspect_trace()` renders a rich terminal UI and can export HTML or text
- `yggdrasil.viz` runs a local FastAPI + WebSocket server and opens a browser tab

## Install

Install the visualizer extra:

```bash
pip install -e ".[viz]"
```

Or from Git:

```bash
pip install "yggdrasil[viz] @ git+https://github.com/hoangdao1/yggdrasil.git"
```

## Post-Run View

Use `serve_trace(...)` after a run has completed:

```python
from yggdrasil.viz import serve_trace

ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
await serve_trace(ctx, store=executor.store)
```

What this does:

- starts a local server on `http://127.0.0.1:7331`
- opens your browser by default
- sends the full trace to the page
- includes a graph store snapshot when you pass `store=...`

Useful options:

- `port=8080` to use a different local port
- `open_browser=False` to avoid auto-opening a tab
- `wait=False` to return immediately instead of blocking
- `wait_seconds=30` to auto-stop after a fixed time when `wait=True`

## Live Streaming During A Run

Use `live_trace(...)` when you want events to appear as execution progresses:

```python
from yggdrasil.viz import live_trace

async with live_trace(executor, port=7331, wait=False) as viz:
    ctx = await executor.run(entry_node_id=agent.node_id, query="hello")

print(viz.url)
```

`live_trace(...)` attaches the visualizer to the executor, streams events as they are emitted, and finalizes the session when the run completes.

When `wait=True`, the context manager keeps the server running until you stop it with `Ctrl-C`.

## What The Browser UI Shows

The current UI includes:

- a live event stream
- an event detail panel
- summary stats such as hops, events, agents, and tools
- a trace graph view
- a database/store view when a graph snapshot is available

The store view becomes much more useful when you pass the executor store into `serve_trace(...)` or use `live_trace(executor)`, which attaches the executor store automatically.

## Typical Debug Flow

Use this rough rule:

- use `print_trace()` for minimal logs
- use `inspect_trace()` for terminal-first debugging and exportable HTML/text
- use `yggdrasil.viz` for an interactive browser session

## Related APIs

- `yggdrasil.viz.serve_trace(...)`
- `yggdrasil.viz.live_trace(...)`
- `yggdrasil.trace_ui.inspect_trace(...)`
- `yggdrasil.trace_ui.print_trace(...)`
