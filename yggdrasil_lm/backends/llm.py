"""LLM backend abstraction for yggdrasil.

Supports Anthropic and any OpenAI-compatible API (Ollama, mlx-lm, vLLM, etc.).

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
    # "end_turn" | "tool_use" | "max_tokens" | "unparsed_tool_call"
    stop_reason: str
    # Chain-of-thought a reasoning model emitted in a side channel (OpenAI
    # `reasoning_content`, Anthropic `thinking` blocks) rather than in `text`.
    # Captured so the executor can (a) salvage it when `text` is empty and (b)
    # tell "the model truncated mid-thought" apart from "the model is done".
    reasoning:  str = ""
    _raw: Any = field(default=None, repr=False)  # backend raw object for message continuation


# ---------------------------------------------------------------------------
# Unparsed tool calls (local models)
# ---------------------------------------------------------------------------
# A local model sometimes emits a tool call as literal TEXT instead of through the
# API's structured `tool_calls` field — the server's parser rejected its output (a
# format it doesn't recognise, or a hybrid of two conventions). The turn then looks
# like a plain final answer, so an agent loop ends mid-task believing the model was
# finished. Detecting it lets the executor ask for a properly-formed call instead of
# silently terminating.
#
# The markup lands in EITHER channel, so both must be inspected: a reasoning model
# often returns an empty/whitespace `content` and puts everything — including the
# tool call it meant to make — in `reasoning_content`. Checking only `content` misses
# exactly the case that motivated this (bonsai-27b emitting a Hermes/Llama hybrid
# into the reasoning channel, leaving `content` as "\n\n").
#
# Matching is deliberately conservative — an explicit opening tag from a known
# convention. Prose that merely mentions tools must not trip it.
import re as _re

_UNPARSED_TOOL_CALL_MARKERS = _re.compile(
    r"""(
          <\s*tool_call\s*>          # Hermes / Qwen / many GGUF chat templates
        | <\s*function\s*=           # Llama-3 / functionary: <function=name>
        | <\s*function_call\s*>
        | <\|\s*tool_call\s*\|>      # ChatML-style sentinel
        | <\s*invoke\s+name\s*=      # Anthropic-XML imitation
    )""",
    _re.IGNORECASE | _re.VERBOSE,
)


def looks_like_unparsed_tool_call(*channels: "str | None") -> bool:
    """Whether ANY response channel carries a tool-call block the API never parsed.

    Pass every channel the model can write into (`content` and `reasoning_content`) —
    the markup shows up in either, and a reasoning model routinely leaves `content`
    blank. Only meaningful for a turn that returned NO structured tool calls while
    tools were on offer — see the callers, which check both."""
    return any(
        _UNPARSED_TOOL_CALL_MARKERS.search(c) is not None
        for c in channels if c
    )


# --- Recovering the call, not just detecting it ------------------------------
# Re-prompting costs a turn and relies on the model complying (bonsai-27b often does
# not). When the markup is present we can usually just READ it: the name and arguments
# are right there. Two dialects cover what local models emit, plus the hybrid of both:
#
#   Hermes / Qwen:  <tool_call>{"name": "f", "arguments": {...}}</tool_call>
#   Llama-3:        <function=f><parameter=k>v</parameter></function>
#   hybrid:         <tool_call><function=f><parameter=k>\nv\n</parameter></function></tool_call>
_FUNC_NAME_RE = _re.compile(r"<\s*function\s*=\s*([A-Za-z0-9_.\-]+)\s*>", _re.IGNORECASE)
_PARAM_RE = _re.compile(
    r"<\s*parameter\s*=\s*([A-Za-z0-9_.\-]+)\s*>(.*?)(?:<\s*/\s*parameter\s*>|(?=<\s*parameter\s*=)|\Z)",
    _re.IGNORECASE | _re.DOTALL)
_HERMES_BLOCK_RE = _re.compile(r"<\s*tool_call\s*>(.*?)(?:<\s*/\s*tool_call\s*>|\Z)",
                               _re.IGNORECASE | _re.DOTALL)


def parse_text_tool_calls(*channels: "str | None") -> list[ToolCall]:
    """Recover structured ToolCalls from tool-call markup the API layer left as text.

    Returns [] when nothing parseable is present — the caller then falls back to
    re-prompting. Never raises: a half-written block is simply not a call."""
    calls: list[ToolCall] = []
    for chan in channels:
        if not chan:
            continue
        # Hermes-style JSON bodies first — a hybrid block also matches here, but its
        # body is not JSON, so it falls through to the Llama scan below.
        for body in _HERMES_BLOCK_RE.findall(chan):
            stripped = body.strip()
            if not stripped.startswith("{"):
                continue
            try:
                obj = json.loads(stripped)
            except Exception:  # noqa: BLE001 — not JSON → try the other dialect
                continue
            name = obj.get("name") or obj.get("function")
            args = obj.get("arguments")
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:  # noqa: BLE001
                    args = {}
            if name:
                calls.append(ToolCall(id=f"recovered_{len(calls)}", name=str(name),
                                      input=args if isinstance(args, dict) else {}))
        # Llama-3 / hybrid: <function=name> with <parameter=key>value</parameter>
        for m in _FUNC_NAME_RE.finditer(chan):
            name = m.group(1)
            # Scan only up to the next function block so params aren't cross-assigned.
            nxt = _FUNC_NAME_RE.search(chan, m.end())
            segment = chan[m.end():nxt.start() if nxt else len(chan)]
            args = {k: v.strip() for k, v in _PARAM_RE.findall(segment)}
            if any(c.name == name and c.input == args for c in calls):
                continue                     # already recovered from the JSON pass
            calls.append(ToolCall(id=f"recovered_{len(calls)}", name=name, input=args))
    return calls


# --- Detecting arguments the SERVER mangled ---------------------------------
# LM Studio sometimes half-parses an XML call into a real `tool_calls` entry whose
# ARGUMENT KEYS are markup fragments, e.g. observed verbatim:
#   {"actions\n</parameter": "<parameter=limit>\n5", "patterns\n</parameter": "..."}
# The call then "succeeds" with every real argument lost — here it ran an unfiltered
# query and the model silently got the wrong answer. A wrong answer is worse than a
# failed call, so treat this as an unparsed call and ask for a clean one.
_MANGLED_KEY_MARKERS = ("</parameter", "<parameter=", "</function", "<function=")


def has_mangled_tool_args(tool_calls: "list[ToolCall]") -> bool:
    """True when any call's argument KEYS carry tool-call markup — a server-side
    mis-parse, not arguments the model meant to send."""
    for call in tool_calls:
        if not isinstance(call.input, dict):
            continue
        for key in call.input:
            low = str(key).lower()
            if any(marker in low for marker in _MANGLED_KEY_MARKERS):
                return True
    return False


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
        reasoning = ""
        tool_calls: list[ToolCall] = []
        for block in response.content:
            if getattr(block, "type", None) == "thinking":
                # Extended-thinking block — chain-of-thought, not the answer.
                reasoning += getattr(block, "thinking", "") or ""
            elif hasattr(block, "text"):
                text = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))

        # Preserve a truncation signal ("max_tokens") distinctly from a genuine end
        # of turn, so the executor can give a mid-thought-truncated turn more room
        # instead of mistaking the empty result for completion.
        match response.stop_reason:
            case "tool_use":
                stop_reason = "tool_use"
            case "max_tokens":
                stop_reason = "max_tokens"
            case _:
                stop_reason = "end_turn"
        return LLMResponse(
            text=text, tool_calls=tool_calls, stop_reason=stop_reason,
            reasoning=reasoning, _raw=response,
        )

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

    Works with Ollama, mlx-lm, vLLM, Together AI, etc.

    Args:
        base_url: API base URL, e.g. "http://localhost:11434/v1" for Ollama.
                  Defaults to the official OpenAI API.
        api_key:  API key. Local servers typically accept any non-empty string.
        **kwargs: Forwarded to openai.AsyncOpenAI.
    """

    def __init__(
        self,
        base_url:    str | None   = None,
        api_key:     str          = "local",
        temperature: float | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package required: pip install 'yggdrasil[openai]'"
            )
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, **kwargs)
        # When set, sent on every completion. Local tool-calling models are far
        # more reliable at emitting well-formed tool calls at a low temperature;
        # left None it preserves the server/default sampling.
        self._temperature = temperature

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
        # Qwen3 requires the first non-system message to be a user message.
        # After tool calls extend_messages returns [assistant, tool, ...] with no leading
        # user turn, so inject one right after the system message when needed.
        system_count = sum(1 for m in oai_messages if m.get("role") == "system")
        first_non_system = oai_messages[system_count] if len(oai_messages) > system_count else None
        if first_non_system is None or first_non_system.get("role") != "user":
            oai_messages.insert(system_count, {"role": "user", "content": "Begin."})

        kwargs: dict[str, Any] = {
            "model":      model,
            "max_tokens": max_tokens,
            "messages":   oai_messages,
        }
        if self._temperature is not None:
            kwargs["temperature"] = self._temperature
        if tools:
            kwargs["tools"] = [_anthropic_to_openai_tool(t) for t in tools]

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg    = choice.message

        text = msg.content or ""
        # Reasoning models (Qwen3, DeepSeek-R1, GLM, …) put their chain-of-thought
        # in a `reasoning_content` side channel and often leave `content` empty on a
        # tool-calling turn. Capture it so the executor can salvage it / detect a
        # mid-thought truncation rather than reading an empty `content` as "done".
        reasoning = getattr(msg, "reasoning_content", None) or ""
        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    input=json.loads(tc.function.arguments),
                ))

        # `length` means the response was cut off at max_tokens — NOT that the model
        # finished. Surfaced as a distinct stop_reason so the executor can retry with
        # a larger budget instead of terminating the agent with an empty result (a
        # reasoning-heavy model can spend the whole budget in `reasoning_content`).
        match choice.finish_reason:
            case "tool_calls":
                stop_reason = "tool_use"
            case "length":
                stop_reason = "max_tokens"
            case _:
                stop_reason = "end_turn"
        # The server half-parsed an XML call into `tool_calls` whose ARGUMENT KEYS are
        # markup fragments — every real argument lost. Running that is worse than
        # failing it (the tool silently answers a different question), so drop the
        # mangled calls and treat the turn as an unparsed call.
        if tools and tool_calls and has_mangled_tool_args(tool_calls):
            recovered = parse_text_tool_calls(text, reasoning)
            tool_calls = recovered
            stop_reason = "tool_use" if recovered else "unparsed_tool_call"

        # The model wrote a tool call as text and the server didn't parse it into
        # `tool_calls`. That is NOT the end of the turn. Prefer RECOVERING it — the
        # name and arguments are right there, and re-prompting both costs a turn and
        # relies on a model that often cannot comply. Only flag for a re-prompt when
        # the markup is present but unparseable.
        if (
            stop_reason == "end_turn"
            and not tool_calls
            and tools
            and looks_like_unparsed_tool_call(text, reasoning)
        ):
            recovered = parse_text_tool_calls(text, reasoning)
            if recovered:
                tool_calls = recovered
                stop_reason = "tool_use"
            else:
                stop_reason = "unparsed_tool_call"
        return LLMResponse(
            text=text, tool_calls=tool_calls, stop_reason=stop_reason,
            reasoning=reasoning, _raw=msg,
        )

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
        match block.get("type"):
            case "text":
                result.append({"type": "text", "text": block.get("text", "")})
            case "image":
                source = block.get("source", {})
                match source.get("type"):
                    case "base64":
                        url = f"data:{source['media_type']};base64,{source['data']}"
                        result.append({"type": "image_url", "image_url": {"url": url}})
                    case "url":
                        url = source["url"]
                        result.append({"type": "image_url", "image_url": {"url": url}})
                    case _:
                        pass  # unsupported source type — skip
            case "image_url":
                # Already in OpenAI format — pass through
                result.append(block)
            case _:
                pass  # Other block types (document, tool_result, etc.) are not converted
    return result


def _convert_messages_for_openai(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of *messages* with list-typed content converted to OpenAI format."""
    return [
        {**msg, "content": _anthropic_to_openai_content(msg["content"])}
        if isinstance(msg.get("content"), list)
        else msg
        for msg in messages
    ]


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
