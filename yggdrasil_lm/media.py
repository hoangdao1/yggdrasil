#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xa0b6cea4

# Compiled with Coconut version 3.2.0

"""Helpers for building multimodal image content blocks.

Follows the Anthropic Messages API content-block schema.  The backend layer
automatically converts these to OpenAI ``image_url`` format when needed.

Quickstart::

    from yggdrasil_lm.media import image_from_file, image_from_url, build_query

    # Ask about a local file
    query = build_query("What's in this image?", image_from_file("photo.jpg"))
    ctx = await app.run(agent, query)

    # Visual RAG — attach an image as context to an agent
    img_ctx = await app.add_image_context("Product photo", url="https://example.com/img.jpg")
    await app.connect_context(agent, img_ctx)
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



import base64  #19 (line in Coconut source)
import mimetypes  #20 (line in Coconut source)
from pathlib import Path  #21 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #22 (line in Coconut source)
    from typing import Any  #22 (line in Coconut source)
else:  #22 (line in Coconut source)
    try:  #22 (line in Coconut source)
        Any = _coconut.typing.Any  #22 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #22 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #22 (line in Coconut source)

# Re-export the canonical QueryContent type so callers only need one import.
from yggdrasil_lm.core.executor import QueryContent  #25 (line in Coconut source)

ImageBlock = dict[str, Any]  #27 (line in Coconut source)

_SUFFIX_TO_MEDIA_TYPE: dict[str, str] = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}  #29 (line in Coconut source)


def image_from_file(path: str | Path, *, media_type: str | None=None) -> ImageBlock:  #38 (line in Coconut source)
    """Build an Anthropic-format image block from a local file (base64-encoded).

    Args:
        path:       Path to the image file.
        media_type: MIME type such as ``"image/png"``.  Auto-detected from the
                    file extension when omitted.

    Returns:
        An Anthropic content block dict::

            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
    """  #50 (line in Coconut source)
    path = Path(path)  #51 (line in Coconut source)
    if media_type is None:  #52 (line in Coconut source)
        media_type = _SUFFIX_TO_MEDIA_TYPE.get(path.suffix.lower())  #53 (line in Coconut source)
        if media_type is None:  #54 (line in Coconut source)
            guessed, _ = mimetypes.guess_type(str(path))  #55 (line in Coconut source)
            media_type = guessed or "image/jpeg"  #56 (line in Coconut source)
    data = ((base64.standard_b64encode)(path.read_bytes())).decode()  #57 (line in Coconut source)
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}  #58 (line in Coconut source)



def image_from_url(url: str) -> ImageBlock:  #64 (line in Coconut source)
    """Build an Anthropic-format image block from a publicly accessible URL.

    Args:
        url: A ``https://`` URL pointing to the image.

    Returns:
        An Anthropic content block dict::

            {"type": "image", "source": {"type": "url", "url": "..."}}
    """  #74 (line in Coconut source)
    return {"type": "image", "source": {"type": "url", "url": url}}  #75 (line in Coconut source)



def image_from_base64(data: str, media_type: str="image/jpeg") -> ImageBlock:  #78 (line in Coconut source)
    """Build an Anthropic-format image block from a pre-encoded base64 string.

    Args:
        data:       Base64-encoded image bytes (no ``data:`` prefix).
        media_type: MIME type, e.g. ``"image/png"``.

    Returns:
        An Anthropic content block dict.
    """  #87 (line in Coconut source)
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}  #88 (line in Coconut source)



def build_query(text: str, *images: ImageBlock) -> QueryContent:  #94 (line in Coconut source)
    """Combine a text prompt with one or more image blocks into a ``QueryContent`` list.

    The text block is placed first so the question appears before the images,
    matching the natural reading order most models are trained on.

    Args:
        text:   The user's question or instruction.
        *images: One or more image blocks created by ``image_from_file``,
                 ``image_from_url``, or ``image_from_base64``.

    Returns:
        A plain ``str`` if no images are provided, otherwise a
        ``list[dict]`` of content blocks::

            [{"type": "text", "text": "..."}, {"type": "image", ...}, ...]

    Example::

        query = build_query(
            "Compare these two diagrams.",
            image_from_file("before.png"),
            image_from_file("after.png"),
        )
        ctx = await app.run(agent, query)
    """  #119 (line in Coconut source)
    if not images:  #120 (line in Coconut source)
        return text  #121 (line in Coconut source)
    blocks: list[dict[str, Any]] = [{"type": "text", "text": text},]  #122 (line in Coconut source)
    blocks.extend(images)  #123 (line in Coconut source)
    return blocks  #124 (line in Coconut source)



__all__ = ["ImageBlock", "QueryContent", "image_from_file", "image_from_url", "image_from_base64", "build_query"]  #127 (line in Coconut source)
