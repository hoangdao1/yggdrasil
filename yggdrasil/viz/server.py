"""FastAPI + WebSocket server for the Yggdrasil browser trace visualizer.

Architecture:
- One FastAPI app, one WebSocket endpoint (/ws), one static HTML route (/)
- TraceEvents are pushed as JSON via WebSocket as they are emitted
- serve_trace() serializes ExecutionContext.trace and streams it post-run
- All state is scoped to a single VizServer instance (no global state)

Dependency: pip install 'yggdrasil[viz]'
"""

import asyncio
import json
import threading
import webbrowser
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any

from yggdrasil.core.edges import Edge
from yggdrasil.core.store import GraphStore
from yggdrasil.observability import explain_run

if TYPE_CHECKING:
    from yggdrasil.core.executor import ExecutionContext, TraceEvent


_STATIC_DIR = Path(__file__).parent / "static"

_RUNTIME_EVENT_TYPES = {
    "pause",
    "resume",
    "retry",
    "validation",
    "permission_denied",
    "checkpoint",
    "transaction",
    "approval_task",
    "lease",
    "schedule",
    "migration",
}


def _event_to_dict(event: "TraceEvent") -> dict[str, Any]:
    """Convert a TraceEvent dataclass to a JSON-serializable dict."""
    return {
        "event_type": event.event_type,
        "event_id": event.event_id,
        "parent_event_id": event.parent_event_id,
        "session_id": event.session_id,
        "node_id": event.node_id,
        "node_name": event.node_name,
        "timestamp": event.timestamp.isoformat(),
        "duration_ms": event.duration_ms,
        "payload": event.payload,
    }


def _node_to_dict(node: Any) -> dict[str, Any]:
    data = node.model_dump(mode="json")
    data["is_valid"] = node.is_valid
    return data


def _edge_to_dict(edge: Edge) -> dict[str, Any]:
    data = edge.model_dump(mode="json")
    data["is_valid"] = edge.is_valid
    return data


async def _store_to_snapshot(store: GraphStore) -> dict[str, Any]:
    nodes = [_node_to_dict(node) for node in await store.list_nodes(only_valid=False)]
    edges = [_edge_to_dict(edge) for edge in await store.list_edges(only_valid=False)]

    nodes_by_type: dict[str, list[dict[str, Any]]] = {}
    edges_by_type: dict[str, list[dict[str, Any]]] = {}
    active_node_count = 0
    active_edge_count = 0

    for node in nodes:
        node_type = str(node.get("node_type", "unknown"))
        nodes_by_type.setdefault(node_type, []).append(node)
        if node.get("is_valid"):
            active_node_count += 1

    for edge in edges:
        edge_type = str(edge.get("edge_type", "unknown"))
        edges_by_type.setdefault(edge_type, []).append(edge)
        if edge.get("is_valid"):
            active_edge_count += 1

    return {
        "summary": {
            "node_count": len(nodes),
            "active_node_count": active_node_count,
            "edge_count": len(edges),
            "active_edge_count": active_edge_count,
            "node_type_counts": {
                key: len(value) for key, value in sorted(nodes_by_type.items())
            },
            "edge_type_counts": {
                key: len(value) for key, value in sorted(edges_by_type.items())
            },
        },
        "nodes": nodes,
        "edges": edges,
        "nodes_by_type": {
            key: sorted(value, key=lambda item: (item.get("name", ""), item.get("node_id", "")))
            for key, value in sorted(nodes_by_type.items())
        },
        "edges_by_type": {
            key: sorted(value, key=lambda item: (item.get("src_id", ""), item.get("dst_id", "")))
            for key, value in sorted(edges_by_type.items())
        },
    }


def _latest_event(events: list[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    for event in reversed(events):
        if event.get("event_type") == event_type:
            return event
    return None


def _summarize_events(
    events: list[dict[str, Any]],
    *,
    session_id: str = "",
    query: str = "",
    finalized: bool = False,
    paused: bool = False,
) -> dict[str, Any]:
    counts = Counter(str(event.get("event_type", "unknown")) for event in events)
    tool_errors = [
        event for event in events
        if event.get("event_type") == "tool_result"
        and event.get("payload", {}).get("success") is False
    ]
    fatal_errors = [
        event for event in events
        if event.get("event_type") == "error"
    ]
    low_conf_routes = [
        event for event in events
        if event.get("event_type") == "routing"
        and isinstance(event.get("payload", {}).get("confidence"), (int, float))
        and float(event["payload"]["confidence"]) < 0.7
    ]
    validation_failures = [
        event for event in events
        if event.get("event_type") == "validation"
        and event.get("payload", {}).get("success") is False
    ]
    permission_denials = [event for event in events if event.get("event_type") == "permission_denied"]
    latest_pause = _latest_event(events, "pause")
    latest_approval = _latest_event(events, "approval_task")
    latest_permission = _latest_event(events, "permission_denied")
    latest_checkpoint = _latest_event(events, "checkpoint")
    runtime_events = [event for event in events if event.get("event_type") in _RUNTIME_EVENT_TYPES]

    current_node_id = ""
    current_node_name = ""
    if events:
        current_node_id = str(events[-1].get("node_id", ""))
        current_node_name = str(events[-1].get("node_name", ""))

    if paused:
        status = "paused"
    elif fatal_errors:
        status = "error"
    elif finalized and (tool_errors or validation_failures or permission_denials):
        status = "completed_with_issues"
    elif finalized:
        status = "completed"
    elif counts:
        status = "running"
    else:
        status = "waiting"

    return {
        "status": status,
        "finalized": finalized,
        "session_id": session_id,
        "query": query,
        "current_node_id": current_node_id,
        "current_node_name": current_node_name,
        "selected_event_id": events[-1].get("event_id") if events else None,
        "counts": dict(sorted(counts.items())),
        "event_count": len(events),
        "error_count": len(tool_errors) + len(validation_failures) + len(permission_denials) + len(fatal_errors),
        "fatal_error_count": len(fatal_errors),
        "warning_count": len(low_conf_routes),
        "low_confidence_route_count": len(low_conf_routes),
        "pause_count": counts.get("pause", 0),
        "approval_count": counts.get("approval_task", 0),
        "checkpoint_count": counts.get("checkpoint", 0),
        "schedule_count": counts.get("schedule", 0),
        "runtime_event_count": len(runtime_events),
        "latest_pause": latest_pause,
        "latest_approval_task": latest_approval,
        "latest_permission_denied": latest_permission,
        "latest_checkpoint": latest_checkpoint,
    }


def _ctx_summary(ctx: "ExecutionContext", *, finalized: bool = False) -> dict[str, Any]:
    return _summarize_events(
        [_event_to_dict(event) for event in ctx.trace],
        session_id=ctx.session_id,
        query=ctx.query,
        finalized=finalized,
        paused=ctx.is_paused(),
    )


class VizServer:
    """Self-contained visualizer server for a single execution session.

    Lifecycle:
        server = VizServer(port=7331)
        await server.start()          # starts uvicorn in a background thread
        server.open_browser()
        server.push_event(event)      # called by the event hook
        server.finalize(ctx)          # marks run complete, sends full snapshot
        await server.stop()
    """

    def __init__(self, port: int = 7331, open_browser: bool = True):
        self.port = port
        self.open_browser = open_browser
        self._app = None
        self._server = None
        self._thread: threading.Thread | None = None
        self._connections: list[Any] = []   # list of WebSocket connections
        self._loop: asyncio.AbstractEventLoop | None = None
        self._started = asyncio.Event()
        self._metadata: dict[str, Any] = {}
        self._summary: dict[str, Any] | None = None
        self._finalized_snapshot: dict[str, Any] | None = None
        self._event_log: list[dict[str, Any]] = []  # replay buffer for late-joining clients
        self._store: GraphStore | None = None
        self._graph_snapshot: dict[str, Any] | None = None
        self._graph_refresh_in_flight = False
        self._run_explanation: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Build the FastAPI app
    # ------------------------------------------------------------------

    def _build_app(self) -> Any:
        try:
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect
            from fastapi.responses import HTMLResponse
            from fastapi.staticfiles import StaticFiles
        except ImportError as e:
            raise ImportError(
                "FastAPI is required for the browser trace visualizer. "
                "Install it with: pip install 'yggdrasil[viz]'"
            ) from e

        app = FastAPI(title="Yggdrasil Trace Visualizer", docs_url=None, redoc_url=None)
        app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

        @app.get("/", response_class=HTMLResponse)
        async def index():
            html_path = _STATIC_DIR / "index.html"
            return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        @app.post("/explain")
        async def explain(body: dict[str, Any]):
            from fastapi.responses import JSONResponse
            session_id = body.get("session_id", "")
            stored_session = self._metadata.get("session_id", "")
            if session_id and stored_session and session_id != stored_session:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"session_id '{session_id}' not found; active session is '{stored_session}'"},
                )
            if self._run_explanation is None:
                return JSONResponse(
                    status_code=404,
                    content={"error": "No explanation available yet; run has not been finalized"},
                )
            return self._run_explanation

        @app.websocket("/ws")
        async def websocket_endpoint(ws: WebSocket):
            await ws.accept()
            self._connections.append(ws)
            # Send current state to late-joining browsers so they sync up
            if self._metadata:
                try:
                    await ws.send_json({"type": "meta", "data": self._metadata})
                except Exception:
                    pass
            if self._summary:
                try:
                    await ws.send_json({"type": "summary", "data": self._summary})
                except Exception:
                    pass
            # Replay any events emitted before this browser connected
            for event_msg in list(self._event_log):
                try:
                    await ws.send_json(event_msg)
                except Exception:
                    break
            if self._graph_snapshot:
                try:
                    await ws.send_json({"type": "graph_state", "data": self._graph_snapshot})
                except Exception:
                    pass
            if self._finalized_snapshot:
                try:
                    await ws.send_json({"type": "finalize", "data": self._finalized_snapshot})
                except Exception:
                    pass
            try:
                while True:
                    # Keep alive; client sends pings
                    await ws.receive_text()
            except WebSocketDisconnect:
                pass
            finally:
                if ws in self._connections:
                    self._connections.remove(ws)

        return app

    # ------------------------------------------------------------------
    # Start / stop
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the uvicorn server in a daemon thread."""
        try:
            import uvicorn
        except ImportError as e:
            raise ImportError(
                "uvicorn is required for the browser trace visualizer. "
                "Install it with: pip install 'yggdrasil[viz]'"
            ) from e

        self._app = self._build_app()

        config = uvicorn.Config(
            self._app,
            host="127.0.0.1",
            port=self.port,
            log_level="error",
            loop="asyncio",
        )
        self._server = uvicorn.Server(config)

        loop_ready = threading.Event()   # daemon loop is up; _loop is set
        bind_ready = threading.Event()   # uvicorn has bound to the port

        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Capture the daemon loop so push_event schedules on the right loop
            # (the one that owns the WebSocket connections).
            self._loop = loop
            loop_ready.set()

            async def _serve():
                # Start serving in the background so we can poll server.started
                # before signalling bind_ready.  ready.set() used to fire before
                # serve() even ran, leaving a race window where the browser
                # would try to connect before the socket was bound.
                serve_task = asyncio.create_task(self._server.serve())
                while not self._server.started:
                    await asyncio.sleep(0.01)
                bind_ready.set()
                await serve_task

            loop.run_until_complete(_serve())

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

        # Wait for the daemon loop to start, then for uvicorn to bind.
        loop_ready.wait(timeout=5.0)
        bind_ready.wait(timeout=5.0)

        if self.open_browser:
            self.launch_browser()

    async def stop(self) -> None:
        """Signal the server to shut down."""
        if self._server:
            self._server.should_exit = True

    def launch_browser(self) -> None:
        webbrowser.open(f"http://127.0.0.1:{self.port}")

    # ------------------------------------------------------------------
    # Event streaming
    # ------------------------------------------------------------------

    def set_metadata(self, *, session_id: str, query: str) -> None:
        self._metadata = {"session_id": session_id, "query": query}
        self._summary = _summarize_events(
            self._event_log_as_events(),
            session_id=session_id,
            query=query,
            finalized=False,
        )
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._broadcast({"type": "meta", "data": self._metadata}),
                self._loop,
            )
            if self._summary:
                asyncio.run_coroutine_threadsafe(
                    self._broadcast({"type": "summary", "data": self._summary}),
                    self._loop,
                )

    def attach_store(self, store: GraphStore) -> None:
        self._store = store
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._refresh_graph_snapshot(), self._loop)

    def refresh_graph_state(self) -> None:
        if self._store and self._loop and self._loop.is_running() and not self._graph_refresh_in_flight:
            asyncio.run_coroutine_threadsafe(self._refresh_graph_snapshot(), self._loop)

    def push_event(self, event: "TraceEvent", ctx: "ExecutionContext") -> None:
        """Sync entry point called by the GraphExecutor event hook."""
        msg = {"type": "event", "data": _event_to_dict(event)}
        self._event_log.append(msg)
        is_fatal = event.event_type == "error"
        self._summary = _ctx_summary(ctx, finalized=is_fatal)
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(msg), self._loop)
            if self._summary:
                asyncio.run_coroutine_threadsafe(
                    self._broadcast({"type": "summary", "data": self._summary}),
                    self._loop,
                )
            self.refresh_graph_state()
            if is_fatal:
                asyncio.run_coroutine_threadsafe(self.finalize(ctx), self._loop)

    async def push_event_async(self, event: "TraceEvent", ctx: "ExecutionContext") -> None:
        """Async variant (called when hook is awaited)."""
        msg = {"type": "event", "data": _event_to_dict(event)}
        self._event_log.append(msg)
        is_fatal = event.event_type == "error"
        self._summary = _ctx_summary(ctx, finalized=is_fatal)
        await self._broadcast(msg)
        if self._summary:
            await self._broadcast({"type": "summary", "data": self._summary})
        await self._refresh_graph_snapshot()
        if is_fatal:
            await self.finalize(ctx)

    async def finalize(self, ctx: "ExecutionContext", store: GraphStore | None = None) -> None:
        """Send the full trace snapshot once execution completes."""
        snapshot_store = store or self._store
        graph_state = await _store_to_snapshot(snapshot_store) if snapshot_store else None
        if graph_state is not None:
            self._graph_snapshot = graph_state
        import dataclasses as _dc
        self._run_explanation = _dc.asdict(explain_run(ctx))
        snapshot = {
            "session_id": ctx.session_id,
            "query": ctx.query,
            "hop_count": ctx.hop_count,
            "events": [_event_to_dict(e) for e in ctx.trace],
            "summary": _ctx_summary(ctx, finalized=True),
            "graph_state": graph_state,
        }
        self._summary = snapshot["summary"]
        self._finalized_snapshot = snapshot
        msg = {"type": "finalize", "data": snapshot}
        if self._loop and self._loop.is_running():
            # Called from the main event loop — schedule broadcast on the
            # server's own daemon loop to avoid cross-loop WebSocket issues.
            asyncio.run_coroutine_threadsafe(
                self._broadcast({"type": "summary", "data": self._summary}),
                self._loop,
            )
            asyncio.run_coroutine_threadsafe(self._broadcast(msg), self._loop)
            # Yield briefly so the daemon loop can process the broadcast.
            await asyncio.sleep(0.1)
        else:
            await self._broadcast({"type": "summary", "data": self._summary})
            await self._broadcast(msg)

    async def _refresh_graph_snapshot(self) -> None:
        if not self._store or self._graph_refresh_in_flight:
            return
        self._graph_refresh_in_flight = True
        try:
            snapshot = await _store_to_snapshot(self._store)
            self._graph_snapshot = snapshot
            await self._broadcast({"type": "graph_state", "data": snapshot})
        finally:
            self._graph_refresh_in_flight = False

    async def _broadcast(self, msg: dict[str, Any]) -> None:
        if not self._connections:
            return
        payload = json.dumps(msg, default=str)
        dead: list[Any] = []
        for ws in list(self._connections):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self._connections:
                self._connections.remove(ws)

    def _event_log_as_events(self) -> list[dict[str, Any]]:
        return [message["data"] for message in self._event_log if message.get("type") == "event"]


# ---------------------------------------------------------------------------
# serve_trace() — post-run entry point
# ---------------------------------------------------------------------------

async def serve_trace(
    ctx: "ExecutionContext",
    *,
    store: GraphStore | None = None,
    port: int = 7331,
    open_browser: bool = True,
    wait: bool = True,
    wait_seconds: int = 0,
) -> None:
    """Open a browser tab showing the full post-run trace.

    Args:
        ctx:          ExecutionContext returned by executor.run().
        port:         Local port to bind (default 7331).
        open_browser: Open the default browser automatically (default True).
        wait:         Block until Ctrl-C if True. Set to False in scripts.
        wait_seconds: If > 0 and wait=True, automatically stop after N seconds.

    Example:
        ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
        await serve_trace(ctx)
    """
    server = VizServer(port=port, open_browser=open_browser)
    await server.start()
    if store is not None:
        server.attach_store(store)
    server.set_metadata(session_id=ctx.session_id, query=ctx.query)
    await server.finalize(ctx, store=store)

    print(f"\nYggdrasil Trace Visualizer running at http://127.0.0.1:{port}")
    print("Press Ctrl-C to stop.\n")

    if wait:
        try:
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            else:
                await asyncio.Event().wait()   # block forever
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass

    await server.stop()


# ---------------------------------------------------------------------------
# live_trace() — context manager for streaming during execution
# ---------------------------------------------------------------------------

class _LiveTraceCtx:
    """Returned by live_trace() — attach the executor inside the 'async with' block."""

    def __init__(self, server: VizServer):
        self._server = server
        self._ctx: "ExecutionContext | None" = None

    def attach(self, executor: Any, ctx: "ExecutionContext") -> None:
        """Wire the executor's event hook to stream events via WebSocket."""
        self._ctx = ctx
        self._server.set_metadata(session_id=ctx.session_id, query=ctx.query)
        executor.add_event_hook(self._server.push_event)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._server.port}"


class live_trace:
    """Async context manager: start the visualizer, stream events during a run.

    Usage:
        async with live_trace(executor) as viz:
            ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
        # Browser tab stays open; press Ctrl-C to exit

    Or with custom port and no auto-wait:
        async with live_trace(executor, port=8080, wait=False) as viz:
            ctx = await executor.run(...)
        await serve_trace(ctx, port=8080, wait=True)
    """

    def __init__(
        self,
        executor: Any,
        *,
        port: int = 7331,
        open_browser: bool = True,
        wait: bool = True,
        wait_seconds: int = 0,
    ):
        self._executor = executor
        self._port = port
        self._open_browser = open_browser
        self._wait = wait
        self._wait_seconds = wait_seconds
        self._server: VizServer | None = None
        self._ctx_wrapper: _LiveTraceCtx | None = None

    async def __aenter__(self) -> _LiveTraceCtx:
        self._server = VizServer(port=self._port, open_browser=self._open_browser)
        await self._server.start()
        self._server.attach_store(self._executor.store)
        self._ctx_wrapper = _LiveTraceCtx(self._server)

        # Monkey-patch executor.run to auto-attach on first call
        _orig_run = self._executor.run
        _wrapper = self

        async def _patched_run(entry_node_id, query, **kwargs):
            ctx = await _orig_run(entry_node_id=entry_node_id, query=query, **kwargs)
            _wrapper._ctx_wrapper._ctx = ctx
            await _wrapper._server.finalize(ctx, store=_wrapper._executor.store)
            return ctx

        # Register event hook before run so live events stream
        self._executor.add_event_hook(self._server.push_event)
        self._executor._patched_run = _patched_run
        self._executor.run = _patched_run  # type: ignore[method-assign]
        self._executor._orig_run = _orig_run

        print(f"\nYggdrasil Trace Visualizer running at http://127.0.0.1:{self._port}")
        return self._ctx_wrapper

    async def __aexit__(self, *_) -> None:
        # Restore original run
        if hasattr(self._executor, "_orig_run"):
            self._executor.run = self._executor._orig_run

        if self._wait and self._server:
            print("Press Ctrl-C to stop the visualizer.\n")
            try:
                if self._wait_seconds > 0:
                    await asyncio.sleep(self._wait_seconds)
                else:
                    await asyncio.Event().wait()
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass
            await self._server.stop()
        # When wait=False the caller is responsible for keeping the process alive;
        # the uvicorn daemon thread stays running until the process exits.
