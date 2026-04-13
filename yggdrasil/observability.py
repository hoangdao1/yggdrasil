"""Data API for structured trace inspection.

This module is the canonical home for functions that return typed objects
from an execution trace. It does NOT render to a terminal or start a server.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yggdrasil.core.executor import (
    ExecutionContext,
    TraceEvent,
    cleanup_session,
    get_runtime_nodes,
    print_trace,
)
from yggdrasil.exporters.otel import export_trace
from yggdrasil.trace_ui import inspect_trace


@dataclass
class RunHopExplanation:
    node_id: str
    node_name: str
    hop: int | None
    summary: str = ""


@dataclass
class RunRoutingExplanation:
    node_id: str
    node_name: str
    intent: str | None
    next_node_id: str | None
    confidence: float | None
    mode: str = "llm"


@dataclass
class RunContextExplanation:
    node_id: str
    node_name: str
    selected_contexts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RunToolCallExplanation:
    node_id: str
    tool_name: str
    callable_ref: str
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunPauseExplanation:
    node_id: str
    node_name: str
    waiting_for: Any = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunSummary:
    routing_decision_count: int = 0
    tool_call_count: int = 0
    context_injection_count: int = 0
    pause_event_count: int = 0


@dataclass
class RunExplanation:
    session_id: str
    query: str
    hop_count: int
    paused: bool
    hops: list[RunHopExplanation] = field(default_factory=list)
    routing: list[RunRoutingExplanation] = field(default_factory=list)
    context: list[RunContextExplanation] = field(default_factory=list)
    tool_calls: list[RunToolCallExplanation] = field(default_factory=list)
    pauses: list[RunPauseExplanation] = field(default_factory=list)
    summary: RunSummary = field(default_factory=RunSummary)


@dataclass
class TraceView:
    hops: list[TraceEvent] = field(default_factory=list)
    agent_starts: list[TraceEvent] = field(default_factory=list)
    agent_ends: list[TraceEvent] = field(default_factory=list)
    tool_calls: list[TraceEvent] = field(default_factory=list)
    tool_results: list[TraceEvent] = field(default_factory=list)
    context_inject: list[TraceEvent] = field(default_factory=list)
    routing: list[TraceEvent] = field(default_factory=list)
    pauses: list[TraceEvent] = field(default_factory=list)


def extract_trace_view(events: list[TraceEvent]) -> TraceView:
    view = TraceView()
    for event in events:
        t = event.event_type
        if t == "hop":
            view.hops.append(event)
        elif t == "agent_start":
            view.agent_starts.append(event)
        elif t == "agent_end":
            view.agent_ends.append(event)
        elif t == "tool_call":
            view.tool_calls.append(event)
        elif t == "tool_result":
            view.tool_results.append(event)
        elif t == "context_inject":
            view.context_inject.append(event)
        elif t == "routing":
            view.routing.append(event)
        elif t == "pause":
            view.pauses.append(event)
    return view


def explain_run(ctx: ExecutionContext) -> RunExplanation:
    """Summarize why a run behaved the way it did."""
    view = extract_trace_view(ctx.trace)
    paused = ctx.is_paused() or bool(view.pauses)

    return RunExplanation(
        session_id=ctx.session_id,
        query=ctx.query,
        hop_count=ctx.hop_count,
        paused=paused,
        hops=[
            RunHopExplanation(
                node_id=e.node_id,
                node_name=e.node_name,
                hop=e.payload.get("hop"),
                summary=e.payload.get("summary", ""),
            )
            for e in view.hops
        ],
        routing=[
            RunRoutingExplanation(
                node_id=e.node_id,
                node_name=e.node_name,
                intent=e.payload.get("intent"),
                next_node_id=e.payload.get("next_node_id"),
                confidence=e.payload.get("confidence"),
                mode=e.payload.get("mode", "llm"),
            )
            for e in view.routing
        ],
        context=[
            RunContextExplanation(
                node_id=e.node_id,
                node_name=e.node_name,
                selected_contexts=e.payload.get("selected_contexts", []),
            )
            for e in view.context_inject
        ],
        tool_calls=[
            RunToolCallExplanation(
                node_id=e.node_id,
                tool_name=e.payload.get("tool_name", e.node_name),
                callable_ref=e.payload.get("callable_ref", ""),
                input=e.payload.get("input", {}),
            )
            for e in view.tool_calls
        ],
        pauses=[
            RunPauseExplanation(
                node_id=e.node_id,
                node_name=e.node_name,
                waiting_for=e.payload.get("waiting_for"),
                reason=e.payload.get("reason", ""),
                metadata=e.payload.get("metadata", {}),
            )
            for e in view.pauses
        ],
        summary=RunSummary(
            routing_decision_count=len(view.routing),
            tool_call_count=len(view.tool_calls),
            context_injection_count=len(view.context_inject),
            pause_event_count=len(view.pauses),
        ),
    )


__all__ = [
    "explain_run",
    "export_trace",
    "RunExplanation",
    "cleanup_session",
    "get_runtime_nodes",
    "inspect_trace",
    "print_trace",
]
