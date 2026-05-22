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
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from yggdrasil_lm.backends.llm import LLMBackend, LLMResponse, ToolCall, ToolResult


__all__ = [
    "StubBackend",
    "end_turn",
    "tool_use",
]


def end_turn(text: str) -> LLMResponse:
    """Build an end-of-turn LLM response carrying plain text."""
    return LLMResponse(text=text, tool_calls=[], stop_reason="end_turn")


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

    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        self.calls.append((model, system, list(messages), list(tools)))
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
        continuation: list[dict[str, Any]] = []
        if response.tool_calls:
            continuation.append({"role": "assistant", "content": str(response.tool_calls)})
        for tr in tool_results:
            continuation.append({"role": "tool", "content": tr.content})
        return list(messages) + continuation
