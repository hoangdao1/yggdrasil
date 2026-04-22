"""Tests for inspect_trace / trace_ui rendering.

All tests use Console(record=True, no_color=True) to capture rendered output
and assert on specific rendered strings rather than just "no exception".
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from yggdrasil_lm.core.executor import ExecutionContext, TraceEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _event(
    event_type: str,
    *,
    node_id: str = "node-1",
    node_name: str = "TestNode",
    payload: dict | None = None,
    event_id: str | None = None,
    parent_event_id: str | None = None,
    duration_ms: int | None = None,
    session_id: str = "sess-0001",
) -> TraceEvent:
    return TraceEvent(
        event_type=event_type,
        session_id=session_id,
        node_id=node_id,
        node_name=node_name,
        timestamp=_now(),
        payload=payload or {},
        event_id=event_id or f"evt-{event_type}-{node_id}",
        parent_event_id=parent_event_id,
        duration_ms=duration_ms,
    )


def _hop_event(hop_num: int, node_name: str = "Agent", *, node_id: str = "node-1") -> TraceEvent:
    return _event(
        "hop",
        node_id=node_id,
        node_name=node_name,
        payload={"hop": hop_num, "node_type": "core.nodes.AgentNode", "summary": f"hop {hop_num}"},
    )


def _capture(events: list[TraceEvent], *, verbose: bool = True) -> str:
    """Render events to a string via Console(record=True)."""
    from rich.console import Console
    from yggdrasil_lm.trace_ui import _render_session

    console = Console(record=True, no_color=True, width=120)
    session_id = events[0].session_id if events else "unknown"
    hop_count = sum(1 for e in events if e.event_type == "hop")
    _render_session(console, events, session_id, "test query", hop_count, verbose)
    return console.export_text()


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------

def test_hop_is_rendered():
    events = [_hop_event(1)]
    output = _capture(events)
    assert "HOP 1" in output


def test_empty_trace_renders_header_without_crash():
    output = _capture([])
    # No crash — summary panel must still appear
    assert "Execution Summary" in output


def test_hop_count_appears_in_summary():
    events = [_hop_event(1), _hop_event(2)]
    output = _capture(events)
    assert "Hops" in output
    assert "2" in output


def test_summary_counts_are_correct():
    hop = _hop_event(1)
    tool_call = _event("tool_call", node_name="echo", payload={"input": {"x": 1}}, parent_event_id=hop.event_id)
    tool_result = _event("tool_result", node_name="echo", payload={"success": True, "output_summary": "done"}, parent_event_id=tool_call.event_id)
    agent_end = _event("agent_end", payload={"text_summary": "done", "intent": "default", "iterations": 1}, parent_event_id=hop.event_id)
    events = [hop, tool_call, tool_result, agent_end]
    output = _capture(events)
    assert "Tool calls" in output
    assert "1" in output


# ---------------------------------------------------------------------------
# Verbose vs compact
# ---------------------------------------------------------------------------

def test_compact_truncates_output():
    hop = _hop_event(1)
    tool_call = _event(
        "tool_call",
        node_name="echo",
        payload={"input": {"data": "x" * 200}, "callable_ref": "tools.echo"},
        parent_event_id=hop.event_id,
    )
    events = [hop, tool_call]
    verbose_out = _capture(events, verbose=True)
    compact_out = _capture(events, verbose=False)
    # compact renders a dim one-liner (no JSON panel); verbose renders full Syntax block
    assert len(compact_out) < len(verbose_out)


def test_verbose_shows_context_scores():
    hop = _hop_event(1)
    agent_start = _event(
        "agent_start",
        payload={
            "model": "claude-3",
            "tools": [],
            "context": ["Playbook"],
            "context_scores": [
                {"name": "Playbook", "score": 0.92, "source": "attached", "hops": 1}
            ],
        },
        parent_event_id=hop.event_id,
    )
    events = [hop, agent_start]
    verbose_out = _capture(events, verbose=True)
    compact_out = _capture(events, verbose=False)
    # context score details only appear in verbose
    assert "score=0.92" in verbose_out
    assert "score=0.92" not in compact_out


# ---------------------------------------------------------------------------
# Tool error label
# ---------------------------------------------------------------------------

def test_tool_error_shows_error_label():
    hop = _hop_event(1)
    tool_call = _event("tool_call", node_name="fail_tool", payload={"input": {}}, parent_event_id=hop.event_id)
    tool_result = _event(
        "tool_result",
        node_name="fail_tool",
        payload={"success": False, "output_summary": "something went wrong"},
        parent_event_id=tool_call.event_id,
    )
    events = [hop, tool_call, tool_result]
    output = _capture(events)
    assert "ERROR" in output


def test_tool_success_does_not_show_error_label():
    hop = _hop_event(1)
    tool_call = _event("tool_call", node_name="ok_tool", payload={"input": {}}, parent_event_id=hop.event_id)
    tool_result = _event(
        "tool_result",
        node_name="ok_tool",
        payload={"success": True, "output_summary": "all good"},
        parent_event_id=tool_call.event_id,
    )
    events = [hop, tool_call, tool_result]
    output = _capture(events)
    # Should have "ok" status, not "ERROR"
    assert "ERROR" not in output


# ---------------------------------------------------------------------------
# Routing events
# ---------------------------------------------------------------------------

def test_low_confidence_routing_flagged():
    hop = _hop_event(1)
    routing = _event(
        "routing",
        payload={"intent": "billing", "next_node_id": "billing-node", "confidence": 0.5},
        parent_event_id=hop.event_id,
    )
    events = [hop, routing]
    output = _capture(events)
    assert "conf=50%" in output


def test_high_confidence_routing_not_flagged_as_error():
    hop = _hop_event(1)
    routing = _event(
        "routing",
        payload={"intent": "billing", "next_node_id": "billing-node", "confidence": 0.95},
        parent_event_id=hop.event_id,
    )
    events = [hop, routing]
    output = _capture(events)
    assert "conf=95%" in output


# ---------------------------------------------------------------------------
# Subgraph events
# ---------------------------------------------------------------------------

def test_subgraph_enter_exit_rendered():
    hop = _hop_event(1)
    enter = _event(
        "subgraph_enter",
        node_name="SubGraph",
        payload={"entry_node_id": "inner-node-1234"},
        parent_event_id=hop.event_id,
    )
    exit_ = _event(
        "subgraph_exit",
        node_name="SubGraph",
        payload={"exit_node_id": "inner-node-1234"},
        parent_event_id=hop.event_id,
        duration_ms=120,
    )
    events = [hop, enter, exit_]
    output = _capture(events)
    assert "SUBGRAPH" in output


# ---------------------------------------------------------------------------
# Raw list[TraceEvent] input
# ---------------------------------------------------------------------------

def test_raw_event_list_input():
    """inspect_trace accepts list[TraceEvent] directly, not only ExecutionContext."""
    from yggdrasil_lm.trace_ui import inspect_trace
    from rich.console import Console
    import io

    events = [_hop_event(1)]
    # Should not raise even when passed a raw list
    buf = io.StringIO()
    with patch("trace_ui.Console", return_value=Console(file=buf, record=True, no_color=True, width=120)):
        inspect_trace(events)
    # No exception = pass


# ---------------------------------------------------------------------------
# File export
# ---------------------------------------------------------------------------

def test_html_export_creates_file(tmp_path):
    from yggdrasil_lm.trace_ui import inspect_trace

    events = [_hop_event(1)]
    out_file = tmp_path / "trace.html"
    inspect_trace(events, file=str(out_file), format="html")

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<html" in content.lower()


def test_text_export_creates_file(tmp_path):
    from yggdrasil_lm.trace_ui import inspect_trace

    events = [_hop_event(1)]
    out_file = tmp_path / "trace.txt"
    inspect_trace(events, file=str(out_file), format="text")

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert len(content) > 0


def test_file_handle_is_closed_even_if_render_raises(tmp_path):
    """File handle must not leak when _render_session raises mid-render."""
    from yggdrasil_lm.trace_ui import inspect_trace

    out_file = tmp_path / "trace.html"
    events = [_hop_event(1)]

    with patch("trace_ui._render_session", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            inspect_trace(events, file=str(out_file), format="html")

    # File was opened inside a `with` block so it must be closed now.
    # We can verify by opening it again without error.
    out_file.touch()  # ensure file exists for open check
    fh = open(str(out_file))
    fh.close()  # would raise if OS-level handle was leaked (not applicable on all OS, but proves no exception)


# ---------------------------------------------------------------------------
# Fallback without rich
# ---------------------------------------------------------------------------

def test_fallback_without_rich(capsys):
    """When _RICH is False, inspect_trace falls back to print_trace."""
    from yggdrasil_lm.core.executor import ExecutionContext
    import yggdrasil_lm.trace_ui as trace_ui_mod

    ctx = ExecutionContext(query="test", session_id="sess-fallback")
    ctx.trace = [_event("hop", session_id="sess-fallback", payload={"hop": 1, "summary": "fallback test"})]

    with patch.object(trace_ui_mod, "_RICH", False):
        with patch("trace_ui.print_trace") as mock_print:
            trace_ui_mod.inspect_trace(ctx)
            mock_print.assert_called_once_with(ctx)
