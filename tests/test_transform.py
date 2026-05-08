"""Tests for TransformNode — split, join, sequential, and topological fan-in."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from yggdrasil_lm.backends.llm import LLMBackend, LLMResponse
from yggdrasil_lm.core.edges import Edge
from yggdrasil_lm.core.executor import GraphExecutor
from yggdrasil_lm.core.nodes import AgentNode, TransformNode
from yggdrasil_lm.core.store import NetworkXGraphStore


# ---------------------------------------------------------------------------
# Minimal stub backend
# ---------------------------------------------------------------------------

class _StubBackend(LLMBackend):
    def __init__(self, text: str = "ok") -> None:
        self._text = text

    async def chat(self, *, model: str, system: str, messages: list, tools: list, **kw: Any) -> LLMResponse:
        return LLMResponse(text=self._text, tool_calls=[], stop_reason="end_turn")

    def extend_messages(self, messages, response, tool_results):
        return messages + [{"role": "assistant", "content": response.text}]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sync_double(data: dict[str, Any]) -> dict[str, Any]:
    value = data.get("value", 0)
    return {"value": value * 2}


async def _async_upper(data: dict[str, Any]) -> dict[str, Any]:
    text = data.get("text", "")
    return {"text": text.upper()}


def _join_fn(data: dict[str, Any]) -> dict[str, Any]:
    parts = [str(v.get("text", v)) if isinstance(v, dict) else str(v) for v in data.values()]
    return {"merged": " | ".join(sorted(parts))}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transform_sync_callable():
    store = NetworkXGraphStore()
    t = TransformNode(name="double", callable_ref="double", is_async=False)
    await store.upsert_node(t)

    executor = GraphExecutor(store, backend=_StubBackend())
    executor.register_tool("double", _sync_double)

    ctx = await executor.run(t.node_id, "ignored", strategy="sequential", state={"value": 5})
    assert ctx.outputs[t.node_id] == {"value": 10}


@pytest.mark.asyncio
async def test_transform_async_callable():
    store = NetworkXGraphStore()
    t = TransformNode(name="upper", callable_ref="upper", is_async=True)
    await store.upsert_node(t)

    executor = GraphExecutor(store, backend=_StubBackend())
    executor.register_tool("upper", _async_upper)

    ctx = await executor.run(t.node_id, "ignored", strategy="sequential", state={"text": "hello world"})
    assert ctx.outputs[t.node_id] == {"text": "HELLO WORLD"}


@pytest.mark.asyncio
async def test_transform_output_key_written_to_state():
    store = NetworkXGraphStore()
    t = TransformNode(name="double", callable_ref="double", is_async=False, output_key="result")
    await store.upsert_node(t)

    executor = GraphExecutor(store, backend=_StubBackend())
    executor.register_tool("double", _sync_double)

    ctx = await executor.run(t.node_id, "ignored", strategy="sequential", state={"value": 3})
    assert "result" in ctx.state.data


@pytest.mark.asyncio
async def test_transform_unregistered_raises():
    store = NetworkXGraphStore()
    t = TransformNode(name="missing", callable_ref="not.registered")
    await store.upsert_node(t)

    executor = GraphExecutor(store, backend=_StubBackend())
    with pytest.raises(RuntimeError, match="not.registered"):
        await executor.run(t.node_id, "x", strategy="sequential")


@pytest.mark.asyncio
async def test_transform_sequential_pipeline():
    """Transform chained after an agent via routing_table in sequential mode."""
    store = NetworkXGraphStore()
    transform = TransformNode(name="T", callable_ref="upper", is_async=True)
    await store.upsert_node(transform)
    agent = AgentNode(name="A", routing_table={"default": transform.node_id})
    await store.upsert_node(agent)

    backend = _StubBackend(text="hello from agent")
    executor = GraphExecutor(store, backend=backend)
    executor.register_tool("upper", _async_upper)

    ctx = await executor.run(agent.node_id, "go", strategy="sequential")
    # The transform receives the agent's output dict {"text": "hello from agent"}
    # and uppercases its "text" field
    result = ctx.outputs[transform.node_id]
    assert result == {"text": "HELLO FROM AGENT"}


@pytest.mark.asyncio
async def test_transform_fan_in_topological():
    """Split → 2 parallel workers → join transform collects both outputs."""
    store = NetworkXGraphStore()

    worker_a = AgentNode(name="WA", routing_table={"default": "__END__"})
    worker_b = AgentNode(name="WB", routing_table={"default": "__END__"})
    joiner = TransformNode(
        name="Joiner",
        callable_ref="join",
        input_keys=[worker_a.node_id, worker_b.node_id],
        output_key="joined",
        is_async=False,
    )
    entry = AgentNode(name="Entry", routing_table={"default": "__END__"})

    for node in [entry, worker_a, worker_b, joiner]:
        await store.upsert_node(node)

    await store.upsert_edge(Edge.delegates_to(entry.node_id, worker_a.node_id))
    await store.upsert_edge(Edge.delegates_to(entry.node_id, worker_b.node_id))
    await store.upsert_edge(Edge.delegates_to(worker_a.node_id, joiner.node_id))
    await store.upsert_edge(Edge.delegates_to(worker_b.node_id, joiner.node_id))

    call_count = {"n": 0}

    class _CountingBackend(LLMBackend):
        async def chat(self, *, model, system, messages, tools, **kw):
            call_count["n"] += 1
            name = "wa" if call_count["n"] % 2 == 1 else "wb"
            return LLMResponse(text=f"result from {name}", tool_calls=[], stop_reason="end_turn")

        def extend_messages(self, messages, response, tool_results):
            return messages + [{"role": "assistant", "content": response.text}]

    executor = GraphExecutor(store, backend=_CountingBackend())
    executor.register_tool("join", _join_fn)

    ctx = await executor.run(entry.node_id, "go", strategy="topological")

    # Both worker outputs must be present in the joined result
    joined = ctx.state.data.get("joined", {})
    assert "merged" in joined
    assert "result from" in joined["merged"]

    # Joiner output is also in ctx.outputs
    assert joiner.node_id in ctx.outputs


@pytest.mark.asyncio
async def test_transform_emits_tool_result_trace_event():
    store = NetworkXGraphStore()
    t = TransformNode(name="upper", callable_ref="upper", is_async=True)
    await store.upsert_node(t)

    executor = GraphExecutor(store, backend=_StubBackend())
    executor.register_tool("upper", _async_upper)

    ctx = await executor.run(t.node_id, "hello", strategy="sequential")
    event_types = [e.event_type for e in ctx.trace]
    assert "tool_result" in event_types
