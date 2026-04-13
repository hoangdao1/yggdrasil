"""Tests for GraphExecutor — sequential, parallel, and topological strategies.

LLM calls are stubbed so these tests run without an API key.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest

from yggdrasil.backends.llm import LLMBackend, LLMResponse, ToolCall
from yggdrasil.core.edges import Edge, EdgeType
from yggdrasil.core.executor import AgentComposer, ContextNavigator, ExecutionContext, GraphExecutor
from yggdrasil.core.nodes import (
    AgentNode,
    ApprovalNode,
    ConstraintRule,
    ContextNode,
    DecisionRule,
    DecisionTable,
    ExecutionPolicy,
    GraphNode,
    RetryPolicy,
    RouteRule,
    SchemaNode,
    ToolNode,
)
from yggdrasil.core.store import NetworkXGraphStore
from yggdrasil.core.executor import TraceEvent, WorkflowState
from yggdrasil.observability import explain_run


# ---------------------------------------------------------------------------
# Stub LLM backend for tests — no API key required
# ---------------------------------------------------------------------------

class StubBackend(LLMBackend):
    """Configurable stub: returns preset responses in order."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = list(responses)
        self._index = 0

    async def chat(self, model, system, messages, tools, max_tokens=8096) -> LLMResponse:
        resp = self._responses[self._index % len(self._responses)]
        self._index += 1
        return resp

    def extend_messages(self, messages, response, tool_results):
        # Minimal continuation — sufficient for tests
        continuation = []
        if response.tool_calls:
            continuation.append({"role": "assistant", "content": str(response.tool_calls)})
        for tr in tool_results:
            continuation.append({"role": "tool", "content": tr.content})
        return messages + continuation


def _end_turn(text: str) -> LLMResponse:
    return LLMResponse(text=text, tool_calls=[], stop_reason="end_turn")


def _tool_use(tool_id: str, name: str, input: dict) -> LLMResponse:
    return LLMResponse(
        text="",
        tool_calls=[ToolCall(id=tool_id, name=name, input=input)],
        stop_reason="tool_use",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    return NetworkXGraphStore()


@pytest.fixture
def executor(store):
    return GraphExecutor(store, backend=StubBackend([_end_turn("stub")]))


# ---------------------------------------------------------------------------
# ContextNode execution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_context_node_returns_content(store, executor):
    ctx_node = ContextNode(name="Fact", content="The sky is blue.")
    await store.upsert_node(ctx_node)

    result = await executor._execute_node(ctx_node, ExecutionContext(query="test"))
    assert result == "The sky is blue."


# ---------------------------------------------------------------------------
# ToolNode execution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tool_node_calls_registered_fn(store, executor):
    tool = ToolNode(name="echo", callable_ref="tools.echo", description="echo")
    await store.upsert_node(tool)

    executor.register_tool("tools.echo", AsyncMock(return_value="pong"))
    result = await executor._execute_tool(tool, ExecutionContext(query="ping"), input_data={"msg": "ping"})
    assert result == "pong"


@pytest.mark.asyncio
async def test_tool_node_raises_if_not_registered(store, executor):
    tool = ToolNode(name="missing", callable_ref="tools.missing", description="x")
    await store.upsert_node(tool)

    with pytest.raises(RuntimeError, match="not registered"):
        await executor._execute_tool(tool, ExecutionContext(query="x"))


# ---------------------------------------------------------------------------
# AgentNode execution (LLM stubbed)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_end_turn_returns_text(store):
    agent = AgentNode(name="A", description="agent", routing_table={"default": "__END__"})
    await store.upsert_node(agent)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Hello from agent.")]))
    ctx = ExecutionContext(query="hi")
    result = await executor._execute_agent(agent, ctx)
    assert result["text"] == "Hello from agent."


@pytest.mark.asyncio
async def test_agent_tool_call_loop(store):
    """Agent calls a tool once then returns."""
    tool = ToolNode(
        name="echo",
        callable_ref="tools.echo",
        description="echo",
        input_schema={"type": "object", "properties": {}},
    )
    agent = AgentNode(name="A", description="agent", routing_table={"default": "__END__"})
    await store.upsert_node(tool)
    await store.upsert_node(agent)
    await store.upsert_edge(Edge.has_tool(agent.node_id, tool.node_id))

    executor = GraphExecutor(store, backend=StubBackend([
        _tool_use("tu_1", "echo", {}),
        _end_turn("Done after tool."),
    ]))
    executor.register_tool("tools.echo", AsyncMock(return_value="echoed"))

    ctx = ExecutionContext(query="run echo")
    result = await executor._execute_agent(agent, ctx)
    assert result["text"] == "Done after tool."


@pytest.mark.asyncio
async def test_context_trace_includes_navigation_metadata(store):
    """context_inject events include ranked context selection details."""
    agent = AgentNode(name="A", description="agent", routing_table={"default": "__END__"})
    ctx_node = ContextNode(name="Fact", content="Fresh fact", embedding=[1.0, 0.0], tags=["fresh"])
    await store.upsert_node(agent)
    await store.upsert_node(ctx_node)
    await store.upsert_edge(Edge.has_context(agent.node_id, ctx_node.node_id, weight=0.9))

    embedder = AsyncMock()
    embedder.embed_text.return_value = [1.0, 0.0]
    executor = GraphExecutor(
        store,
        backend=StubBackend([_end_turn("Hello from agent.")]),
        embedder=embedder,
        context_navigator=ContextNavigator(max_context_nodes=4),
    )

    ctx = ExecutionContext(query="fresh")
    await executor._execute_agent(agent, ctx)

    injects = [e for e in ctx.trace if e.event_type == "context_inject"]
    assert len(injects) == 1
    selected = injects[0].payload["selected_contexts"]
    assert selected[0]["name"] == "Fact"
    assert selected[0]["source"] == "attached"
    assert selected[0]["reasons"]


# ---------------------------------------------------------------------------
# Sequential traversal
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sequential_routing_between_agents(store):
    """ResearcherAgent routes to SynthesizerAgent via routing_table."""
    synthesizer = AgentNode(
        name="Synthesizer",
        description="synth",
        routing_table={"default": "__END__"},
    )
    researcher = AgentNode(
        name="Researcher",
        description="research",
        routing_table={"default": synthesizer.node_id},
    )
    await store.upsert_node(synthesizer)
    await store.upsert_node(researcher)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Research done.")]))
    ctx = await executor.run(researcher.node_id, "research something", strategy="sequential")
    # Both agents should appear in outputs
    assert researcher.node_id  in ctx.outputs
    assert synthesizer.node_id in ctx.outputs


# ---------------------------------------------------------------------------
# Parallel traversal
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parallel_fan_out(store):
    """Supervisor delegates to two workers concurrently."""
    worker1 = AgentNode(name="Worker1", description="w1")
    worker2 = AgentNode(name="Worker2", description="w2")
    supervisor = AgentNode(name="Supervisor", description="sup")

    for n in [worker1, worker2, supervisor]:
        await store.upsert_node(n)
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, worker1.node_id))
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, worker2.node_id))

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Done.")]))
    ctx = await executor.run(supervisor.node_id, "do work", strategy="parallel")
    assert supervisor.node_id in ctx.outputs
    merged = ctx.outputs[supervisor.node_id]
    assert "delegate_results" in merged
    assert worker1.node_id in merged["delegate_results"]
    assert worker2.node_id in merged["delegate_results"]


# ---------------------------------------------------------------------------
# Topological traversal
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_topological_dag(store):
    """Three nodes A → B, A → C, B → D, C → D executed in correct wave order."""
    nodes = {name: AgentNode(name=name, description=name) for name in ["A", "B", "C", "D"]}
    for n in nodes.values():
        await store.upsert_node(n)

    await store.upsert_edge(Edge.delegates_to(nodes["A"].node_id, nodes["B"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["A"].node_id, nodes["C"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["B"].node_id, nodes["D"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["C"].node_id, nodes["D"].node_id))

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Done.")]))
    ctx = await executor.run(nodes["A"].node_id, "query", strategy="topological")
    # All four nodes should have outputs
    for n in nodes.values():
        assert n.node_id in ctx.outputs


# ---------------------------------------------------------------------------
# GraphNode (sub-graph)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_node_descends_into_subgraph(store):
    inner_agent = AgentNode(name="Inner", description="inner")
    await store.upsert_node(inner_agent)

    graph_node = GraphNode(
        name="SubGraph",
        description="wraps inner",
        entry_node_id=inner_agent.node_id,
    )
    await store.upsert_node(graph_node)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Inner done.")]))
    ctx = ExecutionContext(query="test")
    result = await executor._execute_node(graph_node, ctx)
    # Inner agent should have run and produced output
    assert inner_agent.node_id in ctx.outputs


# ---------------------------------------------------------------------------
# Output materialisation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_output_materialised_as_context_node(store):
    tool = ToolNode(name="echo", callable_ref="tools.echo", description="echo")
    await store.upsert_node(tool)

    executor = GraphExecutor(store)
    ctx = ExecutionContext(query="test")
    ctx_node = await executor._materialise_output(tool, "result text", ctx)

    # Context node should be in the store
    stored = await store.get_node(ctx_node.node_id)
    assert stored is not None
    assert stored.node_type == "context"
    assert "result text" in stored.content  # type: ignore[union-attr]

    # PRODUCES edge should exist
    edges = await store.get_edges(tool.node_id, direction="out")
    assert any(e.edge_type == "PRODUCES" for e in edges)


@pytest.mark.asyncio
async def test_deterministic_route_rule_uses_state_before_llm_intent(store):
    reviewer = AgentNode(name="Reviewer", routing_table={"default": "__END__"})
    agent = AgentNode(
        name="Router",
        routing_table={"default": "__END__"},
        route_rules=[
            RouteRule(
                name="needs_review",
                source="state",
                path="approval.required",
                operator="equals",
                value=True,
                target_node_id=reviewer.node_id,
                priority=10,
            )
        ],
    )
    await store.upsert_node(agent)
    await store.upsert_node(reviewer)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("all done")]))
    ctx = await executor.run(agent.node_id, "route me", state={"approval": {"required": True}})

    routing_events = [e for e in ctx.trace if e.event_type == "routing"]
    assert routing_events[0].payload["mode"] == "deterministic"
    assert reviewer.node_id in ctx.outputs


@pytest.mark.asyncio
async def test_pause_resume_and_checkpoint_round_trip(store):
    finisher = AgentNode(name="Finisher", routing_table={"default": "__END__"})
    agent = AgentNode(
        name="Approval",
        routing_table={"default": finisher.node_id},
        pause_after=True,
        wait_for_input="approval",
    )
    await store.upsert_node(finisher)
    await store.upsert_node(agent)

    backend = StubBackend([_end_turn("waiting"), _end_turn("resumed")])
    executor = GraphExecutor(store, backend=backend)

    ctx = await executor.run(agent.node_id, "start")
    assert ctx.is_paused()
    assert ctx.state.pending_pause is not None

    checkpoint = await executor.checkpoint_context(ctx)
    restored = await executor.load_checkpoint(checkpoint.node_id)
    restored.state.data["approval"] = {"approved": True}

    resumed = await executor.resume(finisher.node_id, restored, query="continue")
    assert not resumed.is_paused()
    assert restored.trace
    assert any(e.event_type == "resume" for e in resumed.trace)


@pytest.mark.asyncio
async def test_tool_retries_and_idempotency_cache(store):
    tool = ToolNode(
        name="flaky",
        callable_ref="tools.flaky",
        description="flaky tool",
        execution_policy=ExecutionPolicy(
            retry_policy=RetryPolicy(max_attempts=2),
            idempotency_key="auto",
        ),
    )
    await store.upsert_node(tool)
    executor = GraphExecutor(store)

    calls = {"count": 0}

    async def flaky(payload):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("boom")
        return f"ok:{payload['id']}"

    executor.register_tool("tools.flaky", flaky)
    ctx = ExecutionContext(query="x")

    first = await executor._execute_tool(tool, ctx, input_data={"id": "1"})
    second = await executor._execute_tool(tool, ctx, input_data={"id": "1"})

    assert first == "ok:1"
    assert second == "ok:1"
    assert calls["count"] == 2
    assert any(e.event_type == "retry" for e in ctx.trace)


@pytest.mark.asyncio
async def test_tool_schema_validation_via_inline_and_schema_node(store):
    tool = ToolNode(
        name="validated",
        callable_ref="tools.validated",
        description="validated tool",
        input_schema={
            "type": "object",
            "properties": {"count": {"type": "integer"}},
            "required": ["count"],
        },
        output_schema={"type": "string"},
    )
    schema = SchemaNode(
        name="OutputSchema",
        json_schema={"type": "string"},
    )
    await store.upsert_node(tool)
    await store.upsert_node(schema)
    await store.upsert_edge(
        Edge(
            edge_type=EdgeType.VALIDATES,
            src_id=schema.node_id,
            dst_id=tool.node_id,
            attributes={"phase": "output"},
        )
    )

    executor = GraphExecutor(store)
    executor.register_tool("tools.validated", AsyncMock(return_value="done"))
    ctx = ExecutionContext(query="x")

    result = await executor._execute_tool(tool, ctx, input_data={"count": 1})
    assert result == "done"

    with pytest.raises(ValueError):
        await executor._execute_tool(tool, ctx, input_data={"count": "bad"})


@pytest.mark.asyncio
async def test_event_hook_fires(store):
    agent = AgentNode(name="Hooked", routing_table={"default": "__END__"})
    await store.upsert_node(agent)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("ok")]))
    seen = []
    executor.add_event_hook(lambda event, ctx: seen.append(event.event_type))

    ctx = ExecutionContext(query="q")
    await executor.run(agent.node_id, "q", execution_context=ctx)
    assert "agent_start" in seen


@pytest.mark.asyncio
async def test_agent_state_schema_is_validated_before_execution(store):
    agent = AgentNode(
        name="Guarded",
        routing_table={"default": "__END__"},
        state_schema={
            "type": "object",
            "properties": {"approval": {"type": "boolean"}},
            "required": ["approval"],
        },
    )
    await store.upsert_node(agent)

    backend = StubBackend([_end_turn("should not run")])
    executor = GraphExecutor(store, backend=backend)
    ctx = ExecutionContext(query="q")

    with pytest.raises(ValueError, match="state missing required field 'approval'"):
        await executor.run(agent.node_id, "q", execution_context=ctx)

    assert backend._index == 0
    validation_events = [e for e in ctx.trace if e.event_type == "validation"]
    assert validation_events
    assert validation_events[0].payload["success"] is False


@pytest.mark.asyncio
async def test_topological_dag_runs_dependencies_before_dependents(store):
    nodes = {name: AgentNode(name=name, description=name) for name in ["A", "B", "C", "D"]}
    for n in nodes.values():
        await store.upsert_node(n)

    await store.upsert_edge(Edge.delegates_to(nodes["A"].node_id, nodes["B"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["A"].node_id, nodes["C"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["B"].node_id, nodes["D"].node_id))
    await store.upsert_edge(Edge.delegates_to(nodes["C"].node_id, nodes["D"].node_id))

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("Done.")]))
    ctx = await executor.run(nodes["A"].node_id, "query", strategy="topological")

    hops = [e for e in ctx.trace if e.event_type == "hop"]
    hop_by_name = {event.node_name: event.payload["hop"] for event in hops}

    assert hop_by_name["A"] < hop_by_name["B"]
    assert hop_by_name["A"] < hop_by_name["C"]
    assert hop_by_name["B"] < hop_by_name["D"]
    assert hop_by_name["C"] < hop_by_name["D"]


@pytest.mark.asyncio
async def test_constraint_rule_enforces_cross_step_invariant(store):
    agent = AgentNode(
        name="Constrained",
        routing_table={"default": "__END__"},
        constraint_rules=[
            ConstraintRule(
                name="echo_approval",
                source="result",
                path="text",
                operator="contains",
                compare_to_source="state",
                compare_to_path="approval.status",
                message="Result must mention approval status",
            )
        ],
    )
    await store.upsert_node(agent)
    executor = GraphExecutor(store, backend=StubBackend([_end_turn("missing")]))

    with pytest.raises(ValueError, match="Result must mention approval status"):
        await executor.run(agent.node_id, "q", state={"approval": {"status": "approved"}})


@pytest.mark.asyncio
async def test_approval_node_creates_inbox_task_and_routes_on_resume(store):
    approved = AgentNode(name="Approved", routing_table={"default": "__END__"})
    rejected = AgentNode(name="Rejected", routing_table={"default": "__END__"})
    approval = ApprovalNode(
        name="ManagerApproval",
        instructions="Manager must approve",
        assignees=["mgr-1"],
        sla_seconds=300,
        escalation_target="director",
        approved_target_id=approved.node_id,
        rejected_target_id=rejected.node_id,
    )
    for node in [approved, rejected, approval]:
        await store.upsert_node(node)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("done")]))
    ctx = await executor.run(approval.node_id, "start")
    assert ctx.is_paused()
    assert ctx.state.inbox

    ctx.state.data["approval"] = {"approved": True, "assigned_to": "mgr-1"}
    resumed = await executor.resume(approval.node_id, ctx, query="continue")
    assert approved.node_id in resumed.outputs
    assert any(event.event_type == "approval_task" for event in resumed.trace)


# ---------------------------------------------------------------------------
# DX commit validation tests (c80660c)
# ---------------------------------------------------------------------------

def test_end_node_constant():
    """END_NODE equals '__END__' and works as a routing_table value."""
    from yggdrasil import END_NODE

    assert END_NODE == "__END__"

    agent = AgentNode(name="TestEnd", routing_table={"default": END_NODE})
    assert agent.routing_table["default"] == "__END__"


@pytest.mark.asyncio
async def test_entry_node_not_found_error():
    """GraphExecutor.run raises ValueError with a helpful hint for bad entry node IDs."""
    store = NetworkXGraphStore()
    executor = GraphExecutor(store)

    with pytest.raises(ValueError, match="not found in graph store") as exc_info:
        await executor.run(entry_node_id="bad-id-12345", query="test")

    error_text = str(exc_info.value)
    assert "agent.node_id" in error_text  # hint about correct usage
    assert "bad-id-12345" in error_text    # shows the bad value


def test_agent_node_routing_table_default():
    """AgentNode.routing_table defaults to {'default': '__END__'}, not an empty dict."""
    agent = AgentNode(name="DefaultRouting")
    assert agent.routing_table == {"default": "__END__"}
    assert "default" in agent.routing_table


def test_embedder_import_error_message(monkeypatch):
    """When sentence-transformers is missing, Embedder raises ImportError with install hint."""
    import importlib
    import sys

    # Remove the cached module so we re-execute the import guard
    for mod_name in list(sys.modules):
        if "yggdrasil.retrieval.embedder" in mod_name:
            del sys.modules[mod_name]

    # Simulate sentence_transformers not being installed
    original = sys.modules.get("sentence_transformers")
    sys.modules["sentence_transformers"] = None  # type: ignore[assignment]

    try:
        with pytest.raises(ImportError, match="yggdrasil\\[embeddings\\]"):
            import yggdrasil.retrieval.embedder  # noqa: F401
    finally:
        # Restore original state
        if original is None:
            sys.modules.pop("sentence_transformers", None)
        else:
            sys.modules["sentence_transformers"] = original
        sys.modules.pop("yggdrasil.retrieval.embedder", None)


# ---------------------------------------------------------------------------
# explain_run — pause, migration, graph drift fields
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_explain_run_pause_fields(store):
    """explain_run.paused=True and pauses list populated when workflow pauses."""
    finisher = AgentNode(name="Finisher", routing_table={"default": "__END__"})
    agent = AgentNode(
        name="WaitAgent",
        routing_table={"default": finisher.node_id},
        pause_after=True,
        wait_for_input="approval",
    )
    await store.upsert_node(finisher)
    await store.upsert_node(agent)

    executor = GraphExecutor(store, backend=StubBackend([_end_turn("waiting")]))
    ctx = await executor.run(agent.node_id, "start")

    explanation = explain_run(ctx)
    assert explanation.paused is True
    assert len(explanation.pauses) >= 1
    assert explanation.pauses[0].node_id == agent.node_id


def test_explain_run_paused_true_but_no_pause_event():
    """explain_run.paused is True even when ctx.is_paused() but no pause event in trace."""
    from yggdrasil.core.executor import WorkflowPause
    ctx = ExecutionContext(query="test", session_id="sess-p")
    ctx.state.status = "paused"
    ctx.state.pending_pause = WorkflowPause(
        waiting_for="approval",
        reason="needs sign-off",
        node_id="node-1",
    )
    explanation = explain_run(ctx)
    assert explanation.paused is True
    assert explanation.pauses == []
