"""Reasoning-model turn handling: max_tokens truncation escalation + reasoning salvage.

Covers the executor no longer mistaking a token-truncated, empty turn for a completed
one (it retries with a larger budget, bounded), and the OpenAI backend surfacing
`reasoning_content` + a distinct `max_tokens` stop reason.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.backends.llm import OpenAIBackend
from yggdrasil_lm.testing import StubBackend, end_turn, max_tokens_truncated


# ---------------------------------------------------------------------------
# OpenAI backend: finish_reason mapping + reasoning capture
# ---------------------------------------------------------------------------

def _fake_openai_response(*, content, finish_reason, reasoning=None, tool_calls=None):
    msg = SimpleNamespace(content=content, reasoning_content=reasoning, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg, finish_reason=finish_reason)])


def _backend_returning(resp):
    backend = OpenAIBackend(base_url="http://localhost:0/v1", api_key="test")

    async def _create(**kwargs):
        _backend_returning.last_kwargs = kwargs
        return resp

    backend._client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_create)))
    return backend


@pytest.mark.asyncio
async def test_openai_length_becomes_max_tokens_and_captures_reasoning():
    """A `length` finish with only reasoning_content → stop_reason 'max_tokens', text ''."""
    resp = _fake_openai_response(content=None, finish_reason="length", reasoning="thinking " * 100)
    backend = _backend_returning(resp)

    out = await backend.chat(model="m", system="s", messages=[{"role": "user", "content": "go"}], tools=[])

    assert out.stop_reason == "max_tokens"
    assert out.text == ""
    assert out.reasoning.startswith("thinking ")
    assert out.tool_calls == []


@pytest.mark.asyncio
async def test_openai_tool_calls_and_stop_map_correctly():
    tc = SimpleNamespace(id="c1", function=SimpleNamespace(name="do", arguments="{}"))
    tool_resp = _fake_openai_response(content="", finish_reason="tool_calls", tool_calls=[tc])
    stop_resp = _fake_openai_response(content="done", finish_reason="stop")

    b1 = _backend_returning(tool_resp)
    out1 = await b1.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert out1.stop_reason == "tool_use"
    assert [t.name for t in out1.tool_calls] == ["do"]

    b2 = _backend_returning(stop_resp)
    out2 = await b2.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert out2.stop_reason == "end_turn"
    assert out2.text == "done"


@pytest.mark.asyncio
async def test_openai_forwards_max_tokens():
    resp = _fake_openai_response(content="ok", finish_reason="stop")
    backend = _backend_returning(resp)
    await backend.chat(model="m", system="s", messages=[{"role": "user", "content": "x"}], tools=[], max_tokens=12345)
    assert _backend_returning.last_kwargs["max_tokens"] == 12345


# ---------------------------------------------------------------------------
# Executor: escalation on empty truncation, then completion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_truncated_empty_turn_escalates_then_completes():
    """A max_tokens turn with no output must NOT end the agent: retry with more room."""
    backend = StubBackend([
        max_tokens_truncated(reasoning="reasoning ate the whole budget"),
        end_turn("DONE"),
    ])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # Completed with the real answer, not an empty result.
    assert ctx.outputs[sub.node_id]["text"] == "DONE"
    # Two turns; the second ran with an escalated (doubled) token budget.
    assert len(backend.max_tokens_seen) == 2
    assert backend.max_tokens_seen[1] == backend.max_tokens_seen[0] * 2


@pytest.mark.asyncio
async def test_persistent_truncation_gives_up_bounded_and_salvages_reasoning():
    """If every turn truncates, escalation is bounded and reasoning is salvaged as text."""
    backend = StubBackend(lambda *a: max_tokens_truncated(reasoning="all in the head"))
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    # Bounded: initial call + 2 escalations = 3 chat calls, then terminate (not max_iterations=10).
    assert len(backend.max_tokens_seen) == 3
    assert backend.max_tokens_seen == [8096, 16192, 32000]
    # Never surfaces an empty result — the chain-of-thought is salvaged.
    assert ctx.outputs[sub.node_id]["text"] == "all in the head"


@pytest.mark.asyncio
async def test_end_turn_empty_text_salvages_reasoning():
    """A natural end_turn with empty content still returns the reasoning, never ''."""
    backend = StubBackend([end_turn("", reasoning="the visible answer lived in reasoning")])
    app = GraphApp(backend=backend)
    agent = await app.add_agent("Worker")
    sub = await app.add_subgraph("S", entry=agent)

    ctx = await app.run_subgraph(sub, query="go")

    assert ctx.outputs[sub.node_id]["text"] == "the visible answer lived in reasoning"
