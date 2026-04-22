"""OpenTelemetry exporter for yggdrasil execution traces.

Converts an ExecutionContext trace into OTel spans and pushes them to
whichever TracerProvider the application has configured — Datadog, Signoz,
Grafana Tempo, Honeycomb, Jaeger, or any other OTLP-compatible backend.

Span hierarchy
--------------
Each graph traversal hop becomes a root span.  Agent execution and tool
calls nest beneath it as child spans.  Non-span events (routing decisions,
context injection) are attached as OTel Events on their parent agent span.

    session (resource attribute)
      hop N — <AgentName>            ← root span per hop
        agent: <AgentName>           ← agent execution span
          tool: <ToolName>           ← one span per tool call
          [event] context_inject     ← OTel event on agent span
          [event] routing            ← OTel event on agent span

Timing
------
TraceEvent timestamps are wall-clock datetimes.  agent_end and tool_result
carry duration_ms so exact start times can be reconstructed without a
running clock.  All OTel times are in nanoseconds since epoch.

Quick start
-----------
    # 1. Configure any OTel backend once at startup (see examples below)
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
    )
    trace.set_tracer_provider(provider)

    # 2. Export after every run
    from yggdrasil_lm.exporters.otel import export_trace

    ctx = await executor.run(entry_node_id, query)
    export_trace(ctx)          # sends spans to the configured backend

Requires: pip install 'yggdrasil[observe]'
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yggdrasil_lm.core.executor import ExecutionContext, TraceEvent


# ---------------------------------------------------------------------------
# OTel service / instrumentation name
# ---------------------------------------------------------------------------

_SERVICE_NAME    = "yggdrasil"
_INSTRUMENTATION = "exporters.otel"
_SCHEMA_URL      = "https://opentelemetry.io/schemas/1.26.0"


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def _to_ns(dt: datetime) -> int:
    """Convert a datetime to nanoseconds since epoch (required by OTel API)."""
    return int(dt.timestamp() * 1_000_000_000)


def _end_ns(dt: datetime, duration_ms: int | None) -> int:
    """Compute end time in ns given a timestamp and optional duration."""
    if duration_ms is not None:
        return _to_ns(dt) + duration_ms * 1_000_000
    return _to_ns(dt)


# ---------------------------------------------------------------------------
# ID helpers
# ---------------------------------------------------------------------------

def _trace_id_from_session(session_id: str) -> int:
    """Derive a stable 128-bit OTel trace ID from the session UUID."""
    try:
        return uuid.UUID(session_id).int
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, session_id).int


def _span_id_from_event(event_id: str) -> int:
    """Derive a stable 64-bit OTel span ID from a TraceEvent UUID."""
    try:
        return uuid.UUID(event_id).int & 0xFFFF_FFFF_FFFF_FFFF
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, event_id).int & 0xFFFF_FFFF_FFFF_FFFF


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def export_trace(
    ctx:          "ExecutionContext",
    tracer:       Any = None,
    service_name: str = _SERVICE_NAME,
) -> None:
    """Export an ExecutionContext trace as OpenTelemetry spans.

    Args:
        ctx:          The ExecutionContext returned by executor.run().
        tracer:       An OTel Tracer instance.  Uses the globally-configured
                      TracerProvider when None (the common case).
        service_name: Override the OTel service.name resource attribute.

    The function is a no-op when opentelemetry-sdk is not installed —
    it logs a warning to stderr and returns without raising.
    """
    try:
        from opentelemetry import trace as otel_trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
    except ImportError:
        import sys
        print(
            "[yggdrasil] opentelemetry-sdk not installed — trace export skipped. "
            "Run: pip install 'yggdrasil[observe]'",
            file=sys.stderr,
        )
        return

    if tracer is None:
        tracer = otel_trace.get_tracer(_INSTRUMENTATION, schema_url=_SCHEMA_URL)

    events     = ctx.trace
    session_id = ctx.session_id
    query      = ctx.query

    # Build parent→children index
    children: dict[str | None, list[TraceEvent]] = {}
    for e in events:
        children.setdefault(e.parent_event_id, []).append(e)

    # Derive OTel trace ID from session ID so all spans share the same trace
    trace_id = _trace_id_from_session(session_id)

    # Render top-level events (hops)
    for root_event in children.get(None, []):
        _export_hop(
            tracer, root_event, children,
            trace_id=trace_id, query=query,
        )


# ---------------------------------------------------------------------------
# Hop → root span
# ---------------------------------------------------------------------------

def _export_hop(
    tracer:   Any,
    hop:      "TraceEvent",
    children: dict[str | None, list["TraceEvent"]],
    trace_id: int,
    query:    str,
) -> None:
    """Create one root OTel span per hop and recurse into its children."""
    from opentelemetry.trace import SpanContext, TraceFlags, NonRecordingSpan
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.trace import SpanKind, use_span

    p       = hop.payload
    hop_num = p.get("hop", "")
    span_name = f"hop {hop_num} — {hop.node_name}" if hop_num else hop.node_name

    hop_children = children.get(hop.event_id, [])

    # Compute hop span time from children when hop.duration_ms is not set
    start_ns, end_ns = _hop_times(hop, hop_children)

    hop_attrs: dict[str, Any] = {
        "hop":        hop_num,
        "node_type":  p.get("node_type", ""),
        "node_name":  hop.node_name,
        "session_id": hop.session_id,
        "query":      query,
    }

    span_ctx = SpanContext(
        trace_id=trace_id,
        span_id=_span_id_from_event(hop.event_id),
        is_remote=False,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )
    parent_span = NonRecordingSpan(span_ctx)

    with tracer.start_as_current_span(
        span_name,
        context=_ctx_with_span(parent_span),
        start_time=start_ns,
        attributes=hop_attrs,
    ) as hop_span:
        hop_span.set_attribute("summary", p.get("summary", "")[:500])

        for child in hop_children:
            if child.event_type == "agent_start":
                _export_agent(tracer, child, children, trace_id=trace_id)

        # End at the computed time
        hop_span.end(end_time=end_ns)


# ---------------------------------------------------------------------------
# Agent span (agent_start → agent_end pair)
# ---------------------------------------------------------------------------

def _export_agent(
    tracer:   Any,
    start_ev: "TraceEvent",
    children: dict[str | None, list["TraceEvent"]],
    trace_id: int,
) -> None:
    """Create one OTel span covering the full agent execution."""
    p          = start_ev.payload
    agent_name = start_ev.node_name
    model      = p.get("model", "unknown")

    agent_children = children.get(start_ev.event_id, [])

    # Find agent_end to get end time
    end_event = next(
        (e for e in agent_children if e.event_type == "agent_end"), None
    )
    start_ns = _to_ns(start_ev.timestamp)
    end_ns   = _to_ns(end_event.timestamp) if end_event else start_ns + 1_000_000

    agent_attrs: dict[str, Any] = {
        "agent.name":       agent_name,
        "agent.model":      model,
        "agent.tools":      json.dumps(p.get("tools", [])),
        "agent.context":    json.dumps(p.get("context", [])),
        "agent.query":      p.get("query", "")[:500],
        "llm.system":                   "anthropic",
        "llm.request.model":            model,
        "gen_ai.system":                "anthropic",
        "gen_ai.request.model":         model,
    }

    if end_event:
        agent_attrs["agent.intent"]     = end_event.payload.get("intent", "")
        agent_attrs["agent.iterations"] = end_event.payload.get("iterations", 1)
        agent_attrs["agent.summary"]    = end_event.payload.get("text_summary", "")[:500]

    with tracer.start_as_current_span(
        f"agent: {agent_name}",
        start_time=start_ns,
        attributes=agent_attrs,
    ) as agent_span:
        # Emit non-span child events as OTel Events
        for child in agent_children:
            if child.event_type == "context_inject":
                agent_span.add_event(
                    "context_inject",
                    attributes={
                        "context.names":  json.dumps(child.payload.get("context_names", [])),
                        "context.count":  child.payload.get("count", 0),
                    },
                    timestamp=_to_ns(child.timestamp),
                )
            elif child.event_type == "routing":
                cp = child.payload
                route_attrs: dict[str, Any] = {
                    "routing.intent":      cp.get("intent", ""),
                    "routing.next_node_id": cp.get("next_node_id") or "__END__",
                }
                if cp.get("confidence") is not None:
                    route_attrs["routing.confidence"] = cp["confidence"]
                agent_span.add_event(
                    "routing",
                    attributes=route_attrs,
                    timestamp=_to_ns(child.timestamp),
                )
            elif child.event_type == "tool_call":
                _export_tool(tracer, child, children, trace_id=trace_id)

        agent_span.end(end_time=end_ns)


# ---------------------------------------------------------------------------
# Tool span (tool_call → tool_result pair)
# ---------------------------------------------------------------------------

def _export_tool(
    tracer:    Any,
    call_ev:   "TraceEvent",
    children:  dict[str | None, list["TraceEvent"]],
    trace_id:  int,
) -> None:
    """Create one OTel span covering one tool invocation."""
    from opentelemetry.trace.status import Status, StatusCode

    p         = call_ev.payload
    tool_name = call_ev.node_name
    inp       = p.get("input", {})

    result_children = children.get(call_ev.event_id, [])
    result_ev = next(
        (e for e in result_children if e.event_type == "tool_result"), None
    )

    start_ns = _to_ns(call_ev.timestamp)
    end_ns   = _to_ns(result_ev.timestamp) if result_ev else start_ns + 1_000_000

    tool_attrs: dict[str, Any] = {
        "tool.name":         tool_name,
        "tool.callable_ref": p.get("callable_ref", ""),
        "tool.input":        json.dumps(inp)[:1000],
    }

    success = True
    if result_ev:
        rp = result_ev.payload
        success = rp.get("success", True)
        tool_attrs["tool.output_summary"] = rp.get("output_summary", "")[:500]
        tool_attrs["tool.success"]        = success

    with tracer.start_as_current_span(
        f"tool: {tool_name}",
        start_time=start_ns,
        attributes=tool_attrs,
    ) as tool_span:
        if not success:
            tool_span.set_status(Status(StatusCode.ERROR))

        tool_span.end(end_time=end_ns)


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------

def _hop_times(
    hop:      "TraceEvent",
    hop_children: list["TraceEvent"],
) -> tuple[int, int]:
    """Compute start/end nanoseconds for a hop span."""
    if hop.duration_ms is not None:
        start = _to_ns(hop.timestamp)
        return start, start + hop.duration_ms * 1_000_000

    if hop_children:
        timestamps = [_to_ns(e.timestamp) for e in hop_children]
        start_ns = min(timestamps)

        # Use agent_end duration to find the true end
        agent_ends = [
            e for child in hop_children
            for e in [child]
            if child.event_type == "agent_end" and child.duration_ms
        ]
        if agent_ends:
            end_ns = max(
                _to_ns(e.timestamp) + e.duration_ms * 1_000_000  # type: ignore[operator]
                for e in agent_ends
            )
        else:
            end_ns = max(timestamps) + 1_000_000  # +1ms fallback

        return start_ns, end_ns

    ts = _to_ns(hop.timestamp)
    return ts, ts + 1_000_000


def _ctx_with_span(span: Any) -> Any:
    """Return an OTel Context that sets the given span as current."""
    from opentelemetry import context as otel_context
    from opentelemetry.trace import set_span_in_context
    return set_span_in_context(span)
