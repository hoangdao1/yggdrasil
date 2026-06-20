#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xba2d3504

# Compiled with Coconut version 3.2.0

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

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
_coconut_header_info = ('3.2.0', '311', False)
_coconut_cached__coconut__ = _coconut_sys.modules.get('__coconut__')
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.dirname(_coconut_os.path.abspath(__file__)))
_coconut_pop_path = False
if _coconut_cached__coconut__ is None or getattr(_coconut_cached__coconut__, "_coconut_header_info", None) != _coconut_header_info and _coconut_os.path.dirname(_coconut_cached__coconut__.__file__ or "") != _coconut_file_dir:  # type: ignore
    if _coconut_cached__coconut__ is not None:
        _coconut_sys.modules['_coconut_cached__coconut__'] = _coconut_cached__coconut__
        del _coconut_sys.modules['__coconut__']
    _coconut_sys.path.insert(0, _coconut_file_dir)
    _coconut_pop_path = True
    _coconut_module_name = _coconut_os.path.splitext(_coconut_os.path.basename(_coconut_file_dir))[0]
    if _coconut_module_name and _coconut_module_name[0].isalpha() and all(c.isalpha() or c.isdigit() for c in _coconut_module_name) and "__init__.py" in _coconut_os.listdir(_coconut_file_dir):  # type: ignore
        _coconut_full_module_name = str(_coconut_module_name + ".__coconut__")  # type: ignore
        import __coconut__ as _coconut__coconut__
        _coconut__coconut__.__name__ = _coconut_full_module_name
        for _coconut_v in vars(_coconut__coconut__).values():  # type: ignore
            if getattr(_coconut_v, "__module__", None) == '__coconut__':  # type: ignore
                try:
                    _coconut_v.__module__ = _coconut_full_module_name
                except AttributeError:
                    _coconut_v_type = type(_coconut_v)  # type: ignore
                    if getattr(_coconut_v_type, "__module__", None) == '__coconut__':  # type: ignore
                        _coconut_v_type.__module__ = _coconut_full_module_name
        _coconut_sys.modules[_coconut_full_module_name] = _coconut__coconut__
from __coconut__ import *
from __coconut__ import _coconut_tail_call, _coconut_tco, _namedtuple_of, _coconut, _coconut_Expected, _coconut_MatchError, _coconut_SupportsAdd, _coconut_SupportsMinus, _coconut_SupportsMul, _coconut_SupportsPow, _coconut_SupportsTruediv, _coconut_SupportsFloordiv, _coconut_SupportsMod, _coconut_SupportsAnd, _coconut_SupportsXor, _coconut_SupportsOr, _coconut_SupportsLshift, _coconut_SupportsRshift, _coconut_SupportsMatmul, _coconut_SupportsInv, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_complex_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_arr_concat_op, _coconut_mk_anon_namedtuple, _coconut_matmul, _coconut_py_str, _coconut_flatten, _coconut_multiset, _coconut_back_none_pipe, _coconut_back_none_star_pipe, _coconut_back_none_dubstar_pipe, _coconut_forward_none_compose, _coconut_back_none_compose, _coconut_forward_none_star_compose, _coconut_back_none_star_compose, _coconut_forward_none_dubstar_compose, _coconut_back_none_dubstar_compose, _coconut_call_or_coefficient, _coconut_in, _coconut_not_in, _coconut_attritemgetter, _coconut_if_op, _coconut_CoconutWarning
if _coconut_pop_path:
    _coconut_sys.path.pop(0)
try:
    __file__ = _coconut_os.path.abspath(__file__) if __file__ else __file__
except NameError:
    pass
else:
    if __file__ and '__coconut_cache__' in __file__:
        _coconut_file_comps = []
        while __file__:
            __file__, _coconut_file_comp = _coconut_os.path.split(__file__)
            if not _coconut_file_comp:
                _coconut_file_comps.append(__file__)
                break
            if _coconut_file_comp != '__coconut_cache__':
                _coconut_file_comps.append(_coconut_file_comp)
        __file__ = _coconut_os.path.join(*reversed(_coconut_file_comps))

# Compiled Coconut: -----------------------------------------------------------



import json  #18 (line in Coconut source)
import os  #19 (line in Coconut source)
from abc import ABC  #20 (line in Coconut source)
from abc import abstractmethod  #20 (line in Coconut source)
from dataclasses import dataclass  #21 (line in Coconut source)
from dataclasses import field  #21 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #22 (line in Coconut source)
    from typing import Any  #22 (line in Coconut source)
else:  #22 (line in Coconut source)
    try:  #22 (line in Coconut source)
        Any = _coconut.typing.Any  #22 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #22 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #22 (line in Coconut source)


# ---------------------------------------------------------------------------
# Normalised types shared across backends
# ---------------------------------------------------------------------------

@dataclass  #29 (line in Coconut source)
class ToolCall():  #30 (line in Coconut source)
    """A single tool invocation requested by the LLM."""  #31 (line in Coconut source)
    id: str  #32 (line in Coconut source)
    name: str  #33 (line in Coconut source)
    input: dict[str, Any]  #34 (line in Coconut source)


@dataclass  #37 (line in Coconut source)
class ToolResult():  #38 (line in Coconut source)
    """The result of executing a tool call."""  #39 (line in Coconut source)
    tool_call_id: str  #40 (line in Coconut source)
    content: str  #41 (line in Coconut source)


@dataclass  #44 (line in Coconut source)
class LLMResponse():  #45 (line in Coconut source)
    """Backend-agnostic response from one LLM turn."""  #46 (line in Coconut source)
    text: str  #47 (line in Coconut source)
    tool_calls: list[ToolCall]  #48 (line in Coconut source)
    stop_reason: str  # "end_turn" | "tool_use"  #49 (line in Coconut source)
    _raw: Any = field(default=None, repr=False)  # backend raw object for message continuation  #50 (line in Coconut source)


# ---------------------------------------------------------------------------
# Abstract backend
# ---------------------------------------------------------------------------

class LLMBackend(ABC):  #57 (line in Coconut source)
    """Interface every LLM backend must implement."""  #58 (line in Coconut source)

    @abstractmethod  #60 (line in Coconut source)
    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #61 (line in Coconut source)
        """Send a chat request and return a normalised response."""  #69 (line in Coconut source)


    @abstractmethod  #71 (line in Coconut source)
    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #72 (line in Coconut source)
        """Append the assistant turn + tool results to the message list.

        Each backend formats these differently; this keeps the executor format-agnostic.
        Returns a *new* list (does not mutate the input).
        """  #82 (line in Coconut source)


# ---------------------------------------------------------------------------
# Anthropic backend
# ---------------------------------------------------------------------------


class AnthropicBackend(LLMBackend):  #89 (line in Coconut source)
    """Calls the Anthropic Messages API directly."""  #90 (line in Coconut source)

    def __init__(self, **kwargs: Any) -> None:  #92 (line in Coconut source)
        try:  #93 (line in Coconut source)
            import anthropic  #94 (line in Coconut source)
        except ImportError:  #95 (line in Coconut source)
            raise ImportError("anthropic package required: pip install anthropic")  #96 (line in Coconut source)
        self._client = anthropic.AsyncAnthropic(**kwargs)  #97 (line in Coconut source)


    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #99 (line in Coconut source)
        kwargs: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "system": system, "messages": messages}  #107 (line in Coconut source)
        if tools:  #113 (line in Coconut source)
            kwargs["tools"] = tools  # already in Anthropic format from to_tool_schema()  #114 (line in Coconut source)

        response = await self._client.messages.create(**kwargs)  #116 (line in Coconut source)

        text = ""  #118 (line in Coconut source)
        tool_calls: list[ToolCall] = []  #119 (line in Coconut source)
        for block in response.content:  #120 (line in Coconut source)
            if hasattr(block, "text"):  #121 (line in Coconut source)
                text = block.text  #122 (line in Coconut source)
            elif block.type == "tool_use":  #123 (line in Coconut source)
                tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))  #124 (line in Coconut source)

        stop_reason = "tool_use" if response.stop_reason == "tool_use" else "end_turn"  #126 (line in Coconut source)
        return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason, _raw=response)  #127 (line in Coconut source)


    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #129 (line in Coconut source)
        return messages + [{"role": "assistant", "content": response._raw.content}, {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tr.tool_call_id, "content": tr.content} for tr in tool_results]}]  #135 (line in Coconut source)


# ---------------------------------------------------------------------------
# OpenAI-compatible backend
# ---------------------------------------------------------------------------


class OpenAIBackend(LLMBackend):  #155 (line in Coconut source)
    """Calls any OpenAI-compatible chat completions endpoint.

    Works with Ollama, mlx-lm, vLLM, Together AI, etc.

    Args:
        base_url: API base URL, e.g. "http://localhost:11434/v1" for Ollama.
                  Defaults to the official OpenAI API.
        api_key:  API key. Local servers typically accept any non-empty string.
        **kwargs: Forwarded to openai.AsyncOpenAI.
    """  #165 (line in Coconut source)

    def __init__(self, base_url: str | None=None, api_key: str="local", **kwargs: Any,) -> None:  #167 (line in Coconut source)
        try:  #173 (line in Coconut source)
            from openai import AsyncOpenAI  #174 (line in Coconut source)
        except ImportError:  #175 (line in Coconut source)
            raise ImportError("openai package required: pip install 'yggdrasil[openai]'")  #176 (line in Coconut source)
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, **kwargs)  #179 (line in Coconut source)


    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #181 (line in Coconut source)
        oai_messages: list[dict[str, Any]] = []  #189 (line in Coconut source)
        if system:  #190 (line in Coconut source)
            oai_messages.append({"role": "system", "content": system})  #191 (line in Coconut source)
        oai_messages.extend(_convert_messages_for_openai(messages))  #192 (line in Coconut source)

        kwargs: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "messages": oai_messages}  #194 (line in Coconut source)
        if tools:  #199 (line in Coconut source)
            kwargs["tools"] = (list)((map)(lambda t: _anthropic_to_openai_tool(t), tools))  #200 (line in Coconut source)

        response = await self._client.chat.completions.create(**kwargs)  #202 (line in Coconut source)
        choice = response.choices[0]  #203 (line in Coconut source)
        msg = choice.message  #204 (line in Coconut source)

        text = msg.content or ""  #206 (line in Coconut source)
        tool_calls: list[ToolCall] = []  #207 (line in Coconut source)
        if msg.tool_calls:  #208 (line in Coconut source)
            for tc in msg.tool_calls:  #209 (line in Coconut source)
                tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, input=json.loads(tc.function.arguments)))  #210 (line in Coconut source)

        stop_reason = "tool_use" if choice.finish_reason == "tool_calls" else "end_turn"  #216 (line in Coconut source)
        return LLMResponse(text=text, tool_calls=tool_calls, stop_reason=stop_reason, _raw=msg)  #217 (line in Coconut source)


    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #219 (line in Coconut source)
        raw_msg = response._raw  #225 (line in Coconut source)
        assistant_msg: dict[str, Any] = {"role": "assistant", "content": raw_msg.content}  #226 (line in Coconut source)
        if raw_msg.tool_calls:  #230 (line in Coconut source)
            assistant_msg["tool_calls"] = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in raw_msg.tool_calls]  #231 (line in Coconut source)

        tool_msgs = [{"role": "tool", "tool_call_id": tr.tool_call_id, "content": tr.content} for tr in tool_results]  #243 (line in Coconut source)
        return messages + [assistant_msg,] + tool_msgs  #251 (line in Coconut source)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _anthropic_to_openai_tool(tool: dict[str, Any]) -> dict[str, Any]:  #258 (line in Coconut source)
    """Convert a tool_schema() dict (Anthropic format) to OpenAI function tool format."""  #259 (line in Coconut source)
    return {"type": "function", "function": {"name": tool["name"], "description": tool.get("description", ""), "parameters": tool.get("input_schema", {"type": "object", "properties": {}})}}  #260 (line in Coconut source)



def _anthropic_to_openai_content(content: list[dict[str, Any]]) -> list[dict[str, Any]]:  #270 (line in Coconut source)
    """Convert Anthropic content blocks to OpenAI-compatible content blocks.

    Anthropic image blocks use ``{"type": "image", "source": {...}}``; OpenAI
    uses ``{"type": "image_url", "image_url": {"url": "..."}}``.  Text blocks
    pass through unchanged.  Unknown block types are dropped.
    """  #276 (line in Coconut source)
    result: list[dict[str, Any]] = []  #277 (line in Coconut source)
    for block in content:  #278 (line in Coconut source)
        _coconut_case_match_to_1 = block.get("type")  #279 (line in Coconut source)
        _coconut_case_match_check_1 = False  #279 (line in Coconut source)
        if _coconut_case_match_to_1 == "text":  #279 (line in Coconut source)
            _coconut_case_match_check_1 = True  #279 (line in Coconut source)
        if _coconut_case_match_check_1:  #279 (line in Coconut source)
            result.append({"type": "text", "text": block.get("text", "")})  #281 (line in Coconut source)
        if not _coconut_case_match_check_1:  #282 (line in Coconut source)
            if _coconut_case_match_to_1 == "image":  #282 (line in Coconut source)
                _coconut_case_match_check_1 = True  #282 (line in Coconut source)
            if _coconut_case_match_check_1:  #282 (line in Coconut source)
                source = block.get("source", {})  #283 (line in Coconut source)
                _coconut_case_match_to_0 = source.get("type")  #284 (line in Coconut source)
                _coconut_case_match_check_0 = False  #284 (line in Coconut source)
                if _coconut_case_match_to_0 == "base64":  #284 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #284 (line in Coconut source)
                if _coconut_case_match_check_0:  #284 (line in Coconut source)
                    url = "data:{_coconut_format_0};base64,{_coconut_format_1}".format(_coconut_format_0=(source['media_type']), _coconut_format_1=(source['data']))  #286 (line in Coconut source)
                    result.append({"type": "image_url", "image_url": {"url": url}})  #287 (line in Coconut source)
                if not _coconut_case_match_check_0:  #288 (line in Coconut source)
                    if _coconut_case_match_to_0 == "url":  #288 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #288 (line in Coconut source)
                    if _coconut_case_match_check_0:  #288 (line in Coconut source)
                        url = source["url"]  #289 (line in Coconut source)
                        result.append({"type": "image_url", "image_url": {"url": url}})  #290 (line in Coconut source)
                if not _coconut_case_match_check_0:  #291 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #291 (line in Coconut source)
                    if _coconut_case_match_check_0:  #291 (line in Coconut source)
                        pass  # unsupported source type — skip  #292 (line in Coconut source)
        if not _coconut_case_match_check_1:  #293 (line in Coconut source)
            if _coconut_case_match_to_1 == "image_url":  #293 (line in Coconut source)
                _coconut_case_match_check_1 = True  #293 (line in Coconut source)
            if _coconut_case_match_check_1:  #293 (line in Coconut source)
                result.append(block)  #295 (line in Coconut source)
        if not _coconut_case_match_check_1:  #296 (line in Coconut source)
            _coconut_case_match_check_1 = True  #296 (line in Coconut source)
            if _coconut_case_match_check_1:  #296 (line in Coconut source)
                pass  # Other block types (document, tool_result, etc.) are not converted  #297 (line in Coconut source)
    return result  #298 (line in Coconut source)



def _convert_messages_for_openai(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:  #301 (line in Coconut source)
    """Return a copy of *messages* with list-typed content converted to OpenAI format."""  #302 (line in Coconut source)
    return [{**msg, "content": _anthropic_to_openai_content(msg["content"])} if isinstance(msg.get("content"), list) else msg for msg in messages]  #303 (line in Coconut source)



def default_backend() -> LLMBackend:  #311 (line in Coconut source)
    """Return the default Anthropic backend when the local environment is configured."""  #312 (line in Coconut source)
    api_key = os.getenv("ANTHROPIC_API_KEY")  #313 (line in Coconut source)
    if not api_key:  #314 (line in Coconut source)
        raise RuntimeError("No default LLM backend is configured. Set ANTHROPIC_API_KEY and install 'yggdrasil[anthropic]', or pass backend=... explicitly.")  #315 (line in Coconut source)
    try:  #319 (line in Coconut source)
        return AnthropicBackend(api_key=api_key)  #320 (line in Coconut source)
    except ImportError as exc:  #321 (line in Coconut source)
        raise RuntimeError("The default Anthropic backend is not installed. Install 'yggdrasil[anthropic]' or pass backend=... explicitly.") from exc  #322 (line in Coconut source)
