"""Agent composition and graph execution engine.

Key components:
- AgentComposer  — discovers an agent's tools/context/prompt by traversing edges
- ComposedAgent  — assembled runtime configuration for a single agent invocation
- ExecutionContext — shared mutable state that flows through the graph during a run
- GraphExecutor  — dispatches nodes and follows routing edges to traverse the graph
- TraceEvent     — structured, typed execution event for full observability
- print_trace()  — render a session trace as a human-readable execution tree

Execution strategies:
- sequential  : DFS — run node, route to next, repeat (default for chains)
- parallel    : BFS fan-out — gather all DELEGATES_TO targets concurrently
- topological : DAG waves — graphlib.TopologicalSorter for explicit pipelines
"""

from __future__ import annotations

import asyncio
import functools
import graphlib
import inspect
import json
import logging
import os
import re
import time
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, NamedTuple

from yggdrasil_lm.backends.llm import LLMBackend, ToolResult, default_backend
from yggdrasil_lm.core.edges import Edge, EdgeType
from yggdrasil_lm.core.nodes import (
    AgentNode,
    AnyNode,
    ApprovalNode,
    ConstraintRule,
    ContextNode,
    DecisionRule,
    DecisionTable,
    ExecutionPolicy,
    GraphNode,
    NodeType,
    PromptNode,
    ReasonerNode,
    RouteRule,
    SchemaNode,
    ToolNode,
    TransformNode,
)
from yggdrasil_lm.core.store import GraphStore, _cosine, _normalize

# ---------------------------------------------------------------------------
# TraceEvent — structured, typed execution event
# ---------------------------------------------------------------------------

EventType = Literal[
    "agent_start",
    "agent_end",
    "tool_call",
    "tool_result",
    "routing",
    "context_inject",
    "hop",
    "subgraph_enter",
    "subgraph_exit",
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
    "error",
    "agent_skip",
]

_log = logging.getLogger(__name__)

# When an agent turn is truncated at max_tokens WITHOUT producing an answer or a
# tool call (a reasoning model can spend its whole budget in the chain-of-thought
# before it acts), the executor retries the same turn with a larger output budget
# rather than mistaking the empty result for "done". Bounded so a persistently
# over-budget turn still terminates. Env-tunable; escalations set to 0 disables it.
_MAX_TOKEN_ESCALATIONS = int(os.environ.get("YGG_MAX_TOKEN_ESCALATIONS", "2"))
_TOKEN_ESCALATION_FACTOR = int(os.environ.get("YGG_TOKEN_ESCALATION_FACTOR", "2"))
_TOKEN_ESCALATION_CAP = int(os.environ.get("YGG_TOKEN_ESCALATION_CAP", "32000"))


def _escalation_knobs() -> tuple[int, int, int]:
    """(max escalations, factor, cap) read at USE time, not import time.

    These constants used to be baked in when the module was first imported, which
    silently ignored any caller that set the environment later — and a host app
    naturally does exactly that, because the right cap depends on the model it just
    picked. A server that imports the engine at startup and then sets
    YGG_TOKEN_ESCALATION_CAP=13200 per run kept escalating to the 32000 default: it
    asked a 22000-token-context model for 32000 output tokens, which cannot ever
    return, so the turn truncated, escalated, and truncated again — ~22 minutes per
    doomed attempt with no way for the host to intervene.

    The module constants remain as the documented defaults (and so a test may still
    patch them); a live environment variable wins over them.
    """
    def _knob(env: str, default: int) -> int:
        raw = os.environ.get(env)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:                       # a malformed knob must not kill the run
            return default
    return (
        _knob("YGG_MAX_TOKEN_ESCALATIONS", _MAX_TOKEN_ESCALATIONS),
        _knob("YGG_TOKEN_ESCALATION_FACTOR", _TOKEN_ESCALATION_FACTOR),
        _knob("YGG_TOKEN_ESCALATION_CAP", _TOKEN_ESCALATION_CAP),
    )

# A local model that writes a tool call as TEXT instead of through the tool API (the
# server's parser didn't recognise its format) produces a turn that looks like a final
# answer but did no work — an agent loop would end mid-task. Same treatment as a
# max_tokens truncation: tell the model its call wasn't parsed and let it retry, rather
# than accepting the markup as the result. Bounded, so a model that cannot produce a
# well-formed call still terminates instead of looping to max_iterations.
# Env-tunable; 0 disables the correction (the turn is then terminal, as before).
_MAX_TOOL_CALL_CORRECTIONS = int(os.environ.get("YGG_MAX_TOOL_CALL_CORRECTIONS", "3"))
# A final turn that is BLANK or reads as a narration lead-in ("Now let me resolve all
# the field contexts:") is the model announcing its NEXT action, not finishing. With no
# parseable tool call the loop accepted it as the answer and the agent stopped mid-task.
# Measured on run df80a65a: four aggregator shards ended at 12/23/5/12 of a 100-turn
# budget, their final text either "\n\n" or exactly such a lead-in — none had written
# its output. Nudge once (bounded) rather than accept a non-answer as the result.
# Env-tunable; 0 restores the old behaviour.
_MAX_CONTINUATION_NUDGES = int(os.environ.get("YGG_MAX_CONTINUATION_NUDGES", "2"))
# An agent whose work is DEFINED by artefacts it must leave behind has not finished
# while they are absent, however confident its closing message sounds. A consumer
# declares them on the node as `attributes["completion_paths"]` (paths, absolute or
# relative to the process cwd); the executor treats a terminal turn with any of them
# missing as not-done and asks for the work to be completed. Generic on purpose — the
# engine only checks existence, it never interprets the contents.
# Env-tunable; 0 disables the check.
_MAX_COMPLETION_NUDGES = int(os.environ.get("YGG_MAX_COMPLETION_NUDGES", "2"))


def missing_completion_paths(node: Any) -> list[str]:
    """Declared `completion_paths` for `node` that do not exist yet."""
    attrs = getattr(node, "attributes", None) or {}
    declared = attrs.get("completion_paths") or []
    if isinstance(declared, str):
        declared = [declared]
    if not isinstance(declared, (list, tuple)):
        return []
    from pathlib import Path as _Path
    return [str(p) for p in declared if p and not _Path(str(p)).exists()]

_CONTINUATION_NUDGE = (
    "Your last message did not finish the task and issued no tool call — it read as an "
    "announcement of what you were about to do. Continue now: either make the next tool "
    "call, or, if the work is genuinely complete, state the final result explicitly."
)
# A lead-in announces an action and stops: trailing colon, or an opening like
# "Now let me …" / "Next, I'll …" / "Let me …". Kept narrow so a real answer that
# happens to end in a colon-led list is not mistaken for one (it would have content
# after the colon).
# Anything longer than this is a substantive answer, never a lead-in.
_NARRATION_MAX_LEAD_IN_CHARS = 400

# Routing confidence below this earns a "specify the agent explicitly" warning.
_LOW_CONFIDENCE_THRESHOLD = 0.7

# Recency buckets for context scoring.
_HOUR_SECONDS = 3600
_DAY_SECONDS = 86400

# tool_call payload preview width in the plain-text trace renderer.
_TOOL_INPUT_PREVIEW_CHARS = 60

_NARRATION_LEAD_IN = re.compile(
    r"""^\s*(
          (now\s+)?let(\s+me|'s)\b
        | next\s*[,:]
        | (i|I)\s*(will|'ll)\b
        | (first|then|finally)\s*[,:]
    )""",
    re.IGNORECASE | re.VERBOSE)


def looks_like_narration_only(text: str, reasoning: str = "") -> bool:
    """Whether a no-tool-call turn is an announcement rather than an answer.

    True for blank/whitespace output, and for a short lead-in that ends on a colon
    (the model was about to act). A substantive answer — anything of length that does
    not end mid-announcement — is left alone."""
    body = (text or "").strip()
    if not body:
        # Nothing in `content`. Only a nudge-worthy non-answer if the model was not
        # simply thinking out loud to a real conclusion in the reasoning channel.
        return not (reasoning or "").strip()
    if len(body) > _NARRATION_MAX_LEAD_IN_CHARS:
        return False                      # substantive output, not a lead-in
    return body.endswith(":") and _NARRATION_LEAD_IN.search(body) is not None


_TOOL_CALL_CORRECTION_PROMPT = (
    "Your previous message contained a tool call written as plain text, so it was NOT "
    "executed — nothing ran. Do not describe or hand-write tool calls in your message "
    "content. Re-issue that single call using the tool-calling API, with the arguments "
    "as a JSON object. If you meant to give a final answer instead, reply with the "
    "answer and no tool-call markup."
)

# Bounded rolling history. In a long ReAct loop the message history only ever GROWS
# (each turn appends the assistant message + its tool results), and every turn re-reads
# ALL of it — so cost is O(turns × context). To bound the re-read, once the history is
# long we SHRINK the content of older turns in place (clip long text + tool-result
# bodies, keeping tool_use/tool_call blocks intact so pairing/caching stay valid),
# while keeping the head (task/setup) and the most recent turns full. Batch-triggered
# (every _HISTORY_COMPACT_EVERY turns) so the cache prefix is only invalidated
# occasionally, not every turn. Env-tunable; _HISTORY_COMPACT_EVERY=0 disables it.
_HISTORY_COMPACT_EVERY = int(os.environ.get("YGG_HISTORY_COMPACT_EVERY", "6"))
_HISTORY_HEAD_KEEP = int(os.environ.get("YGG_HISTORY_HEAD_KEEP", "2"))
_HISTORY_RECENT_KEEP = int(os.environ.get("YGG_HISTORY_RECENT_KEEP", "6"))
_HISTORY_ELIDE_CHARS = int(os.environ.get("YGG_HISTORY_ELIDE_CHARS", "600"))
_HISTORY_ELIDE_MARK = "…[history-elided]"


def _clip_for_history(text: str) -> str:
    """Clip an old message's text to a small head, marked so re-compaction is a no-op."""
    if len(text) <= _HISTORY_ELIDE_CHARS or _HISTORY_ELIDE_MARK in text:
        return text
    return text[:_HISTORY_ELIDE_CHARS] + f" {_HISTORY_ELIDE_MARK} (+{len(text) - _HISTORY_ELIDE_CHARS} chars)"


def _shrink_tool_result_content(block: dict[str, Any]) -> None:
    """Clip a tool_result block's inner content in place (string or block list)."""
    inner = block.get("content")
    if isinstance(inner, str):
        block["content"] = _clip_for_history(inner)
    elif isinstance(inner, list):
        for ib in inner:
            if isinstance(ib, dict) and isinstance(ib.get("text"), str):
                ib["text"] = _clip_for_history(ib["text"])


def _shrink_message_content(msg: dict[str, Any]) -> None:
    """Shrink one old message's bulky content IN PLACE, preserving tool_use/tool_call
    blocks (pairing) and roles. Handles both Anthropic (content = str | list of blocks
    incl. tool_use/tool_result) and OpenAI (content = str, plus a tool_calls key) shapes."""
    content = msg.get("content")
    if isinstance(content, str):
        msg["content"] = _clip_for_history(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            bt = block.get("type")
            if bt == "text" and isinstance(block.get("text"), str):
                block["text"] = _clip_for_history(block["text"])
            elif bt == "tool_result":
                _shrink_tool_result_content(block)
            # tool_use / other blocks are left intact (needed for tool pairing).
    # OpenAI 'tool' role messages carry their payload in 'content' (handled above);
    # assistant 'tool_calls' are left untouched.


def _compact_history(messages: list[dict[str, Any]]) -> None:
    """Shrink the MIDDLE of a long message history in place — everything except the
    first _HISTORY_HEAD_KEEP messages (task/setup) and the last _HISTORY_RECENT_KEEP
    (the turns the model is actively working). No messages are removed (tool pairing
    stays valid); only bulky old content is clipped. Idempotent (marked clips are
    skipped), so re-running only touches newly-aged messages."""
    n = len(messages)
    if n <= _HISTORY_HEAD_KEEP + _HISTORY_RECENT_KEEP:
        return
    for msg in messages[_HISTORY_HEAD_KEEP : n - _HISTORY_RECENT_KEEP]:
        if isinstance(msg, dict):
            _shrink_message_content(msg)

# Type alias for multimodal query content (mirrors the Anthropic Messages API).
# A plain str is treated as a single text block.  A list follows the Anthropic
# content-block schema: {"type": "text", "text": "..."} or
# {"type": "image", "source": {"type": "base64"|"url", ...}}.
QueryContent = str | list[dict[str, Any]]


def _query_text(query: QueryContent) -> str:
    """Extract the plain-text portion of a query for routing and context scoring."""
    match query:
        case str():
            return query
        case _:
            return " ".join(block.get("text", "") for block in query if block.get("type") == "text")


@dataclass
class TraceEvent:
    """A single typed event in the execution trace.

    Events form a tree via parent_event_id:
    - agent_start spawns child events (context_inject, tool_call, tool_result, routing)
    - agent_end closes the agent_start span with duration_ms
    - hop records sequential graph traversal steps

    Payload keys per event_type:
    - agent_start:     model, tools (list[str]), context (list[str]), query
    - agent_end:       text_summary (str), intent (str), iterations (int)
    - tool_call:       tool_name (str), callable_ref (str), input (dict)
    - tool_result:     tool_name (str), output_summary (str), success (bool)
    - routing:         intent (str), next_node_id (str|None), confidence (float|None)
    - context_inject:  context_names (list[str]), count (int)
    - hop:             hop (int), node_type (str), summary (str)
    - subgraph_enter:  entry_node_id (str)
    - subgraph_exit:   exit_node_id (str), summary (str)
    """

    event_type:      EventType
    session_id:      str
    node_id:         str
    node_name:       str
    timestamp:       datetime
    payload:         dict[str, Any]
    event_id:        str        = field(default_factory=lambda: str(uuid.uuid4()))
    parent_event_id: str | None = None
    duration_ms:     int | None = None


# ---------------------------------------------------------------------------
# RoutingDecision — white-box routing result
# ---------------------------------------------------------------------------

class RoutingDecision(NamedTuple):
    """LLM routing decision with explicit reasoning and confidence.

    Returned by GraphExecutor.route() / plan() so callers can inspect and
    debug every dispatch choice before (or instead of) executing.
    """

    agent_id: str
    reason: str
    confidence: float

    @property
    def low_confidence_warning(self) -> str | None:
        """Non-None when confidence is below 0.7."""
        if self.confidence < _LOW_CONFIDENCE_THRESHOLD:
            return (
                f"Low-confidence routing ({self.confidence:.0%}) — "
                "consider specifying the agent explicitly."
            )
        return None


# ---------------------------------------------------------------------------
# AgentResult — structured execution envelope
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Execution envelope returned by GraphExecutor.execute()."""

    routed_to:              str
    reason:                 str
    confidence:             float
    context_injected:       list[str]
    result:                 str
    low_confidence_warning: str | None = None


@dataclass
class WorkflowPause:
    """Represents a paused workflow waiting for external input or approval."""

    reason: str
    node_id: str
    node_name: str = ""
    token: str = field(default_factory=lambda: str(uuid.uuid4()))
    waiting_for: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalTask:
    """Inbox item created by an ApprovalNode."""

    task_id: str
    node_id: str
    token: str
    status: str = "pending"
    assignees: list[str] = field(default_factory=list)
    assigned_to: str | None = None
    waiting_for: str | None = None
    due_at: datetime | None = None
    escalation_target: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Typed workflow state carried between nodes."""

    data: dict[str, Any] = field(default_factory=dict)
    schema: dict[str, Any] = field(default_factory=dict)
    status: str = "running"
    graph_version: str = "v1"
    pending_pause: WorkflowPause | None = None
    inbox: dict[str, ApprovalTask] = field(default_factory=dict)
    idempotency_cache: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ExecutionContext — flows through the graph during a run
# ---------------------------------------------------------------------------

@dataclass
class ExecutionContext:
    """Shared mutable state for a single graph traversal.

    Every node reads from and writes to this object.
    The trace list records the full execution history as structured TraceEvent
    objects so callers can inspect, render, or replay exactly what happened.
    """

    query:      QueryContent
    session_id: str                   = field(default_factory=lambda: str(uuid.uuid4()))
    outputs:    dict[str, Any]        = field(default_factory=dict)
    trace:      list[TraceEvent]      = field(default_factory=list)
    max_hops:   int                   = 20
    hop_count:  int                   = 0

    extra_messages: list[dict[str, Any]] = field(default_factory=list)
    state: WorkflowState = field(default_factory=WorkflowState)
    allowed_tools: set[str] | None = None
    _active_subgraphs: list[str] = field(default_factory=list)

    def is_paused(self) -> bool:
        return self.state.status == "paused"

    def snapshot(self) -> dict[str, Any]:
        """Serialize the execution context for durable checkpointing."""
        return {
            "query": self.query,
            "session_id": self.session_id,
            "outputs": self.outputs,
            "trace": [
                {
                    "event_type": event.event_type,
                    "session_id": event.session_id,
                    "node_id": event.node_id,
                    "node_name": event.node_name,
                    "timestamp": event.timestamp.isoformat(),
                    "payload": event.payload,
                    "event_id": event.event_id,
                    "parent_event_id": event.parent_event_id,
                    "duration_ms": event.duration_ms,
                }
                for event in self.trace
            ],
            "max_hops": self.max_hops,
            "hop_count": self.hop_count,
            "extra_messages": self.extra_messages,
            "state": {
                "data": self.state.data,
                "schema": self.state.schema,
                "status": self.state.status,
                "graph_version": self.state.graph_version,
                "pending_pause": None if self.state.pending_pause is None else {
                    "reason": self.state.pending_pause.reason,
                    "node_id": self.state.pending_pause.node_id,
                    "node_name": self.state.pending_pause.node_name,
                    "token": self.state.pending_pause.token,
                    "waiting_for": self.state.pending_pause.waiting_for,
                    "metadata": self.state.pending_pause.metadata,
                },
                "inbox": {
                    task_id: {
                        "task_id": task.task_id,
                        "node_id": task.node_id,
                        "token": task.token,
                        "status": task.status,
                        "assignees": task.assignees,
                        "assigned_to": task.assigned_to,
                        "waiting_for": task.waiting_for,
                        "due_at": task.due_at.isoformat() if task.due_at else None,
                        "escalation_target": task.escalation_target,
                        "created_at": task.created_at.isoformat(),
                        "resolved_at": task.resolved_at.isoformat() if task.resolved_at else None,
                        "metadata": task.metadata,
                    }
                    for task_id, task in self.state.inbox.items()
                },
                "idempotency_cache": self.state.idempotency_cache,
                "metadata": self.state.metadata,
            },
            "allowed_tools": sorted(self.allowed_tools) if self.allowed_tools is not None else None,
        }

    @classmethod
    def from_snapshot(cls, data: dict[str, Any]) -> ExecutionContext:
        """Restore an execution context from snapshot data."""
        raw_state = data.get("state", {})
        pending_pause = raw_state.get("pending_pause")
        state = WorkflowState(
            data=raw_state.get("data", {}),
            schema=raw_state.get("schema", {}),
            status=raw_state.get("status", "running"),
            graph_version=raw_state.get("graph_version", "v1"),
            pending_pause=(
                WorkflowPause(
                    reason=pending_pause.get("reason", ""),
                    node_id=pending_pause.get("node_id", ""),
                    node_name=pending_pause.get("node_name", ""),
                    token=pending_pause.get("token", str(uuid.uuid4())),
                    waiting_for=pending_pause.get("waiting_for"),
                    metadata=pending_pause.get("metadata", {}),
                ) if pending_pause else None
            ),
            inbox={
                task_id: ApprovalTask(
                    task_id=item.get("task_id", task_id),
                    node_id=item.get("node_id", ""),
                    token=item.get("token", str(uuid.uuid4())),
                    status=item.get("status", "pending"),
                    assignees=item.get("assignees", []),
                    assigned_to=item.get("assigned_to"),
                    waiting_for=item.get("waiting_for"),
                    due_at=(
                        datetime.fromisoformat(item["due_at"])
                        if item.get("due_at") else None
                    ),
                    escalation_target=item.get("escalation_target"),
                    created_at=datetime.fromisoformat(item["created_at"])
                    if item.get("created_at") else datetime.now(UTC),
                    resolved_at=(
                        datetime.fromisoformat(item["resolved_at"])
                        if item.get("resolved_at") else None
                    ),
                    metadata=item.get("metadata", {}),
                )
                for task_id, item in raw_state.get("inbox", {}).items()
            },
            idempotency_cache=raw_state.get("idempotency_cache", {}),
            metadata=raw_state.get("metadata", {}),
        )
        return cls(
            query=data.get("query", ""),
            session_id=data.get("session_id", str(uuid.uuid4())),
            outputs=data.get("outputs", {}),
            trace=[
                TraceEvent(
                    event_type=item["event_type"],
                    session_id=item.get("session_id", data.get("session_id", "")),
                    node_id=item.get("node_id", ""),
                    node_name=item.get("node_name", ""),
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    payload=item.get("payload", {}),
                    event_id=item.get("event_id", str(uuid.uuid4())),
                    parent_event_id=item.get("parent_event_id"),
                    duration_ms=item.get("duration_ms"),
                )
                for item in data.get("trace", [])
            ],
            max_hops=data.get("max_hops", 20),
            hop_count=data.get("hop_count", 0),
            extra_messages=data.get("extra_messages", []),
            state=state,
            allowed_tools=set(data["allowed_tools"]) if data.get("allowed_tools") is not None else None,
        )


# ---------------------------------------------------------------------------
# Context navigation
# ---------------------------------------------------------------------------

@dataclass
class ContextSelection:
    """A scored, explainable context selection produced by ContextNavigator."""

    context:    ContextNode
    score:      float
    source:     str
    hops:       int = 0
    path:       list[str] = field(default_factory=list)
    reasons:    list[str] = field(default_factory=list)
    token_count: int = 0


@dataclass
class ContextNavigator:
    """Graph-native context retrieval with expansion, reranking, and budgeting."""

    max_hops: int = 2
    max_context_nodes: int = 8
    max_context_tokens: int = 4000
    semantic_top_k: int = 12
    per_source_limit: int = 2
    expansion_edge_types: tuple[EdgeType, ...] = (
        EdgeType.NEXT,
        EdgeType.SIMILAR_TO,
        EdgeType.MENTIONS,
        EdgeType.COVERS,
        EdgeType.PRODUCES,
    )
    path_decay: float = 0.85
    tag_weight: float = 0.15
    priority_weight: float = 0.1
    recency_weight: float = 0.1
    provenance_weight: float = 0.15
    stale_fact_penalty: float = 0.4
    exclude_stale_facts: bool = True

    async def navigate(
        self,
        store: GraphStore,
        agent_node: AgentNode,
        *,
        query: str | None = None,
        embedder: Any = None,
        session_id: str | None = None,
    ) -> list[ContextSelection]:
        """Select context for an agent using graph traversal and token budgeting."""
        direct_edges = await store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_CONTEXT)
        direct_context_edges: dict[str, Edge] = {}
        seed_map: dict[str, ContextSelection] = {}

        query_vec: list[float] | None = None
        if query and embedder:
            query_vec = _normalize(await embedder.embed_text(query))

        for edge in direct_edges:
            node = await store.get_node(edge.dst_id)
            if not isinstance(node, ContextNode) or not node.is_valid:
                continue
            if self.exclude_stale_facts and not node.is_fact_valid:
                continue
            direct_context_edges[node.node_id] = edge
            seed_map[node.node_id] = self._score_context(
                node,
                query=query,
                query_vec=query_vec,
                direct_edge=edge,
                source="attached",
                hops=0,
                path=[agent_node.node_id, node.node_id],
                path_weight=edge.weight,
                session_id=session_id,
            )

        await self._add_semantic_selections(
            store, seed_map, direct_context_edges,
            query=query, query_vec=query_vec, session_id=session_id,
        )
        await self._add_runtime_selections(
            store, seed_map, direct_context_edges,
            query=query, query_vec=query_vec, session_id=session_id,
        )

        expanded = await self._expand_contexts(
            store,
            list(seed_map.values()),
            query=query,
            query_vec=query_vec,
            direct_context_edges=direct_context_edges,
            session_id=session_id,
        )

        ranked = sorted(expanded.values(), key=lambda s: s.score, reverse=True)
        return self._pack_contexts(ranked)

    async def _add_semantic_selections(
        self,
        store: GraphStore,
        seed_map: dict[str, ContextSelection],
        direct_context_edges: dict[str, Edge],
        *,
        query: str | None,
        query_vec: list[float] | None,
        session_id: str | None,
    ) -> None:
        """Seed semantic-hit ContextNodes into `seed_map` (skipping already-seeded)."""
        if query_vec is None:
            return
        semantic_hits = await store.vector_search(
            query_vec,
            node_types=[NodeType.CONTEXT],
            top_k=self.semantic_top_k,
        )
        for rank, (node, _score) in enumerate(semantic_hits):
            if not isinstance(node, ContextNode) or node.node_id in seed_map or not node.is_valid:
                continue
            if self.exclude_stale_facts and not node.is_fact_valid:
                continue
            seed_map[node.node_id] = self._score_context(
                node,
                query=query,
                query_vec=query_vec,
                direct_edge=direct_context_edges.get(node.node_id),
                source="semantic",
                hops=0,
                path=[node.node_id],
                path_weight=max(0.5, 1.0 - rank * 0.03),
                session_id=session_id,
            )

    async def _add_runtime_selections(
        self,
        store: GraphStore,
        seed_map: dict[str, ContextSelection],
        direct_context_edges: dict[str, Edge],
        *,
        query: str | None,
        query_vec: list[float] | None,
        session_id: str | None,
    ) -> None:
        """Seed the session's runtime-materialised ContextNodes into `seed_map`."""
        if not session_id:
            return
        runtime_nodes = await store.list_nodes(node_type=NodeType.CONTEXT, group_id=session_id)
        for node in runtime_nodes:
            if not isinstance(node, ContextNode):
                continue
            if node.attributes.get("origin") != "runtime":
                continue
            selection = self._score_context(
                node,
                query=query,
                query_vec=query_vec,
                direct_edge=direct_context_edges.get(node.node_id),
                source="runtime",
                hops=0,
                path=[node.node_id],
                path_weight=1.0,
                session_id=session_id,
            )
            existing = seed_map.get(node.node_id)
            if existing is None or selection.score > existing.score:
                seed_map[node.node_id] = selection

    async def _expand_contexts(
        self,
        store: GraphStore,
        seeds: list[ContextSelection],
        *,
        query: str | None,
        query_vec: list[float] | None,
        direct_context_edges: dict[str, Edge],
        session_id: str | None,
    ) -> dict[str, ContextSelection]:
        candidates: dict[str, ContextSelection] = {seed.context.node_id: seed for seed in seeds}
        frontier: deque[tuple[AnyNode, int, list[str], float, str]] = deque(
            (seed.context, 0, list(seed.path), 1.0, seed.source)
            for seed in seeds
        )
        seen_paths: set[tuple[str, int]] = set()

        while frontier:
            current, hops, path, path_weight, origin = frontier.popleft()
            if hops >= self.max_hops:
                continue
            key = (current.node_id, hops)
            if key in seen_paths:
                continue
            seen_paths.add(key)

            for edge in await store.get_edges(current.node_id, direction="both"):
                if edge.edge_type not in self.expansion_edge_types:
                    continue
                neighbor_id = edge.dst_id if edge.src_id == current.node_id else edge.src_id
                neighbor = await store.get_node(neighbor_id)
                if neighbor is None or not neighbor.is_valid:
                    continue

                next_path = path + [neighbor_id]
                next_weight = path_weight * max(edge.weight, 0.1)
                next_hops = hops + 1

                if isinstance(neighbor, ContextNode):
                    if self.exclude_stale_facts and not neighbor.is_fact_valid:
                        continue
                    selection = self._score_context(
                        neighbor,
                        query=query,
                        query_vec=query_vec,
                        direct_edge=direct_context_edges.get(neighbor.node_id),
                        source=f"{origin}+graph",
                        hops=next_hops,
                        path=next_path,
                        path_weight=next_weight,
                        session_id=session_id,
                    )
                    existing = candidates.get(neighbor.node_id)
                    if existing is None or selection.score > existing.score:
                        candidates[neighbor.node_id] = selection

                frontier.append((neighbor, next_hops, next_path, next_weight, origin))

        return candidates

    def _pack_contexts(self, ranked: list[ContextSelection]) -> list[ContextSelection]:
        packed: list[ContextSelection] = []
        total_tokens = 0
        per_source: dict[str, int] = {}

        for selection in ranked:
            source_key = selection.context.source or selection.source or "unknown"
            if per_source.get(source_key, 0) >= self.per_source_limit:
                continue
            if len(packed) >= self.max_context_nodes:
                break
            if packed and total_tokens + selection.token_count > self.max_context_tokens:
                continue

            packed.append(selection)
            total_tokens += selection.token_count
            per_source[source_key] = per_source.get(source_key, 0) + 1

        return packed

    def _score_context(  # noqa: PLR0913 — each parameter is a distinct scoring input
        self,
        ctx: ContextNode,
        *,
        query: str | None,
        query_vec: list[float] | None,
        direct_edge: Edge | None,
        source: str,
        hops: int,
        path: list[str],
        path_weight: float,
        session_id: str | None,
    ) -> ContextSelection:
        semantic = 0.5
        if query_vec is not None and ctx.embedding:
            semantic = max(0.0, _cosine(query_vec, ctx.embedding))

        direct_affinity = direct_edge.weight if direct_edge is not None else 0.5
        path_bonus = (self.path_decay ** hops) * max(path_weight, 0.1)
        priority_bonus = ctx.priority * self.priority_weight
        tag_bonus = self._tag_overlap_bonus(query, ctx)
        recency_bonus = self._recency_bonus(ctx)
        provenance_bonus = self.provenance_weight if ctx.attributes.get("origin") == "runtime" else 0.0
        if session_id and ctx.group_id == session_id:
            provenance_bonus += self.provenance_weight

        score = semantic * direct_affinity * path_bonus
        score += priority_bonus + tag_bonus + recency_bonus + provenance_bonus
        if not ctx.is_fact_valid:
            score -= self.stale_fact_penalty

        reasons = [
            f"semantic={semantic:.2f}",
            f"affinity={direct_affinity:.2f}",
            f"hops={hops}",
        ]
        if priority_bonus:
            reasons.append(f"priority+={priority_bonus:.2f}")
        if tag_bonus:
            reasons.append(f"tags+={tag_bonus:.2f}")
        if recency_bonus:
            reasons.append(f"recent+={recency_bonus:.2f}")
        if provenance_bonus:
            reasons.append(f"runtime+={provenance_bonus:.2f}")
        if not ctx.is_fact_valid:
            reasons.append(f"stale-={self.stale_fact_penalty:.2f}")

        return ContextSelection(
            context=ctx,
            score=score,
            source=source,
            hops=hops,
            path=path,
            reasons=reasons,
            token_count=self._estimate_tokens(ctx),
        )

    def _estimate_tokens(self, ctx: ContextNode) -> int:
        if ctx.token_count > 0:
            return ctx.token_count
        content = ctx.content or ""
        return max(1, len(content.split()) + len(content) // 12)

    def _tag_overlap_bonus(self, query: str | None, ctx: ContextNode) -> float:
        if not query or not ctx.tags:
            return 0.0
        query_lower = query.lower()
        overlap = sum(1 for tag in ctx.tags if tag.lower() in query_lower)
        return overlap * self.tag_weight

    def _recency_bonus(self, ctx: ContextNode) -> float:
        age_s = (datetime.now(UTC) - ctx.valid_at).total_seconds()
        if age_s <= _HOUR_SECONDS:
            return self.recency_weight
        if age_s <= _DAY_SECONDS:
            return self.recency_weight / 2
        return 0.0


# ---------------------------------------------------------------------------
# ComposedAgent — runtime snapshot of an agent's composition
# ---------------------------------------------------------------------------

@dataclass
class ComposedAgent:
    """The fully-resolved runtime configuration for one AgentNode invocation.

    Built by AgentComposer.compose() via graph traversal — not hardcoded.
    """

    agent_node: AgentNode
    tools:      list[ToolNode]
    context:    list[ContextNode]
    context_selection: list[ContextSelection]
    prompt:     PromptNode | None
    delegates:  list[AgentNode]

    def build_system_prompt(self, **prompt_vars: Any) -> str:
        """Assemble the system prompt from the prompt template + context nodes.

        Image context nodes (content_type == "image") are excluded here — they
        are injected as multimodal content blocks in the user message instead.
        """
        parts: list[str] = []

        if self.prompt:
            parts.append(self.prompt.render(**prompt_vars))
        elif self.agent_node.system_prompt:
            parts.append(self.agent_node.system_prompt)

        text_context = [ctx for ctx in self.context if ctx.content_type != "image"]
        if text_context:
            parts.append("\n\n## Relevant Context\n")
            for ctx in text_context:
                header = f"### {ctx.name}" if ctx.name else "###"
                if ctx.source:
                    header += f" (source: {ctx.source})"
                parts.append(f"{header}\n{ctx.content}")

        return "\n".join(parts)

    def build_image_context_blocks(self) -> list[dict[str, Any]]:
        """Return Anthropic-format image blocks for image context nodes."""
        blocks: list[dict[str, Any]] = []
        for ctx in self.context:
            if ctx.content_type != "image":
                continue
            source_type = ctx.attributes.get("image_source", "url")
            if source_type == "base64":
                media_type = ctx.attributes.get("media_type", "image/jpeg")
                blocks.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": ctx.content},
                })
            else:
                blocks.append({
                    "type": "image",
                    "source": {"type": "url", "url": ctx.content},
                })
        return blocks

    def build_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool definitions for all composed tools (backend-agnostic format)."""
        return [t.to_tool_schema() for t in self.tools]

    def explain(self) -> dict[str, Any]:
        """Return a structured explanation of the composed runtime agent."""
        prompt_source = "none"
        prompt_name = ""
        if self.prompt is not None:
            prompt_source = "prompt_node"
            prompt_name = self.prompt.name
        elif self.agent_node.system_prompt:
            prompt_source = "agent_node"

        return {
            "agent": {
                "node_id": self.agent_node.node_id,
                "name": self.agent_node.name,
                "model": self.agent_node.model,
            },
            "prompt": {
                "source": prompt_source,
                "name": prompt_name,
            },
            "tools": [
                {
                    "node_id": tool.node_id,
                    "name": tool.name,
                    "callable_ref": tool.callable_ref,
                    "description": tool.description,
                }
                for tool in self.tools
            ],
            "context": [
                {
                    "node_id": selection.context.node_id,
                    "name": selection.context.name,
                    "source": selection.source,
                    "score": round(selection.score, 4),
                    "hops": selection.hops,
                    "path": selection.path,
                    "reasons": selection.reasons,
                    "token_count": selection.token_count,
                }
                for selection in self.context_selection
            ],
            "delegates": [
                {
                    "node_id": delegate.node_id,
                    "name": delegate.name,
                }
                for delegate in self.delegates
            ],
        }


# ---------------------------------------------------------------------------
# AgentComposer — discovers composition from the graph
# ---------------------------------------------------------------------------

class AgentComposer:
    """Assembles an agent's runtime configuration by traversing graph edges.

    This is the architectural core: composition IS traversal.
    Adding a tool to an agent = upsert_edge(HAS_TOOL, agent, tool). No code change.

    Pass an Embedder instance to enable query-time context re-ranking: context nodes
    are scored by edge.weight * cosine(query, ctx) + priority_bonus instead of
    static edge weight alone.
    """

    def __init__(
        self,
        store: GraphStore,
        embedder: Any = None,
        context_navigator: ContextNavigator | None = None,
    ) -> None:
        self.store = store
        self._embedder = embedder
        self._context_navigator = context_navigator or ContextNavigator()

    async def compose(
        self,
        agent_node: AgentNode,
        query: str | None = None,
        session_id: str | None = None,
    ) -> ComposedAgent:
        node_id = agent_node.node_id

        tool_edges = await self.store.get_edges(node_id, edge_type=EdgeType.HAS_TOOL)
        tool_edges.sort(key=lambda e: e.weight, reverse=True)
        raw_tool_nodes = await asyncio.gather(*[self.store.get_node(e.dst_id) for e in tool_edges])
        tools: list[ToolNode] = [
            n for n in raw_tool_nodes if isinstance(n, ToolNode) and n.is_valid
        ]

        context_selection = await self._context_navigator.navigate(
            self.store,
            agent_node,
            query=query,
            embedder=self._embedder,
            session_id=session_id,
        )
        context = [selection.context for selection in context_selection]

        prompt_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.HAS_PROMPT)
        prompt = next((n for n in prompt_nodes if isinstance(n, PromptNode)), None)

        delegate_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.DELEGATES_TO)
        delegates = [n for n in delegate_nodes if isinstance(n, AgentNode) and n.is_valid]

        return ComposedAgent(
            agent_node=agent_node,
            tools=tools,
            context=context,
            context_selection=context_selection,
            prompt=prompt,
            delegates=delegates,
        )


# ---------------------------------------------------------------------------
# Router prompt templates
# ---------------------------------------------------------------------------

_ROUTER_SYSTEM = (
    "You are a routing classifier. "
    "Respond with a single valid JSON object and nothing else."
)

_ROUTER_TEMPLATE = """\
Select the best agent for this task.

Available agents:
{agent_list}

Task: {query}

Respond with JSON only:
{{"agent": "<id>", "reason": "<one sentence explaining why>", "confidence": <0.0-1.0>}}"""

_INTENT_TEMPLATE = """\
Given this agent output, select the best routing intent.

Available intents:
{intents}
- default

Agent output:
{text}

Respond with JSON only:
{{"intent": "<selected>", "reason": "<brief reason>"}}"""


# ---------------------------------------------------------------------------
# ExecutionOptions — security and tenancy controls for run()
# ---------------------------------------------------------------------------

class ExecutionOptions(NamedTuple):
    """Runtime controls for GraphExecutor.run()."""

    allowed_tools: set[str] | None = None


@dataclass
class ResumeReadiness:
    """Diagnosis of whether a checkpointed/paused context is safe to resume."""

    status: str
    is_paused: bool
    is_stale: bool
    last_event_at: datetime | None
    seconds_since_last_event: float | None
    available: list[str]
    unrecoverable: list[str]

    @property
    def ok(self) -> bool:
        """True when nothing blocks an automatic resume."""
        return not self.is_stale and not self.unrecoverable


# ---------------------------------------------------------------------------
# GraphExecutor — dispatches nodes and traverses the graph
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Schema-directed coercion of tool inputs
# ---------------------------------------------------------------------------
# Small local models routinely emit the RIGHT arguments in the WRONG JSON type —
# most often an array serialised as a comma-separated string
# (`{"actions": "show,hide"}` for `actions: {type: "array"}`), and scalars as
# strings (`{"limit": "5"}`). Input validation runs before the tool is called, so
# such a turn dies as `tool_input.actions must be an array` and the work is lost even
# though the model's INTENT was unambiguous and the fix mechanical.
#
# Coerce only where the declared schema states the target type, and only from a
# lossless textual form. Anything already the right type is untouched; nothing is
# invented; an undeclared key is left exactly as sent (validation still judges it).
# Token spellings a local model may use for JSON booleans in stringified args.
_BOOLEAN_BY_TOKEN: dict[str, bool] = {
    "true": True, "yes": True, "1": True, "on": True,
    "false": False, "no": False, "0": False, "off": False,
}
_SCALAR_PARSERS: dict[str, Callable[[str], Any]] = {"integer": int, "number": float}


def _coerce_scalar(value: Any, target: str) -> Any:
    """Best-effort scalar coercion; returns `value` unchanged when unsure."""
    if target == "boolean":
        if isinstance(value, str):
            return _BOOLEAN_BY_TOKEN.get(value.strip().lower(), value)
        return value
    parser = _SCALAR_PARSERS.get(target)
    if parser is None or not isinstance(value, str):
        return value
    try:
        return parser(value.strip())
    except ValueError:
        return value


def _coerce_array_value(value: Any, spec: dict[str, Any]) -> Any:
    """Coerce a value declared as `array`: CSV string -> items, lone scalar -> [value].

    Item types declared as integer/number/boolean get per-item scalar coercion.
    """
    if isinstance(value, str):
        new = [p for p in (part.strip() for part in value.split(",")) if p]
    elif value is not None:
        new = [value]           # a lone scalar for a list-typed param
    else:
        return value
    item_type = (spec.get("items") or {}).get("type")
    if item_type in ("integer", "number", "boolean"):
        new = [_coerce_scalar(v, item_type) for v in new]
    return new


def coerce_to_schema(payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Return `payload` with values nudged to the types its schema declares.

    Handles the shapes a local model actually gets wrong: a comma-separated (or
    single) string where an array is declared, and a stringified number/bool where a
    scalar is declared. Returns the SAME object when nothing needed changing, so the
    common path allocates nothing."""
    props = (schema or {}).get("properties")
    if not isinstance(props, dict) or not isinstance(payload, dict):
        return payload
    out: dict[str, Any] | None = None
    for key, value in payload.items():
        spec = props.get(key)
        if not isinstance(spec, dict):
            continue
        declared = spec.get("type")
        new = value
        if declared == "array" and not isinstance(value, list):
            new = _coerce_array_value(value, spec)
        elif declared in ("integer", "number", "boolean"):
            new = _coerce_scalar(value, declared)
        if new is not value:
            if out is None:
                out = dict(payload)
            out[key] = new
    return out if out is not None else payload


# Declarative dispatch table for constraint/route rule operators.
_RULE_COMPARATORS: dict[str, Callable[[Any, Any], bool]] = {
    "exists":     lambda left, right: left is not None,
    "truthy":     lambda left, right: bool(left),
    "contains":   lambda left, right: left is not None and right in left,
    "not_equals": lambda left, right: bool(left != right),
    "in":         lambda left, right: right is not None and left in right,
    "regex":      lambda left, right: (
        isinstance(left, str) and isinstance(right, str) and re.search(right, left) is not None
    ),
    "gt":         lambda left, right: bool(left > right),
    "gte":        lambda left, right: bool(left >= right),
    "lt":         lambda left, right: bool(left < right),
    "lte":        lambda left, right: bool(left <= right),
}


@dataclass
class _AgentTurnLoop:
    """Mutable per-invocation state for GraphExecutor._execute_agent's turn loop."""

    messages:              list[dict[str, Any]]
    max_tokens:            int
    iterations:            int = 0
    token_escalations:     int = 0
    tool_call_corrections: int = 0
    continuation_nudges:   int = 0
    completion_nudges:     int = 0


class GraphExecutor:
    """Executes a query by traversing the agent graph.

    Node dispatch is based on node_type:
    - AGENT   → compose + LLM call + tool handling + routing
    - TOOL    → call registered Python callable
    - CONTEXT → return content (passive)
    - GRAPH   → recursive sub-graph execution
    - PROMPT  → render template (usually consumed by AGENT, not executed directly)
    """

    def __init__(
        self,
        store:        GraphStore,
        composer:     AgentComposer | None = None,
        backend:      LLMBackend | None = None,
        embedder:     Any = None,
        context_navigator: ContextNavigator | None = None,
        router_model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        self.store        = store
        self.composer     = composer or AgentComposer(
            store, embedder=embedder, context_navigator=context_navigator
        )
        self._backend: LLMBackend | None = backend or default_backend()
        self._router_model = router_model

        self._tool_fns: dict[str, Any] = {}
        self._event_hooks: list[Callable[[TraceEvent, ExecutionContext], Any]] = []

    def register_tool(self, callable_ref: str, fn: Any) -> None:
        """Register a callable under its dotted ref string."""
        self._tool_fns[callable_ref] = fn

    def add_event_hook(self, fn: Callable[[TraceEvent, ExecutionContext], Any]) -> None:
        """Register a callback invoked for every emitted event."""
        self._event_hooks.append(fn)

    def _require_backend(self) -> LLMBackend:
        """The LLM backend; executors that delegate the LLM loop elsewhere have none."""
        if self._backend is None:
            raise RuntimeError(f"{type(self).__name__} has no LLM backend configured")
        return self._backend

    # ------------------------------------------------------------------
    # Trace emission helper
    # ------------------------------------------------------------------

    def _emit(
        self,
        ctx:             ExecutionContext,
        event_type:      EventType,
        node_id:         str,
        node_name:       str,
        payload:         dict[str, Any],
        event_id:        str | None = None,
        parent_event_id: str | None = None,
        duration_ms:     int | None = None,
    ) -> TraceEvent:
        """Create and append a TraceEvent to ctx.trace. Returns the event."""
        event = TraceEvent(
            event_type=event_type,
            session_id=ctx.session_id,
            node_id=node_id,
            node_name=node_name,
            timestamp=datetime.now(UTC),
            payload=payload,
            event_id=event_id or str(uuid.uuid4()),
            parent_event_id=parent_event_id,
            duration_ms=duration_ms,
        )
        ctx.trace.append(event)
        for hook in getattr(self, "_event_hooks", []):
            hook_result = hook(event, ctx)
            if asyncio.iscoroutine(hook_result):
                asyncio.create_task(hook_result)
        return event

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    async def run(  # noqa: PLR0913, PLR0917 — public execution entry point; options are distinct axes
        self,
        entry_node_id: str,
        query: QueryContent,
        strategy: str = "sequential",
        max_hops: int = 20,
        extra_messages: list[dict[str, Any]] | None = None,
        execution_context: ExecutionContext | None = None,
        state: dict[str, Any] | None = None,
        allowed_tools: list[str] | None = None,
        options: ExecutionOptions | None = None,
        **kwargs: Any,
    ) -> ExecutionContext:
        """Execute a query starting from entry_node_id."""
        ctx = execution_context or ExecutionContext(query=query, max_hops=max_hops)
        ctx.query = query
        ctx.max_hops = max_hops
        if extra_messages:
            ctx.extra_messages = list(extra_messages)
        if state:
            ctx.state.data.update(state)
        if allowed_tools is not None:
            ctx.allowed_tools = set(allowed_tools)
        if options is not None and options.allowed_tools is not None:
            ctx.allowed_tools = options.allowed_tools
        try:
            entry = await self.store.get_node(entry_node_id)
            if entry is None:
                raise ValueError(
                    f"Entry node {entry_node_id!r} not found in graph store.\n"
                    "Hint: use `agent.node_id` (not `agent.name`) as the entry_node_id,\n"
                    "or call `await store.list_nodes()` to inspect what is in the store."
                )
            match strategy:
                case "sequential":
                    await self._run_sequential(entry, ctx)
                case "parallel":
                    await self._run_parallel(entry, ctx)
                case "topological":
                    await self._run_topological(entry_node_id, ctx)
                case _:
                    raise ValueError(f"Unknown strategy: {strategy!r}")
        except Exception as exc:
            _log.error(
                "Executor fatal error [session=%s node=%s]: %s",
                ctx.session_id, entry_node_id, exc, exc_info=True,
            )
            self._emit(
                ctx,
                "error",
                entry_node_id,
                "",
                payload={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )
            raise

        return ctx

    async def resume(
        self,
        entry_node_id: str,
        ctx: ExecutionContext,
        *,
        query: QueryContent | None = None,
        strategy: str = "sequential",
    ) -> ExecutionContext:
        """Resume a paused workflow context."""
        if query is not None:
            ctx.query = query
        ctx.state.status = "running"
        pause = ctx.state.pending_pause
        ctx.state.pending_pause = None
        if pause is not None:
            self._emit(
                ctx,
                "resume",
                pause.node_id,
                pause.node_name,
                payload={"token": pause.token, "waiting_for": pause.waiting_for},
            )
            # If the pause was a pause_before, clear that flag on the node so it
            # doesn't immediately re-pause when revisited during the resumed run.
            if pause.reason == "pause_before":
                try:
                    paused_node = await self.store.get_node(pause.node_id)
                    if isinstance(paused_node, AgentNode):
                        paused_node.pause_before = False
                        await self.store.upsert_node(paused_node)
                except Exception:  # noqa: BLE001 — best effort; worst case the node re-pauses
                    _log.debug("could not clear pause_before on %s", pause.node_id, exc_info=True)
        return await self.run(
            entry_node_id,
            ctx.query,
            strategy=strategy,
            max_hops=ctx.max_hops,
            execution_context=ctx,
        )

    def inspect_resume(
        self,
        ctx: ExecutionContext,
        *,
        stale_after_seconds: float = 1200.0,
        required_outputs: list[str] | None = None,
        now: datetime | None = None,
    ) -> ResumeReadiness:
        """Diagnose whether ``ctx`` is safe to resume — no side effects."""
        last_event_at = max((e.timestamp for e in ctx.trace), default=None)
        if last_event_at is None:
            seconds_since: float | None = None
            is_stale = False
        else:
            current = now or datetime.now(UTC)
            seconds_since = (current - last_event_at).total_seconds()
            is_stale = seconds_since > stale_after_seconds

        available: list[str] = []
        unrecoverable: list[str] = []
        for key in required_outputs or []:
            if key in ctx.outputs or key in ctx.state.data:
                available.append(key)
            else:
                unrecoverable.append(key)

        return ResumeReadiness(
            status=ctx.state.status,
            is_paused=ctx.is_paused(),
            is_stale=is_stale,
            last_event_at=last_event_at,
            seconds_since_last_event=seconds_since,
            available=available,
            unrecoverable=unrecoverable,
        )

    async def batch(  # noqa: PLR0913 — deprecated public API; signature kept stable
        self,
        agent_node_id: str,
        items: list[Any],
        query_fn: Callable[[Any], str],
        *,
        context_fn: Callable[[Any], str | None] | None = None,
        reduce_fn: Callable[[list[Any]], Any] | None = None,
        on_progress: Callable[[Any], Any] | None = None,
        concurrency: int = 5,
        checkpoint: bool = True,
        strategy: str = "sequential",
    ) -> Any:
        """Run an agent over a list of items with concurrency control."""
        import warnings

        from yggdrasil_lm.batch import BatchExecutor
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            _batch = BatchExecutor(self.store, self, concurrency=concurrency)
        return await _batch.run(
            agent_node_id,
            items,
            query_fn,
            context_fn=context_fn,
            reduce_fn=reduce_fn,
            on_progress=on_progress,
            checkpoint=checkpoint,
            strategy=strategy,
        )

    async def checkpoint_context(
        self,
        ctx: ExecutionContext,
        *,
        name: str = "Execution checkpoint",
        max_inline_chars: int | None = None,
    ) -> ContextNode:
        """Persist a resumable execution snapshot as a runtime context node."""
        snap = ctx.snapshot()
        if max_inline_chars is not None:
            snap = await self._offload_snapshot_blobs(ctx, snap, max_inline_chars)
        checkpoint = ContextNode(
            name=name,
            description="Serialized execution checkpoint",
            content=json.dumps(snap, default=str),
            content_type="json",
            source="checkpoint",
            group_id=ctx.session_id,
            attributes={
                "origin": "checkpoint",
                "session_id": ctx.session_id,
                "graph_version": ctx.state.graph_version,
            },
        )
        await self.store.upsert_node(checkpoint)
        self._emit(
            ctx,
            "checkpoint",
            checkpoint.node_id,
            checkpoint.name,
            payload={"checkpoint_node_id": checkpoint.node_id},
        )
        return checkpoint

    async def _offload_snapshot_blobs(
        self,
        ctx: ExecutionContext,
        snap: dict[str, Any],
        max_inline_chars: int,
    ) -> dict[str, Any]:
        """Replace oversized top-level snapshot values with blob node refs."""
        async def offload(value: Any) -> Any:
            try:
                encoded = json.dumps(value, default=str)
            except (TypeError, ValueError):
                return value
            if len(encoded) <= max_inline_chars:
                return value
            blob = ContextNode(
                name="Checkpoint blob",
                description="Offloaded checkpoint payload",
                content=encoded,
                content_type="json",
                source="checkpoint",
                group_id=ctx.session_id,
                attributes={"origin": "checkpoint_blob", "session_id": ctx.session_id},
            )
            await self.store.upsert_node(blob)
            return {"$ygg_blob": blob.node_id}

        outputs = snap.get("outputs")
        if isinstance(outputs, dict):
            for key, value in list(outputs.items()):
                outputs[key] = await offload(value)
        state_data = snap.get("state", {}).get("data")
        if isinstance(state_data, dict):
            for key, value in list(state_data.items()):
                state_data[key] = await offload(value)
        return snap

    async def load_checkpoint(self, checkpoint_node_id: str) -> ExecutionContext:
        """Restore an execution context from a checkpoint node."""
        node = await self.store.get_node(checkpoint_node_id)
        if not isinstance(node, ContextNode):
            raise ValueError(f"Checkpoint node not found: {checkpoint_node_id}")
        snap = json.loads(node.content)
        await self._rehydrate_snapshot_blobs(snap)
        return ExecutionContext.from_snapshot(snap)

    async def _rehydrate_snapshot_blobs(self, snap: dict[str, Any]) -> None:
        """Inverse of ``_offload_snapshot_blobs`` — resolve ``$ygg_blob`` refs."""
        async def resolve(value: Any) -> Any:
            if isinstance(value, dict) and set(value) == {"$ygg_blob"}:
                blob = await self.store.get_node(value["$ygg_blob"])
                if not isinstance(blob, ContextNode):
                    raise ValueError(
                        f"Checkpoint blob node missing: {value['$ygg_blob']}"
                    )
                return json.loads(blob.content)
            return value

        outputs = snap.get("outputs")
        if isinstance(outputs, dict):
            for key, value in list(outputs.items()):
                outputs[key] = await resolve(value)
        state_data = snap.get("state", {}).get("data")
        if isinstance(state_data, dict):
            for key, value in list(state_data.items()):
                state_data[key] = await resolve(value)

    async def resume_from_checkpoint(
        self,
        checkpoint_node_id: str,
        entry_node_id: str,
        *,
        query: QueryContent | None = None,
        strategy: str = "sequential",
    ) -> ExecutionContext:
        """Load a checkpointed context and resume execution."""
        ctx = await self.load_checkpoint(checkpoint_node_id)
        return await self.resume(entry_node_id, ctx, query=query, strategy=strategy)

    def _resolve_json_path(self, payload: Any, path: str) -> Any:
        """Resolve a dotted JSON path against a payload dict."""
        current: Any = payload
        for part in [p for p in path.split(".") if p]:
            match current:
                case {} if part in current:
                    current = current[part]
                case _:
                    return None
        return current

    def _payload_for_source(
        self,
        source: str,
        *,
        state: WorkflowState,
        result: Any = None,
        input_payload: Any = None,
        output_payload: Any = None,
    ) -> Any:
        match source:
            case "result":
                return result
            case "input":
                return input_payload
            case "output":
                return output_payload
            case _:
                return state.data

    def _compare_values(self, operator: str, left: Any, right: Any) -> bool:
        comparator = _RULE_COMPARATORS.get(operator)
        if comparator is None:
            return bool(left == right)   # unknown operator falls back to equality
        return comparator(left, right)

    def _evaluate_constraint_rule(
        self,
        rule: ConstraintRule,
        *,
        state: WorkflowState,
        result: Any = None,
        input_payload: Any = None,
        output_payload: Any = None,
    ) -> bool:
        source_data = self._payload_for_source(
            rule.source,
            state=state,
            result=result,
            input_payload=input_payload,
            output_payload=output_payload,
        )
        left = self._resolve_json_path(source_data, rule.path) if rule.path else source_data
        right = rule.value
        if rule.compare_to_source:
            compare_data = self._payload_for_source(
                rule.compare_to_source,
                state=state,
                result=result,
                input_payload=input_payload,
                output_payload=output_payload,
            )
            right = self._resolve_json_path(compare_data, rule.compare_to_path) if rule.compare_to_path else compare_data
        return self._compare_values(rule.operator, left, right)

    def _evaluate_route_rule(
        self,
        rule: RouteRule,
        *,
        result: dict[str, Any],
        state: WorkflowState,
    ) -> bool:
        source_data = state.data if rule.source == "state" else result
        return self._compare_values(
            rule.operator,
            self._resolve_json_path(source_data, rule.path) if rule.path else source_data,
            rule.value,
        )

    def _describe_constraint_rule(
        self,
        rule: ConstraintRule,
        *,
        state: WorkflowState,
        result: Any = None,
        input_payload: Any = None,
        output_payload: Any = None,
    ) -> dict[str, Any]:
        source_data = self._payload_for_source(
            rule.source,
            state=state,
            result=result,
            input_payload=input_payload,
            output_payload=output_payload,
        )
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data
        expected = rule.value
        if rule.compare_to_source:
            compare_data = self._payload_for_source(
                rule.compare_to_source,
                state=state,
                result=result,
                input_payload=input_payload,
                output_payload=output_payload,
            )
            expected = (
                self._resolve_json_path(compare_data, rule.compare_to_path)
                if rule.compare_to_path else compare_data
            )
        matched = self._compare_values(rule.operator, actual, expected)
        return {
            "name": rule.name,
            "source": rule.source,
            "path": rule.path,
            "operator": rule.operator,
            "actual": actual,
            "expected": expected,
            "matched": matched,
            "compare_to_source": rule.compare_to_source,
            "compare_to_path": rule.compare_to_path,
            "message": rule.message,
        }

    def _describe_route_rule(
        self,
        rule: RouteRule,
        *,
        state: WorkflowState,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        source_data = state.data if rule.source == "state" else result
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data
        matched = self._compare_values(rule.operator, actual, rule.value)
        return {
            "name": rule.name,
            "source": rule.source,
            "path": rule.path,
            "operator": rule.operator,
            "actual": actual,
            "expected": rule.value,
            "matched": matched,
            "priority": rule.priority,
            "target_node_id": rule.target_node_id,
            "pause_on_match": rule.pause_on_match,
        }

    async def _validate_constraint_rules(
        self,
        node: AgentNode,
        *,
        ctx: ExecutionContext,
        result: Any = None,
        input_payload: Any = None,
        output_payload: Any = None,
        parent_event_id: str | None = None,
    ) -> None:
        for rule in node.constraint_rules:
            if rule.source in {"result", "output"} and result is None and output_payload is None:
                continue
            if self._evaluate_constraint_rule(
                rule,
                state=ctx.state,
                result=result,
                input_payload=input_payload,
                output_payload=output_payload,
            ):
                continue
            message = rule.message or f"Constraint {rule.name or rule.path or rule.operator!r} failed"
            self._emit(
                ctx,
                "validation",
                node.node_id,
                node.name or "",
                payload={"success": False, "error": message, "constraint": rule.name},
                parent_event_id=parent_event_id,
            )
            raise ValueError(message)

    def _evaluate_decision_table(
        self,
        table: DecisionTable,
        *,
        state: WorkflowState,
        result: dict[str, Any],
    ) -> DecisionRule | None:
        for rule in sorted(table.rules, key=lambda item: item.priority, reverse=True):
            if all(
                self._evaluate_constraint_rule(condition, state=state, result=result)
                for condition in rule.conditions
            ):
                return rule
        return None

    async def _pause_execution(
        self,
        ctx: ExecutionContext,
        node: AnyNode,
        *,
        reason: str,
        waiting_for: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pause = WorkflowPause(
            reason=reason,
            node_id=node.node_id,
            node_name=node.name or "",
            waiting_for=waiting_for,
            metadata=metadata or {},
        )
        ctx.state.pending_pause = pause
        ctx.state.status = "paused"
        self._emit(
            ctx,
            "pause",
            node.node_id,
            node.name or "",
            payload={
                "reason": reason,
                "token": pause.token,
                "waiting_for": waiting_for,
                "metadata": pause.metadata,
            },
        )

    def _validate_object_schema(
        self,
        payload: Any,
        schema: dict[str, Any],
        *,
        label: str,
    ) -> None:
        """Validate an `object`-typed payload: shape, required keys, property types."""
        if not isinstance(payload, dict):
            raise ValueError(f"{label} must be an object")
        for key in schema.get("required", []):
            if key not in payload:
                raise ValueError(f"{label} missing required field {key!r}")
        for key, subschema in schema.get("properties", {}).items():
            if key in payload:
                self._validate_against_schema(payload[key], subschema, label=f"{label}.{key}")

    def _validate_array_schema(
        self,
        payload: Any,
        schema: dict[str, Any],
        *,
        label: str,
    ) -> None:
        """Validate an `array`-typed payload: shape and per-item recursion."""
        if not isinstance(payload, list):
            raise ValueError(f"{label} must be an array")
        for idx, item in enumerate(payload):
            self._validate_against_schema(item, schema.get("items", {}), label=f"{label}[{idx}]")

    def _validate_against_schema(
        self,
        payload: Any,
        schema: dict[str, Any],
        *,
        label: str,
    ) -> None:
        if not schema:
            return
        schema_type = schema.get("type")
        match schema_type:
            case "object":
                self._validate_object_schema(payload, schema, label=label)
            case "array":
                self._validate_array_schema(payload, schema, label=label)
            case "string" if not isinstance(payload, str):
                raise ValueError(f"{label} must be a string")
            case "integer" if not isinstance(payload, int):
                raise ValueError(f"{label} must be an integer")
            case "number" if not isinstance(payload, (int, float)):
                raise ValueError(f"{label} must be a number")
            case "boolean" if not isinstance(payload, bool):
                raise ValueError(f"{label} must be a boolean")

    async def _validate_node_schemas(
        self,
        node: AnyNode,
        *,
        input_payload: Any = None,
        output_payload: Any = None,
        ctx: ExecutionContext,
        parent_event_id: str | None = None,
    ) -> None:
        try:
            match node:
                case ToolNode():
                    if input_payload is not None:
                        self._validate_against_schema(input_payload, node.input_schema, label="tool_input")
                    if output_payload is not None:
                        self._validate_against_schema(output_payload, node.output_schema, label="tool_output")
                case AgentNode():
                    state_schema = node.state_schema or ctx.state.schema
                    if state_schema:
                        self._validate_against_schema(ctx.state.data, state_schema, label="state")
                    await self._validate_constraint_rules(
                        node,
                        ctx=ctx,
                        result=output_payload,
                        input_payload=input_payload,
                        output_payload=output_payload,
                        parent_event_id=parent_event_id,
                    )
            validates = await self.store.get_edges(node.node_id, edge_type=EdgeType.VALIDATES, direction="in")
            for edge in validates:
                schema_node = await self.store.get_node(edge.src_id)
                if not isinstance(schema_node, SchemaNode):
                    continue
                phase = edge.attributes.get("phase", "output")
                payload = output_payload if phase == "output" else input_payload
                if payload is not None:
                    self._validate_against_schema(payload, schema_node.json_schema, label=f"{phase}_payload")
        except Exception as exc:
            self._emit(
                ctx,
                "validation",
                node.node_id,
                node.name or "",
                payload={"success": False, "error": str(exc)},
                parent_event_id=parent_event_id,
            )
            raise
        self._emit(
            ctx,
            "validation",
            node.node_id,
            node.name or "",
            payload={"success": True},
            parent_event_id=parent_event_id,
        )

    # ------------------------------------------------------------------
    # Sequential (DFS)
    # ------------------------------------------------------------------

    async def _run_sequential(self, node: AnyNode, ctx: ExecutionContext) -> Any:
        if ctx.is_paused():
            return None
        if ctx.hop_count >= ctx.max_hops:
            return None
        ctx.hop_count += 1

        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={
            "hop":       ctx.hop_count,
            "node_type": str(node.node_type),
            "summary":   "",
        })

        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)
        ctx.outputs[node.node_id] = result
        ctx.state.data["_last_node_id"] = node.node_id
        ctx.state.data["_last_output"] = result

        hop_event.payload["summary"] = _summarise(result)

        if ctx.is_paused():
            return result

        match node:
            case AgentNode(routing_table=rt) if rt:
                next_id = await self._route(node, result, ctx, parent_event_id=hop_event.event_id)
                if next_id and next_id != "__END__":
                    next_node = await self.store.get_node(next_id)
                    if next_node:
                        return await self._run_sequential(next_node, ctx)
            case ApprovalNode():
                next_id = result.get("next_node_id") if isinstance(result, dict) else None
                if next_id and next_id != "__END__":
                    next_node = await self.store.get_node(next_id)
                    if next_node:
                        return await self._run_sequential(next_node, ctx)

        return result

    # ------------------------------------------------------------------
    # Parallel (BFS fan-out)
    # ------------------------------------------------------------------

    async def _run_parallel(self, node: AnyNode, ctx: ExecutionContext) -> Any:
        if ctx.is_paused():
            return None
        if ctx.hop_count >= ctx.max_hops:
            return None
        ctx.hop_count += 1
        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={
            "hop":       ctx.hop_count,
            "node_type": str(node.node_type),
            "summary":   "",
        })
        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)
        ctx.outputs[node.node_id] = result
        ctx.state.data["_last_node_id"] = node.node_id
        ctx.state.data["_last_output"] = result
        hop_event.payload["summary"] = _summarise(result)

        delegate_edges = await self.store.get_edges(
            node.node_id, edge_type=EdgeType.DELEGATES_TO
        )
        if not delegate_edges:
            return result

        delegate_nodes = []
        for edge in delegate_edges:
            n = await self.store.get_node(edge.dst_id)
            if n:
                delegate_nodes.append(n)

        sub_results = await asyncio.gather(*[
            self._run_parallel(d, ctx) for d in delegate_nodes
        ])

        merged = {
            "node_result": result,
            "delegate_results": {
                d.node_id: r for d, r in zip(delegate_nodes, sub_results)
            },
        }
        ctx.outputs[node.node_id] = merged
        return merged

    # ------------------------------------------------------------------
    # Topological (DAG waves)
    # ------------------------------------------------------------------

    async def _dependency_map(self, entry_node_id: str) -> dict[str, set[str]]:
        """Map every node reachable from `entry_node_id` to its DELEGATES_TO prerequisites."""
        dep_map: dict[str, set[str]] = {}
        visited: set[str] = set()
        queue = [entry_node_id]

        while queue:
            nid = queue.pop()
            if nid in visited:
                continue
            visited.add(nid)
            edges = await self.store.get_edges(nid, edge_type=EdgeType.DELEGATES_TO)
            dep_map.setdefault(nid, set())
            for e in edges:
                dep_map.setdefault(e.dst_id, set()).add(nid)
                if e.dst_id not in visited:
                    queue.append(e.dst_id)

        await self._add_transform_dependencies(dep_map)
        return dep_map

    async def _add_transform_dependencies(self, dep_map: dict[str, set[str]]) -> None:
        """Wire TransformNode input_keys into the dependency map as extra prerequisites."""
        for nid in list(dep_map):
            node = await self.store.get_node(nid)
            if isinstance(node, TransformNode) and node.input_keys:
                dep_map[nid].update(key for key in node.input_keys if key in dep_map)

    def _claim_ready_nodes(
        self,
        sorter: graphlib.TopologicalSorter[str],
        ctx: ExecutionContext,
    ) -> list[str]:
        """Pop the ready set, marking already-completed (resume) nodes as done."""
        ready = list(sorter.get_ready())
        # Skip nodes whose output is already cached in ctx.outputs (resume support:
        # re-entering from the main entry skips previously completed nodes).
        for nid in ready:
            if nid in ctx.outputs:
                sorter.done(nid)
        return [nid for nid in ready if nid not in ctx.outputs]

    async def _execute_wave(
        self,
        sorter: graphlib.TopologicalSorter[str],
        ready: list[str],
        ctx: ExecutionContext,
        wave: int,
    ) -> None:
        """Run one topological wave concurrently and record outputs + hop events."""
        nodes = list(await asyncio.gather(*[self.store.get_node(nid) for nid in ready]))

        hop_events = []
        valid_nodes = [(nid, n) for nid, n in zip(ready, nodes) if n is not None]
        for nid, n in valid_nodes:
            ctx.hop_count += 1
            hop_event = self._emit(ctx, "hop", nid, n.name or "", payload={
                "hop":       ctx.hop_count,
                "node_type": str(n.node_type),
                "summary":   "",
                "wave":      wave,
            })
            hop_events.append(hop_event)

        t0 = time.monotonic()
        results = await asyncio.gather(*[
            self._execute_node(n, ctx, parent_event_id=he.event_id)
            for (_, n), he in zip(valid_nodes, hop_events)
        ])
        wave_ms = int((time.monotonic() - t0) * 1000)

        for (nid, _), result, hop_event in zip(valid_nodes, results, hop_events):
            # Don't store a paused subgraph's output — it will re-run on resume.
            if not ctx.is_paused():
                ctx.outputs[nid] = result
                ctx.state.data["_last_node_id"] = nid
                ctx.state.data["_last_output"] = result
            hop_event.payload["summary"] = _summarise(result)
            hop_event.payload["wave_ms"] = wave_ms
            sorter.done(nid)

    async def _run_topological(self, entry_node_id: str, ctx: ExecutionContext) -> None:
        """Execute a DAG in topological order using stdlib graphlib."""
        sorter = graphlib.TopologicalSorter(await self._dependency_map(entry_node_id))
        sorter.prepare()

        wave = 0
        while sorter.is_active():
            if ctx.is_paused():
                return
            if ctx.hop_count >= ctx.max_hops:
                return
            wave += 1
            ready = self._claim_ready_nodes(sorter, ctx)
            if not ready:
                continue
            remaining = max(ctx.max_hops - ctx.hop_count, 0)
            if remaining == 0:
                return
            if len(ready) > remaining:
                ready = ready[:remaining]
            await self._execute_wave(sorter, ready, ctx, wave)

    # ------------------------------------------------------------------
    # Node dispatch
    # ------------------------------------------------------------------

    async def _execute_node(
        self,
        node:            AnyNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> Any:
        result: Any = None
        match node:
            case AgentNode():
                result = await self._execute_agent(node, ctx, parent_event_id=parent_event_id)
            case ToolNode():
                result = await self._execute_timed_tool(node, ctx, parent_event_id=parent_event_id)
            case ApprovalNode():
                result = await self._execute_approval(node, ctx, parent_event_id=parent_event_id)
            case ContextNode():
                result = node.content
            case GraphNode():
                result = await self._execute_subgraph(node, ctx, parent_event_id=parent_event_id)
            case TransformNode():
                result = await self._execute_transform(node, ctx, parent_event_id=parent_event_id)
            case ReasonerNode():
                result = await self._execute_reasoner(node, ctx, parent_event_id=parent_event_id)
            case PromptNode():
                result = node.render()
        return result

    async def _execute_timed_tool(
        self,
        node:            ToolNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> Any:
        """Execute a ToolNode and emit its `tool_result` event with timing."""
        t0 = time.monotonic()
        result = await self._execute_tool(node, ctx)
        duration_ms = int((time.monotonic() - t0) * 1000)
        self._emit(
            ctx, "tool_result", node.node_id, node.name or "",
            payload={
                "tool_name": node.name,
                "callable_ref": node.callable_ref,
                "output_summary": _summarise(result),
                "success": True,
                "duration_ms": duration_ms,
            },
            parent_event_id=parent_event_id,
        )
        return result

    # ------------------------------------------------------------------
    # Sub-graph execution
    # ------------------------------------------------------------------

    _MAX_SUBGRAPH_DEPTH = 16

    async def _execute_subgraph(
        self,
        node:            GraphNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> Any:
        """Run a GraphNode: descend, route to exit, surface result."""
        if node.node_id in ctx._active_subgraphs:
            chain = " → ".join(ctx._active_subgraphs + [node.node_id])
            raise ValueError(f"GraphNode cycle detected: {chain}")
        if len(ctx._active_subgraphs) >= self._MAX_SUBGRAPH_DEPTH:
            raise ValueError(
                f"GraphNode recursion depth exceeded "
                f"({self._MAX_SUBGRAPH_DEPTH}) at {node.name or node.node_id!r}"
            )

        if not node.entry_node_id:
            raise ValueError(
                f"GraphNode {node.name or node.node_id!r} has no entry_node_id."
            )
        sub_entry = await self.store.get_node(node.entry_node_id)
        if sub_entry is None:
            raise ValueError(
                f"GraphNode {node.name or node.node_id!r} entry_node_id "
                f"{node.entry_node_id!r} not found in graph store."
            )

        exit_id = node.exit_node_id or node.entry_node_id
        sub_query = self._resolve_subgraph_query(node, ctx)
        sub_state_overlay = self._resolve_subgraph_state(node, ctx)

        self._emit(
            ctx, "subgraph_enter", node.node_id, node.name or "",
            payload={
                "entry_node_id": node.entry_node_id,
                "exit_node_id":  exit_id,
                "strategy":      node.strategy,
                "scoped":        node.scope_outputs,
            },
            parent_event_id=parent_event_id,
        )

        async def _run_subgraph() -> Any:
            return await self._run_scoped_subgraph(
                node, ctx, sub_entry, exit_id, sub_query, sub_state_overlay
            )

        try:
            result = await self._call_with_retry(
                _run_subgraph,
                ctx,
                node=node,
                policy=node.execution_policy,
                parent_event_id=parent_event_id,
            )
        except Exception as exc:
            self._emit(
                ctx, "subgraph_exit", node.node_id, node.name or "",
                payload={
                    "exit_node_id": exit_id,
                    "summary":      "",
                    "error":        str(exc),
                    "error_type":   type(exc).__name__,
                },
                parent_event_id=parent_event_id,
            )
            raise

        self._emit(
            ctx, "subgraph_exit", node.node_id, node.name or "",
            payload={"exit_node_id": exit_id, "summary": _summarise(result)},
            parent_event_id=parent_event_id,
        )
        return result

    async def _dispatch_strategy(
        self,
        strategy: str,
        entry:    AnyNode,
        ctx:      ExecutionContext,
    ) -> None:
        match strategy:
            case "sequential":
                await self._run_sequential(entry, ctx)
            case "parallel":
                await self._run_parallel(entry, ctx)
            case "topological":
                await self._run_topological(entry.node_id, ctx)
            case _:
                raise ValueError(f"Unknown sub-graph strategy: {strategy!r}")

    async def resolve_subgraph_inputs(
        self,
        node: GraphNode | str,
        ctx:  ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """Dry-run a GraphNode's input wiring without executing anything."""
        resolved = await self.store.get_node(node) if isinstance(node, str) else node
        if resolved is None:
            raise ValueError(f"Node {node!r} not found in graph store.")
        if not isinstance(resolved, GraphNode):
            raise ValueError(
                f"resolve_subgraph_inputs expected GraphNode, got {type(resolved).__name__}"
            )
        node = resolved
        if not node.entry_node_id:
            raise ValueError(
                f"GraphNode {node.name or node.node_id!r} has no entry_node_id."
            )
        sub_entry = await self.store.get_node(node.entry_node_id)
        if sub_entry is None:
            raise ValueError(
                f"GraphNode {node.name or node.node_id!r} entry_node_id "
                f"{node.entry_node_id!r} not found in graph store."
            )
        ctx = ctx or ExecutionContext(query="")
        return {
            "entry_node_id": node.entry_node_id,
            "exit_node_id":  node.exit_node_id or node.entry_node_id,
            "strategy":      node.strategy,
            "scope_outputs": node.scope_outputs,
            "query":         self._resolve_subgraph_query(node, ctx),
            "state_overlay": self._resolve_subgraph_state(node, ctx),
        }

    def _resolve_subgraph_query(
        self,
        node: GraphNode,
        ctx:  ExecutionContext,
    ) -> QueryContent:
        """Build the sub-graph's initial query from input_keys."""
        if not node.input_keys:
            return ctx.query
        parts = [
            _text_of(ctx.outputs[key]) if key in ctx.outputs
            else _text_of(ctx.state.data[key]) if key in ctx.state.data
            else None
            for key in node.input_keys
        ]
        return "\n\n".join(p for p in parts if p) or _query_text(ctx.query)

    def _resolve_subgraph_state(
        self,
        node: GraphNode,
        ctx:  ExecutionContext,
    ) -> dict[str, Any]:
        """Resolve input_map aliases against parent outputs / state."""
        if not node.input_map:
            return {}
        return {
            alias: ctx.outputs[source] if source in ctx.outputs else ctx.state.data[source]
            for alias, source in node.input_map.items()
            if source in ctx.outputs or source in ctx.state.data
        }

    # ------------------------------------------------------------------
    # Agent execution
    # ------------------------------------------------------------------

    async def _execute_agent(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        early = await self._agent_prescreen(node, ctx, parent_event_id)
        if early is not None:
            return early
        t0 = time.monotonic()
        _composed, system, tool_defs, agent_event_id, messages = await self._prepare_agent_turn(
            node, ctx, parent_event_id
        )
        loop = _AgentTurnLoop(messages=messages, max_tokens=node.max_tokens)

        for _iteration in range(node.max_iterations):
            loop.iterations += 1
            policy = node.execution_policy
            # Bind this turn's messages and token budget; the loop reassigns both.
            last_response = await self._call_with_retry(
                functools.partial(
                    self._chat_once, node, system, loop.messages, tool_defs, max_tokens=loop.max_tokens
                ),
                ctx,
                node=node,
                policy=policy,
                parent_event_id=agent_event_id,
            )
            recovered = await self._recover_agent_turn(
                node, ctx, last_response, loop, agent_event_id=agent_event_id
            )
            if recovered:
                continue

            # Terminal turn: a natural end of turn, or a truncation we can no longer
            # grow out of. Fall back to the reasoning trace when the model produced
            # only chain-of-thought and no visible answer, so downstream never sees "".
            return await self._finalize_agent_turn(
                node, ctx, last_response,
                agent_event_id=agent_event_id, iterations=loop.iterations, t0=t0,
            )

        return await self._finish_exhausted_agent(
            node, ctx, last_response,
            agent_event_id=agent_event_id, iterations=loop.iterations, t0=t0,
        )

    async def _agent_prescreen(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None,
    ) -> dict[str, Any] | None:
        """Handle pause_before and already-satisfied completion_paths.

        Returns an early-result dict when the agent loop must not run at all.
        """
        if node.pause_before:
            await self._pause_execution(
                ctx,
                node,
                reason="pause_before",
                waiting_for=node.wait_for_input,
            )
            return {"text": "", "intent": "default", "status": "paused"}
        # Pre-satisfied completion_paths → the node's work already exists; skip the
        # agent entirely. The symmetric complement of the not-done check in
        # _handle_completion_turn (a terminal turn with a declared path MISSING is
        # re-prompted): on resume, a fan-out re-executes every agent node, and each
        # "already done" discovery costs a full LLM turn — ~8 minutes per no-op on an
        # always-thinking local model, or a whole re-invocation on a per-call-priced
        # executor. Same contract as the not-done side: existence only, contents
        # never interpreted. Env kill-switch restores the previous behaviour.
        _declared = (getattr(node, "attributes", None) or {}).get("completion_paths") or []
        if (_declared and not missing_completion_paths(node)
                and os.environ.get("YGG_SKIP_COMPLETED_AGENTS", "1") != "0"):
            self._emit(
                ctx, "agent_skip", node.node_id, node.name or "",
                payload={"reason": "completion_paths_already_satisfied",
                         "paths": list(_declared)},
                parent_event_id=parent_event_id,
            )
            return {"text": "already complete: every declared completion path exists",
                    "intent": "complete", "skipped": True}
        return None

    async def _prepare_agent_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None,
    ) -> tuple[ComposedAgent, str, list[dict[str, Any]], str, list[dict[str, Any]]]:
        """Compose the agent, validate inputs, emit start events, build messages.

        Returns (composed, system, tool_defs, agent_event_id, messages).
        """
        composed  = await self.composer.compose(node, query=_query_text(ctx.query), session_id=ctx.session_id)
        system    = composed.build_system_prompt()
        tool_defs = composed.build_tool_schemas()
        if node.state_schema:
            ctx.state.schema = node.state_schema
        await self._validate_node_schemas(
            node,
            ctx=ctx,
            parent_event_id=parent_event_id,
        )

        agent_event_id = str(uuid.uuid4())
        self._emit_agent_start(node, ctx, composed, system, agent_event_id, parent_event_id)
        if composed.context:
            self._emit_context_inject(node, ctx, composed, agent_event_id, parent_event_id)
        return composed, system, tool_defs, agent_event_id, self._agent_messages(composed, ctx)

    def _emit_agent_start(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        composed:        ComposedAgent,
        system:          str,
        agent_event_id:  str,
        parent_event_id: str | None,
    ) -> None:
        """Emit `agent_start` so downstream metrics extraction picks up agent counts."""
        self._emit(
            ctx, "agent_start", node.node_id, node.name or "",
            payload={
                "query":   ctx.query,
                "system":  system,
                "model":   node.model,
                "tools":   [t.name for t in composed.tools],
                "context": [c.name for c in composed.context if c.name],
                "context_scores": [
                    {
                        "name": s.context.name,
                        "score": round(s.score, 4),
                        "source": s.source,
                        "hops": s.hops,
                    }
                    for s in composed.context_selection
                ],
            },
            event_id=agent_event_id,
            parent_event_id=parent_event_id,
        )

    def _emit_context_inject(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        composed:        ComposedAgent,
        agent_event_id:  str,
        parent_event_id: str | None,
    ) -> None:
        """Emit `context_inject` with the injected contexts and their scoring detail."""
        self._emit(
            ctx, "context_inject", node.node_id, node.name or "",
            payload={
                "context_names": [c.name for c in composed.context if c.name],
                "count":         len(composed.context),
                "selected_contexts": [
                    {
                        "node_id": s.context.node_id,
                        "name": s.context.name,
                        "score": round(s.score, 4),
                        "source": s.source,
                        "hops": s.hops,
                        "token_count": s.token_count,
                        "path": s.path,
                        "reasons": s.reasons,
                    }
                    for s in composed.context_selection
                ],
            },
            parent_event_id=agent_event_id,
        )

    def _agent_messages(self, composed: ComposedAgent, ctx: ExecutionContext) -> list[dict[str, Any]]:
        """First-turn message list: prior history, workflow state, then the user query."""
        messages: list[dict[str, Any]] = list(ctx.extra_messages)
        if ctx.state.data:
            messages.append({
                "role": "assistant",
                "content": f"Workflow state:\n{json.dumps(ctx.state.data, sort_keys=True, default=str)}",
            })

        image_ctx_blocks = composed.build_image_context_blocks()
        if image_ctx_blocks:
            user_content: QueryContent = (
                list(ctx.query) + image_ctx_blocks if isinstance(ctx.query, list)
                else [{"type": "text", "text": ctx.query}] + image_ctx_blocks
            )
        else:
            user_content = ctx.query
        messages.append({"role": "user", "content": user_content})
        return messages

    async def _recover_agent_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Handle the recoverable turn shapes (tools, corrections, nudges).

        Returns True when the turn was handled and the iteration loop should
        continue; False means the response is terminal.
        """
        if await self._handle_tool_calls_turn(node, ctx, response, loop, agent_event_id=agent_event_id):
            return True
        if self._handle_unparsed_call_turn(node, ctx, response, loop, agent_event_id=agent_event_id):
            return True
        if self._handle_truncation_turn(node, ctx, response, loop, agent_event_id=agent_event_id):
            return True
        if self._handle_narration_turn(node, ctx, response, loop, agent_event_id=agent_event_id):
            return True
        return self._handle_completion_turn(node, ctx, response, loop, agent_event_id=agent_event_id)

    async def _handle_tool_calls_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Run a tool-call turn: execute tools, extend the conversation, compact history.

        A turn that emitted tool calls is actionable regardless of whether it also
        hit the token limit.
        """
        if not response.tool_calls:
            return False
        tool_results = await self._handle_tool_calls(
            response, node, ctx, parent_event_id=agent_event_id
        )
        loop.messages = self._require_backend().extend_messages(loop.messages, response, tool_results)
        # Bound the re-read: once the history is long, shrink old turns in place
        # every _HISTORY_COMPACT_EVERY iterations (batched so caching stays warm).
        if _HISTORY_COMPACT_EVERY and loop.iterations % _HISTORY_COMPACT_EVERY == 0:
            _compact_history(loop.messages)
        return True

    def _handle_unparsed_call_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Re-prompt after a tool call written as TEXT that the API layer never parsed.

        No tool ran — the turn only LOOKS final. Tell the model the call wasn't
        executed and let it re-issue a well-formed one, instead of accepting raw
        markup as the agent's result (which ended steps mid-task on local models).
        """
        if not (
            response.stop_reason == "unparsed_tool_call"
            and loop.tool_call_corrections < _MAX_TOOL_CALL_CORRECTIONS
        ):
            return False
        loop.tool_call_corrections += 1
        loop.messages = self._require_backend().extend_messages(loop.messages, response, [])
        loop.messages.append({"role": "user", "content": _TOOL_CALL_CORRECTION_PROMPT})
        self._emit(
            ctx, "retry", node.node_id, node.name or "",
            payload={
                "reason":     "unparsed_tool_call",
                "correction": loop.tool_call_corrections,
                "text":       (response.text or "")[:400],
            },
            parent_event_id=agent_event_id,
        )
        return True

    def _handle_truncation_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Escalate the token budget after a truncation with nothing actionable.

        The model's reasoning consumed the whole budget before it could answer or
        call a tool. Give it more room and retry the SAME turn (bounded) instead of
        mistaking the empty result for completion (the root cause of an agent
        silently doing nothing).
        """
        _max_esc, _factor, _cap = _escalation_knobs()
        if not (
            response.stop_reason == "max_tokens"
            and loop.token_escalations < _max_esc
            and _factor > 1
            and loop.max_tokens < _cap
        ):
            return False
        loop.token_escalations += 1
        loop.max_tokens = min(loop.max_tokens * _factor, _cap)
        self._emit(
            ctx, "retry", node.node_id, node.name or "",
            payload={
                "reason":       "max_tokens_truncation",
                "escalation":   loop.token_escalations,
                "max_tokens":   loop.max_tokens,
            },
            parent_event_id=agent_event_id,
        )
        return True

    def _handle_narration_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Nudge after a blank or announce-and-stop turn (bounded).

        A blank or announce-and-stop turn is not an answer — the model was about to
        act. Nudge it to continue instead of accepting a non-answer as the agent's
        result and ending the step mid-task.
        """
        if not (
            loop.continuation_nudges < _MAX_CONTINUATION_NUDGES
            and looks_like_narration_only(response.text, response.reasoning)
        ):
            return False
        loop.continuation_nudges += 1
        loop.messages = self._require_backend().extend_messages(loop.messages, response, [])
        loop.messages.append({"role": "user", "content": _CONTINUATION_NUDGE})
        self._emit(
            ctx, "retry", node.node_id, node.name or "",
            payload={
                "reason": "narration_only_turn",
                "nudge":  loop.continuation_nudges,
                "text":   (response.text or "")[:200],
            },
            parent_event_id=agent_event_id,
        )
        return True

    def _handle_completion_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        response:        Any,
        loop:            _AgentTurnLoop,
        *,
        agent_event_id:  str,
    ) -> bool:
        """Re-prompt when declared completion artefacts are still missing (bounded).

        The node declares artefacts that define "done" and some are missing, so the
        work is not finished no matter how the closing message reads. Say which ones
        and let it finish rather than accepting the claim.
        """
        if loop.completion_nudges >= _MAX_COMPLETION_NUDGES:
            return False
        _absent = missing_completion_paths(node)
        if not _absent:
            return False
        loop.completion_nudges += 1
        loop.messages = self._require_backend().extend_messages(loop.messages, response, [])
        loop.messages.append({"role": "user", "content": (
            "You have not finished: the file(s) this task must produce do not "
            "exist yet — " + ", ".join(_absent) + ". Write them now, then stop. "
            "Do not describe what you would write; write it.")})
        self._emit(
            ctx, "retry", node.node_id, node.name or "",
            payload={"reason": "missing_completion_paths",
                     "nudge": loop.completion_nudges, "missing": _absent[:10]},
            parent_event_id=agent_event_id,
        )
        return True

    def _emit_agent_end(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        text:            str,
        intent:          str,
        iterations:      int,
        agent_event_id:  str,
        t0:              float,
    ) -> None:
        """Emit the closing `agent_end` event for an agent invocation."""
        duration_ms = int((time.monotonic() - t0) * 1000)
        self._emit(
            ctx, "agent_end", node.node_id, node.name or "",
            payload={
                "text_summary":  _summarise(text),
                "full_response": text,
                "intent":        intent,
                "iterations":    iterations,
            },
            parent_event_id=agent_event_id,
            duration_ms=duration_ms,
        )

    async def _finalize_agent_turn(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        last_response:   Any,
        *,
        agent_event_id:  str,
        iterations:      int,
        t0:              float,
    ) -> dict[str, Any]:
        """Validate + emit `agent_end` for the terminal turn; returns the result.

        A natural end of turn, or a truncation we can no longer grow out of. Falls
        back to the reasoning trace when the model produced only chain-of-thought
        and no visible answer, so downstream never sees "".
        """
        final_text = last_response.text or last_response.reasoning
        intent = await self._infer_intent(final_text, node)
        result = {"text": final_text, "intent": intent}
        await self._validate_node_schemas(
            node,
            output_payload=result,
            ctx=ctx,
            parent_event_id=agent_event_id,
        )
        if node.pause_after:
            await self._pause_execution(
                ctx,
                node,
                reason="pause_after",
                waiting_for=node.wait_for_input,
                metadata={"result": result},
            )
        self._emit_agent_end(node, ctx, final_text, intent, iterations, agent_event_id, t0)
        return result

    async def _finish_exhausted_agent(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        last_response:   Any,
        *,
        agent_event_id:  str,
        iterations:      int,
        t0:              float,
    ) -> dict[str, Any]:
        """Iteration budget exhausted: last text (or reasoning) with default intent."""
        text = (last_response.text or last_response.reasoning) if last_response else ""
        result = {"text": text, "intent": "default"}
        await self._validate_node_schemas(
            node,
            output_payload=result,
            ctx=ctx,
            parent_event_id=agent_event_id,
        )
        self._emit_agent_end(node, ctx, text, "default", iterations, agent_event_id, t0)
        return result

    async def _run_scoped_subgraph(
        self,
        node:              GraphNode,
        ctx:               ExecutionContext,
        sub_entry:         AnyNode,
        exit_id:           str,
        sub_query:         QueryContent,
        sub_state_overlay: dict[str, Any] | None,
    ) -> Any:
        """Execute the sub-graph run: scoped child context or in-place with bookkeeping."""
        if node.scope_outputs:
            child = ExecutionContext(
                query=sub_query,
                session_id=ctx.session_id,
                max_hops=max(ctx.max_hops - ctx.hop_count, 1),
                state=ctx.state,
                allowed_tools=ctx.allowed_tools,
                extra_messages=list(ctx.extra_messages),
                _active_subgraphs=ctx._active_subgraphs + [node.node_id],
            )
            if sub_state_overlay:
                ctx.state.data.update(sub_state_overlay)
            await self._dispatch_strategy(node.strategy, sub_entry, child)
            ctx.trace.extend(child.trace)
            ctx.hop_count += child.hop_count
            return child.outputs.get(exit_id)

        ctx._active_subgraphs.append(node.node_id)
        try:
            if sub_state_overlay:
                ctx.state.data.update(sub_state_overlay)
            prev_query = ctx.query
            ctx.query = sub_query
            try:
                await self._dispatch_strategy(node.strategy, sub_entry, ctx)
            finally:
                ctx.query = prev_query
            return ctx.outputs.get(exit_id)
        finally:
            ctx._active_subgraphs.pop()

    async def _execute_approval(
        self,
        node: ApprovalNode,
        ctx: ExecutionContext,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        payload = ctx.state.data.get(node.input_key, {})
        if isinstance(payload, dict) and "approved" in payload:
            approved = bool(payload.get("approved"))
            assigned_to = payload.get("assigned_to")
            task = next(
                (item for item in ctx.state.inbox.values() if item.node_id == node.node_id and item.status == "pending"),
                None,
            )
            if task is not None:
                task.status = "approved" if approved else "rejected"
                task.assigned_to = assigned_to or task.assigned_to
                task.resolved_at = datetime.now(UTC)
            return {
                "approved": approved,
                "next_node_id": node.approved_target_id if approved else node.rejected_target_id,
                "assigned_to": assigned_to,
            }

        assigned_to = node.assignees[0] if node.assignees and node.require_assignment else None
        task = ApprovalTask(
            task_id=str(uuid.uuid4()),
            node_id=node.node_id,
            token=str(uuid.uuid4()),
            assignees=list(node.assignees),
            assigned_to=assigned_to,
            waiting_for=node.instructions or node.name,
            due_at=(
                datetime.now(UTC) + timedelta(seconds=node.sla_seconds)
                if node.sla_seconds else None
            ),
            escalation_target=node.escalation_target or None,
            metadata={"assignment_mode": node.assignment_mode, "input_key": node.input_key},
        )
        ctx.state.inbox[task.task_id] = task
        self._emit(
            ctx,
            "approval_task",
            node.node_id,
            node.name or "",
            payload={
                "task_id": task.task_id,
                "assignees": task.assignees,
                "assigned_to": task.assigned_to,
                "due_at": task.due_at.isoformat() if task.due_at else None,
                "escalation_target": task.escalation_target,
            },
            parent_event_id=parent_event_id,
        )
        if task.due_at and task.escalation_target:
            self._emit(
                ctx,
                "schedule",
                node.node_id,
                node.name or "",
                payload={
                    "task_id": task.task_id,
                    "due_at": task.due_at.isoformat(),
                    "escalation_target": task.escalation_target,
                },
                parent_event_id=parent_event_id,
            )
        await self._pause_execution(
            ctx,
            node,
            reason="approval_wait",
            waiting_for=node.instructions or node.name,
            metadata={"task_id": task.task_id, "token": task.token},
        )
        return {"status": "paused", "task_id": task.task_id, "next_node_id": None}

    async def _handle_tool_calls(
        self,
        response:        Any,
        agent_node:      AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> list[ToolResult]:
        """Execute all tool calls in the response and return normalised results."""
        tool_edges = await self.store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_TOOL)
        tool_map: dict[str, ToolNode] = {}
        for edge in tool_edges:
            tn = await self.store.get_node(edge.dst_id)
            if tn and isinstance(tn, ToolNode):
                tool_map[tn.name] = tn

        results: list[ToolResult] = []
        for tc in response.tool_calls:
            tool_node = tool_map.get(tc.name)
            callable_ref = tool_node.callable_ref if tool_node else ""

            call_event = self._emit(
                ctx, "tool_call",
                tool_node.node_id if tool_node else agent_node.node_id,
                tc.name,
                payload={
                    "tool_name":    tc.name,
                    "callable_ref": callable_ref,
                    "input":        tc.input,
                },
                parent_event_id=parent_event_id,
            )

            t0 = time.monotonic()
            if tool_node is None:
                # Name what IS on the belt. "Tool 'read_file' not found." is a dead end:
                # the model has no way to learn the belt from the error, so it re-tries
                # the same absent tool or gives up, burning turns either way. A leashed
                # worker with only {read_input, write_file} routinely reaches for
                # read_file and lost whole turns to this. Listing the alternatives lets
                # it self-correct on the next turn, which is the difference between a
                # wasted turn and a recovered one. Sorted for determinism.
                #
                # Deliberately NO "did you mean X?" guess: a purely lexical match is
                # blind to intent and steers confidently wrong. difflib scores
                # read_file→write_file above read_file→read_input (they share the
                # longer `_file`), so a worker trying to READ would be pointed at the
                # writer. Listing the belt lets the model pick using the intent only it
                # has; a wrong single suggestion overrides that judgement.
                _available = sorted(tool_map)
                if _available:
                    content = (f"Tool {tc.name!r} not found. "
                               f"Available tools: {', '.join(_available)}.")
                else:
                    content = (f"Tool {tc.name!r} not found. This node has no tools — "
                               "answer directly instead of calling a tool.")
                success = False
            else:
                try:
                    raw = await self._execute_tool(tool_node, ctx, input_data=tc.input)
                    await self._materialise_output(tool_node, raw, ctx)
                    content = raw if isinstance(raw, str) else str(raw)
                    success = True
                except Exception as exc:  # noqa: BLE001 — a tool failure goes back to the model
                    content = f"Tool error: {exc}"
                    success = False

            duration_ms = int((time.monotonic() - t0) * 1000)

            self._emit(
                ctx, "tool_result",
                tool_node.node_id if tool_node else agent_node.node_id,
                tc.name,
                payload={
                    "tool_name":      tc.name,
                    "output_summary": _summarise(content),
                    "success":        success,
                },
                parent_event_id=call_event.event_id,
                duration_ms=duration_ms,
            )

            results.append(ToolResult(tool_call_id=tc.id, content=content))

        return results

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    def _callable_injection_kwargs(self, fn: Any, ctx: ExecutionContext) -> dict[str, Any]:
        """Extra keyword arguments to pass to a tool/transform callable."""
        try:
            params = inspect.signature(fn).parameters
        except (TypeError, ValueError):
            return {}
        kwargs: dict[str, Any] = {}
        if "session_id" in params:
            kwargs["session_id"] = ctx.session_id
        if "ctx" in params:
            kwargs["ctx"] = ctx
        if "store" in params:
            kwargs["store"] = self.store
        return kwargs

    async def _execute_tool(
        self,
        node: ToolNode,
        ctx: ExecutionContext,
        input_data: dict[str, Any] | None = None,
    ) -> Any:
        fn = self._tool_fns.get(node.callable_ref)
        if fn is None:
            raise RuntimeError(
                f"Tool callable not registered: {node.callable_ref!r}. "
                "Call executor.register_tool(ref, fn) before running."
            )

        # `{}` is a VALID call: a tool whose parameters are all optional is invoked with
        # no arguments. Testing truthiness treated that as "no input given" and fell
        # back to the previous node's output, which then failed THIS tool's input schema
        # ("tool_input must be an object" on a call the model made correctly). Only a
        # genuinely absent input (None) may fall back to the upstream payload.
        payload = (input_data if input_data is not None
                   else (list(ctx.outputs.values())[-1] if ctx.outputs else {}))
        # Nudge argument TYPES to what the tool declares before validating: a local
        # model's comma-separated string for an array param is unambiguous, and losing
        # the whole turn to `tool_input.x must be an array` throws away work it did
        # correctly. Only schema-declared, lossless conversions — see coerce_to_schema.
        if isinstance(payload, dict):
            payload = coerce_to_schema(payload, node.input_schema)
        runtime_payload = dict(payload) if isinstance(payload, dict) else {"input": payload}
        await self._validate_node_schemas(node, input_payload=payload, ctx=ctx)
        idempotency_key = self._idempotency_key(node, payload)
        if idempotency_key and idempotency_key in ctx.state.idempotency_cache:
            return ctx.state.idempotency_cache[idempotency_key]

        injected = self._callable_injection_kwargs(fn, ctx)

        async def invoke() -> Any:
            if node.is_async:
                return await fn(runtime_payload, **injected)
            return await asyncio.to_thread(fn, runtime_payload, **injected)

        result = await self._call_with_retry(
            invoke,
            ctx,
            node=node,
            policy=node.execution_policy,
        )
        await self._validate_node_schemas(node, output_payload=result, ctx=ctx)
        if idempotency_key:
            ctx.state.idempotency_cache[idempotency_key] = result
        return result

    async def _execute_transform(
        self,
        node: TransformNode,
        ctx: ExecutionContext,
        parent_event_id: str | None = None,
    ) -> Any:
        fn = self._tool_fns.get(node.callable_ref)
        if fn is None:
            raise RuntimeError(
                f"Transform callable not registered: {node.callable_ref!r}. "
                "Call executor.register_tool(ref, fn) before running."
            )

        if node.input_keys:
            input_data: dict[str, Any] = {
                key: ctx.outputs[key] if key in ctx.outputs else ctx.state.data[key]
                for key in node.input_keys
                if key in ctx.outputs or key in ctx.state.data
            }
        elif ctx.outputs:
            last = list(ctx.outputs.values())[-1]
            input_data = dict(last) if isinstance(last, dict) else {"input": last}
        else:
            input_data = dict(ctx.state.data)

        idempotency_key = self._idempotency_key(node, input_data)
        if idempotency_key and idempotency_key in ctx.state.idempotency_cache:
            return ctx.state.idempotency_cache[idempotency_key]

        t0 = time.monotonic()
        injected = self._callable_injection_kwargs(fn, ctx)

        async def invoke() -> Any:
            if node.is_async:
                return await fn(input_data, **injected)
            return await asyncio.to_thread(fn, input_data, **injected)

        result = await self._call_with_retry(invoke, ctx, node=node, policy=node.execution_policy)
        duration_ms = int((time.monotonic() - t0) * 1000)

        if node.output_key:
            ctx.state.data[node.output_key] = result

        self._emit(
            ctx,
            "tool_result",
            node.node_id,
            node.name or "",
            payload={
                "tool_name": node.name,
                "callable_ref": node.callable_ref,
                "output_summary": _summarise(result),
                "success": True,
                "duration_ms": duration_ms,
            },
            parent_event_id=parent_event_id,
        )

        if idempotency_key:
            ctx.state.idempotency_cache[idempotency_key] = result
        return result

    async def _execute_reasoner(
        self,
        node: ReasonerNode,
        ctx: ExecutionContext,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        """Run the symbolic Datalog reasoner over facts from state + the KG."""
        from yggdrasil_lm.symbolic.datalog import (
            Program,
            Rule,
            fact_to_dict,
            parse_program,
            rule_from_obj,
        )

        rules: list[Rule] = list(parse_program(node.program)) if node.program else []
        for raw in node.rules:
            rules.extend(rule_from_obj(raw))
        program = Program(rules)

        facts = await self._gather_reasoner_facts(node, ctx)

        t0 = time.monotonic()

        def _solve() -> Any:
            return program.solve(facts, with_proof=node.with_proof)

        solution = await self._call_with_retry(
            lambda: asyncio.to_thread(_solve),
            ctx,
            node=node,
            policy=node.execution_policy,
            parent_event_id=parent_event_id,
        )
        duration_ms = int((time.monotonic() - t0) * 1000)

        emitted = solution.derived if node.emit_derived_only else solution.facts
        if node.query:
            wanted = set(node.query)
            emitted = {f for f in emitted if f[0] in wanted}

        if node.fail_on_empty and not emitted:
            raise RuntimeError(
                f"ReasonerNode {node.name or node.node_id!r} derived no facts "
                f"for query {node.query or '*'}"
            )

        result: dict[str, Any] = {
            "facts": [fact_to_dict(f) for f in sorted(emitted, key=repr)],
            "fact_count": len(emitted),
            "input_count": len(facts),
            "predicates": sorted({f[0] for f in emitted}),
        }
        if node.with_proof:
            result["proofs"] = [
                {"fact": fact_to_dict(f), "explanation": solution.explain(f)}
                for f in sorted(emitted, key=repr)
                if f in solution.justifications
            ]

        if node.output_key:
            ctx.state.data[node.output_key] = result

        self._emit(
            ctx,
            "tool_result",
            node.node_id,
            node.name or "",
            payload={
                "tool_name": node.name or "reasoner",
                "node_type": str(node.node_type),
                "output_summary": _summarise(result),
                "fact_count": result["fact_count"],
                "input_count": result["input_count"],
                "predicates": result["predicates"],
                "success": True,
                "duration_ms": duration_ms,
            },
            parent_event_id=parent_event_id,
        )
        return result

    def _facts_from_state(self, src: Any, ctx: ExecutionContext) -> list[Any]:
        """Ground facts from workflow state: declared state_keys or last outputs."""
        if src.state_keys:
            values = (ctx.state.data.get(key) for key in src.state_keys)
            return [
                item
                for value in values
                if value is not None
                for item in (value if isinstance(value, list) else [value])
            ]
        last = list(ctx.outputs.values())[-1] if ctx.outputs else None
        state_facts = ctx.state.data.get("facts")
        if isinstance(last, list):
            output_facts: list[Any] = last
        elif isinstance(last, dict) and isinstance(last.get("facts"), list):
            output_facts = last["facts"]
        else:
            output_facts = []
        return [
            *output_facts,
            *(state_facts if isinstance(state_facts, list) else []),
        ]

    def _facts_from_nodes(self, src: Any, nodes: list[Any]) -> list[Any]:
        """Ground `(node_type, label)` facts for every node in the store."""
        return [
            (str(n.node_type), n.name if (src.use_node_names and n.name) else n.node_id)
            for n in nodes
        ]

    async def _facts_from_edges(self, src: Any) -> list[Any]:
        """Ground `(predicate, src_label, dst_label)` facts for the declared edge types."""
        if not src.edge_types:
            return []
        name_cache: dict[str, str] = {}

        async def _label(node_id: str) -> str:
            if node_id in name_cache:
                return name_cache[node_id]
            if not src.use_node_names:
                name_cache[node_id] = node_id
                return node_id
            n = await self.store.get_node(node_id)
            label = (n.name if n and n.name else node_id)
            name_cache[node_id] = label
            return label

        facts: list[Any] = []
        for etype in src.edge_types:
            try:
                edge_type = EdgeType(etype)
            except ValueError:
                edge_type = None
            edges = (
                await self.store.list_edges(edge_type=edge_type) if edge_type
                else [e for e in await self.store.list_edges() if str(e.edge_type) == etype]
            )
            pred = etype.lower()
            facts.extend([
                (pred, await _label(e.src_id), await _label(e.dst_id))
                for e in edges
            ])
        return facts

    async def _gather_reasoner_facts(
        self,
        node: ReasonerNode,
        ctx: ExecutionContext,
    ) -> list[Any]:
        """Collect ground facts for a reasoner from state and the knowledge graph."""
        src = node.fact_source
        facts: list[Any] = [
            *self._facts_from_state(src, ctx),
            *await self._facts_from_edges(src),
        ]
        if src.include_node_facts:
            facts.extend(self._facts_from_nodes(src, await self.store.list_nodes()))
        return facts

    async def _chat_once(
        self,
        node: AgentNode,
        system: str,
        messages: list[dict[str, Any]],
        tool_defs: list[dict[str, Any]],
        max_tokens: int | None = None,
    ) -> Any:
        return await self._require_backend().chat(
            model=node.model,
            system=system,
            messages=messages,
            tools=tool_defs,
            max_tokens=max_tokens if max_tokens is not None else node.max_tokens,
        )

    async def _call_with_retry(
        self,
        fn: Callable[[], Any],
        ctx: ExecutionContext,
        *,
        node: AnyNode,
        policy: ExecutionPolicy,
        parent_event_id: str | None = None,
    ) -> Any:
        attempts = max(1, policy.retry_policy.max_attempts)
        delay = max(0.0, policy.retry_policy.backoff_seconds)
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                if policy.timeout_seconds:
                    return await asyncio.wait_for(fn(), timeout=policy.timeout_seconds)
                return await fn()
            except Exception as exc:  # noqa: BLE001 — retried per policy, then re-raised
                last_exc = exc
                if attempt >= attempts:
                    break
                self._emit(
                    ctx,
                    "retry",
                    node.node_id,
                    node.name or "",
                    payload={"attempt": attempt, "max_attempts": attempts, "error": str(exc)},
                    parent_event_id=parent_event_id,
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                    delay *= max(policy.retry_policy.backoff_multiplier, 1.0)
        assert last_exc is not None
        raise last_exc

    def _idempotency_key(self, node: ToolNode | TransformNode, payload: Any) -> str:
        template = node.execution_policy.idempotency_key
        if template == "":
            return ""
        if template == "auto":
            return f"{node.node_id}:{json.dumps(payload, sort_keys=True, default=str)}"
        if isinstance(payload, dict) and template in payload:
            return f"{node.node_id}:{payload[template]}"
        return f"{node.node_id}:{template}"

    # ------------------------------------------------------------------
    # Output materialisation
    # ------------------------------------------------------------------

    async def _materialise_output(
        self,
        source_node: AnyNode,
        output: Any,
        ctx: ExecutionContext,
    ) -> ContextNode:
        """Write execution output back into the graph as a ContextNode."""
        from yggdrasil_lm.core.edges import Edge
        from yggdrasil_lm.core.nodes import ContextNode

        content = output if isinstance(output, str) else str(output)
        ctx_node = ContextNode(
            name=f"Output of {source_node.name}",
            description=f"Auto-materialised output from {source_node.node_type} node",
            content=content,
            source=f"node:{source_node.node_id}",
            group_id=ctx.session_id,
            attributes={
                "origin":         "runtime",
                "session_id":     ctx.session_id,
                "source_node_id": source_node.node_id,
            },
        )
        await self.store.upsert_node(ctx_node)
        await self.store.upsert_edge(
            Edge.produces(src_id=source_node.node_id, dst_id=ctx_node.node_id)
        )
        ctx.outputs[ctx_node.node_id] = content
        return ctx_node

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    async def _route(
        self,
        node:            AgentNode,
        result:          dict[str, Any],
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> str | None:
        if node.decision_table is not None:
            decision = self._evaluate_decision_table(node.decision_table, state=ctx.state, result=result)
            if decision is not None:
                self._emit(
                    ctx,
                    "routing",
                    node.node_id,
                    node.name or "",
                    payload={
                        "intent": decision.name or "decision_table",
                        "next_node_id": None if decision.target_node_id == "__END__" else decision.target_node_id,
                        "confidence": 1.0,
                        "mode": "decision_table",
                    },
                    parent_event_id=parent_event_id,
                )
                return decision.target_node_id
            if node.decision_table.strict:
                target = node.decision_table.default_target_id
                self._emit(
                    ctx,
                    "routing",
                    node.node_id,
                    node.name or "",
                    payload={
                        "intent": node.decision_table.default_intent,
                        "next_node_id": None if target == "__END__" else target,
                        "confidence": 1.0,
                        "mode": "decision_table",
                    },
                    parent_event_id=parent_event_id,
                )
                return target
        for rule in sorted(node.route_rules, key=lambda r: r.priority, reverse=True):
            if self._evaluate_route_rule(rule, result=result, state=ctx.state):
                if rule.pause_on_match:
                    await self._pause_execution(
                        ctx,
                        node,
                        reason=rule.name or "route_rule_pause",
                        waiting_for=node.wait_for_input,
                        metadata={"rule": rule.name, "target": rule.target_node_id},
                    )
                self._emit(
                    ctx,
                    "routing",
                    node.node_id,
                    node.name or "",
                    payload={
                        "intent": rule.name or "route_rule",
                        "next_node_id": None if rule.target_node_id == "__END__" else rule.target_node_id,
                        "confidence": 1.0,
                        "mode": "deterministic",
                    },
                    parent_event_id=parent_event_id,
                )
                return rule.target_node_id
        intent = result.get("intent", "default")
        next_id = node.routing_table.get(intent) or node.routing_table.get("default", "__END__")

        self._emit(ctx, "routing", node.node_id, node.name or "",
                   payload={
                       "intent":       intent,
                       "next_node_id": next_id if next_id != "__END__" else None,
                       "confidence":   None,
                       "mode":         "llm",
                   },
                   parent_event_id=parent_event_id)

        return next_id

    async def _infer_intent(self, text: str, node: AgentNode) -> str:
        """Classify routing intent from agent output text."""
        if not node.routing_table:
            return "default"
        intents = [intent for intent in node.routing_table if intent != "default"]
        if not intents:
            return "default"

        keyword_intent = self._infer_intent_keywords(text, node)
        if keyword_intent != "default":
            return keyword_intent

        if self._backend is None:
            return "default"

        prompt = _INTENT_TEMPLATE.format(
            intents="\n".join(f"- {intent}" for intent in intents),
            text=text[:2000],
        )
        try:
            response = await self._require_backend().chat(
                model=self._router_model,
                system=_ROUTER_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                tools=[],
            )
            data = json.loads(response.text.strip())
            return str(data.get("intent", "default"))
        except Exception:  # noqa: BLE001 — intent inference is advisory; fall back to default
            return "default"

    def _infer_intent_keywords(self, text: str, node: AgentNode) -> str:
        """Keyword-based intent fallback (no LLM call)."""
        text_lower = text.lower()
        for intent in node.routing_table:
            if intent != "default" and intent.lower() in text_lower:
                return intent
        return "default"

    # ------------------------------------------------------------------
    # White-box routing: plan + execute (two-phase dispatch)
    # ------------------------------------------------------------------

    async def route(
        self,
        query: str,
        candidates: list[AgentNode] | None = None,
    ) -> RoutingDecision:
        """LLM-based router: pick the best AgentNode for *query*."""
        if candidates is None:
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]

        if not candidates:
            raise ValueError("No valid AgentNode candidates found in the store.")

        if len(candidates) == 1:
            return RoutingDecision(candidates[0].node_id, "Only one agent available.", 1.0)

        agent_list = "\n".join(f"- {n.node_id}: {n.description}" for n in candidates)
        prompt = _ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)

        try:
            response = await self._require_backend().chat(
                model=self._router_model,
                system=_ROUTER_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                tools=[],
            )
            data = json.loads(response.text.strip())
            return RoutingDecision(
                str(data["agent"]),
                str(data.get("reason", "")),
                float(data.get("confidence", 0.5)),
            )
        except Exception:  # noqa: BLE001 — any LLM/parse failure falls back to the first agent
            return RoutingDecision(
                candidates[0].node_id,
                "Fallback: router response could not be parsed.",
                0.5,
            )

    async def plan(self, query: str) -> RoutingDecision:
        """Deprecated alias for route()."""
        import warnings
        warnings.warn(
            "GraphExecutor.plan() is deprecated and will be removed in a future release. "
            "Use GraphExecutor.route() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.route(query)

    async def execute(
        self,
        agent_id: str,
        query: QueryContent,
        routing: RoutingDecision | None = None,
    ) -> AgentResult:
        """Phase 2 of two-phase dispatch: run *agent_id* and return a structured envelope."""
        node = await self.store.get_node(agent_id)
        if node is None or not isinstance(node, AgentNode):
            raise ValueError(f"Agent node not found or not an AgentNode: {agent_id!r}")

        composed = await self.composer.compose(node, query=_query_text(query))
        context_names = [c.name for c in composed.context if c.name]

        ctx = ExecutionContext(query=query)
        raw = await self._execute_agent(node, ctx)
        text = raw.get("text", "")

        decision = routing or RoutingDecision(agent_id, "Direct execution (no routing phase).", 1.0)

        return AgentResult(
            routed_to=agent_id,
            reason=decision.reason,
            confidence=decision.confidence,
            context_injected=context_names,
            result=text,
            low_confidence_warning=decision.low_confidence_warning,
        )


# ---------------------------------------------------------------------------
# print_trace() — render a session trace as a human-readable execution tree
# ---------------------------------------------------------------------------

def _trace_fmt_ms(ms: int | None) -> str:
    """`[123ms]` for timed events, empty string otherwise."""
    return f"[{ms}ms]" if ms is not None else ""


def _render_trace_hop(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render a hop line, then its child events one level deeper."""
    p = event.payload
    pad = "  " * indent
    node_type = p.get("node_type", "").split(".")[-1].upper()
    hop_num   = p.get("hop", "")
    hop_label = f"hop {hop_num}  " if hop_num else ""
    print(f"{pad}{hop_label}{node_type}  {event.node_name}")
    for child in children.get(event.event_id, []):
        _render_trace_event(child, children, indent + 1)


def _render_trace_agent_start(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render agent tools/context and the ranked context list; children share the level."""
    p = event.payload
    pad = "  " * indent
    tools = ", ".join(p.get("tools", [])) or "none"
    ctx_l = p.get("context", [])
    ctx_s = f"  context: {', '.join(ctx_l)}" if ctx_l else ""
    print(f"{pad}tools: {tools}{ctx_s}")
    if p.get("context_scores"):
        ranked = [
            f"{item.get('name')}[{item.get('score')}, {item.get('source')}, hops={item.get('hops')}]"
            for item in p["context_scores"]
        ]
        print(f"{pad}ranked_context: {' | '.join(ranked)}")
    for child in children.get(event.event_id, []):
        _render_trace_event(child, children, indent)


def _render_trace_context_inject(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render injected context names and, per selected context, its scoring detail."""
    p = event.payload
    pad = "  " * indent
    names = ", ".join(p.get("context_names", [])) or "—"
    count = p.get("count", 0)
    print(f"{pad}context_inject  {names}  ({count} nodes)")
    for item in p.get("selected_contexts", []):
        reasons = ", ".join(item.get("reasons", []))
        print(
            f"{pad}  selected  {item.get('name')}  score={item.get('score')}  "
            f"source={item.get('source')}  hops={item.get('hops')}  "
            f"tokens={item.get('token_count')}"
        )
        if reasons:
            print(f"{pad}    reasons  {reasons}")

def _render_trace_agent_end(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the agent's final summary, intent, iterations and timing."""
    p = event.payload
    pad = "  " * indent
    ms = _trace_fmt_ms(event.duration_ms)
    summary = p.get("text_summary", "")
    intent  = p.get("intent", "default")
    iters   = p.get("iterations", 1)
    iter_s  = f"  iters={iters}" if iters > 1 else ""
    print(f"{pad}agent_end  {summary!r}  intent={intent}{iter_s}  {ms}")


def _render_trace_tool_call(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the tool call with a truncated input preview, then its result child."""
    p = event.payload
    pad = "  " * indent
    inp = json.dumps(p.get("input", {}), ensure_ascii=False)
    inp = inp[:_TOOL_INPUT_PREVIEW_CHARS] + "…" if len(inp) > _TOOL_INPUT_PREVIEW_CHARS else inp
    print(f"{pad}tool_call  {event.node_name}  {inp}")
    for child in children.get(event.event_id, []):
        _render_trace_event(child, children, indent + 1)


def _render_trace_tool_result(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the tool result status, summary and timing."""
    p = event.payload
    pad = "  " * indent
    ms = _trace_fmt_ms(event.duration_ms)
    status  = "ok" if p.get("success") else "err"
    summary = p.get("output_summary", "")
    print(f"{pad}tool_result  {event.node_name}  {status}  {summary!r}  {ms}")


def _render_trace_routing(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the routing decision: intent → next node, with optional confidence."""
    p = event.payload
    pad = "  " * indent
    intent  = p.get("intent", "default")
    next_id = p.get("next_node_id") or "__END__"
    conf    = p.get("confidence")
    conf_s  = f"  conf={conf:.0%}" if conf is not None else ""
    print(f"{pad}routing  {intent} → {next_id}{conf_s}")


def _render_trace_subgraph_enter(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the sub-graph entry line, then the sub-graph's events one level deeper."""
    p = event.payload
    pad = "  " * indent
    print(f"{pad}subgraph_enter  {event.node_name}  entry={p.get('entry_node_id','')}")
    for child in children.get(event.event_id, []):
        _render_trace_event(child, children, indent + 1)


def _render_trace_subgraph_exit(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render the sub-graph exit line with timing."""
    pad = "  " * indent
    ms = _trace_fmt_ms(event.duration_ms)
    print(f"{pad}subgraph_exit   {event.node_name}  {ms}")


_TRACE_EVENT_RENDERERS: dict[
    str, Callable[[TraceEvent, dict[str | None, list[TraceEvent]], int], None]
] = {
    "hop":             _render_trace_hop,
    "agent_start":     _render_trace_agent_start,
    "context_inject":  _render_trace_context_inject,
    "agent_end":       _render_trace_agent_end,
    "tool_call":       _render_trace_tool_call,
    "tool_result":     _render_trace_tool_result,
    "routing":         _render_trace_routing,
    "subgraph_enter":  _render_trace_subgraph_enter,
    "subgraph_exit":   _render_trace_subgraph_exit,
}


def _render_trace_event(
    event: TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    indent: int,
) -> None:
    """Render one trace event via its per-type renderer; unknown types are skipped."""
    renderer = _TRACE_EVENT_RENDERERS.get(event.event_type)
    if renderer is not None:
        renderer(event, children, indent)


def print_trace(ctx: ExecutionContext | list[TraceEvent], *, width: int = 72) -> None:
    """Print the execution trace as a human-readable tree."""
    match ctx:
        case ExecutionContext():
            events = ctx.trace
            session_id = ctx.session_id[:8]
            query = _query_text(ctx.query)
        case _:
            events = ctx
            session_id = events[0].session_id[:8] if events else "?"
            query = ""

    sep = "═" * width
    print(f"\nSession {session_id}  {query!r}")
    print(sep)

    children: dict[str | None, list[TraceEvent]] = {}
    for e in events:
        children.setdefault(e.parent_event_id, []).append(e)

    root_events = children.get(None, [])
    for event in root_events:
        _render_trace_event(event, children, indent=0)
    hops = sum(1 for e in root_events if e.event_type == "hop")

    agent_ends = [e for e in events if e.event_type == "agent_end"]
    total_ms = sum(e.duration_ms for e in agent_ends if e.duration_ms is not None)

    print(sep)
    ms_s = f" · {total_ms}ms" if total_ms else ""
    print(f"Total: {hops} hops · {len(agent_ends)} agent_end events{ms_s}\n")


# ---------------------------------------------------------------------------
# Runtime node utilities
# ---------------------------------------------------------------------------

async def get_runtime_nodes(
    store:      GraphStore,
    session_id: str | None = None,
    only_valid: bool = True,
) -> list[ContextNode]:
    """Return runtime-materialised ContextNodes without graph traversal."""
    candidates = await store.list_nodes(
        node_type=NodeType.CONTEXT,
        group_id=session_id,
        only_valid=only_valid,
    )
    return [
        n for n in candidates
        if isinstance(n, ContextNode) and n.attributes.get("origin") == "runtime"
    ]


async def cleanup_session(
    store:      GraphStore,
    session_id: str,
    hard:       bool = False,
) -> int:
    """Expire (or hard-delete) all runtime nodes from *session_id*."""
    nodes = await store.list_nodes(group_id=session_id, only_valid=False)
    count = 0
    for node in nodes:
        in_edges = await store.get_edges(
            node.node_id, edge_type=EdgeType.PRODUCES, direction="in", only_valid=False
        )
        for edge in in_edges:
            if hard:
                await store.delete_edge(edge.edge_id)
            else:
                await store.expire_edge(edge.edge_id)

        if hard:
            await store.delete_node(node.node_id)
        else:
            await store.expire_node(node.node_id)
        count += 1

    return count


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarise(value: Any, max_len: int = 200) -> str:
    s = value if isinstance(value, str) else str(value)
    return s[:max_len] + "…" if len(s) > max_len else s


def _text_of(value: Any) -> str:
    """Best-effort extraction of a string payload from a node output."""
    match value:
        case None:
            return ""
        case str():
            return value
        case {}:
            for key in ("text", "output", "result", "content"):
                v = value.get(key)
                if isinstance(v, str):
                    return v
            return str(value)
        case _:
            return str(value)
