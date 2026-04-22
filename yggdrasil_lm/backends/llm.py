"""LLM backend abstraction for yggdrasil.

Supports Anthropic and any OpenAI-compatible API (Ollama, mlx-lm, LM Studio, etc.).

Usage:
    # Anthropic (default)
    backend = AnthropicBackend()

    # Ollama
    backend = OpenAIBackend(base_url="http://localhost:11434/v1", api_key="ollama")

    # mlx-lm
    backend = OpenAIBackend(base_url="http://localhost:8080/v1", api_key="mlx")

    executor = GraphExecutor(store, backend=backend)
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Normalised types shared across backends
# ---------------------------------------------------------------------------

@dataclass
class ToolCall:
    """A single tool invocation requested by the LLM."""
    id:    str
    name:  str
    input: dict[str, Any]


@dataclass
class ToolResult:
    """The result of executing a tool call."""
    tool_call_id: str
    content:      str


@dataclass
class LLMResponse:
    """Backend-agnostic response from one LLM turn."""
    text:       str
    tool_calls: list[ToolCall]
    stop_reason: str           # "end_turn" | "tool_use"
    _raw: Any = field(default=None, repr=False)  # backend raw object for message continuation


# ---------------------------------------------------------------------------
# Abstract backend
# ---------------------------------------------------------------------------

class LLMBackend(ABC):
    """Interface every LLM backend must implement."""

    @abstractmethod
    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        """Send a chat request and return a normalised response."""

    @abstractmethod
    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        """Append the assistant turn + tool results to the message list.

        Each backend formats these differently; this keeps the executor format-agnostic.
        Returns a *new* list (does not mutate the input).
        """


# ---------------------------------------------------------------------------
# Anthropic backend
# ---------------------------------------------------------------------------

class AnthropicBackend(LLMBackend):
    """Calls the Anthropic Messages API directly."""

    def __init__(self, **kwargs: Any) -> None:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")
        self._client = anthropic.AsyncAnthropic(**kwargs)

    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model":      model,
            "max_tokens": max_tokens,
            "system":     system,
            "messages":   messages,
        }
        if tools:
            kwargs["tools"] = tools  # already in Anthropic format from to_tool_schema()

        response = await self._client.messages.create(**kwargs)

        text = ""
        tool_calls: list[ToolCall] = []
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))

        stop_reason = "tool_use" if response.stop_reason == "tool_use" else "end_turn"
        return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason, _raw=response)

    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        return messages + [
            {"role": "assistant", "content": response._raw.content},
            {
                "role": "user",
                "content": [
                    {
                        "type":        "tool_result",
                        "tool_use_id": tr.tool_call_id,
                        "content":     tr.content,
                    }
                    for tr in tool_results
                ],
            },
        ]


# ---------------------------------------------------------------------------
# OpenAI-compatible backend
# ---------------------------------------------------------------------------

class OpenAIBackend(LLMBackend):
    """Calls any OpenAI-compatible chat completions endpoint.

    Works with Ollama, mlx-lm, LM Studio, vLLM, Together AI, etc.

    Args:
        base_url: API base URL, e.g. "http://localhost:11434/v1" for Ollama.
                  Defaults to the official OpenAI API.
        api_key:  API key. Local servers typically accept any non-empty string.
        **kwargs: Forwarded to openai.AsyncOpenAI.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key:  str        = "local",
        **kwargs: Any,
    ) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package required: pip install 'yggdrasil[openai]'"
            )
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, **kwargs)

    async def chat(
        self,
        model:      str,
        system:     str,
        messages:   list[dict[str, Any]],
        tools:      list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        oai_messages: list[dict[str, Any]] = []
        if system:
            oai_messages.append({"role": "system", "content": system})
        oai_messages.extend(_convert_messages_for_openai(messages))

        kwargs: dict[str, Any] = {
            "model":      model,
            "max_tokens": max_tokens,
            "messages":   oai_messages,
        }
        if tools:
            kwargs["tools"] = [_anthropic_to_openai_tool(t) for t in tools]

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg    = choice.message

        text = msg.content or ""
        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    input=json.loads(tc.function.arguments),
                ))

        stop_reason = "tool_use" if choice.finish_reason == "tool_calls" else "end_turn"
        return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason, _raw=msg)

    def extend_messages(
        self,
        messages:     list[dict[str, Any]],
        response:     LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        raw_msg = response._raw
        assistant_msg: dict[str, Any] = {
            "role":    "assistant",
            "content": raw_msg.content,
        }
        if raw_msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id":   tc.id,
                    "type": "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in raw_msg.tool_calls
            ]

        tool_msgs = [
            {
                "role":         "tool",
                "tool_call_id": tr.tool_call_id,
                "content":      tr.content,
            }
            for tr in tool_results
        ]
        return messages + [assistant_msg] + tool_msgs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _anthropic_to_openai_tool(tool: dict[str, Any]) -> dict[str, Any]:
    """Convert a tool_schema() dict (Anthropic format) to OpenAI function tool format."""
    return {
        "type": "function",
        "function": {
            "name":        tool["name"],
            "description": tool.get("description", ""),
            "parameters":  tool.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


def _anthropic_to_openai_content(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Anthropic content blocks to OpenAI-compatible content blocks.

    Anthropic image blocks use ``{"type": "image", "source": {...}}``; OpenAI
    uses ``{"type": "image_url", "image_url": {"url": "..."}}``.  Text blocks
    pass through unchanged.  Unknown block types are dropped.
    """
    result: list[dict[str, Any]] = []
    for block in content:
        btype = block.get("type")
        if btype == "text":
            result.append({"type": "text", "text": block.get("text", "")})
        elif btype == "image":
            source = block.get("source", {})
            stype = source.get("type")
            if stype == "base64":
                url = f"data:{source['media_type']};base64,{source['data']}"
            elif stype == "url":
                url = source["url"]
            else:
                continue  # unsupported source type — skip
            result.append({"type": "image_url", "image_url": {"url": url}})
        elif btype == "image_url":
            # Already in OpenAI format — pass through
            result.append(block)
        # Other block types (document, tool_result, etc.) are not converted
    return result


def _convert_messages_for_openai(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of *messages* with list-typed content converted to OpenAI format."""
    result = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            result.append({**msg, "content": _anthropic_to_openai_content(content)})
        else:
            result.append(msg)
    return result


def default_backend() -> LLMBackend:
    """Return the default Anthropic backend when the local environment is configured."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No default LLM backend is configured. Set ANTHROPIC_API_KEY and install "
            "'yggdrasil[anthropic]', or pass backend=... explicitly."
        )
    try:
        return AnthropicBackend(api_key=api_key)
    except ImportError as exc:
        raise RuntimeError(
            "The default Anthropic backend is not installed. Install "
            "'yggdrasil[anthropic]' or pass backend=... explicitly."
        ) from exc
