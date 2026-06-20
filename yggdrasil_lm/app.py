#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xee6ae81b

# Compiled with Coconut version 3.2.0

"""Beginner-friendly builder API for yggdrasil.

This module keeps the core graph primitives available while offering a smaller,
task-oriented surface for first-time users and code-generation tools.
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



import base64  #7 (line in Coconut source)
import mimetypes  #8 (line in Coconut source)
from pathlib import Path  #9 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #10 (line in Coconut source)
    from typing import Any  #10 (line in Coconut source)
else:  #10 (line in Coconut source)
    try:  #10 (line in Coconut source)
        Any = _coconut.typing.Any  #10 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #10 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #10 (line in Coconut source)

from yggdrasil_lm.backends.llm import AnthropicBackend  #12 (line in Coconut source)
from yggdrasil_lm.backends.llm import LLMBackend  #12 (line in Coconut source)
from yggdrasil_lm.backends.llm import OpenAIBackend  #12 (line in Coconut source)
from yggdrasil_lm.core.edges import Edge  #13 (line in Coconut source)
from yggdrasil_lm.core.executor import GraphExecutor  #14 (line in Coconut source)
from yggdrasil_lm.core.executor import QueryContent  #14 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import ContextNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import FactSource  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import GraphNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import PromptNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import ReasonerNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #15 (line in Coconut source)
from yggdrasil_lm.core.nodes import TransformNode  #15 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #25 (line in Coconut source)
from yggdrasil_lm.core.store import NetworkXGraphStore  #25 (line in Coconut source)
from yggdrasil_lm.tools.registry import ToolRegistry  #26 (line in Coconut source)
from yggdrasil_lm.tools.registry import default_registry  #26 (line in Coconut source)

NodeRef = AgentNode | ToolNode | ContextNode | PromptNode | TransformNode | ReasonerNode | GraphNode | str  #28 (line in Coconut source)
END_NODE = "__END__"  #29 (line in Coconut source)


@_coconut_tco  #32 (line in Coconut source)
def create_agent(name: str, *, description: str="", model: str="claude-sonnet-4-6", system_prompt: str="", routing_table: dict[str, str] | None=None, max_iterations: int=10, **kwargs: Any,) -> AgentNode:  #32 (line in Coconut source)
    """Create an AgentNode with beginner-friendly defaults."""  #42 (line in Coconut source)
    return _coconut_tail_call(AgentNode, name=name, description=description, model=model, system_prompt=system_prompt, routing_table=routing_table or {"default": END_NODE}, max_iterations=max_iterations, **kwargs)  #43 (line in Coconut source)



@_coconut_tco  #54 (line in Coconut source)
def create_tool(name: str, *, callable_ref: str, description: str="", input_schema: dict[str, Any] | None=None, output_schema: dict[str, Any] | None=None, is_async: bool=True, **kwargs: Any,) -> ToolNode:  #54 (line in Coconut source)
    """Create a ToolNode with sane defaults."""  #64 (line in Coconut source)
    return _coconut_tail_call(ToolNode, name=name, description=description, callable_ref=callable_ref, input_schema=input_schema or {"type": "object", "properties": {}}, output_schema=output_schema or {}, is_async=is_async, **kwargs)  #65 (line in Coconut source)



@_coconut_tco  #76 (line in Coconut source)
def create_transform(name: str, *, callable_ref: str, description: str="", input_keys: list[str] | None=None, output_key: str="", is_async: bool=True, **kwargs: Any,) -> TransformNode:  #76 (line in Coconut source)
    """Create a TransformNode — a pure-Python data reshape step with no LLM."""  #86 (line in Coconut source)
    return _coconut_tail_call(TransformNode, name=name, description=description, callable_ref=callable_ref, input_keys=input_keys or [], output_key=output_key, is_async=is_async, **kwargs)  #87 (line in Coconut source)



@_coconut_tco  #98 (line in Coconut source)
def create_reasoner(name: str, *, program: str="", rules: list[dict[str, Any]] | None=None, state_keys: list[str] | None=None, edge_types: list[str] | None=None, include_node_facts: bool=False, query: list[str] | None=None, output_key: str="inferred", emit_derived_only: bool=True, with_proof: bool=False, fail_on_empty: bool=False, description: str="", **kwargs: Any,) -> ReasonerNode:  #98 (line in Coconut source)
    """Create a ReasonerNode — a symbolic Datalog inference step (no LLM).

    ``program`` is Datalog source (see ``yggdrasil_lm.symbolic.datalog``); facts
    are pulled from ``state_keys`` and/or knowledge-graph ``edge_types``.
    """  #118 (line in Coconut source)
    return _coconut_tail_call(ReasonerNode, name=name, description=description, program=program, rules=rules or [], fact_source=FactSource(state_keys=state_keys or [], edge_types=edge_types or [], include_node_facts=include_node_facts), query=query or [], output_key=output_key, emit_derived_only=emit_derived_only, with_proof=with_proof, fail_on_empty=fail_on_empty, **kwargs)  #119 (line in Coconut source)



@_coconut_tco  #138 (line in Coconut source)
def create_context(name: str, content: str, *, description: str="", **kwargs: Any,) -> ContextNode:  #138 (line in Coconut source)
    """Create a ContextNode."""  #145 (line in Coconut source)
    return _coconut_tail_call(ContextNode, name=name, content=content, description=description, **kwargs)  #146 (line in Coconut source)



@_coconut_tco  #149 (line in Coconut source)
def create_subgraph(name: str, *, entry: AgentNode | str, exit: AgentNode | str | None=None, description: str="", strategy: str="sequential", input_keys: list[str] | None=None, input_map: dict[str, str] | None=None, scope_outputs: bool=True, **kwargs: Any,) -> GraphNode:  #149 (line in Coconut source)
    """Create a GraphNode that wraps a sub-graph as a single reusable step.

    Args:
        entry: AgentNode or node_id that the sub-graph starts from.
        exit:  AgentNode or node_id whose output is the sub-graph's result.
               Defaults to entry.
        strategy: "sequential" | "parallel" | "topological".
        input_keys: parent node_ids / state keys to thread into the sub-run
            as its initial query.
        input_map: {alias: source_key} pairs surfaced under state.data.
        scope_outputs: keep inner outputs scoped (default) or merge into parent.
    """  #172 (line in Coconut source)
    entry_id = entry if isinstance(entry, str) else entry.node_id  #173 (line in Coconut source)
    exit_id = (exit if isinstance(exit, str) else (exit.node_id if exit is not None else ""))  #174 (line in Coconut source)
    return _coconut_tail_call(GraphNode, name=name, description=description, entry_node_id=entry_id, exit_node_id=exit_id, strategy=strategy, input_keys=input_keys or [], input_map=input_map or {}, scope_outputs=scope_outputs, **kwargs)  #177 (line in Coconut source)



@_coconut_tco  #190 (line in Coconut source)
def create_prompt(name: str, template: str, *, description: str="", **kwargs: Any,) -> PromptNode:  #190 (line in Coconut source)
    """Create a PromptNode."""  #197 (line in Coconut source)
    return _coconut_tail_call(PromptNode, name=name, template=template, description=description, **kwargs)  #198 (line in Coconut source)



@_coconut_tco  #201 (line in Coconut source)
def create_executor(store: GraphStore, *, provider: str | None=None, backend: LLMBackend | None=None, **backend_kwargs: Any,) -> GraphExecutor:  #201 (line in Coconut source)
    """Create a GraphExecutor from a small set of backend profiles.

    Args:
        store: Graph storage backend.
        provider: One of "anthropic", "claude-code", "compatible", "openai",
            "openai-compatible", or None.
        backend: Explicit backend instance. Takes precedence over provider.
        **backend_kwargs: Passed to the backend constructor when provider is set.
    """  #216 (line in Coconut source)
    if backend is not None:  #217 (line in Coconut source)
        return _coconut_tail_call(GraphExecutor, store, backend=backend)  #218 (line in Coconut source)
    if provider is None:  #219 (line in Coconut source)
        return _coconut_tail_call(GraphExecutor, store)  #220 (line in Coconut source)

    provider_key = provider.strip().lower()  #222 (line in Coconut source)
    _coconut_case_match_to_0 = provider_key  #223 (line in Coconut source)
    _coconut_case_match_check_0 = False  #223 (line in Coconut source)
    if _coconut_case_match_to_0 == "anthropic":  #223 (line in Coconut source)
        _coconut_case_match_check_0 = True  #223 (line in Coconut source)
    if _coconut_case_match_check_0:  #223 (line in Coconut source)
        return _coconut_tail_call(GraphExecutor, store, backend=AnthropicBackend(**backend_kwargs))  #225 (line in Coconut source)
    if not _coconut_case_match_check_0:  #226 (line in Coconut source)
        _coconut_case_match_check_0 = True  #226 (line in Coconut source)
        if _coconut_case_match_check_0:  #226 (line in Coconut source)
            _coconut_case_match_check_0 = False  #226 (line in Coconut source)
            if not _coconut_case_match_check_0:  #226 (line in Coconut source)
                if _coconut_case_match_to_0 == "claude-code":  #226 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #226 (line in Coconut source)

            if not _coconut_case_match_check_0:  #226 (line in Coconut source)
                if _coconut_case_match_to_0 == "claude_code":  #226 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #226 (line in Coconut source)

            if not _coconut_case_match_check_0:  #226 (line in Coconut source)
                if _coconut_case_match_to_0 == "claudecode":  #226 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #226 (line in Coconut source)


        if _coconut_case_match_check_0:  #226 (line in Coconut source)
            from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor  #227 (line in Coconut source)
            return _coconut_tail_call(ClaudeCodeExecutor, store, **backend_kwargs)  #228 (line in Coconut source)
    if not _coconut_case_match_check_0:  #229 (line in Coconut source)
        _coconut_case_match_check_0 = True  #229 (line in Coconut source)
        if _coconut_case_match_check_0:  #229 (line in Coconut source)
            _coconut_case_match_check_0 = False  #229 (line in Coconut source)
            if not _coconut_case_match_check_0:  #229 (line in Coconut source)
                if _coconut_case_match_to_0 == "openai":  #229 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #229 (line in Coconut source)

            if not _coconut_case_match_check_0:  #229 (line in Coconut source)
                if _coconut_case_match_to_0 == "openai-compatible":  #229 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #229 (line in Coconut source)

            if not _coconut_case_match_check_0:  #229 (line in Coconut source)
                if _coconut_case_match_to_0 == "compatible":  #229 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #229 (line in Coconut source)


        if _coconut_case_match_check_0:  #229 (line in Coconut source)
            return _coconut_tail_call(GraphExecutor, store, backend=OpenAIBackend(**backend_kwargs))  #230 (line in Coconut source)
    if not _coconut_case_match_check_0:  #231 (line in Coconut source)
        _coconut_case_match_check_0 = True  #231 (line in Coconut source)
        if _coconut_case_match_check_0:  #231 (line in Coconut source)
            raise ValueError(("Unknown provider: {_coconut_format_0!r}. Use 'anthropic', 'claude-code', ".format(_coconut_format_0=(provider)) + "'compatible', or pass backend=..."))  #232 (line in Coconut source)



class GraphApp():  #238 (line in Coconut source)
    """Thin builder facade for the yggdrasil runtime.

    This class keeps the low-level graph primitives available, but presents them
    in a sequence that is easier to teach:
    1. create nodes
    2. connect them
    3. register tool implementations
    4. run the graph
    """  #247 (line in Coconut source)

    def __init__(self, *, store: GraphStore | None=None, executor: GraphExecutor | None=None, provider: str | None=None, backend: LLMBackend | None=None, tool_registry: ToolRegistry | None=None, **backend_kwargs: Any,) -> None:  #249 (line in Coconut source)
        self.store = store or NetworkXGraphStore()  #259 (line in Coconut source)
        self._executor = executor  #260 (line in Coconut source)
        self._provider = provider  #261 (line in Coconut source)
        self._backend = backend  #262 (line in Coconut source)
        self._backend_kwargs = backend_kwargs  #263 (line in Coconut source)
        self.tool_registry = tool_registry or default_registry  #264 (line in Coconut source)


    @property  #266 (line in Coconut source)
    def executor(self) -> GraphExecutor:  #267 (line in Coconut source)
        """Lazily create the executor when it is first needed."""  #268 (line in Coconut source)
        if self._executor is None:  #269 (line in Coconut source)
            self._executor = create_executor(self.store, provider=self._provider, backend=self._backend, **self._backend_kwargs)  #270 (line in Coconut source)
        return self._executor  #276 (line in Coconut source)


    async def add_agent(self, name: str, **kwargs: Any) -> AgentNode:  #278 (line in Coconut source)
        agent = create_agent(name, **kwargs)  #279 (line in Coconut source)
        await self.store.upsert_node(agent)  #280 (line in Coconut source)
        return agent  #281 (line in Coconut source)


    async def add_tool(self, name: str, *, fn: Any | None=None, attach: bool=False, agent: AgentNode | str | None=None, **kwargs: Any,) -> ToolNode:  #283 (line in Coconut source)
        tool = create_tool(name, **kwargs)  #292 (line in Coconut source)
        await self.store.upsert_node(tool)  #293 (line in Coconut source)
        if fn is not None:  #294 (line in Coconut source)
            self.register_tool(tool.callable_ref, fn)  #295 (line in Coconut source)
        if attach:  #296 (line in Coconut source)
            if agent is None:  #297 (line in Coconut source)
                raise ValueError("agent=... is required when attach=True")  #298 (line in Coconut source)
            await self.connect_tool(agent, tool)  #299 (line in Coconut source)
        return tool  #300 (line in Coconut source)


    async def add_transform(self, name: str, *, fn: Any | None=None, **kwargs: Any,) -> TransformNode:  #302 (line in Coconut source)
        transform = create_transform(name, **kwargs)  #309 (line in Coconut source)
        await self.store.upsert_node(transform)  #310 (line in Coconut source)
        if fn is not None:  #311 (line in Coconut source)
            self.executor.register_tool(transform.callable_ref, fn)  #312 (line in Coconut source)
        return transform  #313 (line in Coconut source)


    async def add_reasoner(self, name: str, **kwargs: Any) -> ReasonerNode:  #315 (line in Coconut source)
        """Register a ReasonerNode — the symbolic half of a neurosymbolic graph.

        See ``create_reasoner`` for arguments. Example::

            reasoner = await app.add_reasoner(
                "EligibilityRules",
                program='''
                    eligible(?p) :- applicant(?p, ?age), ?age >= 18, resident(?p).
                ''',
                state_keys=["facts"],   # facts an upstream agent extracted
                query=["eligible"],
            )
        """  #328 (line in Coconut source)
        reasoner = create_reasoner(name, **kwargs)  #329 (line in Coconut source)
        await self.store.upsert_node(reasoner)  #330 (line in Coconut source)
        return reasoner  #331 (line in Coconut source)


    async def add_context(self, name: str, content: str, **kwargs: Any) -> ContextNode:  #333 (line in Coconut source)
        ctx = create_context(name, content, **kwargs)  #334 (line in Coconut source)
        await self.store.upsert_node(ctx)  #335 (line in Coconut source)
        return ctx  #336 (line in Coconut source)


    async def add_image_context(self, name: str, *, url: str | None=None, path: str | Path | None=None, data: str | None=None, media_type: str | None=None, description: str="", **kwargs: Any,) -> ContextNode:  #338 (line in Coconut source)
        """Create an image ContextNode for visual RAG.

        Provide exactly one of ``url``, ``path``, or ``data``.

        Args:
            name:        Human-readable label shown in traces.
            url:         Publicly accessible image URL.
            path:        Local file path — the image is base64-encoded at call time.
            data:        Pre-encoded base64 string (no ``data:`` URI prefix).
            media_type:  MIME type (e.g. ``"image/png"``). Auto-detected from
                         ``path`` when omitted; defaults to ``"image/jpeg"``.
            description: Optional description stored on the node.

        Returns:
            A :class:`ContextNode` with ``content_type="image"`` wired for
            visual RAG.  Connect it to an agent with
            ``await app.connect_context(agent, ctx_node)``.

        Example::

            photo = await app.add_image_context("Product photo", url="https://cdn.example.com/p.jpg")
            await app.connect_context(agent, photo)
            ctx = await app.run(agent, "Describe this product.")
        """  #372 (line in Coconut source)
        sources = [s for s in (url, path, data) if s is not None]  #373 (line in Coconut source)
        if len(sources) != 1:  #374 (line in Coconut source)
            raise ValueError("Provide exactly one of: url=, path=, or data=")  #375 (line in Coconut source)

        if url is not None:  #377 (line in Coconut source)
            node = ContextNode(name=name, description=description, content=url, content_type="image", attributes={"image_source": "url"}, **kwargs)  #378 (line in Coconut source)
        else:  #386 (line in Coconut source)
            if path is not None:  #387 (line in Coconut source)
                file_path = Path(path)  #388 (line in Coconut source)
                if media_type is None:  #389 (line in Coconut source)
                    _suffix_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}  #390 (line in Coconut source)
                    media_type = _suffix_map.get(file_path.suffix.lower())  #394 (line in Coconut source)
                    if media_type is None:  #395 (line in Coconut source)
                        guessed, _ = mimetypes.guess_type(str(file_path))  #396 (line in Coconut source)
                        media_type = guessed or "image/jpeg"  #397 (line in Coconut source)
                raw_data = base64.standard_b64encode(file_path.read_bytes()).decode()  #398 (line in Coconut source)
            else:  #399 (line in Coconut source)
                raw_data = data  # type: ignore[assignment]  #400 (line in Coconut source)
                if media_type is None:  #401 (line in Coconut source)
                    media_type = "image/jpeg"  #402 (line in Coconut source)

            node = ContextNode(name=name, description=description, content=raw_data, content_type="image", attributes={"image_source": "base64", "media_type": media_type}, **kwargs)  #404 (line in Coconut source)

        await self.store.upsert_node(node)  #413 (line in Coconut source)
        return node  #414 (line in Coconut source)


    async def add_subgraph(self, name: str, *, entry: AgentNode | str, exit: AgentNode | str | None=None, **kwargs: Any,) -> GraphNode:  #416 (line in Coconut source)
        """Register a GraphNode that wraps a sub-graph as a single reusable step.

        See ``create_subgraph`` for argument details.
        """  #427 (line in Coconut source)
        node = create_subgraph(name, entry=entry, exit=exit, **kwargs)  #428 (line in Coconut source)
        await self.store.upsert_node(node)  #429 (line in Coconut source)
        return node  #430 (line in Coconut source)


    async def add_prompt(self, name: str, template: str, **kwargs: Any) -> PromptNode:  #432 (line in Coconut source)
        prompt = create_prompt(name, template, **kwargs)  #433 (line in Coconut source)
        await self.store.upsert_node(prompt)  #434 (line in Coconut source)
        return prompt  #435 (line in Coconut source)


    def register_tool(self, callable_ref: str, fn: Any) -> None:  #437 (line in Coconut source)
        self.executor.register_tool(callable_ref, fn)  #438 (line in Coconut source)


    def use_default_tools(self) -> None:  #440 (line in Coconut source)
        self.tool_registry.attach(self.executor)  #441 (line in Coconut source)


    async def connect_tool(self, agent: AgentNode | str, tool: ToolNode | str, *, weight: float | None=None, **kwargs: Any,) -> Edge:  #443 (line in Coconut source)
        return await self.store.attach_tool(self._node_id(agent), self._node_id(tool), weight=weight, **kwargs)  #451 (line in Coconut source)


    async def connect_context(self, agent: AgentNode | str, context: ContextNode | str, *, weight: float | None=None, **kwargs: Any,) -> Edge:  #458 (line in Coconut source)
        return await self.store.attach_context(self._node_id(agent), self._node_id(context), weight=weight, **kwargs)  #466 (line in Coconut source)


    async def connect_prompt(self, agent: AgentNode | str, prompt: PromptNode | str, **kwargs: Any,) -> Edge:  #473 (line in Coconut source)
        edge = Edge.has_prompt(self._node_id(agent), self._node_id(prompt), **kwargs)  #479 (line in Coconut source)
        await self.store.upsert_edge(edge)  #480 (line in Coconut source)
        return edge  #481 (line in Coconut source)


    async def delegate(self, src_agent: AgentNode | str, dst_agent: AgentNode | str, **kwargs: Any,) -> Edge:  #483 (line in Coconut source)
        edge = Edge.delegates_to(self._node_id(src_agent), self._node_id(dst_agent), **kwargs)  #489 (line in Coconut source)
        await self.store.upsert_edge(edge)  #490 (line in Coconut source)
        return edge  #491 (line in Coconut source)


    async def run(self, entry_node: AgentNode | str, query: QueryContent, *, strategy: str="sequential", **kwargs: Any,):  #493 (line in Coconut source)
        return await self.executor.run(entry_node_id=self._node_id(entry_node), query=query, strategy=strategy, **kwargs)  #501 (line in Coconut source)


    async def run_subgraph(self, subgraph: GraphNode | str, *, inputs: dict[str, Any] | None=None, query: str | None=None, **kwargs: Any,):  #508 (line in Coconut source)
        """Run a ``GraphNode`` in isolation — the testing / unit-of-work entry point.

        Args:
            subgraph: A ``GraphNode`` (or its node_id) to invoke directly.
            inputs:   Dict merged into ``state.data`` before the sub-graph fires.
                      Keys should match whatever the inner nodes (or the
                      ``input_map`` source keys) read from state.
            query:    Initial query string. If omitted, ``input_keys`` /
                      ``input_map`` on the GraphNode drive the resolved query;
                      otherwise a placeholder empty string is used.
            **kwargs: Forwarded to ``executor.run`` (e.g. ``max_hops``, ``options``).

        Returns:
            The ``ExecutionContext`` from the run. The sub-graph's result lives
            at ``ctx.outputs[subgraph.node_id]``.
        """  #531 (line in Coconut source)
        state = dict(kwargs.pop("state", None) or {})  #532 (line in Coconut source)
        if inputs:  #533 (line in Coconut source)
            state.update(inputs)  #534 (line in Coconut source)
        return await self.executor.run(entry_node_id=self._node_id(subgraph), query=query if query is not None else "", state=state or None, **kwargs)  #535 (line in Coconut source)


    async def dry_run_subgraph(self, subgraph: GraphNode | str, *, inputs: dict[str, Any] | None=None,) -> dict[str, Any]:  #542 (line in Coconut source)
        """Resolve a sub-graph's wiring without executing — for fast smoke tests.

        Returns the entry/exit ids, strategy, resolved query, and state overlay
        the executor would use if you ran this sub-graph now. See
        ``GraphExecutor.resolve_subgraph_inputs``.
        """  #553 (line in Coconut source)
        from yggdrasil_lm.core.executor import ExecutionContext  #554 (line in Coconut source)

        ctx = ExecutionContext(query="")  #556 (line in Coconut source)
        if inputs:  #557 (line in Coconut source)
            ctx.state.data.update(inputs)  #558 (line in Coconut source)
        return await self.executor.resolve_subgraph_inputs(self._node_id(subgraph), ctx)  #559 (line in Coconut source)


    def _node_id(self, node: NodeRef) -> str:  #561 (line in Coconut source)
        _coconut_case_match_to_1 = node  #562 (line in Coconut source)
        _coconut_case_match_check_1 = False  #562 (line in Coconut source)
        _coconut_match_temp_0 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #562 (line in Coconut source)
        _coconut_case_match_check_1 = True  #562 (line in Coconut source)
        if _coconut_case_match_check_1:  #562 (line in Coconut source)
            _coconut_case_match_check_1 = False  #562 (line in Coconut source)
            if not _coconut_case_match_check_1:  #562 (line in Coconut source)
                if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_1, str)):  #562 (line in Coconut source)
                    _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #562 (line in Coconut source)
                    if _coconut_match_temp_1:  #562 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #562 (line in Coconut source)

            if not _coconut_case_match_check_1:  #562 (line in Coconut source)
                if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_1, str)):  #562 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #562 (line in Coconut source)
                if _coconut_case_match_check_1:  #562 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #562 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #562 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #562 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #562 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #562 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #562 (line in Coconut source)
                            _coconut_match_temp_2 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #562 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #562 (line in Coconut source)
                                raise _coconut.TypeError("str.__match_args__ must be a tuple")  #562 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_2) < 0:  #562 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #562 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #562 (line in Coconut source)




        if _coconut_case_match_check_1:  #562 (line in Coconut source)
            return node  #564 (line in Coconut source)
        if not _coconut_case_match_check_1:  #565 (line in Coconut source)
            _coconut_case_match_check_1 = True  #565 (line in Coconut source)
            if _coconut_case_match_check_1:  #565 (line in Coconut source)
                return node.node_id  #566 (line in Coconut source)



__all__ = ["GraphApp", "create_agent", "create_context", "create_executor", "create_prompt", "create_subgraph", "create_tool", "create_transform"]  #569 (line in Coconut source)
