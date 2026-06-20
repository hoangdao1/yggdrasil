#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x23481010

# Compiled with Coconut version 3.2.0

"""Claude Code sub-agent backend for GraphExecutor.

Replaces the direct Anthropic Messages API call with a Claude Code Agent SDK
invocation. Each AgentNode runs as a full autonomous Claude Code sub-agent,
with its graph-registered ToolNodes bridged in as an in-process MCP server.

Usage:
    executor = ClaudeCodeExecutor(
        store,
        allowed_tools=["Bash", "Read", "Glob", "Grep", "WebSearch"],
        permission_mode="acceptEdits",
        cwd="/path/to/project",
    )
    default_registry.attach(executor)
    ctx = await executor.run(agent.node_id, "analyse the codebase")

Requirements:
    pip install 'yggdrasil[claude-code]'
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



import asyncio  #21 (line in Coconut source)
import json  #22 (line in Coconut source)
import os  #23 (line in Coconut source)
import shutil  #24 (line in Coconut source)
import time  #25 (line in Coconut source)
import uuid  #26 (line in Coconut source)
from dataclasses import dataclass  #27 (line in Coconut source)
from dataclasses import field  #27 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Any  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Any = _coconut.typing.Any  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Callable  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Callable = _coconut.typing.Callable  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)

from yggdrasil_lm.backends.llm import LLMBackend  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import LLMResponse  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import ToolResult  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import default_backend  #30 (line in Coconut source)
from yggdrasil_lm.core.executor import AgentComposer  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import ExecutionContext  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import GraphExecutor  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import RoutingDecision  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import _ROUTER_SYSTEM  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import _ROUTER_TEMPLATE  #31 (line in Coconut source)
from yggdrasil_lm.core.executor import _summarise  #31 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #40 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #40 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #41 (line in Coconut source)

# ---------------------------------------------------------------------------
# Optional SDK imports — kept at module level so tests can patch them.
# All are None when claude-agent-sdk is not installed; the executor raises a
# clear ImportError at call time rather than at import time.
# ---------------------------------------------------------------------------
try:  #48 (line in Coconut source)
    from claude_agent_sdk import AssistantMessage  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import ClaudeAgentOptions  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import ClaudeSDKClient  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import ResultMessage  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import TextBlock  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import create_sdk_mcp_server  # type: ignore[import]  #49 (line in Coconut source)
    from claude_agent_sdk import tool as cc_tool  # type: ignore[import]  #49 (line in Coconut source)
    try:  #58 (line in Coconut source)
        from claude_agent_sdk import ToolUseBlock  # type: ignore[import]  #59 (line in Coconut source)
    except ImportError:  #60 (line in Coconut source)
        ToolUseBlock = None  # type: ignore[assignment]  #61 (line in Coconut source)
    _SDK_AVAILABLE = True  #62 (line in Coconut source)
except ImportError:  #63 (line in Coconut source)
    AssistantMessage = None  # type: ignore[assignment,misc]  #64 (line in Coconut source)
    ClaudeAgentOptions = None  # type: ignore[assignment,misc]  #65 (line in Coconut source)
    ClaudeSDKClient = None  # type: ignore[assignment,misc]  #66 (line in Coconut source)
    ResultMessage = None  # type: ignore[assignment,misc]  #67 (line in Coconut source)
    TextBlock = None  # type: ignore[assignment,misc]  #68 (line in Coconut source)
    ToolUseBlock = None  # type: ignore[assignment]  #69 (line in Coconut source)
    create_sdk_mcp_server = None  # type: ignore[assignment]  #70 (line in Coconut source)
    cc_tool = None  # type: ignore[assignment]  #71 (line in Coconut source)
    _SDK_AVAILABLE = False  #72 (line in Coconut source)


# ---------------------------------------------------------------------------
# Internal result type for SDK runs
# ---------------------------------------------------------------------------

@dataclass  #79 (line in Coconut source)
class _AgentRunResult():  #80 (line in Coconut source)
    """Raw data returned from a single Claude Code SDK invocation."""  #81 (line in Coconut source)
    text: str  #82 (line in Coconut source)
    tool_calls: int  #83 (line in Coconut source)
    cost_usd: float | None  #84 (line in Coconut source)
    tool_events: list[dict[str, Any]] = field(default_factory=list)  #85 (line in Coconut source)


class _ClaudeCodeBootstrapBackend(LLMBackend):  #88 (line in Coconut source)
    """Placeholder backend used only to satisfy GraphExecutor initialization."""  #89 (line in Coconut source)

    async def chat(self, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]], max_tokens: int=8096,) -> LLMResponse:  #91 (line in Coconut source)
        raise RuntimeError("ClaudeCodeExecutor does not use LLMBackend.chat().")  #99 (line in Coconut source)


    def extend_messages(self, messages: list[dict[str, Any]], response: LLMResponse, tool_results: list[ToolResult],) -> list[dict[str, Any]]:  #101 (line in Coconut source)
        raise RuntimeError("ClaudeCodeExecutor does not use LLMBackend.extend_messages().")  #107 (line in Coconut source)



class ClaudeCodeAgentError(RuntimeError):  #110 (line in Coconut source)
    """Structured error raised when the Claude Code SDK returns a failed result."""  #111 (line in Coconut source)

    def __init__(self, subtype: str, result: str) -> None:  #113 (line in Coconut source)
        self.subtype = subtype  #114 (line in Coconut source)
        self.result = result  #115 (line in Coconut source)
        super().__init__("Claude Code agent error ({_coconut_format_0}): {_coconut_format_1}".format(_coconut_format_0=(subtype), _coconut_format_1=(result)))  #116 (line in Coconut source)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@_coconut_tco  #123 (line in Coconut source)
def _json_type_to_python(type_str: str) -> type:  #123 (line in Coconut source)
    return _coconut_tail_call({"string": str, "integer": int, "number": float, "boolean": bool, "array": list, "object": dict}.get, type_str, str)  #124 (line in Coconut source)



def _validate_tool_args(args: dict[str, Any], schema: dict[str, Any], tool_name: str) -> None:  #134 (line in Coconut source)
    if not schema:  #135 (line in Coconut source)
        return  #136 (line in Coconut source)
    if schema.get("type") == "object" and not isinstance(args, dict):  #137 (line in Coconut source)
        raise ValueError("{_coconut_format_0} input must be an object".format(_coconut_format_0=(tool_name)))  #138 (line in Coconut source)
    for key in schema.get("required", []):  #139 (line in Coconut source)
        if key not in args:  #140 (line in Coconut source)
            raise ValueError("{_coconut_format_0} input missing required field {_coconut_format_1!r}".format(_coconut_format_0=(tool_name), _coconut_format_1=(key)))  #141 (line in Coconut source)
    for key, subschema in schema.get("properties", {}).items():  #142 (line in Coconut source)
        if key not in args:  #143 (line in Coconut source)
            continue  #144 (line in Coconut source)
        value = args[key]  #145 (line in Coconut source)
        schema_type = subschema.get("type")  #146 (line in Coconut source)
        if "enum" in subschema and value not in subschema["enum"]:  #147 (line in Coconut source)
            raise ValueError("{_coconut_format_0}.{_coconut_format_1} must be one of {_coconut_format_2!r}".format(_coconut_format_0=(tool_name), _coconut_format_1=(key), _coconut_format_2=(subschema['enum'])))  #148 (line in Coconut source)
        expected_type = _json_type_to_python(schema_type or "")  #149 (line in Coconut source)
        if schema_type == "number":  #150 (line in Coconut source)
            ok = isinstance(value, (int, float)) and not isinstance(value, bool)  #151 (line in Coconut source)
        elif schema_type == "integer":  #152 (line in Coconut source)
            ok = isinstance(value, int) and not isinstance(value, bool)  #153 (line in Coconut source)
        elif schema_type:  #154 (line in Coconut source)
            ok = isinstance(value, expected_type)  #155 (line in Coconut source)
        else:  #156 (line in Coconut source)
            ok = True  #157 (line in Coconut source)
        if not ok:  #158 (line in Coconut source)
            raise ValueError("{_coconut_format_0}.{_coconut_format_1} must be a {_coconut_format_2}".format(_coconut_format_0=(tool_name), _coconut_format_1=(key), _coconut_format_2=(schema_type)))  #159 (line in Coconut source)



@_coconut_tco  #162 (line in Coconut source)
def _format_tool_content(result: Any) -> str:  #162 (line in Coconut source)
    _coconut_case_match_to_0 = result  #163 (line in Coconut source)
    _coconut_case_match_check_0 = False  #163 (line in Coconut source)
    _coconut_match_temp_0 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #163 (line in Coconut source)
    _coconut_case_match_check_0 = True  #163 (line in Coconut source)
    if _coconut_case_match_check_0:  #163 (line in Coconut source)
        _coconut_case_match_check_0 = False  #163 (line in Coconut source)
        if not _coconut_case_match_check_0:  #163 (line in Coconut source)
            if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #163 (line in Coconut source)
                _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #163 (line in Coconut source)
                if _coconut_match_temp_1:  #163 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #163 (line in Coconut source)

        if not _coconut_case_match_check_0:  #163 (line in Coconut source)
            if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #163 (line in Coconut source)
                _coconut_case_match_check_0 = True  #163 (line in Coconut source)
            if _coconut_case_match_check_0:  #163 (line in Coconut source)
                _coconut_case_match_check_0 = False  #163 (line in Coconut source)
                if not _coconut_case_match_check_0:  #163 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #163 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #163 (line in Coconut source)

                if not _coconut_case_match_check_0:  #163 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #163 (line in Coconut source)
                        _coconut_match_temp_2 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #163 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #163 (line in Coconut source)
                            raise _coconut.TypeError("str.__match_args__ must be a tuple")  #163 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_2) < 0:  #163 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #163 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #163 (line in Coconut source)




    if _coconut_case_match_check_0:  #163 (line in Coconut source)
        return result  #165 (line in Coconut source)
    if not _coconut_case_match_check_0:  #166 (line in Coconut source)
        _coconut_case_match_check_0 = True  #166 (line in Coconut source)
        if _coconut_case_match_check_0:  #166 (line in Coconut source)
            try:  #167 (line in Coconut source)
                return json.dumps(result, default=str, sort_keys=True)  #168 (line in Coconut source)
            except TypeError:  #169 (line in Coconut source)
                return _coconut_tail_call(str, result)  #170 (line in Coconut source)



def _extract_tool_event(block: Any) -> dict[str, Any]:  #173 (line in Coconut source)
    return {"id": getattr(block, "id", None), "name": getattr(block, "name", "claude_code_builtin"), "input": getattr(block, "input", None)}  #174 (line in Coconut source)



@_coconut_tco  #181 (line in Coconut source)
def _build_mcp_server(composed: Any, tool_fns: dict, on_tool_result: Callable[[ToolNode, dict[str, Any], Any, bool, int], None] | None=None,) -> Any | None:  #181 (line in Coconut source)
    """Wrap each ComposedAgent ToolNode as an in-process Agent SDK MCP tool.

    Returns a server object (from create_sdk_mcp_server) to pass to
    ClaudeAgentOptions.mcp_servers, or None when no tools can be bridged.

    Requires: pip install 'yggdrasil[claude-code]'
    """  #192 (line in Coconut source)
    if not _SDK_AVAILABLE:  #193 (line in Coconut source)
        raise ImportError("claude-agent-sdk is required for tool bridging: pip install 'yggdrasil[claude-code]'")  #194 (line in Coconut source)

    sdk_tools = []  #199 (line in Coconut source)

    for tn in composed.tools:  #201 (line in Coconut source)
        fn = tool_fns.get(tn.callable_ref)  #202 (line in Coconut source)
        if fn is None:  #203 (line in Coconut source)
            continue  #204 (line in Coconut source)

        props = tn.input_schema.get("properties", {})  #206 (line in Coconut source)
        param_types = {k: _json_type_to_python(v.get("type", "string")) for k, v in props.items()}  #207 (line in Coconut source)
# Fallback for tools that declare no properties
        if not param_types:  #212 (line in Coconut source)
            param_types = {"input": str}  #213 (line in Coconut source)

        is_async = tn.is_async  #215 (line in Coconut source)

        def _make_handler(tool_node: ToolNode, tool_fn: Any, async_fn: bool) -> Any:  #217 (line in Coconut source)
            async def handler(args: dict) -> dict:  #218 (line in Coconut source)
                t0 = time.monotonic()  #219 (line in Coconut source)
                success = False  #220 (line in Coconut source)
                result: Any = None  #221 (line in Coconut source)
                try:  #222 (line in Coconut source)
                    _validate_tool_args(args, tool_node.input_schema, tool_node.name)  #223 (line in Coconut source)
                    result = (await tool_fn(args) if async_fn else await asyncio.to_thread(tool_fn, args))  #224 (line in Coconut source)
                    success = True  #229 (line in Coconut source)
                    return {"content": [{"type": "text", "text": _format_tool_content(result)},]}  #230 (line in Coconut source)
                except Exception as exc:  #231 (line in Coconut source)
                    result = {"error": str(exc), "tool": tool_node.name}  #232 (line in Coconut source)
                    return {"isError": True, "content": [{"type": "text", "text": _format_tool_content(result)},]}  #233 (line in Coconut source)
                finally:  #237 (line in Coconut source)
                    if on_tool_result:  #238 (line in Coconut source)
                        duration_ms = int((time.monotonic() - t0) * 1000)  #239 (line in Coconut source)
                        on_tool_result(tool_node, args, result, success, duration_ms)  #240 (line in Coconut source)

            return handler  #241 (line in Coconut source)


        handler = _make_handler(tn, fn, is_async)  #243 (line in Coconut source)
        decorated = cc_tool(tn.name, tn.description, param_types)(handler)  #244 (line in Coconut source)
        sdk_tools.append(decorated)  #245 (line in Coconut source)

    if not sdk_tools:  #247 (line in Coconut source)
        return None  #248 (line in Coconut source)

    return _coconut_tail_call(create_sdk_mcp_server, "yggdrasil-tools", tools=sdk_tools)  #250 (line in Coconut source)


# ---------------------------------------------------------------------------
# ClaudeCodeExecutor
# ---------------------------------------------------------------------------


class ClaudeCodeExecutor(GraphExecutor):  #257 (line in Coconut source)
    """GraphExecutor that runs each AgentNode as a Claude Code sub-agent.

    All graph traversal, routing, context composition, and ToolNode bridging
    work identically to GraphExecutor. Only _execute_agent is replaced: instead
    of driving the Anthropic Messages API directly it spawns a Claude Code
    sub-agent via the Agent SDK.

    Graph-registered ToolNodes are bridged to the sub-agent as an in-process
    MCP server (requires ClaudeSDKClient). When no ToolNodes are present the
    lighter query() path is used instead.

    Args:
        store:             Graph store.
        composer:          AgentComposer instance; auto-created if None.
        embedder:          Optional Embedder for query-time context re-ranking.
        allowed_tools:     Claude Code built-in tools available to sub-agents
                           (default: Read, Glob, Grep, Bash, WebSearch).
        extra_mcp_servers: Additional MCP servers merged into every sub-agent
                           invocation (stdio/http format or SDK server objects).
        permission_mode:   How to handle permission prompts
                           ("default" | "acceptEdits" | "bypassPermissions").
        max_budget_usd:    Optional per-invocation USD budget cap.
        cwd:               Working directory for file operations.
        cli_path:          Path to the Claude Code CLI binary. When set, overrides
                           the bundled CLI inside claude_agent_sdk. Use this to
                           point at your system-installed ``claude`` so sub-agents
                           authenticate via your Claude Code account rather than
                           ANTHROPIC_API_KEY.
    """  #286 (line in Coconut source)

    def __init__(self, store: GraphStore, composer: AgentComposer | None=None, embedder: Any=None, allowed_tools: list[str] | None=None, extra_mcp_servers: dict | None=None, permission_mode: str="default", max_budget_usd: float | None=None, cwd: str | None=None, cli_path: str | None=None,) -> None:  #288 (line in Coconut source)
        super().__init__(store, composer=composer, backend=_ClaudeCodeBootstrapBackend(), embedder=embedder, router_model="claude-haiku-4-5-20251001")  #300 (line in Coconut source)
        self._backend = None  # not used — Agent SDK owns the LLM loop  #307 (line in Coconut source)

        self._allowed_tools = ["Read", "Glob", "Grep", "Bash", "WebSearch"] if allowed_tools is None else allowed_tools  #309 (line in Coconut source)
        self._extra_mcp = extra_mcp_servers or {}  #310 (line in Coconut source)
        self._permission_mode = permission_mode  #311 (line in Coconut source)
        self._max_budget_usd = max_budget_usd  #312 (line in Coconut source)
        self._cwd = cwd  #313 (line in Coconut source)
        self._cli_path = cli_path  #314 (line in Coconut source)

# ------------------------------------------------------------------
# Override: LLM routing (lazily init backend — not used for execution)
# ------------------------------------------------------------------


    async def route(self, query: str, candidates: list[AgentNode] | None=None,) -> RoutingDecision:  #320 (line in Coconut source)
        """Route using the system Claude Code CLI so no API key is needed.

        Calls the CLI with ``--print`` (non-agentic, single response) using the
        same routing prompt as the parent class, but authenticated via the
        Claude Code account instead of ANTHROPIC_API_KEY.
        """  #330 (line in Coconut source)
        from yggdrasil_lm.core.store import NodeType  #331 (line in Coconut source)

        if candidates is None:  #333 (line in Coconut source)
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)  #334 (line in Coconut source)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]  #335 (line in Coconut source)

        if not candidates:  #337 (line in Coconut source)
            raise ValueError("No valid AgentNode candidates found in the store.")  #338 (line in Coconut source)

        if len(candidates) == 1:  #340 (line in Coconut source)
            return RoutingDecision(agent_id=candidates[0].node_id, reason="Only one agent available.", confidence=1.0)  #341 (line in Coconut source)

        cli = self._cli_path or shutil.which("claude")  #347 (line in Coconut source)
        if not cli:  #348 (line in Coconut source)
# Fallback to Anthropic backend if no CLI found
            if self._backend is None:  #350 (line in Coconut source)
                self._backend = default_backend()  #351 (line in Coconut source)
            return await super().route(query, candidates)  #352 (line in Coconut source)

        agent_list = "\n".join(("- {_coconut_format_0}: {_coconut_format_1}".format(_coconut_format_0=(n.node_id), _coconut_format_1=(n.description)) for n in candidates))  #354 (line in Coconut source)
        prompt = "{_coconut_format_0}\n\n{_coconut_format_1}".format(_coconut_format_0=(_ROUTER_SYSTEM), _coconut_format_1=(_ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)))  #355 (line in Coconut source)

        proc_env = {**os.environ, "ANTHROPIC_API_KEY": ""}  #357 (line in Coconut source)
        try:  #358 (line in Coconut source)
            proc = await asyncio.create_subprocess_exec(cli, "--print", "--output-format", "text", prompt, env=proc_env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)  #359 (line in Coconut source)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)  #365 (line in Coconut source)
            if proc.returncode:  #366 (line in Coconut source)
                err = stderr.decode(errors="replace").strip()  #367 (line in Coconut source)
                raise RuntimeError("Claude Code router failed ({_coconut_format_0}): {_coconut_format_1}".format(_coconut_format_0=(proc.returncode), _coconut_format_1=(err)))  #368 (line in Coconut source)
            text = stdout.decode().strip()  #369 (line in Coconut source)
# Strip markdown code fences if present
            if text.startswith("```"):  #371 (line in Coconut source)
                text = "\n".join((line for line in text.splitlines() if not line.startswith("```"))).strip()  #372 (line in Coconut source)
            data = json.loads(text)  #376 (line in Coconut source)
            agent_id = str(data["agent"])  #377 (line in Coconut source)
            candidate_ids = {agent.node_id for agent in candidates}  #378 (line in Coconut source)
            if agent_id not in candidate_ids:  #379 (line in Coconut source)
                raise ValueError("Router returned unknown agent id {_coconut_format_0!r}".format(_coconut_format_0=(agent_id)))  #380 (line in Coconut source)
            return RoutingDecision(agent_id=agent_id, reason=str(data.get("reason", "")), confidence=float(data.get("confidence", 0.5)))  #381 (line in Coconut source)
        except Exception as exc:  #386 (line in Coconut source)
            return RoutingDecision(agent_id=candidates[0].node_id, reason="Fallback: CLI routing failed ({_coconut_format_0}).".format(_coconut_format_0=(type(exc).__name__)), confidence=0.5)  #387 (line in Coconut source)

# ------------------------------------------------------------------
# Override: run each AgentNode as a Claude Code sub-agent
# ------------------------------------------------------------------


    async def _execute_agent(self, node: AgentNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #397 (line in Coconut source)
        if not _SDK_AVAILABLE:  #403 (line in Coconut source)
            raise ImportError("claude-agent-sdk is required: pip install 'yggdrasil[claude-code]'")  #404 (line in Coconut source)

        import time as _time  #408 (line in Coconut source)
        t0 = _time.monotonic()  #409 (line in Coconut source)

        composed = await self.composer.compose(node, query=ctx.query)  #411 (line in Coconut source)
        system = composed.build_system_prompt()  #412 (line in Coconut source)

# Emit agent_start so downstream metrics extraction picks up agent counts.
        agent_event_id = str(uuid.uuid4())  #415 (line in Coconut source)
        self._emit(ctx, "agent_start", node.node_id, node.name or "", payload={"query": ctx.query, "model": node.model, "tools": [t.name for t in composed.tools], "context": [c.name for c in composed.context if c.name]}, event_id=agent_event_id, parent_event_id=parent_event_id)  #416 (line in Coconut source)
        if composed.context:  #427 (line in Coconut source)
            self._emit(ctx, "context_inject", node.node_id, node.name or "", payload={"context_names": [c.name for c in composed.context if c.name], "count": len(composed.context)}, parent_event_id=agent_event_id)  #428 (line in Coconut source)

# Build MCP server map — start with any user-supplied servers
        mcp_servers: dict = dict(self._extra_mcp)  #438 (line in Coconut source)

        bridged_tool_names: set[str] = set()  #440 (line in Coconut source)

        def record_mcp_tool_result(tool_node: ToolNode, args: dict[str, Any], result: Any, success: bool, duration_ms: int,) -> None:  #442 (line in Coconut source)
            bridged_tool_names.add(tool_node.name)  #449 (line in Coconut source)
            call_event = self._emit(ctx, "tool_call", tool_node.node_id, tool_node.name, payload={"tool_name": tool_node.name, "callable_ref": tool_node.callable_ref, "input": args, "source": "claude_code_mcp"}, parent_event_id=agent_event_id)  #450 (line in Coconut source)
            if success:  #460 (line in Coconut source)
                ctx.outputs[tool_node.node_id] = result  #461 (line in Coconut source)
            self._emit(ctx, "tool_result", tool_node.node_id, tool_node.name, payload={"tool_name": tool_node.name, "output_summary": (_summarise)((_format_tool_content)(result)), "success": success, "source": "claude_code_mcp"}, parent_event_id=call_event.event_id, duration_ms=duration_ms)  #462 (line in Coconut source)

# Bridge graph-registered ToolNodes as an in-process MCP server

        tool_mcp = _build_mcp_server(composed, self._tool_fns, record_mcp_tool_result)  #475 (line in Coconut source)
        if tool_mcp:  #476 (line in Coconut source)
            mcp_servers["yggdrasil-tools"] = tool_mcp  #477 (line in Coconut source)

        options = ClaudeAgentOptions(system_prompt=system, allowed_tools=self._allowed_tools, mcp_servers=mcp_servers or None, max_turns=node.max_iterations, model=node.model, permission_mode=self._permission_mode, cwd=self._cwd, env={"ANTHROPIC_API_KEY": ""}, **({"max_budget_usd": self._max_budget_usd} if self._max_budget_usd else {}), **({"cli_path": self._cli_path} if self._cli_path else {}))  #479 (line in Coconut source)

        try:  #492 (line in Coconut source)
            run_result: _AgentRunResult = await (self._run_with_sdk_client(ctx.query, options) if tool_mcp else self._run_with_query(ctx.query, options))  #493 (line in Coconut source)
        except ClaudeCodeAgentError as exc:  #498 (line in Coconut source)
            self._emit(ctx, "error", node.node_id, node.name or "", payload={"source": "claude_code", "subtype": exc.subtype, "message": exc.result}, parent_event_id=agent_event_id)  #499 (line in Coconut source)
            raise  #508 (line in Coconut source)
        except Exception as exc:  #509 (line in Coconut source)
            self._emit(ctx, "error", node.node_id, node.name or "", payload={"source": "claude_code", "subtype": type(exc).__name__, "message": str(exc)}, parent_event_id=agent_event_id)  #510 (line in Coconut source)
            raise  #519 (line in Coconut source)

# Built-in Claude Code tools do not return structured results through the
# same in-process bridge, but ToolUseBlock still gives useful call data.
        for tool_event in run_result.tool_events:  #523 (line in Coconut source)
            tool_name = str(tool_event.get("name") or "claude_code_builtin")  #524 (line in Coconut source)
            if tool_name in bridged_tool_names:  #525 (line in Coconut source)
                continue  #526 (line in Coconut source)
            call_event = self._emit(ctx, "tool_call", node.node_id, node.name or "", payload={"tool_name": tool_name, "callable_ref": "", "input": tool_event.get("input"), "tool_call_id": tool_event.get("id"), "source": "claude_code_builtin"}, parent_event_id=agent_event_id)  #527 (line in Coconut source)
            self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": tool_name, "output_summary": "Result handled inside Claude Code.", "success": True, "source": "claude_code_builtin"}, parent_event_id=call_event.event_id)  #538 (line in Coconut source)

        intent = await self._infer_intent(run_result.text, node)  #549 (line in Coconut source)
        duration_ms = int((_time.monotonic() - t0) * 1000)  #550 (line in Coconut source)
        self._emit(ctx, "agent_end", node.node_id, node.name or "", payload={"text_summary": run_result.text[:120], "intent": intent, "iterations": 1, "cost_usd": run_result.cost_usd}, parent_event_id=agent_event_id, duration_ms=duration_ms)  #551 (line in Coconut source)

        return {"text": run_result.text, "intent": intent}  #563 (line in Coconut source)

# ------------------------------------------------------------------
# Two execution paths
# ------------------------------------------------------------------


    async def _run_with_query(self, prompt: str, options: Any) -> _AgentRunResult:  #569 (line in Coconut source)
        """Use query() — sufficient when no in-process MCP server is needed."""  #570 (line in Coconut source)
        from claude_agent_sdk import query as cc_query  # type: ignore[import]  #571 (line in Coconut source)

        result_text = ""  #573 (line in Coconut source)
        tool_call_count = 0  #574 (line in Coconut source)
        cost_usd: float | None = None  #575 (line in Coconut source)
        tool_events: list[dict[str, Any]] = []  #576 (line in Coconut source)

        async for message in cc_query(prompt=prompt, options=options):  #578 (line in Coconut source)
            _coconut_case_match_to_1 = message  #579 (line in Coconut source)
            _coconut_case_match_check_1 = False  #579 (line in Coconut source)
            _coconut_match_temp_3 = _coconut.getattr(AssistantMessage, "_coconut_is_data", False) or _coconut.isinstance(AssistantMessage, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AssistantMessage)  # type: ignore  #579 (line in Coconut source)
            _coconut_case_match_check_1 = True  #579 (line in Coconut source)
            if _coconut_case_match_check_1:  #579 (line in Coconut source)
                _coconut_case_match_check_1 = False  #579 (line in Coconut source)
                if not _coconut_case_match_check_1:  #579 (line in Coconut source)
                    if (_coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_1, AssistantMessage)):  #579 (line in Coconut source)
                        _coconut_match_temp_4 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #579 (line in Coconut source)
                        if _coconut_match_temp_4:  #579 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #579 (line in Coconut source)

                if not _coconut_case_match_check_1:  #579 (line in Coconut source)
                    if (not _coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_1, AssistantMessage)):  #579 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #579 (line in Coconut source)
                    if _coconut_case_match_check_1:  #579 (line in Coconut source)
                        _coconut_case_match_check_1 = False  #579 (line in Coconut source)
                        if not _coconut_case_match_check_1:  #579 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #579 (line in Coconut source)
                                _coconut_case_match_check_1 = True  #579 (line in Coconut source)

                        if not _coconut_case_match_check_1:  #579 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #579 (line in Coconut source)
                                _coconut_match_temp_5 = _coconut.getattr(AssistantMessage, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #579 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_5, _coconut.tuple):  #579 (line in Coconut source)
                                    raise _coconut.TypeError("AssistantMessage.__match_args__ must be a tuple")  #579 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_5) < 0:  #579 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AssistantMessage' only supports %s)" % (_coconut.len(_coconut_match_temp_5),))  #579 (line in Coconut source)
                                _coconut_case_match_check_1 = True  #579 (line in Coconut source)




            if _coconut_case_match_check_1:  #579 (line in Coconut source)
                for block in message.content:  #581 (line in Coconut source)
                    if ToolUseBlock and isinstance(block, ToolUseBlock):  #582 (line in Coconut source)
                        tool_call_count += 1  #583 (line in Coconut source)
                        tool_events.append(_extract_tool_event(block))  #584 (line in Coconut source)
            if not _coconut_case_match_check_1:  #585 (line in Coconut source)
                _coconut_match_temp_6 = _coconut.getattr(ResultMessage, "_coconut_is_data", False) or _coconut.isinstance(ResultMessage, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ResultMessage)  # type: ignore  #585 (line in Coconut source)
                _coconut_case_match_check_1 = True  #585 (line in Coconut source)
                if _coconut_case_match_check_1:  #585 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #585 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #585 (line in Coconut source)
                        if (_coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_1, ResultMessage)):  #585 (line in Coconut source)
                            _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #585 (line in Coconut source)
                            if _coconut_match_temp_7:  #585 (line in Coconut source)
                                _coconut_case_match_check_1 = True  #585 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #585 (line in Coconut source)
                        if (not _coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_1, ResultMessage)):  #585 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #585 (line in Coconut source)
                        if _coconut_case_match_check_1:  #585 (line in Coconut source)
                            _coconut_case_match_check_1 = False  #585 (line in Coconut source)
                            if not _coconut_case_match_check_1:  #585 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #585 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #585 (line in Coconut source)

                            if not _coconut_case_match_check_1:  #585 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #585 (line in Coconut source)
                                    _coconut_match_temp_8 = _coconut.getattr(ResultMessage, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #585 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #585 (line in Coconut source)
                                        raise _coconut.TypeError("ResultMessage.__match_args__ must be a tuple")  #585 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_8) < 0:  #585 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ResultMessage' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #585 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #585 (line in Coconut source)




                if _coconut_case_match_check_1:  #585 (line in Coconut source)
                    if getattr(message, "is_error", False):  #586 (line in Coconut source)
                        subtype = getattr(message, "subtype", "unknown")  #587 (line in Coconut source)
                        raise ClaudeCodeAgentError(subtype, message.result or "")  #588 (line in Coconut source)
                    result_text = message.result or ""  #589 (line in Coconut source)
                    cost_usd = getattr(message, "total_cost_usd", None)  #590 (line in Coconut source)

        return _AgentRunResult(text=result_text, tool_calls=tool_call_count, cost_usd=cost_usd, tool_events=tool_events)  #592 (line in Coconut source)


    async def _run_with_sdk_client(self, prompt: str, options: Any) -> _AgentRunResult:  #599 (line in Coconut source)
        """Use ClaudeSDKClient — required for in-process SDK MCP servers."""  #600 (line in Coconut source)
        parts: list[str] = []  #601 (line in Coconut source)
        tool_call_count = 0  #602 (line in Coconut source)
        cost_usd: float | None = None  #603 (line in Coconut source)
        tool_events: list[dict[str, Any]] = []  #604 (line in Coconut source)

        async with ClaudeSDKClient(options=options) as client:  #606 (line in Coconut source)
            await client.query(prompt)  #607 (line in Coconut source)
            async for message in client.receive_response():  #608 (line in Coconut source)
                _coconut_case_match_to_2 = message  #609 (line in Coconut source)
                _coconut_case_match_check_2 = False  #609 (line in Coconut source)
                _coconut_match_temp_9 = _coconut.getattr(AssistantMessage, "_coconut_is_data", False) or _coconut.isinstance(AssistantMessage, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AssistantMessage)  # type: ignore  #609 (line in Coconut source)
                _coconut_case_match_check_2 = True  #609 (line in Coconut source)
                if _coconut_case_match_check_2:  #609 (line in Coconut source)
                    _coconut_case_match_check_2 = False  #609 (line in Coconut source)
                    if not _coconut_case_match_check_2:  #609 (line in Coconut source)
                        if (_coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_2, AssistantMessage)):  #609 (line in Coconut source)
                            _coconut_match_temp_10 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #609 (line in Coconut source)
                            if _coconut_match_temp_10:  #609 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #609 (line in Coconut source)

                    if not _coconut_case_match_check_2:  #609 (line in Coconut source)
                        if (not _coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_2, AssistantMessage)):  #609 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #609 (line in Coconut source)
                        if _coconut_case_match_check_2:  #609 (line in Coconut source)
                            _coconut_case_match_check_2 = False  #609 (line in Coconut source)
                            if not _coconut_case_match_check_2:  #609 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #609 (line in Coconut source)
                                    _coconut_case_match_check_2 = True  #609 (line in Coconut source)

                            if not _coconut_case_match_check_2:  #609 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #609 (line in Coconut source)
                                    _coconut_match_temp_11 = _coconut.getattr(AssistantMessage, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #609 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_11, _coconut.tuple):  #609 (line in Coconut source)
                                        raise _coconut.TypeError("AssistantMessage.__match_args__ must be a tuple")  #609 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_11) < 0:  #609 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AssistantMessage' only supports %s)" % (_coconut.len(_coconut_match_temp_11),))  #609 (line in Coconut source)
                                    _coconut_case_match_check_2 = True  #609 (line in Coconut source)




                if _coconut_case_match_check_2:  #609 (line in Coconut source)
                    for block in message.content:  #611 (line in Coconut source)
                        if isinstance(block, TextBlock):  #612 (line in Coconut source)
                            parts.append(block.text)  #613 (line in Coconut source)
                        if ToolUseBlock and isinstance(block, ToolUseBlock):  #614 (line in Coconut source)
                            tool_call_count += 1  #615 (line in Coconut source)
                            tool_events.append(_extract_tool_event(block))  #616 (line in Coconut source)
                if not _coconut_case_match_check_2:  #617 (line in Coconut source)
                    _coconut_match_temp_12 = _coconut.getattr(ResultMessage, "_coconut_is_data", False) or _coconut.isinstance(ResultMessage, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ResultMessage)  # type: ignore  #617 (line in Coconut source)
                    _coconut_case_match_check_2 = True  #617 (line in Coconut source)
                    if _coconut_case_match_check_2:  #617 (line in Coconut source)
                        _coconut_case_match_check_2 = False  #617 (line in Coconut source)
                        if not _coconut_case_match_check_2:  #617 (line in Coconut source)
                            if (_coconut_match_temp_12) and (_coconut.isinstance(_coconut_case_match_to_2, ResultMessage)):  #617 (line in Coconut source)
                                _coconut_match_temp_13 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #617 (line in Coconut source)
                                if _coconut_match_temp_13:  #617 (line in Coconut source)
                                    _coconut_case_match_check_2 = True  #617 (line in Coconut source)

                        if not _coconut_case_match_check_2:  #617 (line in Coconut source)
                            if (not _coconut_match_temp_12) and (_coconut.isinstance(_coconut_case_match_to_2, ResultMessage)):  #617 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #617 (line in Coconut source)
                            if _coconut_case_match_check_2:  #617 (line in Coconut source)
                                _coconut_case_match_check_2 = False  #617 (line in Coconut source)
                                if not _coconut_case_match_check_2:  #617 (line in Coconut source)
                                    if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #617 (line in Coconut source)
                                        _coconut_case_match_check_2 = True  #617 (line in Coconut source)

                                if not _coconut_case_match_check_2:  #617 (line in Coconut source)
                                    if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #617 (line in Coconut source)
                                        _coconut_match_temp_14 = _coconut.getattr(ResultMessage, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #617 (line in Coconut source)
                                        if not _coconut.isinstance(_coconut_match_temp_14, _coconut.tuple):  #617 (line in Coconut source)
                                            raise _coconut.TypeError("ResultMessage.__match_args__ must be a tuple")  #617 (line in Coconut source)
                                        if _coconut.len(_coconut_match_temp_14) < 0:  #617 (line in Coconut source)
                                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ResultMessage' only supports %s)" % (_coconut.len(_coconut_match_temp_14),))  #617 (line in Coconut source)
                                        _coconut_case_match_check_2 = True  #617 (line in Coconut source)




                    if _coconut_case_match_check_2:  #617 (line in Coconut source)
                        if getattr(message, "is_error", False):  #618 (line in Coconut source)
                            subtype = getattr(message, "subtype", "unknown")  #619 (line in Coconut source)
                            raise ClaudeCodeAgentError(subtype, message.result or "")  #620 (line in Coconut source)
                        cost_usd = getattr(message, "total_cost_usd", None)  #621 (line in Coconut source)

        return _AgentRunResult(text="\n".join(parts), tool_calls=tool_call_count, cost_usd=cost_usd, tool_events=tool_events)  #623 (line in Coconut source)
