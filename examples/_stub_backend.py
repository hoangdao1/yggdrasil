"""Utility backends for runnable local examples.

These examples intentionally avoid network access and API keys so they can be
run directly after `pip install -e .`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yggdrasil.backends.llm import LLMBackend, LLMResponse, ToolCall


def end_turn(text: str) -> LLMResponse:
    return LLMResponse(text=text, tool_calls=[], stop_reason="end_turn")


def tool_use(tool_id: str, name: str, input_data: dict[str, Any]) -> LLMResponse:
    return LLMResponse(
        text="",
        tool_calls=[ToolCall(id=tool_id, name=name, input=input_data)],
        stop_reason="tool_use",
    )


class SequenceBackend(LLMBackend):
    """Return preset responses in order."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = list(responses)
        self._index = 0

    async def chat(
        self,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        response = self._responses[self._index % len(self._responses)]
        self._index += 1
        return response

    def extend_messages(
        self,
        messages: list[dict[str, Any]],
        response: LLMResponse,
        tool_results: list[Any],
    ) -> list[dict[str, Any]]:
        continuation = list(messages)
        if response.tool_calls:
            continuation.append({"role": "assistant", "content": str(response.tool_calls)})
        for tool_result in tool_results:
            continuation.append({"role": "tool", "content": tool_result.content})
        return continuation


@dataclass
class SmartReply:
    """Rule for name-based replies in tiny local examples."""

    contains: str
    text: str


class RuleBasedBackend(LLMBackend):
    """Return a reply based on the active system prompt."""

    def __init__(self, rules: list[SmartReply], default_text: str = "done") -> None:
        self.rules = rules
        self.default_text = default_text

    async def chat(
        self,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        for rule in self.rules:
            if rule.contains.lower() in system.lower():
                return end_turn(rule.text)
        return end_turn(self.default_text)

    def extend_messages(
        self,
        messages: list[dict[str, Any]],
        response: LLMResponse,
        tool_results: list[Any],
    ) -> list[dict[str, Any]]:
        return messages
