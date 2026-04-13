"""Yggdrasil browser trace visualizer.

Self-hosted, offline browser UI for inspecting graph execution traces.
Runs as a local FastAPI + WebSocket server. No sign-up, no cloud, no API key.

Quick start (post-run):
    from yggdrasil.viz import serve_trace

    ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
    await serve_trace(ctx)   # opens http://127.0.0.1:7331 in your browser

Live streaming (events appear as the graph runs):
    from yggdrasil.viz import live_trace

    async with live_trace(executor) as viz:
        ctx = await executor.run(entry_node_id=agent.node_id, query="hello")

Install:
    pip install 'yggdrasil[viz]'
"""

from yggdrasil.viz.server import VizServer, live_trace, serve_trace

__all__ = ["serve_trace", "live_trace", "VizServer"]
