#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd9cab5de

# Compiled with Coconut version 3.2.0

"""Tool registry — maps callable_ref strings to Python callables.

Usage:
    registry = ToolRegistry()
    registry.register("mymodule.my_fn", my_fn)

    # Or use the decorator:
    @registry.tool("mymodule.my_fn")
    async def my_fn(input: dict) -> str: ...

    # Attach to executor:
    for ref, fn in registry.items():
        executor.register_tool(ref, fn)

    # Or in one call:
    registry.attach(executor)
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



import importlib  #19 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #20 (line in Coconut source)
    from typing import Any  #20 (line in Coconut source)
else:  #20 (line in Coconut source)
    try:  #20 (line in Coconut source)
        Any = _coconut.typing.Any  #20 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #20 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #20 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #20 (line in Coconut source)
    from typing import Callable  #20 (line in Coconut source)
else:  #20 (line in Coconut source)
    try:  #20 (line in Coconut source)
        Callable = _coconut.typing.Callable  #20 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #20 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #20 (line in Coconut source)

from yggdrasil_lm.tools.code_exec import run_python  #22 (line in Coconut source)
from yggdrasil_lm.tools.echo import echo  #23 (line in Coconut source)
from yggdrasil_lm.tools.kg_query import facts as kg_facts  #24 (line in Coconut source)
from yggdrasil_lm.tools.kg_query import neighbors as kg_neighbors  #25 (line in Coconut source)
from yggdrasil_lm.tools.kg_query import reachable as kg_reachable  #26 (line in Coconut source)
from yggdrasil_lm.tools.web_search import search as web_search  #27 (line in Coconut source)


class ToolRegistry():  #30 (line in Coconut source)
    """Central registry mapping callable_ref strings to Python callables.

    callable_ref format: "module.path.function_name"
    e.g. "tools.web_search.search"
    """  #35 (line in Coconut source)

    def __init__(self) -> None:  #37 (line in Coconut source)
        self._registry: dict[str, Callable[..., Any]] = {}  #38 (line in Coconut source)


    def register(self, callable_ref: str, fn: Callable[..., Any]) -> None:  #40 (line in Coconut source)
        """Register a callable under its dotted ref string."""  #41 (line in Coconut source)
        self._registry[callable_ref] = fn  #42 (line in Coconut source)


    def tool(self, callable_ref: str) -> Callable:  #44 (line in Coconut source)
        """Decorator to register a function."""  #45 (line in Coconut source)
        def decorator(fn: Callable) -> Callable:  #46 (line in Coconut source)
            self.register(callable_ref, fn)  #47 (line in Coconut source)
            return fn  #48 (line in Coconut source)

        return decorator  #49 (line in Coconut source)


    @_coconut_tco  #51 (line in Coconut source)
    def get(self, callable_ref: str) -> Callable[..., Any] | None:  #51 (line in Coconut source)
        return _coconut_tail_call(self._registry.get, callable_ref)  #52 (line in Coconut source)


    @_coconut_tco  #54 (line in Coconut source)
    def items(self):  #54 (line in Coconut source)
        return _coconut_tail_call(self._registry.items)  #55 (line in Coconut source)


    def load(self, callable_ref: str) -> Callable[..., Any]:  #57 (line in Coconut source)
        """Load a callable from a dotted import path if not already registered.

        e.g. "tools.web_search.search" imports ``yggdrasil_lm.tools.web_search``
        and returns its ``.search`` attribute. A bare ``tools.*`` ref (the
        documented short form, also used by the default registrations) is
        resolved against the ``yggdrasil_lm`` package; a fully-qualified ref is
        imported as-is.
        """  #65 (line in Coconut source)
        if callable_ref in self._registry:  #66 (line in Coconut source)
            return self._registry[callable_ref]  #67 (line in Coconut source)

        parts = callable_ref.rsplit(".", 1)  #69 (line in Coconut source)
        if len(parts) != 2:  #70 (line in Coconut source)
            raise ImportError("Invalid callable_ref: {_coconut_format_0!r}".format(_coconut_format_0=(callable_ref)))  #71 (line in Coconut source)
        module_path, fn_name = parts  #72 (line in Coconut source)

        candidates = [module_path,]  #74 (line in Coconut source)
# Short refs like "tools.echo" live under the package, not at top level.
        if not module_path.startswith("yggdrasil_lm."):  #76 (line in Coconut source)
            candidates.append("yggdrasil_lm.{_coconut_format_0}".format(_coconut_format_0=(module_path)))  #77 (line in Coconut source)

        module = None  #79 (line in Coconut source)
        last_err: ImportError | None = None  #80 (line in Coconut source)
        for candidate in candidates:  #81 (line in Coconut source)
            try:  #82 (line in Coconut source)
                module = importlib.import_module(candidate)  #83 (line in Coconut source)
                break  #84 (line in Coconut source)
            except ImportError as exc:  #85 (line in Coconut source)
                last_err = exc  #86 (line in Coconut source)
        if module is None:  #87 (line in Coconut source)
            raise ImportError(("Could not import module for callable_ref {_coconut_format_0!r} ".format(_coconut_format_0=(callable_ref)) + "(tried {_coconut_format_0})".format(_coconut_format_0=(candidates)))) from last_err  #88 (line in Coconut source)

        fn = getattr(module, fn_name)  #93 (line in Coconut source)
        self.register(callable_ref, fn)  #94 (line in Coconut source)
        return fn  #95 (line in Coconut source)


    def attach(self, executor: Any) -> None:  #97 (line in Coconut source)
        """Register all tools in this registry with a GraphExecutor."""  #98 (line in Coconut source)
        for ref, fn in self._registry.items():  #99 (line in Coconut source)
            executor.register_tool(ref, fn)  #100 (line in Coconut source)


    def __contains__(self, ref: str) -> bool:  #102 (line in Coconut source)
        return ref in self._registry  #103 (line in Coconut source)


    @_coconut_tco  #105 (line in Coconut source)
    def __len__(self) -> int:  #105 (line in Coconut source)
        return _coconut_tail_call(len, self._registry)  #106 (line in Coconut source)


# ---------------------------------------------------------------------------
# Global default registry (import and use directly)
# ---------------------------------------------------------------------------


default_registry = ToolRegistry()  #113 (line in Coconut source)


# ---------------------------------------------------------------------------
# Built-in tool implementations
# ---------------------------------------------------------------------------

default_registry.register("tools.web_search.search", web_search)  #120 (line in Coconut source)


# ---------------------------------------------------------------------------
# run_python is NOT registered in default_registry.
#
# SECURITY: This tool grants any LLM agent that receives it FULL CODE EXECUTION
# capability on the host machine — no sandbox, no capability restrictions, only
# a timeout. Prompt injection via web search results or file contents can trigger
# arbitrary OS commands.
#
# To opt in explicitly:
#   from yggdrasil_lm.tools.registry import run_python
#   executor.register_tool("tools.code_exec.run_python", run_python)
# ---------------------------------------------------------------------------
default_registry.register("tools.echo.echo", echo)  #135 (line in Coconut source)

# Knowledge-graph-as-factbase tools (the symbolic query surface). These receive
# the live GraphStore via `store` keyword injection — safe, read-only.
default_registry.register("tools.kg_query.neighbors", kg_neighbors)  #139 (line in Coconut source)
default_registry.register("tools.kg_query.reachable", kg_reachable)  #140 (line in Coconut source)
default_registry.register("tools.kg_query.facts", kg_facts)  #141 (line in Coconut source)
