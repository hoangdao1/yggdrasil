#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf9e88630

# Compiled with Coconut version 3.2.0

"""Yggdrasil — a knowledge graph where every node is an active agent."""

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



END_NODE: str = "__END__"  #3 (line in Coconut source)

from yggdrasil_lm.batch import BatchItemResult  #5 (line in Coconut source)
from yggdrasil_lm.batch import BatchRun  #5 (line in Coconut source)
from yggdrasil_lm.batch import BatchStatus  #5 (line in Coconut source)
from yggdrasil_lm.app import GraphApp  #6 (line in Coconut source)
from yggdrasil_lm.app import create_agent  #6 (line in Coconut source)
from yggdrasil_lm.app import create_context  #6 (line in Coconut source)
from yggdrasil_lm.app import create_executor  #6 (line in Coconut source)
from yggdrasil_lm.app import create_prompt  #6 (line in Coconut source)
from yggdrasil_lm.app import create_reasoner  #6 (line in Coconut source)
from yggdrasil_lm.app import create_tool  #6 (line in Coconut source)
from yggdrasil_lm.app import create_transform  #6 (line in Coconut source)
from yggdrasil_lm.backends.llm import AnthropicBackend  #16 (line in Coconut source)
from yggdrasil_lm.backends.llm import OpenAIBackend  #16 (line in Coconut source)
from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor  #17 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import ApprovalNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import ContextNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import ExecutionPolicy  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import FactSource  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import GraphNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import ReasonerNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import RetryPolicy  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import RouteRule  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #18 (line in Coconut source)
from yggdrasil_lm.core.nodes import TransformNode  #18 (line in Coconut source)
from yggdrasil_lm.symbolic import Program  #31 (line in Coconut source)
from yggdrasil_lm.symbolic import Solution  #31 (line in Coconut source)
from yggdrasil_lm.symbolic import fact  #31 (line in Coconut source)
from yggdrasil_lm.core.edges import Edge  #32 (line in Coconut source)
from yggdrasil_lm.core.edges import EdgeType  #32 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #33 (line in Coconut source)
from yggdrasil_lm.core.store import NetworkXGraphStore  #33 (line in Coconut source)
from yggdrasil_lm.core.executor import ExecutionContext  #34 (line in Coconut source)
from yggdrasil_lm.core.executor import ExecutionOptions  #34 (line in Coconut source)
from yggdrasil_lm.core.executor import GraphExecutor  #34 (line in Coconut source)
from yggdrasil_lm.core.executor import ResumeReadiness  #34 (line in Coconut source)
from yggdrasil_lm.core.executor import TraceEvent  #34 (line in Coconut source)
from yggdrasil_lm.core.executor import print_trace  #34 (line in Coconut source)
from yggdrasil_lm.observability import RunExplanation  #42 (line in Coconut source)
from yggdrasil_lm.observability import explain_run  #42 (line in Coconut source)
from yggdrasil_lm.trace_ui import inspect_trace  #43 (line in Coconut source)
from yggdrasil_lm.media import ImageBlock  #44 (line in Coconut source)
from yggdrasil_lm.media import QueryContent  #44 (line in Coconut source)
from yggdrasil_lm.media import image_from_file  #44 (line in Coconut source)
from yggdrasil_lm.media import image_from_url  #44 (line in Coconut source)
from yggdrasil_lm.media import image_from_base64  #44 (line in Coconut source)
from yggdrasil_lm.media import build_query  #44 (line in Coconut source)

__all__ = ["GraphApp", "create_agent", "create_context", "create_executor", "create_prompt", "create_reasoner", "create_tool", "create_transform", "AnthropicBackend", "OpenAIBackend", "ClaudeCodeExecutor", "BatchRun", "BatchItemResult", "BatchStatus", "AgentNode", "ApprovalNode", "ContextNode", "ToolNode", "GraphNode", "TransformNode", "ReasonerNode", "FactSource", "Program", "Solution", "fact", "RetryPolicy", "ExecutionPolicy", "RouteRule", "Edge", "EdgeType", "END_NODE", "GraphStore", "NetworkXGraphStore", "GraphExecutor", "ExecutionContext", "ExecutionOptions", "ResumeReadiness", "TraceEvent", "explain_run", "RunExplanation", "print_trace", "inspect_trace", "ImageBlock", "QueryContent", "image_from_file", "image_from_url", "image_from_base64", "build_query"]  #53 (line in Coconut source)
