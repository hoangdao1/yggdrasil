#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xbf8563a5

# Compiled with Coconut version 3.2.0

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

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
_coconut_header_info = ('3.2.0', '311', False)
_coconut_cached__coconut__ = _coconut_sys.modules.get('__coconut__')
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.abspath(__file__))
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



import json  #24 (line in Coconut source)
from dataclasses import asdict  #25 (line in Coconut source)
from pathlib import Path  #26 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #27 (line in Coconut source)
    from typing import Any  #27 (line in Coconut source)
else:  #27 (line in Coconut source)
    try:  #27 (line in Coconut source)
        Any = _coconut.typing.Any  #27 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #27 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #27 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #27 (line in Coconut source)
    from typing import Callable  #27 (line in Coconut source)
else:  #27 (line in Coconut source)
    try:  #27 (line in Coconut source)
        Callable = _coconut.typing.Callable  #27 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #27 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #27 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #27 (line in Coconut source)
    from typing import Sequence  #27 (line in Coconut source)
else:  #27 (line in Coconut source)
    try:  #27 (line in Coconut source)
        Sequence = _coconut.typing.Sequence  #27 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #27 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #27 (line in Coconut source)

from yggdrasil_lm.backends.llm import LLMBackend  #29 (line in Coconut source)
from yggdrasil_lm.backends.llm import LLMResponse  #29 (line in Coconut source)
from yggdrasil_lm.backends.llm import ToolCall  #29 (line in Coconut source)
from yggdrasil_lm.backends.llm import ToolResult  #29 (line in Coconut source)


__all__ = ["StubBackend", "RecordingBackend", "end_turn", "tool_use"]  #32 (line in Coconut source)


@_coconut_tco  #40 (line in Coconut source)
def end_turn(text: str) -> LLMResponse:  #40 (line in Coconut source)
    """Build an end-of-turn LLM response carrying plain text."""  #41 (line in Coconut source)
    return _coconut_tail_call(LLMResponse, text=text, tool_calls=[], stop_reason="end_turn")  #42 (line in Coconut source)



@_coconut_tco  #45 (line in Coconut source)
def tool_use(tool_id: str, name: str, input: dict[str, Any]) -> LLMResponse:  #45 (line in Coconut source)
    """Build a tool-call LLM response."""  #46 (line in Coconut source)
    return _coconut_tail_call(LLMResponse, text="", tool_calls=[ToolCall(id=tool_id, name=name, input=input),], stop_reason="tool_use")  #47 (line in Coconut source)



class StubBackend(LLMBackend):  #54 (line in Coconut source)
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
    """  #68 (line in Coconut source)

    def __init__(self, responses: Sequence[LLMResponse] | Callable[..., LLMResponse],) -> None:  #70 (line in Coconut source)
        self._responses = responses  #74 (line in Coconut source)
        self._index = 0  #75 (line in Coconut source)
        self.calls: list[tuple[str, str, list[dict[str, Any]], list[dict[str, Any]]]] = []  #76 (line in Coconut source)


    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #78 (line in Coconut source)
        self.calls.append((model, system, list(messages), list(tools)))  #86 (line in Coconut source)
        if callable(self._responses):  #87 (line in Coconut source)
            return self._responses(model, system, messages, tools)  #88 (line in Coconut source)
        responses = list(self._responses)  #89 (line in Coconut source)
        if not responses:  #90 (line in Coconut source)
            raise RuntimeError("StubBackend has no responses configured")  #91 (line in Coconut source)
        resp = responses[self._index % len(responses)]  #92 (line in Coconut source)
        self._index += 1  #93 (line in Coconut source)
        return resp  #94 (line in Coconut source)


    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #96 (line in Coconut source)
        continuation: list[dict[str, Any]] = ([{"role": "assistant", "content": str(response.tool_calls)},] if response.tool_calls else [])  #102 (line in Coconut source)
        tool_entries = [{"role": "tool", "content": tr.content} for tr in tool_results]  #106 (line in Coconut source)
        return list(messages) + continuation + tool_entries  #107 (line in Coconut source)


    @classmethod  #109 (line in Coconut source)
    @_coconut_tco  #110 (line in Coconut source)
    def from_recording(cls, path: str | Path) -> "StubBackend":  #110 (line in Coconut source)
        """Load a fixture written by ``RecordingBackend`` and replay it in order.

        The recorded ``LLMResponse`` objects are reconstructed (without the
        backend-specific ``_raw`` field, which is not serialised).
        """  #115 (line in Coconut source)
        responses = (((lambda data: [_response_from_dict(entry["response"]) for entry in data]))((json.loads)(Path(path).read_text())))  #116 (line in Coconut source)
        return _coconut_tail_call(cls, responses)  #121 (line in Coconut source)


# ---------------------------------------------------------------------------
# Recording backend
# ---------------------------------------------------------------------------


def _response_to_dict(resp: LLMResponse) -> dict[str, Any]:  #128 (line in Coconut source)
    return {"text": resp.text, "tool_calls": [asdict(tc) for tc in resp.tool_calls], "stop_reason": resp.stop_reason}  #129 (line in Coconut source)



@_coconut_tco  #136 (line in Coconut source)
def _response_from_dict(data: dict[str, Any]) -> LLMResponse:  #136 (line in Coconut source)
    return _coconut_tail_call(LLMResponse, text=data["text"], tool_calls=[ToolCall(**tc) for tc in data.get("tool_calls", [])], stop_reason=data["stop_reason"])  #137 (line in Coconut source)



class RecordingBackend(LLMBackend):  #144 (line in Coconut source)
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
    """  #165 (line in Coconut source)

    def __init__(self, inner: LLMBackend, path: str | Path) -> None:  #167 (line in Coconut source)
        self._inner = inner  #168 (line in Coconut source)
        self._path = Path(path)  #169 (line in Coconut source)
        self._entries: list[dict[str, Any]] = []  #170 (line in Coconut source)
        self._started = False  #171 (line in Coconut source)


    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #173 (line in Coconut source)
        response = await self._inner.chat(model, system, messages, tools, max_tokens)  #181 (line in Coconut source)
        self._entries.append({"request": {"model": model, "system": system, "messages": messages, "tools": tools}, "response": _response_to_dict(response)})  #182 (line in Coconut source)
        self._flush()  #191 (line in Coconut source)
        return response  #192 (line in Coconut source)


    @_coconut_tco  #194 (line in Coconut source)
    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #194 (line in Coconut source)
        return _coconut_tail_call(self._inner.extend_messages, messages, response, tool_results)  #200 (line in Coconut source)


    def _flush(self) -> None:  #202 (line in Coconut source)
        self._path.parent.mkdir(parents=True, exist_ok=True)  #203 (line in Coconut source)
        self._path.write_text(json.dumps(self._entries, indent=2, default=str))  #204 (line in Coconut source)
