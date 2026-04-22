"""Tests for the yggdrasil.viz browser trace visualizer.

Uses ollama model: gemma4:26b (configured via OllamaBackend).
LLM calls are stubbed where possible; the viz layer is tested directly.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yggdrasil_lm.core.edges import Edge
from yggdrasil_lm.core.executor import ExecutionContext, TraceEvent
from yggdrasil_lm.core.nodes import AgentNode, ContextNode
from yggdrasil_lm.core.store import NetworkXGraphStore
from yggdrasil_lm.viz.server import VizServer, _event_to_dict, _store_to_snapshot, _summarize_events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(
    event_type: str = "agent_start",
    node_id: str = "node-1",
    node_name: str = "TestNode",
    session_id: str | None = None,
    payload: dict | None = None,
    parent_event_id: str | None = None,
    duration_ms: int | None = None,
) -> TraceEvent:
    return TraceEvent(
        event_type=event_type,
        session_id=session_id or str(uuid.uuid4()),
        node_id=node_id,
        node_name=node_name,
        timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        payload=payload or {},
        parent_event_id=parent_event_id,
        duration_ms=duration_ms,
    )


def _make_ctx(query: str = "test query", num_events: int = 0) -> ExecutionContext:
    session = str(uuid.uuid4())
    ctx = ExecutionContext(query=query, session_id=session)
    for i in range(num_events):
        ctx.trace.append(_make_event(session_id=session, node_id=f"node-{i}"))
    return ctx


# ---------------------------------------------------------------------------
# _event_to_dict
# ---------------------------------------------------------------------------

class TestEventToDict:
    def test_basic_fields_present(self):
        event = _make_event(
            event_type="agent_start",
            node_id="abc",
            node_name="MyAgent",
            payload={"model": "gemma4:26b", "tools": ["search"]},
        )
        d = _event_to_dict(event)
        assert d["event_type"] == "agent_start"
        assert d["node_id"] == "abc"
        assert d["node_name"] == "MyAgent"
        assert d["payload"] == {"model": "gemma4:26b", "tools": ["search"]}

    def test_timestamp_is_iso_string(self):
        event = _make_event()
        d = _event_to_dict(event)
        assert isinstance(d["timestamp"], str)
        assert "2025-01-01" in d["timestamp"]

    def test_optional_fields_none(self):
        event = _make_event()
        d = _event_to_dict(event)
        assert d["parent_event_id"] is None
        assert d["duration_ms"] is None

    def test_optional_fields_set(self):
        event = _make_event(parent_event_id="parent-123", duration_ms=42)
        d = _event_to_dict(event)
        assert d["parent_event_id"] == "parent-123"
        assert d["duration_ms"] == 42

    def test_event_id_present(self):
        event = _make_event()
        d = _event_to_dict(event)
        assert "event_id" in d
        assert isinstance(d["event_id"], str)

    def test_all_event_types(self):
        for et in ["agent_start", "agent_end", "tool_call", "tool_result", "routing",
                   "context_inject", "hop", "subgraph_enter", "subgraph_exit"]:
            d = _event_to_dict(_make_event(event_type=et))
            assert d["event_type"] == et


# ---------------------------------------------------------------------------
# VizServer — unit tests (no real HTTP server started)
# ---------------------------------------------------------------------------

class TestVizServerBroadcast:
    @pytest.mark.asyncio
    async def test_broadcast_skips_empty_connections(self):
        server = VizServer(port=19999, open_browser=False)
        # No connections — should not raise
        await server._broadcast({"type": "test"})

    @pytest.mark.asyncio
    async def test_broadcast_sends_json_to_connections(self):
        server = VizServer(port=19999, open_browser=False)
        ws = AsyncMock()
        server._connections.append(ws)

        msg = {"type": "event", "data": {"node_id": "n1"}}
        await server._broadcast(msg)

        ws.send_text.assert_called_once()
        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["type"] == "event"
        assert sent["data"]["node_id"] == "n1"

    @pytest.mark.asyncio
    async def test_broadcast_removes_dead_connections(self):
        server = VizServer(port=19999, open_browser=False)
        dead_ws = AsyncMock()
        dead_ws.send_text.side_effect = Exception("connection closed")
        server._connections.append(dead_ws)

        await server._broadcast({"type": "ping"})
        assert dead_ws not in server._connections

    @pytest.mark.asyncio
    async def test_broadcast_multiple_connections(self):
        server = VizServer(port=19999, open_browser=False)
        ws1, ws2 = AsyncMock(), AsyncMock()
        server._connections.extend([ws1, ws2])

        await server._broadcast({"type": "hop"})
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_continues_after_one_dead_connection(self):
        server = VizServer(port=19999, open_browser=False)
        dead_ws = AsyncMock()
        dead_ws.send_text.side_effect = Exception("gone")
        live_ws = AsyncMock()
        server._connections.extend([dead_ws, live_ws])

        await server._broadcast({"type": "event", "data": {}})
        live_ws.send_text.assert_called_once()
        assert dead_ws not in server._connections
        assert live_ws in server._connections


# ---------------------------------------------------------------------------
# VizServer — set_metadata
# ---------------------------------------------------------------------------

class TestVizServerMetadata:
    def test_set_metadata_stores_values(self):
        server = VizServer(port=19999, open_browser=False)
        server._loop = MagicMock()
        server._loop.is_running.return_value = False

        with patch("asyncio.run_coroutine_threadsafe"):
            server.set_metadata(session_id="sess-1", query="hello world")

        assert server._metadata["session_id"] == "sess-1"
        assert server._metadata["query"] == "hello world"

    def test_set_metadata_triggers_broadcast(self):
        server = VizServer(port=19999, open_browser=False)
        server._loop = MagicMock()
        server._loop.is_running.return_value = True

        with patch("asyncio.run_coroutine_threadsafe") as mock_rcts:
            server.set_metadata(session_id="s", query="q")
            assert mock_rcts.call_count == 2
            for call in mock_rcts.call_args_list:
                assert call[0][1] is server._loop
                call[0][0].close()


# ---------------------------------------------------------------------------
# VizServer — push_event (sync)
# ---------------------------------------------------------------------------

class TestVizServerPushEvent:
    def test_push_event_schedules_when_loop_running(self):
        server = VizServer(port=19999, open_browser=False)
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = True
        server._loop = mock_loop

        event = _make_event(event_type="tool_call", payload={"tool_name": "search"})
        ctx = _make_ctx()

        with patch("asyncio.run_coroutine_threadsafe") as mock_rcts:
            server.push_event(event, ctx)
            assert mock_rcts.call_count == 2
            for call in mock_rcts.call_args_list:
                assert call[0][1] is mock_loop
                call[0][0].close()

    def test_push_event_noop_when_loop_none(self):
        server = VizServer(port=19999, open_browser=False)
        server._loop = None
        event = _make_event()
        ctx = _make_ctx()
        # Should not raise
        with patch("asyncio.run_coroutine_threadsafe") as mock_rcts:
            server.push_event(event, ctx)
            mock_rcts.assert_not_called()

    def test_push_event_noop_when_loop_not_running(self):
        server = VizServer(port=19999, open_browser=False)
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False
        server._loop = mock_loop
        event = _make_event()
        ctx = _make_ctx()
        with patch("asyncio.run_coroutine_threadsafe") as mock_rcts:
            server.push_event(event, ctx)
            mock_rcts.assert_not_called()

    @pytest.mark.asyncio
    async def test_push_event_async_sends_message(self):
        server = VizServer(port=19999, open_browser=False)
        ws = AsyncMock()
        server._connections.append(ws)

        event = _make_event(event_type="routing", payload={"intent": "search"})
        ctx = _make_ctx()
        await server.push_event_async(event, ctx)

        calls = [json.loads(c[0][0]) for c in ws.send_text.call_args_list]
        assert calls[0]["type"] == "event"
        assert calls[0]["data"]["event_type"] == "routing"
        assert calls[1]["type"] == "summary"


class TestSummaryHelpers:
    def test_summarize_events_counts_runtime_and_errors(self):
        events = [
            _event_to_dict(_make_event(event_type="pause", payload={"reason": "waiting"})),
            _event_to_dict(_make_event(event_type="tool_result", payload={"success": False})),
            _event_to_dict(_make_event(event_type="routing", payload={"confidence": 0.4})),
        ]

        summary = _summarize_events(events, session_id="s1", query="hello", finalized=True, paused=True)

        assert summary["status"] == "paused"
        assert summary["error_count"] == 1
        assert summary["warning_count"] == 1
        assert summary["runtime_event_count"] == 1
        assert summary["counts"]["pause"] == 1


# ---------------------------------------------------------------------------
# VizServer — finalize
# ---------------------------------------------------------------------------

class TestVizServerFinalize:
    @pytest.mark.asyncio
    async def test_finalize_sends_snapshot(self):
        server = VizServer(port=19999, open_browser=False)
        ws = AsyncMock()
        server._connections.append(ws)

        ctx = _make_ctx(query="what is 2+2?", num_events=3)
        await server.finalize(ctx)

        sent_messages = [json.loads(c[0][0]) for c in ws.send_text.call_args_list]
        sent = sent_messages[-1]
        assert sent["type"] == "finalize"
        data = sent["data"]
        assert data["query"] == "what is 2+2?"
        assert data["session_id"] == ctx.session_id
        assert data["hop_count"] == 0
        assert len(data["events"]) == 3
        assert data["summary"]["event_count"] == 3

    @pytest.mark.asyncio
    async def test_finalize_no_connections_no_error(self):
        server = VizServer(port=19999, open_browser=False)
        ctx = _make_ctx()
        await server.finalize(ctx)  # should not raise

    @pytest.mark.asyncio
    async def test_finalize_stores_snapshot_for_late_joiners(self):
        """Regression: browser connecting after finalize must receive the snapshot."""
        server = VizServer(port=19999, open_browser=False)
        assert server._finalized_snapshot is None

        ctx = _make_ctx(query="late joiner test", num_events=2)
        await server.finalize(ctx)

        # Snapshot is now stored — a late-joining WebSocket can read it
        assert server._finalized_snapshot is not None
        assert server._finalized_snapshot["query"] == "late joiner test"
        assert len(server._finalized_snapshot["events"]) == 2

    @pytest.mark.asyncio
    async def test_finalize_events_are_serializable(self):
        server = VizServer(port=19999, open_browser=False)
        ws = AsyncMock()
        server._connections.append(ws)

        ctx = _make_ctx(num_events=2)
        ctx.trace[0].payload = {"tool_name": "search", "input": {"q": "ollama gemma4"}}
        ctx.trace[1].payload = {"output_summary": "found results", "success": True}
        await server.finalize(ctx)

        raw = ws.send_text.call_args[0][0]
        parsed = json.loads(raw)  # should not raise
        assert len(parsed["data"]["events"]) == 2

    @pytest.mark.asyncio
    async def test_finalize_includes_graph_state_when_store_provided(self):
        server = VizServer(port=19999, open_browser=False)
        ws = AsyncMock()
        server._connections.append(ws)

        store = NetworkXGraphStore()
        agent = AgentNode(name="Planner")
        context = ContextNode(name="Policy", content="policy text")
        await store.upsert_node(agent)
        await store.upsert_node(context)
        await store.upsert_edge(Edge.has_context(agent.node_id, context.node_id))

        ctx = _make_ctx(query="show db state")
        await server.finalize(ctx, store=store)

        sent = json.loads(ws.send_text.call_args_list[-1][0][0])
        graph_state = sent["data"]["graph_state"]
        assert graph_state["summary"]["node_count"] == 2
        assert graph_state["summary"]["edge_count"] == 1
        assert graph_state["summary"]["node_type_counts"]["agent"] == 1
        assert graph_state["summary"]["node_type_counts"]["context"] == 1
        assert graph_state["summary"]["edge_type_counts"]["HAS_CONTEXT"] == 1


# ---------------------------------------------------------------------------
# VizServer — websocket endpoint (send metadata on connect)
# ---------------------------------------------------------------------------

class TestVizServerWebSocketBehavior:
    @pytest.mark.asyncio
    async def test_connected_browser_receives_graph_state_snapshot(self):
        from fastapi import WebSocketDisconnect

        server = VizServer(port=19999, open_browser=False)
        store = NetworkXGraphStore()
        await store.upsert_node(AgentNode(name="Router"))
        server._graph_snapshot = await _store_to_snapshot(store)

        ws = AsyncMock()
        ws.receive_text.side_effect = WebSocketDisconnect()

        app = server._build_app()
        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        await ws_route.endpoint(ws)

        types_sent = [c[0][0]["type"] for c in ws.send_json.call_args_list]
        assert "graph_state" in types_sent

    @pytest.mark.asyncio
    async def test_connected_browser_receives_live_trace_event(self):
        from fastapi import WebSocketDisconnect

        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        ctx = _make_ctx()
        event = _make_event(event_type="tool_call", payload={"tool_name": "search"})
        release_connection = asyncio.Event()

        ws = AsyncMock()

        async def _receive_text():
            await release_connection.wait()
            raise WebSocketDisconnect()

        ws.receive_text.side_effect = _receive_text

        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        endpoint_task = asyncio.create_task(ws_route.endpoint(ws))
        await asyncio.sleep(0)

        await server.push_event_async(event, ctx)

        ws.accept.assert_called_once()
        messages = [json.loads(c[0][0]) for c in ws.send_text.call_args_list]

        assert messages[0]["type"] == "event"
        assert messages[0]["data"]["event_type"] == "tool_call"
        assert messages[0]["data"]["payload"] == {"tool_name": "search"}
        assert messages[1]["type"] == "summary"

        release_connection.set()
        await endpoint_task

    @pytest.mark.asyncio
    async def test_late_joining_browser_receives_buffered_trace_event(self):
        from fastapi import WebSocketDisconnect

        server = VizServer(port=19999, open_browser=False)
        ctx = _make_ctx()
        event = _make_event(event_type="tool_result", payload={"success": True})
        server.push_event(event, ctx)
        release_connection = asyncio.Event()
        ws = AsyncMock()

        async def _receive_text():
            await release_connection.wait()
            raise WebSocketDisconnect()

        ws.receive_text.side_effect = _receive_text

        app = server._build_app()
        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        endpoint_task = asyncio.create_task(ws_route.endpoint(ws))
        await asyncio.sleep(0)

        ws.accept.assert_called_once()
        calls = [c[0][0] for c in ws.send_json.call_args_list]
        assert calls[0]["type"] == "summary"
        assert calls[1]["type"] == "event"
        assert calls[1]["data"]["event_type"] == "tool_result"
        assert calls[1]["data"]["payload"] == {"success": True}

        release_connection.set()
        await endpoint_task

    @pytest.mark.asyncio
    async def test_late_joining_client_receives_finalized_snapshot(self):
        """Regression: browser connecting after serve_trace finalize must get 'finalize' message."""
        server = VizServer(port=19999, open_browser=False)
        server._metadata = {"session_id": "s1", "query": "hello"}
        server._summary = {"status": "completed", "event_count": 1}
        server._finalized_snapshot = {
            "session_id": "s1",
            "query": "hello",
            "hop_count": 1,
            "events": [{"event_type": "hop"}],
        }

        from fastapi import WebSocketDisconnect
        ws = AsyncMock()
        ws.receive_text.side_effect = WebSocketDisconnect()

        app = server._build_app()
        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        await ws_route.endpoint(ws)

        # Should have sent both meta AND finalize
        calls = ws.send_json.call_args_list
        types_sent = [c[0][0]["type"] for c in calls]
        assert "meta" in types_sent
        assert "summary" in types_sent
        assert "finalize" in types_sent

        finalize_msg = next(c[0][0] for c in calls if c[0][0]["type"] == "finalize")
        assert finalize_msg["data"]["query"] == "hello"
        assert len(finalize_msg["data"]["events"]) == 1

    @pytest.mark.asyncio
    async def test_late_joining_client_receives_metadata(self):
        """A client that connects after set_metadata should receive the meta message."""
        server = VizServer(port=19999, open_browser=False)
        server._metadata = {"session_id": "s1", "query": "hello"}
        server._summary = {"status": "waiting", "event_count": 0}

        from fastapi import WebSocketDisconnect
        ws = AsyncMock()
        # Simulate disconnect after first receive
        ws.receive_text.side_effect = WebSocketDisconnect()

        app = server._build_app()
        # Find the websocket route handler
        ws_route = None
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/ws":
                ws_route = route
                break

        assert ws_route is not None
        await ws_route.endpoint(ws)

        # ws.accept() should have been called
        ws.accept.assert_called_once()
        sent = [c[0][0] for c in ws.send_json.call_args_list]
        assert sent[0] == {"type": "meta", "data": {"session_id": "s1", "query": "hello"}}
        assert sent[1]["type"] == "summary"

    @pytest.mark.asyncio
    async def test_new_client_no_metadata_skips_send(self):
        """A client connecting before set_metadata should not get a meta message."""
        server = VizServer(port=19999, open_browser=False)
        # _metadata is empty

        from fastapi import WebSocketDisconnect
        ws = AsyncMock()
        ws.receive_text.side_effect = WebSocketDisconnect()

        app = server._build_app()
        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        await ws_route.endpoint(ws)

        ws.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_connection_removed_on_disconnect(self):
        server = VizServer(port=19999, open_browser=False)

        from fastapi import WebSocketDisconnect
        ws = AsyncMock()
        ws.receive_text.side_effect = WebSocketDisconnect()

        app = server._build_app()
        ws_route = next(r for r in app.routes if hasattr(r, "path") and r.path == "/ws")
        await ws_route.endpoint(ws)

        assert ws not in server._connections

    def test_websocket_endpoint_accepts_connection_via_full_asgi_stack(self):
        """Regression: ISSUE-001 — from __future__ import annotations in server.py caused
        FastAPI DI to treat `ws: WebSocket` as a query parameter (WebSocketRequestValidationError),
        resulting in HTTP 403 instead of a WebSocket upgrade. This test goes through
        the full FastAPI/Starlette ASGI stack to catch that class of regression."""
        from starlette.testclient import TestClient

        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()

        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                # If DI is broken, the line above raises an exception (403 status).
                # A successful accept means FastAPI resolved `ws: WebSocket` correctly.
                ws.send_text("ping")
                # Server stays alive until disconnect; just connecting is enough.


# ---------------------------------------------------------------------------
# VizServer — HTTP routes
# ---------------------------------------------------------------------------

class TestVizServerHttpRoutes:
    def test_build_app_creates_fastapi_app(self):
        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_app_has_index_and_health_routes(self):
        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        paths = {r.path for r in app.routes if hasattr(r, "path")}
        assert "/" in paths
        assert "/health" in paths
        assert "/ws" in paths
        assert "/static" in paths
        assert "/explain" in paths

    @pytest.mark.asyncio
    async def test_explain_returns_run_explanation_when_finalized(self):
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        ctx = _make_ctx(query="explain me", num_events=2)
        await server.finalize(ctx)

        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/explain", json={"session_id": ctx.session_id})

        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == ctx.session_id
        assert data["query"] == "explain me"
        assert "hops" in data
        assert "tool_calls" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_explain_returns_404_before_finalize(self):
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/explain", json={"session_id": "any-id"})
        assert resp.status_code == 404
        assert "finalized" in resp.json()["error"]

    @pytest.mark.asyncio
    async def test_explain_returns_404_for_wrong_session_id(self):
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        ctx = _make_ctx(query="test", num_events=1)
        await server.finalize(ctx)
        server._metadata = {"session_id": ctx.session_id, "query": "test"}

        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/explain", json={"session_id": "wrong-session-id"})
        assert resp.status_code == 404
        assert "not found" in resp.json()["error"]

    @pytest.mark.asyncio
    async def test_explain_accepts_empty_session_id(self):
        """No session_id in body — returns the stored explanation without session check."""
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        ctx = _make_ctx(query="no session filter", num_events=1)
        await server.finalize(ctx)

        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/explain", json={})
        assert resp.status_code == 200
        assert resp.json()["query"] == "no session filter"

    @pytest.mark.asyncio
    async def test_health_route_returns_ok(self):
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_index_route_returns_html(self):
        from httpx import AsyncClient, ASGITransport
        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "/static/app.js" in resp.text

    @pytest.mark.asyncio
    async def test_static_asset_routes_return_content(self):
        from httpx import AsyncClient, ASGITransport

        server = VizServer(port=19999, open_browser=False)
        app = server._build_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            js_resp = await client.get("/static/app.js")
            css_resp = await client.get("/static/styles.css")

        assert js_resp.status_code == 200
        assert "javascript" in js_resp.headers["content-type"] or js_resp.text
        assert css_resp.status_code == 200
        assert "text/css" in css_resp.headers["content-type"]


# ---------------------------------------------------------------------------
# VizServer — stop
# ---------------------------------------------------------------------------

class TestVizServerStop:
    @pytest.mark.asyncio
    async def test_stop_sets_should_exit(self):
        server = VizServer(port=19999, open_browser=False)
        mock_uvicorn_server = MagicMock()
        mock_uvicorn_server.should_exit = False
        server._server = mock_uvicorn_server

        await server.stop()
        assert mock_uvicorn_server.should_exit is True

    @pytest.mark.asyncio
    async def test_stop_no_server_no_error(self):
        server = VizServer(port=19999, open_browser=False)
        server._server = None
        await server.stop()  # should not raise


# ---------------------------------------------------------------------------
# serve_trace integration (mocked server)
# ---------------------------------------------------------------------------

class TestServeTrace:
    @pytest.mark.asyncio
    async def test_serve_trace_calls_finalize(self):
        from yggdrasil_lm.viz.server import serve_trace

        ctx = _make_ctx(query="ollama gemma4:26b test", num_events=2)

        mock_server = AsyncMock(spec=VizServer)
        mock_server._metadata = {}
        mock_server.port = 19999

        with patch("viz.server.VizServer", return_value=mock_server):
            with patch("builtins.print"):
                await serve_trace(ctx, port=19999, open_browser=False, wait=False)

        mock_server.start.assert_called_once()
        mock_server.finalize.assert_called_once_with(ctx, store=None)
        mock_server.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_serve_trace_sets_metadata(self):
        from yggdrasil_lm.viz.server import serve_trace

        ctx = _make_ctx(query="yggdrasil test")

        mock_server = AsyncMock(spec=VizServer)
        mock_server.port = 19999
        mock_server._metadata = {}

        with patch("viz.server.VizServer", return_value=mock_server):
            with patch("builtins.print"):
                await serve_trace(ctx, port=19999, open_browser=False, wait=False)

        mock_server.set_metadata.assert_called_once_with(
            session_id=ctx.session_id, query=ctx.query
        )

    @pytest.mark.asyncio
    async def test_serve_trace_passes_store_to_finalize(self):
        from yggdrasil_lm.viz.server import serve_trace

        ctx = _make_ctx(query="yggdrasil test")
        store = NetworkXGraphStore()

        mock_server = AsyncMock(spec=VizServer)
        mock_server.port = 19999
        mock_server._metadata = {}

        with patch("viz.server.VizServer", return_value=mock_server):
            with patch("builtins.print"):
                await serve_trace(ctx, store=store, port=19999, open_browser=False, wait=False)

        mock_server.attach_store.assert_called_once_with(store)
        mock_server.finalize.assert_called_once_with(ctx, store=store)
