"""Hermetic testing helpers for yggdrasil graphs.

This module provides a deterministic LLM backend and small response factories
so unit tests (and users) can exercise graphs — including sub-graphs — without
ever reaching a real model.

Typical usage:

```python
from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.testing import StubBackend, end_turn

backend = StubBackend([end_turn("CLAIM: fast"), end_turn("VERDICT: HYPE")])
app = GraphApp(backend=backend)
sub = await app.add_subgraph("Pipeline", entry=extractor, exit=critic)
ctx = await app.run_subgraph(sub, inputs={"product": "..."})
assert "HYPE" in ctx.outputs[sub.node_id]["text"]
```

For tests that need to validate against real LLM behaviour once and then
replay deterministically, see ``RecordingBackend`` below.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Sequence

from yggdrasil_lm.backends.llm import LLMBackend, LLMResponse, ToolCall, ToolResult


__all__ = [
    "StubBackend",
    "RecordingBackend",
    "end_turn",
    "tool_use",
    "max_tokens_truncated",
    "unparsed_tool_call",
]


def end_turn(text: str, reasoning: str = "") -> LLMResponse:
    """Build an end-of-turn LLM response carrying plain text."""
    return LLMResponse(text=text, tool_calls=[], stop_reason="end_turn", reasoning=reasoning)


def max_tokens_truncated(text: str = "", reasoning: str = "") -> LLMResponse:
    """Build a turn truncated at the output-token limit (finish_reason='length').

    Models the failure mode where a reasoning model spends its whole budget in the
    chain-of-thought (`reasoning`) and returns no answer/tool call — the executor
    should give it more room, not treat the empty result as done.
    """
    return LLMResponse(text=text, tool_calls=[], stop_reason="max_tokens", reasoning=reasoning)


def unparsed_tool_call(text: str) -> LLMResponse:
    """Build a turn whose tool call was emitted as TEXT and never parsed.

    Models the local-model failure mode where the server's tool-call parser doesn't
    recognise the model's format and leaves the markup in `content`: the turn carries
    no structured tool calls, so it looks final while having done no work. The executor
    should ask for a well-formed call rather than accept the markup as the result.
    """
    return LLMResponse(text=text, tool_calls=[], stop_reason="unparsed_tool_call")


def tool_use(tool_id: str, name: str, input: dict[str, Any]) -> LLMResponse:
    """Build a tool-call LLM response."""
    return LLMResponse(
        text="",
        tool_calls=[ToolCall(id=tool_id, name=name, input=input)],
        stop_reason="tool_use",
    )


class StubBackend(LLMBackend):
    """A deterministic LLM backend for tests.

    Returns the supplied responses in order, looping once the list is exhausted
    so a small response set can drive a longer run. Accepts a callable instead
    of a list to compute responses dynamically (e.g. inspect ``messages``).

    Args:
        responses: Either a sequence of ``LLMResponse`` objects to return in
            order, or a callable ``(model, system, messages, tools) -> LLMResponse``.

    Attributes:
        calls: List of ``(model, system, messages, tools)`` tuples — one per
            ``chat`` invocation. Useful for asserting the executor's behaviour.
    """

    def __init__(
        self,
        responses: Sequence[LLMResponse] | Callable[..., LLMResponse],
    ) -> None:
        self._responses = responses
        self._index = 0
        self.calls: list[tuple[str, str, list[dict[str, Any]], list[dict[str, Any]]]] = []
        # Output-token budget seen on each chat() call, in order — lets tests assert
        # the executor's max_tokens escalation on a truncated turn.
        self.max_tokens_seen: list[int] = []

    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        self.calls.append((model, system, list(messages), list(tools)))
        self.max_tokens_seen.append(max_tokens)
        if callable(self._responses):
            return self._responses(model, system, messages, tools)
        responses = list(self._responses)
        if not responses:
            raise RuntimeError("StubBackend has no responses configured")
        resp = responses[self._index % len(responses)]
        self._index += 1
        return resp

    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        continuation: list[dict[str, Any]] = (
            [{"role": "assistant", "content": str(response.tool_calls)}]
            if response.tool_calls else []
        )
        tool_entries = [{"role": "tool", "content": tr.content} for tr in tool_results]
        return list(messages) + continuation + tool_entries

    @classmethod
    def from_recording(cls, path: str | Path) -> "StubBackend":
        """Load a fixture written by ``RecordingBackend`` and replay it in order.

        The recorded ``LLMResponse`` objects are reconstructed (without the
        backend-specific ``_raw`` field, which is not serialised).
        """
        data = json.loads(Path(path).read_text())
        responses = [_response_from_dict(entry["response"]) for entry in data]
        return cls(responses)


# ---------------------------------------------------------------------------
# Recording backend
# ---------------------------------------------------------------------------

def _response_to_dict(resp: LLMResponse) -> dict[str, Any]:
    return {
        "text":        resp.text,
        "tool_calls":  [asdict(tc) for tc in resp.tool_calls],
        "stop_reason": resp.stop_reason,
        "reasoning":   resp.reasoning,
    }


def _response_from_dict(data: dict[str, Any]) -> LLMResponse:
    return LLMResponse(
        text=data["text"],
        tool_calls=[ToolCall(**tc) for tc in data.get("tool_calls", [])],
        stop_reason=data["stop_reason"],
        reasoning=data.get("reasoning", ""),
    )


class RecordingBackend(LLMBackend):
    """Wraps a real LLM backend and persists each ``chat`` call to a JSON file.

    First test run hits the wrapped backend (real API) and writes a fixture;
    subsequent runs can replay deterministically via
    ``StubBackend.from_recording(path)`` — no network, no cost.

    Args:
        inner: The real backend to delegate to (e.g. ``AnthropicBackend()``).
        path: Where to write the recording. The file is created (or
            overwritten) on the first ``chat`` call and appended to on each
            subsequent call within the same process.

    Example:
        >>> # First run — populates the fixture
        >>> backend = RecordingBackend(AnthropicBackend(), "tests/fixtures/critic.json")
        >>> app = GraphApp(backend=backend)
        >>> ctx = await app.run(agent, "review this product")
        >>>
        >>> # Subsequent runs — fully offline
        >>> backend = StubBackend.from_recording("tests/fixtures/critic.json")
    """

    def __init__(self, inner: LLMBackend, path: str | Path) -> None:
        self._inner = inner
        self._path  = Path(path)
        self._entries: list[dict[str, Any]] = []
        self._started = False

    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        response = await self._inner.chat(model, system, messages, tools, max_tokens)
        self._entries.append({
            "request": {
                "model":    model,
                "system":   system,
                "messages": messages,
                "tools":    tools,
            },
            "response": _response_to_dict(response),
        })
        self._flush()
        return response

    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        return self._inner.extend_messages(messages, response, tool_results)

    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._entries, indent=2, default=str))
