"""Tests for RecordingBackend ↔ StubBackend.from_recording round-trip."""

from __future__ import annotations

import json
from typing import Any

import pytest

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.backends.llm import LLMBackend, LLMResponse, ToolCall, ToolResult
from yggdrasil_lm.testing import (
    RecordingBackend,
    StubBackend,
    end_turn,
    tool_use,
)


class FakeRealBackend(LLMBackend):
    """Stands in for a real backend (AnthropicBackend, etc.) in tests."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = responses
        self._i = 0

    async def chat(self, model, system, messages, tools, max_tokens=8096):
        resp = self._responses[self._i]
        self._i += 1
        return resp

    def extend_messages(self, messages, response, tool_results):
        return messages


@pytest.mark.asyncio
async def test_recording_backend_writes_fixture(tmp_path):
    fixture = tmp_path / "rec.json"
    inner = FakeRealBackend([end_turn("hello")])
    backend = RecordingBackend(inner, fixture)

    resp = await backend.chat("m", "sys", [{"role": "user", "content": "hi"}], [])
    assert resp.text == "hello"

    data = json.loads(fixture.read_text())
    assert len(data) == 1
    assert data[0]["request"]["model"]    == "m"
    assert data[0]["request"]["system"]   == "sys"
    assert data[0]["response"]["text"]    == "hello"
    assert data[0]["response"]["stop_reason"] == "end_turn"


@pytest.mark.asyncio
async def test_recording_then_replay_round_trip(tmp_path):
    fixture = tmp_path / "rec.json"
    inner = FakeRealBackend([
        tool_use("call-1", "echo", {"text": "hi"}),
        end_turn("done"),
    ])
    rec = RecordingBackend(inner, fixture)
    await rec.chat("m", "sys", [], [])
    await rec.chat("m", "sys", [], [])

    replay = StubBackend.from_recording(fixture)
    r1 = await replay.chat("m", "sys", [], [])
    r2 = await replay.chat("m", "sys", [], [])

    assert r1.stop_reason     == "tool_use"
    assert r1.tool_calls[0].name == "echo"
    assert r1.tool_calls[0].input == {"text": "hi"}
    assert r2.text            == "done"
    assert r2.stop_reason     == "end_turn"


@pytest.mark.asyncio
async def test_recording_via_graphapp_then_replay(tmp_path):
    """End-to-end: record a GraphApp run, then replay against a fresh app."""
    fixture = tmp_path / "agent.json"
    inner = FakeRealBackend([end_turn("real output")])

    app1 = GraphApp(backend=RecordingBackend(inner, fixture))
    agent1 = await app1.add_agent("Bot")
    ctx1 = await app1.run(agent1, "query")
    assert ctx1.outputs[agent1.node_id]["text"] == "real output"

    app2 = GraphApp(backend=StubBackend.from_recording(fixture))
    agent2 = await app2.add_agent("Bot")
    ctx2 = await app2.run(agent2, "query")
    assert ctx2.outputs[agent2.node_id]["text"] == "real output"


def test_live_llm_marker_is_registered(pytestconfig):
    markers = pytestconfig.getini("markers")
    assert any("live_llm" in m for m in markers)
