#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd92a0006

# Compiled with Coconut version 3.2.0

"""Node embedder — generates dense vectors for nodes using sentence-transformers.

Usage:
    embedder = Embedder()
    await embedder.embed_node(store, node)           # embed one node in-place
    await embedder.embed_all(store, node_types=[...])  # batch embed
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



import asyncio  #9 (line in Coconut source)
import json  #10 (line in Coconut source)
import os  #11 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #12 (line in Coconut source)
    from typing import Any  #12 (line in Coconut source)
else:  #12 (line in Coconut source)
    try:  #12 (line in Coconut source)
        Any = _coconut.typing.Any  #12 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #12 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #12 (line in Coconut source)

try:  #14 (line in Coconut source)
    from sentence_transformers import SentenceTransformer  #15 (line in Coconut source)
except ImportError as _e:  #16 (line in Coconut source)
    raise ImportError("sentence-transformers is required for Embedder. Install it with: pip install 'yggdrasil[embeddings]'") from _e  #17 (line in Coconut source)

from yggdrasil_lm.core.nodes import AnyNode  #22 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #22 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #23 (line in Coconut source)


EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")  #26 (line in Coconut source)


class Embedder():  #29 (line in Coconut source)
    """Generates and stores embeddings for graph nodes.

    The embedding source text is: f"{node.name}: {node.description}"
    For ContextNodes, the content is appended (up to 2000 chars).
    """  #34 (line in Coconut source)

    def __init__(self, model: str=EMBED_MODEL) -> None:  #36 (line in Coconut source)
        self.model = model  #37 (line in Coconut source)
        self._client: Any = None  #38 (line in Coconut source)


    def _get_client(self) -> SentenceTransformer:  #40 (line in Coconut source)
        if self._client is None:  #41 (line in Coconut source)
            self._client = SentenceTransformer(self.model)  #42 (line in Coconut source)
        return self._client  #43 (line in Coconut source)


    def _node_text(self, node: AnyNode) -> str:  #45 (line in Coconut source)
        """Produce the text to embed for a given node."""  #46 (line in Coconut source)
        from yggdrasil_lm.core.nodes import ContextNode  #47 (line in Coconut source)
        from yggdrasil_lm.core.nodes import ToolNode  #47 (line in Coconut source)
        parts = []  #48 (line in Coconut source)
        if node.name:  #49 (line in Coconut source)
            parts.append(node.name)  #50 (line in Coconut source)
        if node.description:  #51 (line in Coconut source)
            parts.append(node.description)  #52 (line in Coconut source)
        _coconut_case_match_to_0 = node  #53 (line in Coconut source)
        _coconut_case_match_check_0 = False  #53 (line in Coconut source)
        _coconut_match_temp_0 = _coconut.getattr(ContextNode, "_coconut_is_data", False) or _coconut.isinstance(ContextNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ContextNode)  # type: ignore  #53 (line in Coconut source)
        _coconut_case_match_check_0 = True  #53 (line in Coconut source)
        if _coconut_case_match_check_0:  #53 (line in Coconut source)
            _coconut_case_match_check_0 = False  #53 (line in Coconut source)
            if not _coconut_case_match_check_0:  #53 (line in Coconut source)
                _coconut_match_set_name_content = _coconut_sentinel  #53 (line in Coconut source)
                if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, ContextNode)):  #53 (line in Coconut source)
                    _coconut_match_temp_1 = _coconut.getattr(_coconut_case_match_to_0, 'content', _coconut_sentinel)  #53 (line in Coconut source)
                    _coconut_match_temp_2 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) if _coconut_case_match_to_0.__match_args__[i] not in ('content',)) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #53 (line in Coconut source)
                    if (_coconut_match_temp_1 is not _coconut_sentinel) and (_coconut_match_temp_2):  #53 (line in Coconut source)
                        _coconut_match_set_name_content = _coconut_match_temp_1  #53 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #53 (line in Coconut source)
                if _coconut_case_match_check_0:  #53 (line in Coconut source)
                    if _coconut_match_set_name_content is not _coconut_sentinel:  #53 (line in Coconut source)
                        content = _coconut_match_set_name_content  #53 (line in Coconut source)

            if not _coconut_case_match_check_0:  #53 (line in Coconut source)
                _coconut_match_set_name_content = _coconut_sentinel  #53 (line in Coconut source)
                if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, ContextNode)):  #53 (line in Coconut source)
                    _coconut_match_temp_4 = _coconut.getattr(_coconut_case_match_to_0, 'content', _coconut_sentinel)  #53 (line in Coconut source)
                    if _coconut_match_temp_4 is not _coconut_sentinel:  #53 (line in Coconut source)
                        _coconut_match_set_name_content = _coconut_match_temp_4  #53 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #53 (line in Coconut source)
                if _coconut_case_match_check_0:  #53 (line in Coconut source)
                    _coconut_case_match_check_0 = False  #53 (line in Coconut source)
                    if not _coconut_case_match_check_0:  #53 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #53 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #53 (line in Coconut source)

                    if not _coconut_case_match_check_0:  #53 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #53 (line in Coconut source)
                            _coconut_match_temp_3 = _coconut.getattr(ContextNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #53 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_3, _coconut.tuple):  #53 (line in Coconut source)
                                raise _coconut.TypeError("ContextNode.__match_args__ must be a tuple")  #53 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_3) < 0:  #53 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ContextNode' only supports %s)" % (_coconut.len(_coconut_match_temp_3),))  #53 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #53 (line in Coconut source)


                if _coconut_case_match_check_0:  #53 (line in Coconut source)
                    if _coconut_match_set_name_content is not _coconut_sentinel:  #53 (line in Coconut source)
                        content = _coconut_match_set_name_content  #53 (line in Coconut source)


        if _coconut_case_match_check_0 and not (content):  #53 (line in Coconut source)
            _coconut_case_match_check_0 = False  #53 (line in Coconut source)
        if _coconut_case_match_check_0:  #53 (line in Coconut source)
            parts.append(content[:2000])  #55 (line in Coconut source)
        if not _coconut_case_match_check_0:  #56 (line in Coconut source)
            _coconut_match_temp_5 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #56 (line in Coconut source)
            _coconut_case_match_check_0 = True  #56 (line in Coconut source)
            if _coconut_case_match_check_0:  #56 (line in Coconut source)
                _coconut_case_match_check_0 = False  #56 (line in Coconut source)
                if not _coconut_case_match_check_0:  #56 (line in Coconut source)
                    _coconut_match_set_name_schema = _coconut_sentinel  #56 (line in Coconut source)
                    if (_coconut_match_temp_5) and (_coconut.isinstance(_coconut_case_match_to_0, ToolNode)):  #56 (line in Coconut source)
                        _coconut_match_temp_6 = _coconut.getattr(_coconut_case_match_to_0, 'input_schema', _coconut_sentinel)  #56 (line in Coconut source)
                        _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) if _coconut_case_match_to_0.__match_args__[i] not in ('input_schema',)) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #56 (line in Coconut source)
                        if (_coconut_match_temp_6 is not _coconut_sentinel) and (_coconut_match_temp_7):  #56 (line in Coconut source)
                            _coconut_match_set_name_schema = _coconut_match_temp_6  #56 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #56 (line in Coconut source)
                    if _coconut_case_match_check_0:  #56 (line in Coconut source)
                        if _coconut_match_set_name_schema is not _coconut_sentinel:  #56 (line in Coconut source)
                            schema = _coconut_match_set_name_schema  #56 (line in Coconut source)

                if not _coconut_case_match_check_0:  #56 (line in Coconut source)
                    _coconut_match_set_name_schema = _coconut_sentinel  #56 (line in Coconut source)
                    if (not _coconut_match_temp_5) and (_coconut.isinstance(_coconut_case_match_to_0, ToolNode)):  #56 (line in Coconut source)
                        _coconut_match_temp_9 = _coconut.getattr(_coconut_case_match_to_0, 'input_schema', _coconut_sentinel)  #56 (line in Coconut source)
                        if _coconut_match_temp_9 is not _coconut_sentinel:  #56 (line in Coconut source)
                            _coconut_match_set_name_schema = _coconut_match_temp_9  #56 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #56 (line in Coconut source)
                    if _coconut_case_match_check_0:  #56 (line in Coconut source)
                        _coconut_case_match_check_0 = False  #56 (line in Coconut source)
                        if not _coconut_case_match_check_0:  #56 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #56 (line in Coconut source)
                                _coconut_case_match_check_0 = True  #56 (line in Coconut source)

                        if not _coconut_case_match_check_0:  #56 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #56 (line in Coconut source)
                                _coconut_match_temp_8 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #56 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #56 (line in Coconut source)
                                    raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #56 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_8) < 0:  #56 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #56 (line in Coconut source)
                                _coconut_case_match_check_0 = True  #56 (line in Coconut source)


                    if _coconut_case_match_check_0:  #56 (line in Coconut source)
                        if _coconut_match_set_name_schema is not _coconut_sentinel:  #56 (line in Coconut source)
                            schema = _coconut_match_set_name_schema  #56 (line in Coconut source)


            if _coconut_case_match_check_0 and not (schema):  #56 (line in Coconut source)
                _coconut_case_match_check_0 = False  #56 (line in Coconut source)
            if _coconut_case_match_check_0:  #56 (line in Coconut source)
                parts.append(json.dumps(schema)[:500])  #57 (line in Coconut source)
        return ": ".join(parts) or node.node_id  #58 (line in Coconut source)


    async def embed_text(self, text: str) -> list[float]:  #60 (line in Coconut source)
        """Embed a single text string and return the vector."""  #61 (line in Coconut source)
        client = self._get_client()  #62 (line in Coconut source)
        vec = await asyncio.to_thread(client.encode, text, normalize_embeddings=True)  #63 (line in Coconut source)
        return vec.tolist()  #64 (line in Coconut source)


    async def embed_node(self, store: GraphStore, node: AnyNode) -> AnyNode:  #66 (line in Coconut source)
        """Compute and store an embedding for a single node."""  #67 (line in Coconut source)
        text = self._node_text(node)  #68 (line in Coconut source)
        vec = await self.embed_text(text)  #69 (line in Coconut source)
        updated = node.model_copy(update={"embedding": vec})  #70 (line in Coconut source)
        await store.upsert_node(updated)  #71 (line in Coconut source)
        return updated  #72 (line in Coconut source)


    async def embed_all(self, store: GraphStore, node_types: list[NodeType] | None=None, skip_existing: bool=True,) -> int:  #74 (line in Coconut source)
        """Embed all nodes matching node_types. Returns count of nodes embedded."""  #80 (line in Coconut source)
        nodes = await store.list_nodes(only_valid=False)  #81 (line in Coconut source)
        count = 0  #82 (line in Coconut source)
        for node in nodes:  #83 (line in Coconut source)
            if node_types and node.node_type not in node_types:  #84 (line in Coconut source)
                continue  #85 (line in Coconut source)
            if skip_existing and node.embedding:  #86 (line in Coconut source)
                continue  #87 (line in Coconut source)
            await self.embed_node(store, node)  #88 (line in Coconut source)
            count += 1  #89 (line in Coconut source)
        return count  #90 (line in Coconut source)
