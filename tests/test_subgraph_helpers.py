"""Tests for sub-graph testing helpers: StubBackend, dry_run, run_subgraph."""

from __future__ import annotations

import pytest

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.core.executor import ExecutionContext, GraphExecutor
from yggdrasil_lm.core.nodes import AgentNode, GraphNode
from yggdrasil_lm.core.store import NetworkXGraphStore
from yggdrasil_lm.testing import StubBackend, end_turn, tool_use


# ---------------------------------------------------------------------------
# Public testing module
# ---------------------------------------------------------------------------

def test_stub_backend_returns_responses_in_order():
    backend = StubBackend([end_turn("A"), end_turn("B")])
    import asyncio
    r1 = asyncio.run(backend.chat("m", "", [], []))
    r2 = asyncio.run(backend.chat("m", "", [], []))
    assert r1.text == "A"
    assert r2.text == "B"
    assert len(backend.calls) == 2


def test_stub_backend_loops_when_exhausted():
    backend = StubBackend([end_turn("only")])
    import asyncio
    r1 = asyncio.run(backend.chat("m", "", [], []))
    r2 = asyncio.run(backend.chat("m", "", [], []))
    assert r1.text == r2.text == "only"


def test_stub_backend_callable_form():
    def make(model, system, messages, tools):
        return end_turn(f"saw {len(messages)} messages")
    backend = StubBackend(make)
    import asyncio
    r = asyncio.run(backend.chat("m", "", [{"role": "user", "content": "hi"}], []))
    assert "saw 1 messages" in r.text


def test_tool_use_helper():
    resp = tool_use("call_1", "echo", {"x": 1})
    assert resp.stop_reason == "tool_use"
    assert resp.tool_calls[0].name == "echo"
    assert resp.tool_calls[0].input == {"x": 1}


# ---------------------------------------------------------------------------
# Dry-run input resolution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dry_run_resolves_input_map_against_state():
    store = NetworkXGraphStore()
    inner = AgentNode(name="Inner")
    await store.upsert_node(inner)
    sub = GraphNode(
        name="Wired",
        entry_node_id=inner.node_id,
        input_map={"product_text": "current_product"},
    )
    await store.upsert_node(sub)

    executor = GraphExecutor(store, backend=StubBackend([end_turn("ok")]))
    ctx = ExecutionContext(query="parent query")
    ctx.state.data["current_product"] = "QuantumBoost X9"

    info = await executor.resolve_subgraph_inputs(sub, ctx)
    assert info["entry_node_id"] == inner.node_id
    assert info["exit_node_id"] == inner.node_id   # default to entry
    assert info["strategy"] == "sequential"
    assert info["scope_outputs"] is True
    assert info["state_overlay"] == {"product_text": "QuantumBoost X9"}


@pytest.mark.asyncio
async def test_dry_run_with_input_keys_concatenates():
    store = NetworkXGraphStore()
    inner = AgentNode(name="Inner")
    await store.upsert_node(inner)
    sub = GraphNode(
        name="WithKeys",
        entry_node_id=inner.node_id,
        input_keys=["context_a", "context_b"],
    )
    await store.upsert_node(sub)

    executor = GraphExecutor(store, backend=StubBackend([end_turn("ok")]))
    ctx = ExecutionContext(query="parent")
    ctx.state.data["context_a"] = "first"
    ctx.state.data["context_b"] = "second"

    info = await executor.resolve_subgraph_inputs(sub, ctx)
    assert "first" in info["query"]
    assert "second" in info["query"]


@pytest.mark.asyncio
async def test_dry_run_rejects_non_graph_node():
    store = NetworkXGraphStore()
    agent = AgentNode(name="NotASub")
    await store.upsert_node(agent)
    executor = GraphExecutor(store, backend=StubBackend([end_turn("x")]))
    with pytest.raises(ValueError, match="expected GraphNode"):
        await executor.resolve_subgraph_inputs(agent)


@pytest.mark.asyncio
async def test_dry_run_via_app():
    app = GraphApp(backend=StubBackend([end_turn("x")]))
    inner = await app.add_agent("Inner")
    sub = await app.add_subgraph(
        "S",
        entry=inner,
        input_map={"alias": "src"},
    )
    info = await app.dry_run_subgraph(sub, inputs={"src": "value"})
    assert info["state_overlay"] == {"alias": "value"}


# ---------------------------------------------------------------------------
# run_subgraph sugar
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_subgraph_executes_top_level():
    app = GraphApp(backend=StubBackend([end_turn("DONE")]))
    inner = await app.add_agent("Inner")
    sub = await app.add_subgraph("S", entry=inner)
    ctx = await app.run_subgraph(sub, query="go")
    assert ctx.outputs[sub.node_id]["text"] == "DONE"
    # scope_outputs=True default — inner not leaked into parent outputs
    assert inner.node_id not in ctx.outputs


@pytest.mark.asyncio
async def test_run_subgraph_threads_inputs_into_state():
    """Inputs supplied via run_subgraph land in state.data so input_map can read them."""
    app = GraphApp(backend=StubBackend([end_turn("ok")]))
    inner = await app.add_agent("Inner")
    sub = await app.add_subgraph(
        "S",
        entry=inner,
        input_map={"alias": "raw"},
    )
    ctx = await app.run_subgraph(sub, inputs={"raw": "hello"})
    # input_map applied during sub-run
    assert ctx.state.data.get("alias") == "hello"
    # original input still there too
    assert ctx.state.data.get("raw") == "hello"


@pytest.mark.asyncio
async def test_run_subgraph_replay_pattern():
    """Demo of the canonical hermetic test pattern using StubBackend."""
    responses = [end_turn("CLAIM: fast"), end_turn("VERDICT: HYPE")]
    backend = StubBackend(responses)
    app = GraphApp(backend=backend)

    extractor = await app.add_agent("Extractor")
    critic    = await app.add_agent("Critic", routing_table={"default": "__END__"})
    extractor.routing_table = {"default": critic.node_id}
    await app.store.upsert_node(extractor)

    sub = await app.add_subgraph("Pipeline", entry=extractor, exit=critic)
    ctx = await app.run_subgraph(sub, query="review")
    # Critic's verdict surfaces, extractor's claim does not.
    assert "HYPE" in ctx.outputs[sub.node_id]["text"]
    # StubBackend recorded both turns.
    assert len(backend.calls) == 2
