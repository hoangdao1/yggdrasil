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
import graphlib
import json
import logging
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Literal

from yggdrasil_lm.backends.llm import LLMBackend, ToolResult, default_backend
from yggdrasil_lm.core.edges import Edge, EdgeType
from yggdrasil_lm.core.nodes import (
    AgentNode,
    ApprovalNode,
    AnyNode,
    ConstraintRule,
    ContextNode,
    DecisionRule,
    DecisionTable,
    ExecutionPolicy,
    GraphNode,
    NodeType,
    PromptNode,
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
]

_log = logging.getLogger(__name__)

# Type alias for multimodal query content (mirrors the Anthropic Messages API).
# A plain str is treated as a single text block.  A list follows the Anthropic
# content-block schema: {"type": "text", "text": "..."} or
# {"type": "image", "source": {"type": "base64"|"url", ...}}.
QueryContent = str | list[dict[str, Any]]


def _query_text(query: QueryContent) -> str:
    """Extract the plain-text portion of a query for routing and context scoring."""
    if isinstance(query, str):
        return query
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
    event_id:        str       = field(default_factory=lambda: str(uuid.uuid4()))
    parent_event_id: str | None = None
    duration_ms:     int | None = None


# ---------------------------------------------------------------------------
# RoutingDecision — white-box routing result
# ---------------------------------------------------------------------------

@dataclass
class RoutingDecision:
    """LLM routing decision with explicit reasoning and confidence.

    Returned by GraphExecutor.route() / plan() so callers can inspect and
    debug every dispatch choice before (or instead of) executing.
    """

    agent_id:   str    # node_id of the selected AgentNode
    reason:     str    # one-sentence explanation from the LLM router
    confidence: float  # 0.0–1.0

    @property
    def low_confidence_warning(self) -> str | None:
        """Non-None when confidence is below 0.7."""
        if self.confidence < 0.7:
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
    """Execution envelope returned by GraphExecutor.execute().

    Bundles the agent's output with the routing metadata that produced it,
    making the full dispatch chain observable and debuggable.
    """

    routed_to:              str        # agent node_id that was executed
    reason:                 str        # why this agent was chosen
    confidence:             float      # router confidence (1.0 for direct calls)
    context_injected:       list[str]  # ContextNode names in the system prompt
    result:                 str        # agent output text
    low_confidence_warning: str | None = None  # set when confidence < 0.7


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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
    outputs:    dict[str, Any]        = field(default_factory=dict)   # node_id → output
    trace:      list[TraceEvent]      = field(default_factory=list)   # structured events
    max_hops:   int                   = 20
    hop_count:  int                   = 0

    # Optional: inject additional context into every LLM call
    extra_messages: list[dict[str, Any]] = field(default_factory=list)
    state: WorkflowState = field(default_factory=WorkflowState)
    allowed_tools: set[str] | None = None

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
    def from_snapshot(cls, data: dict[str, Any]) -> "ExecutionContext":
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
                    if item.get("created_at") else datetime.now(timezone.utc),
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
            selection = self._score_context(
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
            seed_map[node.node_id] = selection

        if query_vec is not None:
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
                selection = self._score_context(
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
                seed_map[node.node_id] = selection

        if session_id:
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

    def _score_context(
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
        age_s = (datetime.now(timezone.utc) - ctx.valid_at).total_seconds()
        if age_s <= 3600:
            return self.recency_weight
        if age_s <= 86400:
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
        """Assemble the system prompt from the prompt template + context nodes."""
        parts: list[str] = []

        if self.prompt:
            parts.append(self.prompt.render(**prompt_vars))
        elif self.agent_node.system_prompt:
            parts.append(self.agent_node.system_prompt)

        if self.context:
            parts.append("\n\n## Relevant Context\n")
            for ctx in self.context:
                header = f"### {ctx.name}" if ctx.name else "###"
                if ctx.source:
                    header += f" (source: {ctx.source})"
                parts.append(f"{header}\n{ctx.content}")

        return "\n".join(parts)

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

        # 1. Discover tools via HAS_TOOL edges (order by edge weight desc)
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

        # 3. Discover prompt template via HAS_PROMPT edge (first match)
        prompt_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.HAS_PROMPT)
        prompt = next((n for n in prompt_nodes if isinstance(n, PromptNode)), None)

        # 4. Discover delegate agents via DELEGATES_TO edges
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

@dataclass
class ExecutionOptions:
    """Runtime controls for GraphExecutor.run().

    Pass as ``options=ExecutionOptions(...)`` to customize execution.
    """

    allowed_tools: set[str] | None = None


# ---------------------------------------------------------------------------
# GraphExecutor — dispatches nodes and traverses the graph
# ---------------------------------------------------------------------------

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
        self._backend     = backend or default_backend()
        self._router_model = router_model

        # callable_ref → async/sync Python callable
        # Populated via register_tool() or via ToolRegistry
        self._tool_fns: dict[str, Any] = {}
        self._event_hooks: list[Callable[[TraceEvent, ExecutionContext], Any]] = []

    def register_tool(self, callable_ref: str, fn: Any) -> None:
        """Register a callable under its dotted ref string."""
        self._tool_fns[callable_ref] = fn

    def add_event_hook(self, fn: Callable[[TraceEvent, ExecutionContext], Any]) -> None:
        """Register a callback invoked for every emitted event."""
        self._event_hooks.append(fn)

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
            timestamp=datetime.now(timezone.utc),
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

    async def run(
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
        """Execute a query starting from entry_node_id.

        strategy:
          "sequential"  — DFS: run → route → next (default for agent chains)
          "parallel"    — BFS: fan-out to all DELEGATES_TO targets concurrently
          "topological" — DAG waves using graphlib.TopologicalSorter

        extra_messages:
          Optional list of {"role": ..., "content": ...} dicts prepended to the
          message history before the main query.  Used by BatchExecutor to inject
          per-item context without mutating the graph.

        options:
          Runtime controls. Pass as ``options=ExecutionOptions(...)``
          to override allowed_tools.
        """
        ctx = execution_context or ExecutionContext(query=query, max_hops=max_hops)
        ctx.query = query
        ctx.max_hops = max_hops
        if extra_messages:
            ctx.extra_messages = list(extra_messages)
        if state:
            ctx.state.data.update(state)
        if allowed_tools is not None:
            ctx.allowed_tools = set(allowed_tools)
        if options is not None:
            if options.allowed_tools is not None:
                ctx.allowed_tools = options.allowed_tools
        try:
            entry = await self.store.get_node(entry_node_id)
            if entry is None:
                raise ValueError(
                    f"Entry node {entry_node_id!r} not found in graph store.\n"
                    "Hint: use `agent.node_id` (not `agent.name`) as the entry_node_id,\n"
                    "or call `await store.list_nodes()` to inspect what is in the store."
                )
            if strategy == "sequential":
                await self._run_sequential(entry, ctx)
            elif strategy == "parallel":
                await self._run_parallel(entry, ctx)
            elif strategy == "topological":
                await self._run_topological(entry_node_id, ctx)
            else:
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
        return await self.run(
            entry_node_id,
            ctx.query,
            strategy=strategy,
            max_hops=ctx.max_hops,
            execution_context=ctx,
        )

    async def batch(
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
        """Run an agent over a list of items with concurrency control.

        Convenience wrapper over BatchExecutor.  Prefer this over constructing
        ``BatchExecutor`` directly.

        Example::

            run = await executor.batch(
                agent.node_id,
                documents,
                query_fn=lambda doc: f"Summarise: {doc['title']}",
                context_fn=lambda doc: doc["body"],
                on_progress=lambda r: print(f"{r.progress:.0%}"),
            )
            print(run.status)

        Returns a ``BatchRun`` dataclass.
        """
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
    ) -> ContextNode:
        """Persist a resumable execution snapshot as a runtime context node."""
        checkpoint = ContextNode(
            name=name,
            description="Serialized execution checkpoint",
            content=json.dumps(ctx.snapshot(), default=str),
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

    async def load_checkpoint(self, checkpoint_node_id: str) -> ExecutionContext:
        """Restore an execution context from a checkpoint node."""
        node = await self.store.get_node(checkpoint_node_id)
        if not isinstance(node, ContextNode):
            raise ValueError(f"Checkpoint node not found: {checkpoint_node_id}")
        return ExecutionContext.from_snapshot(json.loads(node.content))

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
            if isinstance(current, dict):
                if part not in current:
                    return None
                current = current[part]
                continue
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
        if source == "result":
            return result
        if source == "input":
            return input_payload
        if source == "output":
            return output_payload
        return state.data

    def _compare_values(self, operator: str, left: Any, right: Any) -> bool:
        if operator == "exists":
            return left is not None
        if operator == "truthy":
            return bool(left)
        if operator == "contains":
            return left is not None and right in left
        if operator == "not_equals":
            return left != right
        if operator == "in":
            return left in right if right is not None else False
        if operator == "regex":
            return isinstance(left, str) and isinstance(right, str) and re.search(right, left) is not None
        if operator == "gt":
            return left > right
        if operator == "gte":
            return left >= right
        if operator == "lt":
            return left < right
        if operator == "lte":
            return left <= right
        return left == right

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
        return self._compare_values(
            rule.operator,
            self._resolve_json_path(
                state.data if rule.source == "state" else result,
                rule.path,
            ) if rule.path else (state.data if rule.source == "state" else result),
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
        if schema_type == "object":
            if not isinstance(payload, dict):
                raise ValueError(f"{label} must be an object")
            required = schema.get("required", [])
            for key in required:
                if key not in payload:
                    raise ValueError(f"{label} missing required field {key!r}")
            properties = schema.get("properties", {})
            for key, subschema in properties.items():
                if key in payload:
                    self._validate_against_schema(payload[key], subschema, label=f"{label}.{key}")
            return
        if schema_type == "array":
            if not isinstance(payload, list):
                raise ValueError(f"{label} must be an array")
            item_schema = schema.get("items", {})
            for idx, item in enumerate(payload):
                self._validate_against_schema(item, item_schema, label=f"{label}[{idx}]")
            return
        if schema_type == "string" and not isinstance(payload, str):
            raise ValueError(f"{label} must be a string")
        if schema_type == "integer" and not isinstance(payload, int):
            raise ValueError(f"{label} must be an integer")
        if schema_type == "number" and not isinstance(payload, (int, float)):
            raise ValueError(f"{label} must be a number")
        if schema_type == "boolean" and not isinstance(payload, bool):
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
            if isinstance(node, ToolNode):
                if input_payload is not None:
                    self._validate_against_schema(input_payload, node.input_schema, label="tool_input")
                if output_payload is not None:
                    self._validate_against_schema(output_payload, node.output_schema, label="tool_output")
            if isinstance(node, AgentNode):
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

        # Emit hop first so it becomes the parent container for all child events
        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={
            "hop":       ctx.hop_count,
            "node_type": str(node.node_type),
            "summary":   "",  # filled in below after execution
        })

        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)
        ctx.outputs[node.node_id] = result
        ctx.state.data["_last_node_id"] = node.node_id
        ctx.state.data["_last_output"] = result

        # Back-fill summary now that we have the result
        hop_event.payload["summary"] = _summarise(result)

        if ctx.is_paused():
            return result

        # Follow routing for AgentNodes
        if isinstance(node, AgentNode) and node.routing_table:
            next_id = await self._route(node, result, ctx, parent_event_id=hop_event.event_id)
            if next_id and next_id != "__END__":
                next_node = await self.store.get_node(next_id)
                if next_node:
                    return await self._run_sequential(next_node, ctx)
        if isinstance(node, ApprovalNode):
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

    async def _run_topological(self, entry_node_id: str, ctx: ExecutionContext) -> None:
        """Execute a DAG in topological order using stdlib graphlib.

        Nodes with no unresolved dependencies execute in parallel per wave.
        Results flow downstream via ctx.outputs.
        """
        # Build local dependency dict from the graph reachable from entry.
        # TransformNode.input_keys that reference node_ids in the graph are
        # treated as explicit fan-in dependencies so the sorter waits for all
        # listed branches before firing the transform.
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

        # Second pass: add TransformNode.input_keys as explicit dependencies.
        for nid in list(dep_map):
            node = await self.store.get_node(nid)
            if isinstance(node, TransformNode) and node.input_keys:
                for key in node.input_keys:
                    if key in dep_map:  # key is a node_id in this subgraph
                        dep_map[nid].add(key)

        sorter = graphlib.TopologicalSorter(dep_map)
        sorter.prepare()

        wave = 0
        while sorter.is_active():
            if ctx.is_paused():
                return
            if ctx.hop_count >= ctx.max_hops:
                return
            wave += 1
            ready = list(sorter.get_ready())
            remaining = max(ctx.max_hops - ctx.hop_count, 0)
            if remaining == 0:
                return
            if len(ready) > remaining:
                ready = ready[:remaining]
            nodes = list(await asyncio.gather(*[self.store.get_node(nid) for nid in ready]))

            # Emit hop events before execution so they parent the child events
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
                ctx.outputs[nid] = result
                ctx.state.data["_last_node_id"] = nid
                ctx.state.data["_last_output"] = result
                hop_event.payload["summary"] = _summarise(result)
                hop_event.payload["wave_ms"] = wave_ms
                sorter.done(nid)

    # ------------------------------------------------------------------
    # Node dispatch
    # ------------------------------------------------------------------

    async def _execute_node(
        self,
        node:            AnyNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> Any:
        if isinstance(node, AgentNode):
            return await self._execute_agent(node, ctx, parent_event_id=parent_event_id)
        if isinstance(node, ToolNode):
            return await self._execute_tool(node, ctx)
        if isinstance(node, ApprovalNode):
            return await self._execute_approval(node, ctx, parent_event_id=parent_event_id)
        if isinstance(node, ContextNode):
            return node.content
        if isinstance(node, GraphNode):
            self._emit(ctx, "subgraph_enter", node.node_id, node.name or "",
                       payload={"entry_node_id": node.entry_node_id},
                       parent_event_id=parent_event_id)
            sub_entry = await self.store.get_node(node.entry_node_id)
            result = None
            if sub_entry:
                result = await self._run_sequential(sub_entry, ctx)
            self._emit(ctx, "subgraph_exit", node.node_id, node.name or "",
                       payload={"exit_node_id": node.exit_node_id or "", "summary": _summarise(result)},
                       parent_event_id=parent_event_id)
            return result
        if isinstance(node, TransformNode):
            return await self._execute_transform(node, ctx, parent_event_id=parent_event_id)
        if isinstance(node, PromptNode):
            return node.render()
        return None

    # ------------------------------------------------------------------
    # Agent execution
    # ------------------------------------------------------------------

    async def _execute_agent(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        if node.pause_before:
            await self._pause_execution(
                ctx,
                node,
                reason="pause_before",
                waiting_for=node.wait_for_input,
            )
            return {"text": "", "intent": "default", "status": "paused"}
        t0 = time.monotonic()
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

        # Emit agent_start as child of the hop event; generate its own event_id
        # so tool_call / context_inject / agent_end can reference it as parent.
        agent_event_id = str(uuid.uuid4())
        self._emit(
            ctx, "agent_start", node.node_id, node.name or "",
            payload={
                "query":   ctx.query,
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

        # Emit context_inject if any context was assembled
        if composed.context:
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

        # Build message history — inject prior outputs as assistant context
        messages: list[dict[str, Any]] = list(ctx.extra_messages)
        if ctx.state.data:
            messages.append({
                "role": "assistant",
                "content": f"Workflow state:\n{json.dumps(ctx.state.data, sort_keys=True, default=str)}",
            })
        messages.append({"role": "user", "content": ctx.query})

        last_response = None
        iterations = 0

        # Agentic tool-call loop
        for _iteration in range(node.max_iterations):
            iterations += 1
            policy = node.execution_policy
            try:
                last_response = await self._call_with_retry(
                    lambda: self._chat_once(node, system, messages, tool_defs),
                    ctx,
                    node=node,
                    policy=policy,
                    parent_event_id=agent_event_id,
                )
            except Exception:
                raise

            if last_response.stop_reason == "end_turn":
                intent = await self._infer_intent(last_response.text, node)
                result = {"text": last_response.text, "intent": intent}
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
                duration_ms = int((time.monotonic() - t0) * 1000)
                self._emit(
                    ctx, "agent_end", node.node_id, node.name or "",
                    payload={
                        "text_summary": _summarise(last_response.text),
                        "intent":       intent,
                        "iterations":   iterations,
                    },
                    parent_event_id=agent_event_id,
                    duration_ms=duration_ms,
                )
                return result

            if last_response.stop_reason == "tool_use":
                tool_results = await self._handle_tool_calls(
                    last_response, node, ctx, parent_event_id=agent_event_id
                )
                messages = self._backend.extend_messages(messages, last_response, tool_results)
                continue

            # Unexpected stop reason — return what we have
            break

        text = last_response.text if last_response else ""
        duration_ms = int((time.monotonic() - t0) * 1000)
        self._emit(
            ctx, "agent_end", node.node_id, node.name or "",
            payload={
                "text_summary": _summarise(text),
                "intent":       "default",
                "iterations":   iterations,
            },
            parent_event_id=agent_event_id,
            duration_ms=duration_ms,
        )
        result = {"text": text, "intent": "default"}
        await self._validate_node_schemas(
            node,
            output_payload=result,
            ctx=ctx,
            parent_event_id=agent_event_id,
        )
        return result

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
                task.resolved_at = datetime.now(timezone.utc)
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
                datetime.now(timezone.utc) + timedelta(seconds=node.sla_seconds)
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
        response:        Any,   # LLMResponse
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

            # Emit tool_call event
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
                content = f"Tool {tc.name!r} not found."
                success = False
            else:
                try:
                    raw = await self._execute_tool(tool_node, ctx, input_data=tc.input)
                    await self._materialise_output(tool_node, raw, ctx)
                    content = raw if isinstance(raw, str) else str(raw)
                    success = True
                except Exception as exc:
                    content = f"Tool error: {exc}"
                    success = False

            duration_ms = int((time.monotonic() - t0) * 1000)

            # Emit tool_result event
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

        payload = input_data or (list(ctx.outputs.values())[-1] if ctx.outputs else {})
        runtime_payload = dict(payload) if isinstance(payload, dict) else {"input": payload}
        await self._validate_node_schemas(node, input_payload=payload, ctx=ctx)
        idempotency_key = self._idempotency_key(node, payload)
        if idempotency_key:
            if idempotency_key in ctx.state.idempotency_cache:
                return ctx.state.idempotency_cache[idempotency_key]

        async def invoke() -> Any:
            if node.is_async:
                return await fn(runtime_payload)
            return await asyncio.to_thread(fn, runtime_payload)

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

        # Collect fan-in inputs: each input_key is tried first as a node_id in
        # ctx.outputs, then as a key in ctx.state.data.  When no input_keys are
        # declared, use the last output if available, otherwise ctx.state.data
        # (covers the case where the transform is the entry node).
        if node.input_keys:
            input_data: dict[str, Any] = {}
            for key in node.input_keys:
                if key in ctx.outputs:
                    input_data[key] = ctx.outputs[key]
                elif key in ctx.state.data:
                    input_data[key] = ctx.state.data[key]
        elif ctx.outputs:
            last = list(ctx.outputs.values())[-1]
            input_data = dict(last) if isinstance(last, dict) else {"input": last}
        else:
            input_data = dict(ctx.state.data)

        idempotency_key = self._idempotency_key(node, input_data)
        if idempotency_key and idempotency_key in ctx.state.idempotency_cache:
            return ctx.state.idempotency_cache[idempotency_key]

        t0 = time.monotonic()

        async def invoke() -> Any:
            if node.is_async:
                return await fn(input_data)
            return await asyncio.to_thread(fn, input_data)

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

    async def _chat_once(
        self,
        node: AgentNode,
        system: str,
        messages: list[dict[str, Any]],
        tool_defs: list[dict[str, Any]],
    ) -> Any:
        return await self._backend.chat(
            model=node.model,
            system=system,
            messages=messages,
            tools=tool_defs,
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
            except Exception as exc:
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

    def _idempotency_key(self, node: ToolNode, payload: Any) -> str:
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
        """Write execution output back into the graph as a ContextNode.

        The resulting context is reachable by future agents via vector_search
        or explicit HAS_CONTEXT edges — no external memory store needed.

        Runtime nodes are tagged so they can be identified and cleaned up
        without graph traversal:
        - group_id = ctx.session_id       → fast session-scoped queries
        - attributes["origin"] = "runtime" → discriminates from predefined nodes
          even when group_id is filtered by something other than session
        """
        from yggdrasil_lm.core.nodes import ContextNode
        from yggdrasil_lm.core.edges import Edge

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
        """Classify routing intent from agent output text.

        Uses an LLM for accurate intent detection when a backend and routing
        table are available; falls back to keyword matching otherwise.
        """
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
            response = await self._backend.chat(
                model=self._router_model,
                system=_ROUTER_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                tools=[],
            )
            data = json.loads(response.text.strip())
            return str(data.get("intent", "default"))
        except Exception:
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
        """LLM-based router: pick the best AgentNode for *query*.

        Makes a single lightweight LLM call that returns structured JSON with
        an explicit reason and confidence score, making routing fully observable.

        Args:
            query:      The user task or query string.
            candidates: AgentNodes to consider; defaults to all valid agents
                        in the store.

        Returns:
            RoutingDecision with agent_id, reason, confidence (and an optional
            low_confidence_warning when confidence < 0.7).

        Falls back to the first candidate at confidence 0.5 if JSON parsing fails.
        """
        if candidates is None:
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]

        if not candidates:
            raise ValueError("No valid AgentNode candidates found in the store.")

        if len(candidates) == 1:
            return RoutingDecision(
                agent_id=candidates[0].node_id,
                reason="Only one agent available.",
                confidence=1.0,
            )

        agent_list = "\n".join(f"- {n.node_id}: {n.description}" for n in candidates)
        prompt = _ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)

        try:
            response = await self._backend.chat(
                model=self._router_model,
                system=_ROUTER_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                tools=[],
            )
            data = json.loads(response.text.strip())
            return RoutingDecision(
                agent_id=str(data["agent"]),
                reason=str(data.get("reason", "")),
                confidence=float(data.get("confidence", 0.5)),
            )
        except Exception:
            return RoutingDecision(
                agent_id=candidates[0].node_id,
                reason="Fallback: router response could not be parsed.",
                confidence=0.5,
            )

    async def plan(self, query: str) -> RoutingDecision:
        """Deprecated alias for route().

        .. deprecated::
            Use ``await executor.route(query)`` instead.  ``plan()`` will be
            removed in a future release.
        """
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
        """Phase 2 of two-phase dispatch: run *agent_id* and return a structured envelope.

        Args:
            agent_id: node_id of the AgentNode to execute.
            query:    The user task — a plain string or a multimodal content list.
            routing:  RoutingDecision from plan(); if omitted, a direct-execution
                      stub is used (confidence 1.0, no warning).

        Returns:
            AgentResult with routed_to, reason, confidence, context_injected,
            result, and an optional low_confidence_warning.
        """
        node = await self.store.get_node(agent_id)
        if node is None or not isinstance(node, AgentNode):
            raise ValueError(f"Agent node not found or not an AgentNode: {agent_id!r}")

        composed = await self.composer.compose(node, query=_query_text(query))
        context_names = [c.name for c in composed.context if c.name]

        ctx = ExecutionContext(query=query)
        raw = await self._execute_agent(node, ctx)
        text = raw.get("text", "") if isinstance(raw, dict) else str(raw)

        decision = routing or RoutingDecision(
            agent_id=agent_id,
            reason="Direct execution (no routing phase).",
            confidence=1.0,
        )

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

def print_trace(ctx: ExecutionContext | list[TraceEvent], *, width: int = 72) -> None:
    """Print the execution trace as a human-readable tree.

    Groups events by parent_event_id to show the agent → tool → result
    hierarchy. Emits timing, intent, confidence warnings, and context
    injection summaries inline.

    Args:
        ctx:   An ExecutionContext (uses ctx.trace and ctx.session_id / ctx.query)
               or a raw list[TraceEvent].
        width: Console width for the separator line (default 72).

    Example output::

        Session a1b2c3d4  "research and summarise quantum computing"
        ════════════════════════════════════════════════════════════════════════
        hop 1  AGENT  researcher
          context_inject  web_results, doc_chunk  (2 nodes)
          tool_call       web_search  {"query": "quantum computing 2024"}
            tool_result   web_search  ok  "Results: quantum…"          [12ms]
          routing         synthesis_needed → synthesizer_node_id
          agent_end       "Based on the research, quantum…"  intent=synthesis_needed  [45ms]
        hop 2  AGENT  synthesizer
          agent_end       "Final summary: …"  intent=default  [32ms]
        ════════════════════════════════════════════════════════════════════════
        Total: 2 hops · 2 agent_end events · 77ms
    """
    if isinstance(ctx, ExecutionContext):
        events = ctx.trace
        session_id = ctx.session_id[:8]
        query = _query_text(ctx.query)
    else:
        events = ctx
        session_id = events[0].session_id[:8] if events else "?"
        query = ""

    sep = "═" * width
    print(f"\nSession {session_id}  {query!r}")
    print(sep)

    # Index events by event_id for O(1) parent lookup
    by_id: dict[str, TraceEvent] = {e.event_id: e for e in events}
    # Group children by parent_event_id
    children: dict[str | None, list[TraceEvent]] = {}
    for e in events:
        children.setdefault(e.parent_event_id, []).append(e)

    def _fmt_ms(ms: int | None) -> str:
        return f"[{ms}ms]" if ms is not None else ""

    def _render(event: TraceEvent, indent: int) -> None:
        pad = "  " * indent
        t   = event.event_type
        p   = event.payload
        ms  = _fmt_ms(event.duration_ms)

        if t == "hop":
            node_type = p.get("node_type", "").split(".")[-1].upper()
            hop_num   = p.get("hop", "")
            hop_label = f"hop {hop_num}  " if hop_num else ""
            print(f"{pad}{hop_label}{node_type}  {event.node_name}")
            for child in children.get(event.event_id, []):
                _render(child, indent + 1)

        elif t == "agent_start":
            tools = ", ".join(p.get("tools", [])) or "none"
            ctx_l = p.get("context", [])
            ctx_s = f"  context: {', '.join(ctx_l)}" if ctx_l else ""
            print(f"{pad}tools: {tools}{ctx_s}")
            if p.get("context_scores"):
                ranked = []
                for item in p["context_scores"]:
                    ranked.append(
                        f"{item.get('name')}[{item.get('score')}, {item.get('source')}, hops={item.get('hops')}]"
                    )
                print(f"{pad}ranked_context: {' | '.join(ranked)}")
            for child in children.get(event.event_id, []):
                _render(child, indent)

        elif t == "context_inject":
            names = ", ".join(p.get("context_names", [])) or "—"
            count = p.get("count", 0)
            print(f"{pad}context_inject  {names}  ({count} nodes)")
            selected = p.get("selected_contexts", [])
            for item in selected:
                reasons = ", ".join(item.get("reasons", []))
                print(
                    f"{pad}  selected  {item.get('name')}  score={item.get('score')}  "
                    f"source={item.get('source')}  hops={item.get('hops')}  "
                    f"tokens={item.get('token_count')}"
                )
                if reasons:
                    print(f"{pad}    reasons  {reasons}")

        elif t == "agent_end":
            summary = p.get("text_summary", "")
            intent  = p.get("intent", "default")
            iters   = p.get("iterations", 1)
            iter_s  = f"  iters={iters}" if iters > 1 else ""
            print(f"{pad}agent_end  {summary!r}  intent={intent}{iter_s}  {ms}")

        elif t == "tool_call":
            inp = json.dumps(p.get("input", {}), ensure_ascii=False)
            inp = inp[:60] + "…" if len(inp) > 60 else inp
            print(f"{pad}tool_call  {event.node_name}  {inp}")
            for child in children.get(event.event_id, []):
                _render(child, indent + 1)

        elif t == "tool_result":
            status  = "ok" if p.get("success") else "err"
            summary = p.get("output_summary", "")
            print(f"{pad}tool_result  {event.node_name}  {status}  {summary!r}  {ms}")

        elif t == "routing":
            intent  = p.get("intent", "default")
            next_id = p.get("next_node_id") or "__END__"
            conf    = p.get("confidence")
            conf_s  = f"  conf={conf:.0%}" if conf is not None else ""
            print(f"{pad}routing  {intent} → {next_id}{conf_s}")

        elif t == "subgraph_enter":
            print(f"{pad}subgraph_enter  {event.node_name}  entry={p.get('entry_node_id','')}")
            for child in children.get(event.event_id, []):
                _render(child, indent + 1)

        elif t == "subgraph_exit":
            print(f"{pad}subgraph_exit   {event.node_name}  {ms}")

    # Render top-level events (no parent) in order.
    # With the current design, only "hop" and "subgraph_enter/exit" are top-level;
    # agent_start / agent_end are children of hop events.
    total_ms = 0
    hops     = 0
    ends     = 0
    for event in children.get(None, []):
        _render(event, indent=0)
        if event.event_type == "hop":
            hops += 1

    for event in events:
        if event.event_type == "agent_end":
            ends += 1
            if event.duration_ms:
                total_ms += event.duration_ms

    print(sep)
    ms_s = f" · {total_ms}ms" if total_ms else ""
    print(f"Total: {hops} hops · {ends} agent_end events{ms_s}\n")


# ---------------------------------------------------------------------------
# Runtime node utilities
# ---------------------------------------------------------------------------

async def get_runtime_nodes(
    store:      GraphStore,
    session_id: str | None = None,
    only_valid: bool = True,
) -> list[ContextNode]:
    """Return runtime-materialised ContextNodes without graph traversal.

    Uses the ``attributes["origin"] == "runtime"`` tag set by
    ``_materialise_output`` as the discriminator, so no edge traversal is
    needed.  When *session_id* is provided the query is further narrowed to
    ``group_id == session_id``, making it O(nodes-in-session) instead of
    O(all-nodes).

    Args:
        store:      The graph store to query.
        session_id: Limit results to a specific session.  Pass
                    ``ctx.session_id`` from a completed run.  When ``None``
                    all runtime nodes across all sessions are returned.
        only_valid: Skip expired nodes (default True).

    Returns:
        List of ContextNode objects tagged as runtime-materialised.

    Example::

        ctx = await executor.run(agent.node_id, "query")

        # All runtime nodes from this session
        nodes = await get_runtime_nodes(store, session_id=ctx.session_id)
        for n in nodes:
            print(n.name, n.attributes["source_node_id"])

        # All runtime nodes across every session (slower)
        all_runtime = await get_runtime_nodes(store)
    """
    candidates = await store.list_nodes(
        node_type=NodeType.CONTEXT,
        group_id=session_id,   # None → no group_id filter; str → fast path
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
    """Expire (or hard-delete) all runtime nodes from *session_id*.

    Because runtime nodes are written with ``group_id = session_id``,
    ``store.list_nodes(group_id=session_id)`` returns exactly the nodes
    created during that run — no edge traversal required.

    The PRODUCES edges that connect source nodes to the materialised
    ContextNodes are soft-expired too (or hard-deleted when ``hard=True``),
    keeping the graph consistent.

    Args:
        store:      The graph store to clean up.
        session_id: The session to clean up; pass ``ctx.session_id``.
        hard:       When True, hard-delete nodes and edges instead of
                    soft-expiring them.  Soft-expire (the default) preserves
                    history and allows point-in-time queries.

    Returns:
        Number of nodes removed/expired.

    Example::

        ctx = await executor.run(agent.node_id, "query")

        # Soft-expire (preserves history)
        n = await cleanup_session(store, ctx.session_id)
        print(f"Expired {n} runtime nodes")

        # Hard-delete (frees memory / storage)
        n = await cleanup_session(store, ctx.session_id, hard=True)
    """
    nodes = await store.list_nodes(group_id=session_id, only_valid=False)
    count = 0
    for node in nodes:
        # Expire/delete inbound PRODUCES edges to keep the graph consistent
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
