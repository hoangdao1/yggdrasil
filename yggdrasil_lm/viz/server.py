#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x78afc42f

# Compiled with Coconut version 3.2.0

"""FastAPI + WebSocket server for the Yggdrasil browser trace visualizer.

Architecture:
- One FastAPI app, one WebSocket endpoint (/ws), one static HTML route (/)
- TraceEvents are pushed as JSON via WebSocket as they are emitted
- serve_trace() serializes ExecutionContext.trace and streams it post-run
- All state is scoped to a single VizServer instance (no global state)

Dependency: pip install 'yggdrasil[viz]'
"""

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
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
_coconut_cached__coconut__ = _coconut_sys.modules.get('_coconut_cached__coconut__', _coconut_sys.modules.get('__coconut__'))

import functools as _coconut_functools
_coconut_getattr = getattr
def _coconut_wraps(base_func):
    def wrap(new_func):
        new_func_module = _coconut_getattr(new_func, "__module__")
        _coconut_functools.update_wrapper(new_func, base_func)
        if new_func_module is not None:
            new_func.__module__ = new_func_module
        return new_func
    return wrap
from builtins import chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, repr
py_bytes, py_chr, py_dict, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_super, py_zip, py_filter, py_reversed, py_enumerate, py_repr, py_min, py_max = bytes, chr, dict, hex, input, int, map, object, oct, open, print, range, str, super, zip, filter, reversed, enumerate, repr, min, max
_coconut_py_str, _coconut_py_super, _coconut_py_dict, _coconut_py_min, _coconut_py_max = str, super, dict, min, max
exec("_coconut_exec = exec")
py_breakpoint = breakpoint
class _coconut_missing_module:
    __slots__ = ("_import_err",)
    def __init__(self, error):
        self._import_err = error
    def __getattr__(self, name):
        raise self._import_err
@_coconut_wraps(_coconut_py_super)
def _coconut_super(type=None, object_or_type=None):
    if type is None:
        if object_or_type is not None:
            raise _coconut.TypeError("invalid use of super()")
        frame = _coconut_sys._getframe(1)
        try:
            cls = frame.f_locals["__class__"]
        except _coconut.AttributeError:
            raise _coconut.RuntimeError("super(): __class__ cell not found") from None
        self = frame.f_locals[frame.f_code.co_varnames[0]]
        return _coconut_py_super(cls, self)
    return _coconut_py_super(type, object_or_type)
super = py_super
class _coconut:
    import collections, copy, functools, types, itertools, operator, threading, os, warnings, contextlib, traceback, weakref, multiprocessing, inspect
    from multiprocessing import dummy as multiprocessing_dummy
    import copyreg
    import asyncio
    asyncio_Return = StopIteration
    try:
        import async_generator
    except ImportError as async_generator_import_err:
        async_generator = _coconut_missing_module(async_generator_import_err)
    try:
        import tstr
    except ImportError as tstr_import_err:
        tstr = _coconut_missing_module(tstr_import_err)
    import pickle
    OrderedDict = collections.OrderedDict
    import collections.abc as abc
    typing = types.ModuleType(_coconut_py_str("typing"))
    try:
        import typing_extensions
    except ImportError:
        typing_extensions = None
    else:
        for _name in dir(typing_extensions):
            if not _name.startswith("__"):
                setattr(typing, _name, getattr(typing_extensions, _name))
    typing.__doc__ = "Coconut version of typing that makes use of typing.typing_extensions when possible.\n\n" + (getattr(typing, "__doc__") or "The typing module is not available at runtime in Python 3.4 or earlier; try hiding your typedefs behind an 'if TYPE_CHECKING:' block.")
    import typing as _typing
    for _name in dir(_typing):
        if not hasattr(typing, _name):
            setattr(typing, _name, getattr(_typing, _name))

    def _typing_getattr(name):
        raise _coconut.AttributeError("typing.%s is not available on the current Python version and couldn't be looked up in typing_extensions; try hiding your typedefs behind an 'if TYPE_CHECKING:' block" % (name,))
    typing.__getattr__ = _typing_getattr
    _typing_getattr = staticmethod(_typing_getattr)
    zip_longest = itertools.zip_longest
    try:
        import numpy
    except ImportError as numpy_import_err:
        numpy = _coconut_missing_module(numpy_import_err)
    else:
        abc.Sequence.register(numpy.ndarray)
    numpy_modules = ('numpy', 'torch', 'jaxlib', 'pandas', 'xarray')
    xarray_modules = ('xarray',)
    pandas_modules = ('pandas',)
    jax_numpy_modules = ('jaxlib',)
    tee_type = type(itertools.tee((), 1)[0])
    reiterables = abc.Sequence, abc.Mapping, abc.Set
    fmappables = list, tuple, dict, set, frozenset, bytes, bytearray
    abc.Sequence.register(collections.deque)
    Ellipsis, NotImplemented, NotImplementedError, Exception, AttributeError, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, RuntimeError, all, any, bool, bytes, callable, chr, classmethod, complex, dict, enumerate, filter, float, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, locals, globals, map, min, max, next, object, ord, property, range, reversed, set, setattr, slice, str, sum, super, tuple, type, vars, zip, repr, print = Ellipsis, NotImplemented, NotImplementedError, Exception, AttributeError, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, RuntimeError, all, any, bool, bytes, callable, chr, classmethod, complex, dict, enumerate, filter, float, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, locals, globals, map, min, max, next, object, ord, property, range, reversed, set, setattr, slice, str, sum, super, tuple, type, vars, zip, repr, print
@_coconut_wraps(_coconut.functools.partial)
def _coconut_partial(_coconut_func, *args, **kwargs):
    partial_func = _coconut.functools.partial(_coconut_func, *args, **kwargs)
    partial_func.__name__ = _coconut.getattr(_coconut_func, "__name__", None)
    return partial_func
def _coconut_handle_cls_kwargs(**kwargs):
    """Some code taken from six under the terms of its MIT license."""
    metaclass = kwargs.pop("metaclass", None)
    if kwargs and metaclass is None:
        raise _coconut.TypeError("unexpected keyword argument(s) in class definition: %r" % (kwargs,))
    def coconut_handle_cls_kwargs_wrapper(cls):
        if metaclass is None:
            return cls
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get("__slots__")
        if slots is not None:
            if _coconut.isinstance(slots, _coconut.str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop("__dict__", None)
        orig_vars.pop("__weakref__", None)
        if _coconut.hasattr(cls, "__qualname__"):
            orig_vars["__qualname__"] = cls.__qualname__
        return metaclass(cls.__name__, cls.__bases__, orig_vars, **kwargs)
    return coconut_handle_cls_kwargs_wrapper
def _coconut_handle_cls_stargs(*args):
    temp_names = ["_coconut_base_cls_%s" % (i,) for i in _coconut.range(_coconut.len(args))]
    ns = _coconut_py_dict(_coconut.zip(temp_names, args))
    _coconut_exec("class _coconut_cls_stargs_base(" + ", ".join(temp_names) + "): pass", ns)
    return ns["_coconut_cls_stargs_base"]
class _coconut_baseclass:
    __slots__ = ("__weakref__",)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.__reduce__() == other.__reduce__()
    def __hash__(self):
        return _coconut.hash(self.__reduce__())
    def __setstate__(self, setvars):
        for k, v in setvars.items():
            _coconut.setattr(self, k, v)
    def __iter_getitem__(self, index):
        getitem = _coconut.getattr(self, "__getitem__", None)
        if getitem is None:
            raise _coconut.NotImplementedError
        return getitem(index)
class _coconut_base_callable(_coconut_baseclass):
    __slots__ = ()
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return _coconut.types.MethodType(self, obj)
class _coconut_Sentinel(_coconut_baseclass):
    __slots__ = ()
    def __reduce__(self):
        return (self.__class__, ())
_coconut_sentinel = _coconut_Sentinel()
def _coconut_get_base_module(obj):
    return obj.__class__.__module__.split(".", 1)[0]
def _coconut_xarray_to_pandas(obj):
    import xarray
    if isinstance(obj, xarray.Dataset):
        return obj.to_dataframe()
    elif isinstance(obj, xarray.DataArray):
        return obj.to_series()
    else:
        return obj.to_pandas()
def _coconut_xarray_to_numpy(obj):
    import xarray
    if isinstance(obj, xarray.Dataset):
        return obj.to_dataframe().to_numpy()
    else:
        return obj.to_numpy()
class CoconutWarning(Warning):
    """Exception class used for all Coconut warnings."""
    __slots__ = ()
_coconut_CoconutWarning = CoconutWarning
class MatchError(_coconut_baseclass, Exception):
    """Pattern-matching error. Has attributes .pattern, .value, and .message."""
    max_val_repr_len = 500
    def __init__(self, pattern=None, value=None):
        self.pattern = pattern
        self.value = value
        self._message = None
    @property
    def message(self):
        if self._message is None:
            val_repr = _coconut.repr(self.value)
            self._message = "pattern-matching failed for %s in %s" % (_coconut.repr(self.pattern), val_repr if _coconut.len(val_repr) <= self.max_val_repr_len else val_repr[:self.max_val_repr_len] + "...")
            Exception.__init__(self, self._message)
        return self._message
    def __repr__(self):
        self.message
        return Exception.__repr__(self)
    def __str__(self):
        self.message
        return Exception.__str__(self)
    def __unicode__(self):
        self.message
        return Exception.__unicode__(self)
    def __reduce__(self):
        return (self.__class__, (self.pattern, self.value), {"_message": self._message})
    def __setstate__(self, state):
        _coconut_baseclass.__setstate__(self, state)
        if self._message is not None:
            Exception.__init__(self, self._message)
_coconut_cached_MatchError = None if _coconut_cached__coconut__ is None else getattr(_coconut_cached__coconut__, "MatchError", None)
if _coconut_cached_MatchError is not None:
    for _coconut_varname in dir(MatchError):
        try:
            setattr(_coconut_cached_MatchError, _coconut_varname, getattr(MatchError, _coconut_varname))
        except (AttributeError, TypeError):
            pass
    MatchError = _coconut_cached_MatchError
class _coconut_tail_call(_coconut_baseclass):
    __slots__ = ("func", "args", "kwargs")
    def __init__(self, _coconut_func, *args, **kwargs):
        self.func = _coconut_func
        self.args = args
        self.kwargs = kwargs
    def __reduce__(self):
        return (self.__class__, (self.func, self.args, self.kwargs))
_coconut_tco_func_dict = _coconut.weakref.WeakValueDictionary()
def _coconut_tco(func):
    @_coconut_wraps(func)
    def tail_call_optimized_func(*args, **kwargs):
        call_func = func
        while True:
            if _coconut.isinstance(call_func, _coconut_base_pattern_func):
                call_func = call_func._coconut_tco_func
            elif _coconut.isinstance(call_func, _coconut.types.MethodType):
                wkref_func = _coconut_tco_func_dict.get(_coconut.id(call_func.__func__))
                if wkref_func is call_func.__func__:
                    if call_func.__self__ is None:
                        call_func = call_func._coconut_tco_func
                    else:
                        call_func = _coconut_partial(call_func._coconut_tco_func, call_func.__self__)
            else:
                wkref_func = _coconut_tco_func_dict.get(_coconut.id(call_func))
                if wkref_func is call_func:
                    call_func = call_func._coconut_tco_func
            result = call_func(*args, **kwargs)  # use 'coconut --no-tco' to clean up your traceback
            if not isinstance(result, _coconut_tail_call):
                return result
            call_func, args, kwargs = result.func, result.args, result.kwargs
    tail_call_optimized_func._coconut_tco_func = func
    tail_call_optimized_func.__module__ = _coconut.getattr(func, "__module__", None)
    tail_call_optimized_func.__name__ = _coconut.getattr(func, "__name__", None)
    tail_call_optimized_func.__qualname__ = _coconut.getattr(func, "__qualname__", None)
    _coconut_tco_func_dict[_coconut.id(tail_call_optimized_func)] = tail_call_optimized_func
    return tail_call_optimized_func
@_coconut_wraps(_coconut.itertools.tee)
def tee(iterable, n=2):
    if n < 0:
        raise _coconut.ValueError("tee: n cannot be negative")
    elif n == 0:
        return ()
    elif n == 1:
        return (iterable,)
    elif _coconut.isinstance(iterable, _coconut.reiterables):
        return (iterable,) * n
    else:
        if _coconut.getattr(iterable, "__getitem__", None) is not None or _coconut.isinstance(iterable, (_coconut.tee_type, _coconut.abc.Sized, _coconut.abc.Container)):
            existing_copies = [iterable]
            while _coconut.len(existing_copies) < n:
                try:
                    copy = _coconut.copy.copy(iterable)
                except _coconut.TypeError:
                    break
                else:
                    existing_copies.append(copy)
            else:
                return _coconut.tuple(existing_copies)
        return _coconut.itertools.tee(iterable, n)
class _coconut_has_iter(_coconut_baseclass):
    __slots__ = ("iter",)
    def __new__(cls, iterable):
        self = _coconut.super(_coconut_has_iter, cls).__new__(cls)
        self.iter = iterable
        return self
    def get_new_iter(self):
        """Tee the underlying iterator."""
        self.iter = _coconut_reiterable(self.iter)
        return self.iter
    def __fmap__(self, func):
        return _coconut_map(func, self)
class reiterable(_coconut_has_iter):
    """Allow an iterator to be iterated over multiple times with the same results."""
    __slots__ = ()
    def __new__(cls, iterable):
        if _coconut.isinstance(iterable, _coconut.reiterables):
            return iterable
        return _coconut.super(_coconut_reiterable, cls).__new__(cls, iterable)
    def get_new_iter(self):
        """Tee the underlying iterator."""
        self.iter, new_iter = _coconut_tee(self.iter)
        return new_iter
    def __iter__(self):
        return _coconut.iter(self.get_new_iter())
    def __repr__(self):
        return "reiterable(%s)" % (_coconut.repr(self.get_new_iter()),)
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(self.get_new_iter())
    def __getitem__(self, index):
        return _coconut_iter_getitem(self.get_new_iter(), index)
    def __reversed__(self):
        return _coconut_reversed(self.get_new_iter())
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.get_new_iter())
    def __contains__(self, elem):
        return elem in self.get_new_iter()
    def count(self, elem):
        """Count the number of times elem appears in the iterable."""
        return self.get_new_iter().count(elem)
    def index(self, elem):
        """Find the index of elem in the iterable."""
        return self.get_new_iter().index(elem)
_coconut.reiterables = (reiterable,) + _coconut.reiterables
def _coconut_iter_getitem_special_case(iterable, start, stop, step):
    iterable = _coconut.itertools.islice(iterable, start, None)
    cache = _coconut.collections.deque(_coconut.itertools.islice(iterable, -stop), maxlen=-stop)
    for index, item in _coconut.enumerate(iterable):
        cached_item = cache.popleft()
        if index % step == 0:
            yield cached_item
        cache.append(item)
def _coconut_iter_getitem(iterable, index):
    """Iterator slicing works just like sequence slicing, including support for negative indices and slices, and support for `slice` objects in the same way as can be done with normal slicing.

    Coconut's iterator slicing is very similar to Python's `itertools.islice`, but unlike `itertools.islice`, Coconut's iterator slicing supports negative indices, and will preferentially call an object's `__iter_getitem__` (always used if available) or `__getitem__` (only used if the object is a collections.abc.Sequence). Coconut's iterator slicing is also optimized to work well with all of Coconut's built-in objects, only computing the elements of each that are actually necessary to extract the desired slice.

    Some code taken from more_itertools under the terms of its MIT license.
    """
    obj_iter_getitem = _coconut.getattr(iterable, "__iter_getitem__", None)
    if obj_iter_getitem is None and _coconut.isinstance(iterable, _coconut.abc.Sequence):
        obj_iter_getitem = _coconut.getattr(iterable, "__getitem__", None)
    if obj_iter_getitem is not None:
        try:
            result = obj_iter_getitem(index)
        except _coconut.NotImplementedError:
            pass
        else:
            return result
    if not _coconut.isinstance(index, _coconut.slice):
        index = _coconut.operator.index(index)
        if index < 0:
            return _coconut.collections.deque(iterable, maxlen=-index)[0]
        result = _coconut.next(_coconut.itertools.islice(iterable, index, index + 1), _coconut_sentinel)
        if result is _coconut_sentinel:
            raise _coconut.IndexError(".$[] index out of range")
        return result
    start = _coconut.operator.index(index.start) if index.start is not None else None
    stop = _coconut.operator.index(index.stop) if index.stop is not None else None
    step = _coconut.operator.index(index.step) if index.step is not None else 1
    if step == 0:
        raise _coconut.ValueError("slice step cannot be zero")
    if start is None and stop is None and step == -1:
        obj_reversed = _coconut.getattr(iterable, "__reversed__", None)
        if obj_reversed is not None:
            try:
                result = obj_reversed()
            except _coconut.NotImplementedError:
                pass
            else:
                if result is not _coconut.NotImplemented:
                    return result
    if step >= 0:
        start = 0 if start is None else start
        if start < 0:
            cache = _coconut.collections.deque(_coconut.enumerate(iterable, 1), maxlen=-start)
            len_iter = cache[-1][0] if cache else 0
            i = _coconut.max(len_iter + start, 0)
            if stop is None:
                j = len_iter
            elif stop >= 0:
                j = _coconut.min(stop, len_iter)
            else:
                j = _coconut.max(len_iter + stop, 0)
            n = j - i
            if n <= 0:
                return ()
            if n < -start or step != 1:
                cache = _coconut.itertools.islice(cache, 0, n, step)
            return _coconut_map(_coconut.operator.itemgetter(1), cache)
        elif stop is None or stop >= 0:
            return _coconut.itertools.islice(iterable, start, stop, step)
        else:
            return _coconut_iter_getitem_special_case(iterable, start, stop, step)
    else:
        start = -1 if start is None else start
        if stop is not None and stop < 0:
            n = -stop - 1
            cache = _coconut.collections.deque(_coconut.enumerate(iterable, 1), maxlen=n)
            len_iter = cache[-1][0] if cache else 0
            if start < 0:
                i, j = start, stop
            else:
                i, j = _coconut.min(start - len_iter, -1), None
            return _coconut_map(_coconut.operator.itemgetter(1), _coconut.tuple(cache)[i:j:step])
        else:
            if stop is not None:
                m = stop + 1
                iterable = _coconut.itertools.islice(iterable, m, None)
            if start < 0:
                i = start
                n = None
            elif stop is None:
                i = None
                n = start + 1
            else:
                i = None
                n = start - stop
            if n is not None:
                if n <= 0:
                    return ()
                iterable = _coconut.itertools.islice(iterable, 0, n)
            return _coconut.tuple(iterable)[i::step]
class _coconut_attritemgetter(_coconut_base_callable):
    __slots__ = ("attr", "is_iter_and_items")
    def __init__(self, attr, *is_iter_and_items):
        self.attr = attr
        self.is_iter_and_items = is_iter_and_items
    def __call__(self, obj):
        out = obj
        if self.attr is not None:
            out = _coconut.getattr(out, self.attr)
        for is_iter, item in self.is_iter_and_items:
            if is_iter:
                out = _coconut_iter_getitem(out, item)
            else:
                out = out[item]
        return out
    def __repr__(self):
        return "." + (self.attr or "") + "".join(("$" if is_iter else "") + "[" + _coconut.repr(item) + "]" for is_iter, item in self.is_iter_and_items)
    def __reduce__(self):
        return (self.__class__, (self.attr,) + self.is_iter_and_items)
class _coconut_compostion_baseclass(_coconut_base_callable):
    def __init__(self, func, *func_infos):
        try:
            _coconut.functools.update_wrapper(self, func)
        except _coconut.AttributeError:
            pass
        if _coconut.isinstance(func, self.__class__):
            self._coconut_func = func._coconut_func
            func_infos = func._coconut_func_infos + func_infos
        else:
            self._coconut_func = func
        self._coconut_func_infos = []
        for f_info in func_infos:
            f = f_info[0]
            if _coconut.isinstance(f, self.__class__):
                self._coconut_func_infos.append((f._coconut_func,) + f_info[1:])
                self._coconut_func_infos += f._coconut_func_infos
            else:
                self._coconut_func_infos.append(f_info)
        self._coconut_func_infos = _coconut.tuple(self._coconut_func_infos)
    def __reduce__(self):
        return (self.__class__, (self._coconut_func,) + self._coconut_func_infos)
class _coconut_base_compose(_coconut_compostion_baseclass):
    __slots__ = ()
    def __call__(self, *args, **kwargs):
        arg = self._coconut_func(*args, **kwargs)
        for f, stars, none_aware in self._coconut_func_infos:
            if none_aware and arg is None:
                return arg
            if stars == 0:
                arg = f(arg)
            elif stars == 1:
                arg = f(*arg)
            elif stars == 2:
                arg = f(**arg)
            else:
                raise _coconut.RuntimeError("invalid internal stars value " + _coconut.repr(stars) + " in " + _coconut.repr(self) + " (you should report this at https://github.com/evhub/coconut/issues/new)")
        return arg
    def __repr__(self):
        return _coconut.repr(self._coconut_func) + " " + " ".join(".." + "?"*none_aware + "*"*stars + "> " + _coconut.repr(f) for f, stars, none_aware in self._coconut_func_infos)
class _coconut_async_compose(_coconut_compostion_baseclass):
    __slots__ = ()
    async def __call__(self, *args, **kwargs):
        arg = await self._coconut_func(*args, **kwargs)
        for f, await_f in self._coconut_func_infos:
            arg = f(arg)
            if await_f:
                arg = await arg
        return arg
    def __repr__(self):
        return _coconut.repr(self._coconut_func) + " " + " ".join("`and_then" + "_await"*await_f + "` " + _coconut.repr(f) for f, await_f in self._coconut_func_infos)
def and_then(first_async_func, second_func):
    """Compose an async function with a normal function.

    Effectively equivalent to:
        def and_then[**T, U, V](
            first_async_func: async (**T) -> U,
            second_func: U -> V,
        ) -> async (**T) -> V =
            async def (*args, **kwargs) => (
                first_async_func(*args, **kwargs)
                |> await
                |> second_func
            )
    """
    return _coconut_async_compose(first_async_func, (second_func, False))
def and_then_await(first_async_func, second_async_func):
    """Compose two async functions.

    Effectively equivalent to:
        def and_then_await[**T, U, V](
            first_async_func: async (**T) -> U,
            second_async_func: async U -> V,
        ) -> async (**T) -> V =
            async def (*args, **kwargs) => (
                first_async_func(*args, **kwargs)
                |> await
                |> second_async_func
                |> await
            )
    """
    return _coconut_async_compose(first_async_func, (second_async_func, True))
def _coconut_forward_compose(func, *funcs):
    """Forward composition operator (..>).

    (..>)(f, g) is effectively equivalent to (*args, **kwargs) => g(f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 0, False) for f in funcs))
def _coconut_back_compose(*funcs):
    """Backward composition operator (<..).

    (<..)(f, g) is effectively equivalent to (*args, **kwargs) => f(g(*args, **kwargs))."""
    return _coconut_forward_compose(*_coconut.reversed(funcs))
def _coconut_forward_none_compose(func, *funcs):
    """Forward none-aware composition operator (..?>).

    (..?>)(f, g) is effectively equivalent to (*args, **kwargs) => g?(f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 0, True) for f in funcs))
def _coconut_back_none_compose(*funcs):
    """Backward none-aware composition operator (<..?).

    (<..?)(f, g) is effectively equivalent to (*args, **kwargs) => f?(g(*args, **kwargs))."""
    return _coconut_forward_none_compose(*_coconut.reversed(funcs))
def _coconut_forward_star_compose(func, *funcs):
    """Forward star composition operator (..*>).

    (..*>)(f, g) is effectively equivalent to (*args, **kwargs) => g(*f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 1, False) for f in funcs))
def _coconut_back_star_compose(*funcs):
    """Backward star composition operator (<*..).

    (<*..)(f, g) is effectively equivalent to (*args, **kwargs) => f(*g(*args, **kwargs))."""
    return _coconut_forward_star_compose(*_coconut.reversed(funcs))
def _coconut_forward_none_star_compose(func, *funcs):
    """Forward none-aware star composition operator (..?*>).

    (..?*>)(f, g) is effectively equivalent to (*args, **kwargs) => g?(*f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 1, True) for f in funcs))
def _coconut_back_none_star_compose(*funcs):
    """Backward none-aware star composition operator (<*?..).

    (<*?..)(f, g) is effectively equivalent to (*args, **kwargs) => f?(*g(*args, **kwargs))."""
    return _coconut_forward_none_star_compose(*_coconut.reversed(funcs))
def _coconut_forward_dubstar_compose(func, *funcs):
    """Forward double star composition operator (..**>).

    (..**>)(f, g) is effectively equivalent to (*args, **kwargs) => g(**f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 2, False) for f in funcs))
def _coconut_back_dubstar_compose(*funcs):
    """Backward double star composition operator (<**..).

    (<**..)(f, g) is effectively equivalent to (*args, **kwargs) => f(**g(*args, **kwargs))."""
    return _coconut_forward_dubstar_compose(*_coconut.reversed(funcs))
def _coconut_forward_none_dubstar_compose(func, *funcs):
    """Forward none-aware double star composition operator (..?**>).

    (..?**>)(f, g) is effectively equivalent to (*args, **kwargs) => g?(**f(*args, **kwargs))."""
    return _coconut_base_compose(func, *((f, 2, True) for f in funcs))
def _coconut_back_none_dubstar_compose(*funcs):
    """Backward none-aware double star composition operator (<**?..).

    (<**?..)(f, g) is effectively equivalent to (*args, **kwargs) => f?(**g(*args, **kwargs))."""
    return _coconut_forward_none_dubstar_compose(*_coconut.reversed(funcs))
def _coconut_pipe(x, f):
    """Pipe operator (|>). Equivalent to (x, f) => f(x)."""
    return f(x)
def _coconut_star_pipe(xs, f):
    """Star pipe operator (*|>). Equivalent to (xs, f) => f(*xs)."""
    return f(*xs)
def _coconut_dubstar_pipe(kws, f):
    """Double star pipe operator (**|>). Equivalent to (kws, f) => f(**kws)."""
    return f(**kws)
def _coconut_back_pipe(f, x):
    """Backward pipe operator (<|). Equivalent to (f, x) => f(x)."""
    return f(x)
def _coconut_back_star_pipe(f, xs):
    """Backward star pipe operator (<*|). Equivalent to (f, xs) => f(*xs)."""
    return f(*xs)
def _coconut_back_dubstar_pipe(f, kws):
    """Backward double star pipe operator (<**|). Equivalent to (f, kws) => f(**kws)."""
    return f(**kws)
def _coconut_none_pipe(x, f):
    """Nullable pipe operator (|?>). Equivalent to (x, f) => f(x) if x is not None else None."""
    return None if x is None else f(x)
def _coconut_none_star_pipe(xs, f):
    """Nullable star pipe operator (|?*>). Equivalent to (xs, f) => f(*xs) if xs is not None else None."""
    return None if xs is None else f(*xs)
def _coconut_none_dubstar_pipe(kws, f):
    """Nullable double star pipe operator (|?**>). Equivalent to (kws, f) => f(**kws) if kws is not None else None."""
    return None if kws is None else f(**kws)
def _coconut_back_none_pipe(f, x):
    """Nullable backward pipe operator (<?|). Equivalent to (f, x) => f(x) if x is not None else None."""
    return None if x is None else f(x)
def _coconut_back_none_star_pipe(f, xs):
    """Nullable backward star pipe operator (<*?|). Equivalent to (f, xs) => f(*xs) if xs is not None else None."""
    return None if xs is None else f(*xs)
def _coconut_back_none_dubstar_pipe(f, kws):
    """Nullable backward double star pipe operator (<**?|). Equivalent to (kws, f) => f(**kws) if kws is not None else None."""
    return None if kws is None else f(**kws)
def _coconut_assert(cond, msg=None):
    """Assert operator (assert). Asserts condition with optional message."""
    if not cond:
        assert False, msg if msg is not None else "(assert) got falsey value " + _coconut.repr(cond)
def _coconut_raise(exc=None, from_exc=None):
    """Raise operator (raise). Raises exception with optional cause."""
    if exc is None:
        raise
    if from_exc is not None:
        exc.__cause__ = from_exc
    raise exc
def _coconut_bool_and(a, b):
    """Boolean and operator (and). Equivalent to (a, b) => a and b."""
    return a and b
def _coconut_bool_or(a, b):
    """Boolean or operator (or). Equivalent to (a, b) => a or b."""
    return a or b
def _coconut_in(a, b):
    """Containment operator (in). Equivalent to (a, b) => a in b."""
    return a in b
def _coconut_not_in(a, b):
    """Negative containment operator (not in). Equivalent to (a, b) => a not in b."""
    return a not in b
def _coconut_none_coalesce(a, b):
    """None coalescing operator (??). Equivalent to (a, b) => a if a is not None else b."""
    return b if a is None else a
def _coconut_minus(a, b=_coconut_sentinel):
    """Minus operator (-). Effectively equivalent to (a, b=None) => a - b if b is not None else -a."""
    if b is _coconut_sentinel:
        return -a
    return a - b
def _coconut_comma_op(*args):
    """Comma operator (,). Equivalent to (*args) => args."""
    return args
def _coconut_if_op(cond, if_true, if_false):
    """If operator (if). Equivalent to (cond, if_true, if_false) => if_true if cond else if_false."""
    return if_true if cond else if_false
_coconut_matmul = _coconut.operator.matmul
class scan(_coconut_has_iter):
    """Reduce func over iterable, yielding intermediate results,
    optionally starting from initial."""
    __slots__ = ("func", "initial")
    def __new__(cls, function, iterable, initial=_coconut_sentinel):
        self = _coconut.super(_coconut_scan, cls).__new__(cls, iterable)
        self.func = function
        self.initial = initial
        return self
    def __repr__(self):
        return "scan(%r, %s%s)" % (self.func, _coconut.repr(self.iter), "" if self.initial is _coconut_sentinel else ", " + _coconut.repr(self.initial))
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter, self.initial))
    def __copy__(self):
        return self.__class__(self.func, self.get_new_iter(), self.initial)
    def __iter__(self):
        acc = self.initial
        if acc is not _coconut_sentinel:
            yield acc
        for item in self.iter:
            if acc is _coconut_sentinel:
                acc = item
            else:
                acc = self.func(acc, item)
            yield acc
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.iter)
class reversed(_coconut_has_iter):
    __slots__ = ()
    __doc__ = getattr(_coconut.reversed, "__doc__", "<see help(py_reversed)>")
    def __new__(cls, iterable):
        if _coconut.isinstance(iterable, _coconut.range):
            return iterable[::-1]
        if _coconut.getattr(iterable, "__reversed__", None) is None or _coconut.isinstance(iterable, (_coconut.list, _coconut.tuple)):
            return _coconut.super(_coconut_reversed, cls).__new__(cls, iterable)
        return _coconut.reversed(iterable)
    def __repr__(self):
        return "reversed(%s)" % (_coconut.repr(self.iter),)
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(self.get_new_iter())
    def __iter__(self):
        return _coconut.iter(_coconut.reversed(self.iter))
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return _coconut_iter_getitem(self.iter, _coconut.slice(-(index.start + 1) if index.start is not None else None, -(index.stop + 1) if index.stop else None, -(index.step if index.step is not None else 1)))
        return _coconut_iter_getitem(self.iter, -(index + 1))
    def __reversed__(self):
        return self.iter
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.iter)
    def __contains__(self, elem):
        return elem in self.iter
    def count(self, elem):
        """Count the number of times elem appears in the reversed iterable."""
        return self.iter.count(elem)
    def index(self, elem):
        """Find the index of elem in the reversed iterable."""
        return _coconut.len(self.iter) - self.iter.index(elem) - 1
    def __fmap__(self, func):
        return self.__class__(_coconut_map(func, self.iter))
class flatten(_coconut_has_iter):
    """Flatten an iterable of iterables into a single iterable.
    Only flattens the top level of the iterable."""
    __slots__ = ("levels", "_made_reit")
    def __new__(cls, iterable, levels=1):
        if levels is not None:
            levels = _coconut.operator.index(levels)
            if levels < 0:
                raise _coconut.ValueError("flatten: levels cannot be negative")
            if levels == 0:
                return iterable
        self = _coconut.super(_coconut_flatten, cls).__new__(cls, iterable)
        self.levels = levels
        self._made_reit = False
        return self
    def get_new_iter(self):
        """Tee the underlying iterator."""
        if not self._made_reit:
            for i in _coconut.reversed(_coconut.range(0 if self.levels is None else self.levels + 1)):
                mapper = _coconut_reiterable
                for _ in _coconut.range(i):
                    mapper = _coconut.functools.partial(_coconut_map, mapper)
                self.iter = mapper(self.iter)
            self._made_reit = True
        return self.iter
    def __iter__(self):
        if self.levels is None:
            return self._iter_all_levels()
        new_iter = self.iter
        for _ in _coconut.range(self.levels):
            new_iter = _coconut.itertools.chain.from_iterable(new_iter)
        return new_iter
    def _iter_all_levels(self, new=False):
        """Iterate over all levels of the iterable."""
        for item in (self.get_new_iter() if new else self.iter):
            if _coconut.isinstance(item, _coconut.abc.Iterable):
                for subitem in self.__class__(item, None):
                    yield subitem
            else:
                yield item
    def __reversed__(self):
        if self.levels is None:
            return _coconut.reversed(_coconut.tuple(self._iter_all_levels(new=True)))
        reversed_iter = self.get_new_iter()
        for i in _coconut.reversed(_coconut.range(self.levels + 1)):
            reverser = _coconut_reversed
            for _ in _coconut.range(i):
                reverser = _coconut.functools.partial(_coconut_map, reverser)
            reversed_iter = reverser(reversed_iter)
        return self.__class__(reversed_iter, self.levels)
    def __repr__(self):
        return "flatten(" + _coconut.repr(self.iter) + (", " + _coconut.repr(self.levels) if self.levels is not None else "") + ")"
    def __reduce__(self):
        return (self.__class__, (self.iter, self.levels))
    def __copy__(self):
        return self.__class__(self.get_new_iter(), self.levels)
    def __contains__(self, elem):
        if self.levels == 1:
            return _coconut.any(elem in it for it in self.get_new_iter())
        raise _coconut.TypeError("flatten.__contains__ only supported for levels=1")
    def count(self, elem):
        """Count the number of times elem appears in the flattened iterable."""
        if self.levels != 1:
            raise _coconut.ValueError("flatten.count only supported for levels=1")
        return _coconut.sum(it.count(elem) for it in self.get_new_iter())
    def index(self, elem):
        """Find the index of elem in the flattened iterable."""
        if self.levels != 1:
            raise _coconut.ValueError("flatten.index only supported for levels=1")
        ind = 0
        for it in self.get_new_iter():
            try:
                return ind + it.index(elem)
            except _coconut.ValueError:
                ind += _coconut.len(it)
        raise _coconut.ValueError("%r not in %r" % (elem, self))
    def __fmap__(self, func):
        if self.levels == 1:
            return self.__class__(_coconut_map(_coconut_partial(_coconut_map, func), self.get_new_iter()))
        return _coconut_map(func, self)
class cartesian_product(_coconut_baseclass):
    __slots__ = ("iters", "repeat")
    __doc__ = getattr(_coconut.itertools.product, "__doc__", "Cartesian product of input iterables.") + """

Additionally supports Cartesian products of numpy arrays."""
    def __new__(cls, *iterables, **kwargs):
        repeat = _coconut.operator.index(kwargs.pop("repeat", 1))
        if kwargs:
            raise _coconut.TypeError("cartesian_product() got unexpected keyword arguments " + _coconut.repr(kwargs))
        if repeat == 0:
            iterables = ()
            repeat = 1
        if repeat < 0:
            raise _coconut.ValueError("cartesian_product: repeat cannot be negative")
        if iterables:
            it_modules = [_coconut_get_base_module(it) for it in iterables]
            if _coconut.all(mod in _coconut.numpy_modules for mod in it_modules):
                iterables = tuple((it.to_numpy() if mod in _coconut.pandas_modules else _coconut_xarray_to_numpy(it) if mod in _coconut.xarray_modules else it) for it, mod in _coconut.zip(iterables, it_modules))
                if _coconut.any(mod in _coconut.jax_numpy_modules for mod in it_modules):
                    from jax import numpy
                else:
                    numpy = _coconut.numpy
                iterables *= repeat
                dtype = numpy.result_type(*iterables)
                arr = numpy.empty([_coconut.len(a) for a in iterables] + [_coconut.len(iterables)], dtype=dtype)
                for i, a in _coconut.enumerate(numpy.ix_(*iterables)):
                    arr[..., i] = a
                return arr.reshape(-1, _coconut.len(iterables))
        self = _coconut.super(_coconut_cartesian_product, cls).__new__(cls)
        self.iters = iterables
        self.repeat = repeat
        return self
    def __iter__(self):
        return _coconut.itertools.product(*self.iters, repeat=self.repeat)
    def __repr__(self):
        return "cartesian_product(" + ", ".join(_coconut.repr(it) for it in self.iters) + (", repeat=" + _coconut.repr(self.repeat) if self.repeat != 1 else "") + ")"
    def __reduce__(self):
        return (self.__class__, self.iters, {"repeat": self.repeat})
    def __copy__(self):
        self.iters = _coconut.tuple(_coconut_reiterable(it) for it in self.iters)
        return self.__class__(*self.iters, repeat=self.repeat)
    @property
    def all_iters(self):
        return _coconut.itertools.chain.from_iterable(_coconut.itertools.repeat(self.iters, self.repeat))
    def __len__(self):
        total_len = 1
        for it in self.iters:
            if not _coconut.isinstance(it, _coconut.abc.Sized):
                return _coconut.NotImplemented
            total_len *= _coconut.len(it)
        return total_len ** self.repeat
    def __contains__(self, elem):
        for e, it in _coconut.zip_longest(elem, self.all_iters, fillvalue=_coconut_sentinel):
            if e is _coconut_sentinel or it is _coconut_sentinel or e not in it:
                return False
        return True
    def count(self, elem):
        """Count the number of times elem appears in the product."""
        total_count = 1
        for e, it in _coconut.zip_longest(elem, self.all_iters, fillvalue=_coconut_sentinel):
            if e is _coconut_sentinel or it is _coconut_sentinel:
                return 0
            total_count *= it.count(e)
            if not total_count:
                return total_count
        return total_count
    def __fmap__(self, func):
        return _coconut_map(func, self)
class map(_coconut_baseclass, _coconut.map):
    __slots__ = ("func", "iters")
    __doc__ = getattr(_coconut.map, "__doc__", "<see help(py_map)>")
    def __new__(cls, function, *iterables, **kwargs):
        strict = kwargs.pop("strict", False)
        if kwargs:
            raise _coconut.TypeError(cls.__name__ + "() got unexpected keyword arguments " + _coconut.repr(kwargs))
        if strict and _coconut.len(iterables) > 1:
            return _coconut_starmap(function, _coconut_zip(*iterables, strict=True))
        self = _coconut.map.__new__(cls, function, *iterables)
        self.func = function
        self.iters = iterables
        return self
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self.func, *(_coconut_iter_getitem(it, index) for it in self.iters))
        return self.func(*(_coconut_iter_getitem(it, index) for it in self.iters))
    def __reversed__(self):
        return self.__class__(self.func, *(_coconut_reversed(it) for it in self.iters))
    def __len__(self):
        if not _coconut.all(_coconut.isinstance(it, _coconut.abc.Sized) for it in self.iters):
            return _coconut.NotImplemented
        return _coconut.min((_coconut.len(it) for it in self.iters), default=0)
    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.func, ", ".join((_coconut.repr(it) for it in self.iters)))
    def __reduce__(self):
        return (self.__class__, (self.func,) + self.iters)
    def __copy__(self):
        self.iters = _coconut.tuple(_coconut_reiterable(it) for it in self.iters)
        return self.__class__(self.func, *self.iters)
    def __iter__(self):
        return _coconut.map(self.func, *self.iters)
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self.func, func), *self.iters)
class _coconut_parallel_map_func_wrapper(_coconut_baseclass):
    __slots__ = ("map_cls", "func", "star")
    def __init__(self, map_cls, func, star):
        self.map_cls = map_cls
        self.func = func
        self.star = star
    def __reduce__(self):
        return (self.__class__, (self.map_cls, self.func, self.star))
    def __call__(self, *args, **kwargs):
        self.map_cls._get_pool_stack().append(None)
        try:
            if self.star:
                assert _coconut.len(args) == 1, "internal process_map/thread_map error (you should report this at https://github.com/evhub/coconut/issues/new)"
                return self.func(*args[0], **kwargs)
            else:
                return self.func(*args, **kwargs)
        except:
            _coconut.print(self.map_cls.__name__ + " error:")
            _coconut.traceback.print_exc()
            raise
        finally:
            assert self.map_cls._get_pool_stack().pop() is None, "internal process_map/thread_map error (you should report this at https://github.com/evhub/coconut/issues/new)"
class _coconut_base_parallel_map(map):
    __slots__ = ("result", "chunksize", "strict", "stream", "ordered")
    @classmethod
    def _get_pool_stack(cls):
        return cls._threadlocal_ns.__dict__.setdefault("pool_stack", [None])
    def __new__(cls, function, *iterables, **kwargs):
        self = _coconut.super(_coconut_base_parallel_map, cls).__new__(cls, function, *iterables)
        self.result = None
        self.chunksize = kwargs.pop("chunksize", 1)
        self.strict = kwargs.pop("strict", False)
        self.stream = kwargs.pop("stream", False)
        self.ordered = kwargs.pop("ordered", True)
        if kwargs:
            raise _coconut.TypeError(cls.__name__ + "() got unexpected keyword arguments " + _coconut.repr(kwargs))
        if not self.stream and cls._get_pool_stack()[-1] is not None:
            return self.to_tuple()
        return self
    def __reduce__(self):
        return (self.__class__, (self.func,) + self.iters, {"chunksize": self.chunksize, "strict": self.strict, "stream": self.stream, "ordered": self.ordered})
    @classmethod
    @_coconut.contextlib.contextmanager
    def multiple_sequential_calls(cls, max_workers=None):
        """Context manager that causes nested calls to use the same pool."""
        if cls._get_pool_stack()[-1] is None:
            cls._get_pool_stack()[-1] = cls._make_pool(max_workers)
            try:
                yield
            finally:
                cls._get_pool_stack()[-1].terminate()
                cls._get_pool_stack()[-1] = None
        elif max_workers is not None:
            self.map_cls._get_pool_stack().append(cls._make_pool(max_workers))
            try:
                yield
            finally:
                cls._get_pool_stack()[-1].terminate()
                cls._get_pool_stack().pop()
        else:
            yield
    def _execute_map(self):
        map_func = self._get_pool_stack()[-1].imap if self.ordered else self._get_pool_stack()[-1].imap_unordered
        if _coconut.len(self.iters) == 1:
            return map_func(_coconut_parallel_map_func_wrapper(self.__class__, self.func, False), self.iters[0], self.chunksize)
        elif self.strict:
            return map_func(_coconut_parallel_map_func_wrapper(self.__class__, self.func, True), _coconut_zip(*self.iters, strict=True), self.chunksize)
        else:
            return map_func(_coconut_parallel_map_func_wrapper(self.__class__, self.func, True), _coconut.zip(*self.iters), self.chunksize)
    def to_tuple(self):
        """Execute the map operation and return the results as a tuple."""
        if self.result is None:
            with self.multiple_sequential_calls():
                self.result = _coconut.tuple(self._execute_map())
            self.func = _coconut_ident
            self.iters = (self.result,)
        return self.result
    def to_stream(self):
        """Stream the map operation, yielding results one at a time."""
        if self._get_pool_stack()[-1] is None:
            raise _coconut.RuntimeError("cannot stream outside of " + cls.__name__ + ".multiple_sequential_calls context")
        return self._execute_map()
    def __iter__(self):
        if self.stream:
            return self.to_stream()
        else:
            return _coconut.iter(self.to_tuple())
class process_map(_coconut_base_parallel_map):
    """Multi-process implementation of map. Requires arguments to be pickleable.

    For multiple sequential calls, use:
        with process_map.multiple_sequential_calls():
            ...
    """
    __slots__ = ()
    _threadlocal_ns = _coconut.threading.local()
    @staticmethod
    def _make_pool(max_workers=None):
        return _coconut.multiprocessing.Pool(max_workers)
class thread_map(_coconut_base_parallel_map):
    """Multi-thread implementation of map.

    For multiple sequential calls, use:
        with thread_map.multiple_sequential_calls():
            ...
    """
    __slots__ = ()
    _threadlocal_ns = _coconut.threading.local()
    @staticmethod
    def _make_pool(max_workers=None):
        return _coconut.multiprocessing_dummy.Pool(_coconut.multiprocessing.cpu_count() * 5 if max_workers is None else max_workers)
class zip(_coconut_baseclass, _coconut.zip):
    __slots__ = ("iters", "strict")
    __doc__ = getattr(_coconut.zip, "__doc__", "<see help(py_zip)>")
    def __new__(cls, *iterables, **kwargs):
        self = _coconut.zip.__new__(cls, *iterables)
        self.iters = iterables
        self.strict = kwargs.pop("strict", False)
        if kwargs:
            raise _coconut.TypeError(cls.__name__ + "() got unexpected keyword arguments " + _coconut.repr(kwargs))
        return self
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(*(_coconut_iter_getitem(it, index) for it in self.iters), strict=self.strict)
        return _coconut.tuple(_coconut_iter_getitem(it, index) for it in self.iters)
    def __reversed__(self):
        return self.__class__(*(_coconut_reversed(it) for it in self.iters), strict=self.strict)
    def __len__(self):
        if not _coconut.all(_coconut.isinstance(it, _coconut.abc.Sized) for it in self.iters):
            return _coconut.NotImplemented
        return _coconut.min((_coconut.len(it) for it in self.iters), default=0)
    def __repr__(self):
        return "zip(%s%s)" % (", ".join((_coconut.repr(it) for it in self.iters)), ", strict=True" if self.strict else "")
    def __reduce__(self):
        return (self.__class__, self.iters, {"strict": self.strict})
    def __copy__(self):
        self.iters = _coconut.tuple(_coconut_reiterable(it) for it in self.iters)
        return self.__class__(*self.iters, strict=self.strict)
    def __iter__(self):
        for items in _coconut.iter(_coconut.zip(*self.iters, strict=self.strict)):
            yield items
    def __fmap__(self, func):
        return _coconut_map(func, self)
class zip_longest(zip):
    __slots__ = ("fillvalue",)
    __doc__ = getattr(_coconut.zip_longest, "__doc__", "Version of zip that fills in missing values with fillvalue.")
    def __new__(cls, *iterables, **kwargs):
        self = _coconut.super(_coconut_zip_longest, cls).__new__(cls, *iterables, strict=False)
        self.fillvalue = kwargs.pop("fillvalue", None)
        if kwargs:
            raise _coconut.TypeError(cls.__name__ + "() got unexpected keyword arguments " + _coconut.repr(kwargs))
        return self
    def __getitem__(self, index):
        self_len = None
        if _coconut.isinstance(index, _coconut.slice):
            if self_len is None:
                self_len = self.__len__()
                if self_len is _coconut.NotImplemented:
                    return self_len
            new_ind = _coconut.slice(index.start + self_len if index.start is not None and index.start < 0 else index.start, index.stop + self_len if index.stop is not None and index.stop < 0 else index.stop, index.step)
            return self.__class__(*(_coconut_iter_getitem(it, new_ind) for it in self.iters))
        if index < 0:
            if self_len is None:
                self_len = self.__len__()
                if self_len is _coconut.NotImplemented:
                    return self_len
            index += self_len
        result = []
        got_non_default = False
        for it in self.iters:
            try:
                result.append(_coconut_iter_getitem(it, index))
            except _coconut.IndexError:
                result.append(self.fillvalue)
            else:
                got_non_default = True
        if not got_non_default:
            raise _coconut.IndexError("zip_longest index out of range")
        return _coconut.tuple(result)
    def __len__(self):
        if not _coconut.all(_coconut.isinstance(it, _coconut.abc.Sized) for it in self.iters):
            return _coconut.NotImplemented
        return _coconut.max((_coconut.len(it) for it in self.iters), default=0)
    def __repr__(self):
        return "zip_longest(%s, fillvalue=%s)" % (", ".join((_coconut.repr(it) for it in self.iters)), _coconut.repr(self.fillvalue))
    def __reduce__(self):
        return (self.__class__, self.iters, {"fillvalue": self.fillvalue})
    def __copy__(self):
        self.iters = _coconut.tuple(_coconut_reiterable(it) for it in self.iters)
        return self.__class__(*self.iters, fillvalue=self.fillvalue)
    def __iter__(self):
        return _coconut.iter(_coconut.zip_longest(*self.iters, fillvalue=self.fillvalue))
class filter(_coconut_baseclass, _coconut.filter):
    __slots__ = ("func", "iter")
    __doc__ = getattr(_coconut.filter, "__doc__", "<see help(py_filter)>")
    def __new__(cls, function, iterable):
        self = _coconut.filter.__new__(cls, function, iterable)
        self.func = function
        self.iter = iterable
        return self
    def __reversed__(self):
        return self.__class__(self.func, _coconut_reversed(self.iter))
    def __repr__(self):
        return "filter(%r, %s)" % (self.func, _coconut.repr(self.iter))
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __copy__(self):
        self.iter = _coconut_reiterable(self.iter)
        return self.__class__(self.func, self.iter)
    def __iter__(self):
        return _coconut.iter(_coconut.filter(self.func, self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class enumerate(_coconut_baseclass, _coconut.enumerate):
    __slots__ = ("iter", "start")
    __doc__ = getattr(_coconut.enumerate, "__doc__", "<see help(py_enumerate)>")
    def __new__(cls, iterable, start=0):
        start = _coconut.operator.index(start)
        self = _coconut.enumerate.__new__(cls, iterable, start)
        self.iter = iterable
        self.start = start
        return self
    def __repr__(self):
        return "enumerate(%s, %r)" % (_coconut.repr(self.iter), self.start)
    def __fmap__(self, func):
        return _coconut_map(func, self)
    def __reduce__(self):
        return (self.__class__, (self.iter, self.start))
    def __copy__(self):
        self.iter = _coconut_reiterable(self.iter)
        return self.__class__(self.iter, self.start)
    def __iter__(self):
        return _coconut.iter(_coconut.enumerate(self.iter, self.start))
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(_coconut_iter_getitem(self.iter, index), self.start + (0 if index.start is None else index.start if index.start >= 0 else _coconut.len(self.iter) + index.start))
        return (self.start + index, _coconut_iter_getitem(self.iter, index))
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.iter)
class multi_enumerate(_coconut_has_iter):
    """Enumerate an iterable of iterables. Works like enumerate, but indexes
    through inner iterables and produces a tuple index representing the index
    in each inner iterable. Supports indexing.

    For numpy arrays, uses np.nditer under the hood and supports len.
    """
    __slots__ = ()
    def __repr__(self):
        return "multi_enumerate(%s)" % (_coconut.repr(self.iter),)
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(self.get_new_iter())
    @property
    def is_numpy(self):
        return _coconut_get_base_module(self.iter) in _coconut.numpy_modules
    def __iter__(self):
        if self.is_numpy:
            it = _coconut.numpy.nditer(self.iter, ["multi_index", "refs_ok"], [["readonly"]])
            for x in it:
                x, = x.flatten()
                yield it.multi_index, x
        else:
            ind = [-1]
            its = [_coconut.iter(self.iter)]
            while its:
                ind[-1] += 1
                try:
                    x = _coconut.next(its[-1])
                except _coconut.StopIteration:
                    ind.pop()
                    its.pop()
                else:
                    if _coconut.isinstance(x, _coconut.abc.Iterable):
                        ind.append(-1)
                        its.append(_coconut.iter(x))
                    else:
                        yield _coconut.tuple(ind), x
    def __getitem__(self, index):
        if self.is_numpy and not _coconut.isinstance(index, _coconut.slice):
            multi_ind = []
            for i in _coconut.reversed(self.iter.shape):
                multi_ind.append(index % i)
                index //= i
            multi_ind = _coconut.tuple(_coconut.reversed(multi_ind))
            return multi_ind, self.iter[multi_ind]
        return _coconut_iter_getitem(_coconut.iter(self), index)
    def __len__(self):
        if self.is_numpy:
            return self.iter.size
        return _coconut.NotImplemented
class count(_coconut_baseclass):
    __slots__ = ("start", "step")
    __doc__ = getattr(_coconut.itertools.count, "__doc__", "count(start, step) returns an infinite iterator starting at start and increasing by step.")
    def __init__(self, start=0, step=1):
        self.start = start
        self.step = step
    def __reduce__(self):
        return (self.__class__, (self.start, self.step))
    def __repr__(self):
        return "count(%s, %s)" % (_coconut.repr(self.start), _coconut.repr(self.step))
    def __iter__(self):
        while True:
            yield self.start
            if self.step:
                self.start += self.step
    def __fmap__(self, func):
        return _coconut_map(func, self)
    def __contains__(self, elem):
        if not self.step:
            return elem == self.start
        if self.step > 0 and elem < self.start or self.step < 0 and elem > self.start:
            return False
        return (elem - self.start) % self.step == 0
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            if (index.start is None or index.start >= 0) and (index.stop is None or index.stop >= 0):
                new_start, new_step = self.start, self.step
                if self.step and index.start is not None:
                    new_start += self.step * index.start
                if self.step and index.step is not None:
                    new_step *= index.step
                if index.stop is None:
                    return self.__class__(new_start, new_step)
                if self.step and _coconut.isinstance(self.start, _coconut.int) and _coconut.isinstance(self.step, _coconut.int):
                    return _coconut.range(new_start, self.start + self.step * index.stop, new_step)
                return _coconut_map(self.__getitem__, _coconut.range(index.start if index.start is not None else 0, index.stop, index.step if index.step is not None else 1))
            raise _coconut.IndexError("count() indices cannot be negative")
        if index < 0:
            raise _coconut.IndexError("count() indices cannot be negative")
        return self.start + self.step * index if self.step else self.start
    def count(self, elem):
        """Count the number of times elem appears in the count."""
        if not self.step:
            return _coconut.float("inf") if elem == self.start else 0
        return _coconut.int(elem in self)
    def index(self, elem):
        """Find the index of elem in the count."""
        if elem not in self:
            raise _coconut.ValueError(_coconut.repr(elem) + " not in " + _coconut.repr(self))
        return (elem - self.start) // self.step if self.step else 0
    def __reversed__(self):
        if not self.step:
            return self
        raise _coconut.TypeError(_coconut.repr(self) + " object is not reversible")
class cycle(_coconut_has_iter):
    """cycle is a modified version of itertools.cycle with a times parameter
    that controls the number of times to cycle through the given iterable
    before stopping."""
    __slots__ = ("times",)
    def __new__(cls, iterable, times=None):
        self = _coconut.super(_coconut_cycle, cls).__new__(cls, iterable)
        if times is None:
            self.times = None
        else:
            self.times = _coconut.operator.index(times)
            if self.times < 0:
                raise _coconut.ValueError("cycle: times cannot be negative")
        return self
    def __reduce__(self):
        return (self.__class__, (self.iter, self.times))
    def __copy__(self):
        return self.__class__(self.get_new_iter(), self.times)
    def __repr__(self):
        return "cycle(%s, %r)" % (_coconut.repr(self.iter), self.times)
    def __iter__(self):
        i = 0
        while self.times is None or i < self.times:
            for x in self.get_new_iter():
                yield x
            i += 1
    def __contains__(self, elem):
        return elem in self.iter
    def __getitem__(self, index):
        if not _coconut.isinstance(index, _coconut.slice):
            if self.times is not None and index // _coconut.len(self.iter) >= self.times:
                raise _coconut.IndexError("cycle index out of range")
            return self.iter[index % _coconut.len(self.iter)]
        if self.times is None:
            return _coconut_map(self.__getitem__, _coconut_count()[index])
        else:
            return _coconut_map(self.__getitem__, _coconut_range(0, _coconut.len(self))[index])
    def __len__(self):
        if self.times is None or not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.iter) * self.times
    def __reversed__(self):
        if self.times is None:
            raise _coconut.TypeError(_coconut.repr(self) + " object is not reversible")
        return self.__class__(_coconut_reversed(self.get_new_iter()), self.times)
    def count(self, elem):
        """Count the number of times elem appears in the cycle."""
        return self.iter.count(elem) * (float("inf") if self.times is None else self.times)
    def index(self, elem):
        """Find the index of elem in the cycle."""
        if elem not in self.iter:
            raise _coconut.ValueError(_coconut.repr(elem) + " not in " + _coconut.repr(self))
        return self.iter.index(elem)
class windowsof(_coconut_has_iter):
    """Produces an iterable that effectively mimics a sliding window over iterable of the given size.
    The step determines the spacing between windowsof.

    If the size is larger than the iterable, windowsof will produce an empty iterable.
    If that is not the desired behavior, fillvalue can be passed and will be used in place of missing values."""
    __slots__ = ("size", "fillvalue", "step")
    def __new__(cls, size, iterable, fillvalue=_coconut_sentinel, step=1):
        self = _coconut.super(_coconut_windowsof, cls).__new__(cls, iterable)
        self.size = _coconut.operator.index(size)
        if self.size < 1:
            raise _coconut.ValueError("windowsof: size must be >= 1; not %r" % (self.size,))
        self.fillvalue = fillvalue
        self.step = _coconut.operator.index(step)
        if self.step < 1:
            raise _coconut.ValueError("windowsof: step must be >= 1; not %r" % (self.step,))
        return self
    def __reduce__(self):
        return (self.__class__, (self.size, self.iter, self.fillvalue, self.step))
    def __copy__(self):
        return self.__class__(self.size, self.get_new_iter(), self.fillvalue, self.step)
    def __repr__(self):
        return "windowsof(" + _coconut.repr(self.size) + ", " + _coconut.repr(self.iter) + (", fillvalue=" + _coconut.repr(self.fillvalue) if self.fillvalue is not _coconut_sentinel else "") + (", step=" + _coconut.repr(self.step) if self.step != 1 else "") + ")"
    def __iter__(self):
        cache = _coconut.collections.deque()
        i = 0
        for x in self.iter:
            i += 1
            cache.append(x)
            if _coconut.len(cache) == self.size:
                yield _coconut.tuple(cache)
                for _ in _coconut.range(self.step):
                    cache.popleft()
        if self.fillvalue is not _coconut_sentinel and (i < self.size or i % self.step != 0):
            while _coconut.len(cache) < self.size:
                cache.append(self.fillvalue)
            yield _coconut.tuple(cache)
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        if _coconut.len(self.iter) < self.size:
            return 0 if self.fillvalue is _coconut_sentinel else 1
        return (_coconut.len(self.iter) - self.size + self.step) // self.step + _coconut.int(_coconut.len(self.iter) % self.step != 0 if self.fillvalue is not _coconut_sentinel else 0)
class groupsof(_coconut_has_iter):
    """groupsof(n, iterable) splits iterable into groups of size n.

    If the length of the iterable is not divisible by n, the last group will be of size < n.
    """
    __slots__ = ("group_size", "fillvalue")
    def __new__(cls, n, iterable, fillvalue=_coconut_sentinel):
        self = _coconut.super(_coconut_groupsof, cls).__new__(cls, iterable)
        self.group_size = _coconut.operator.index(n)
        if self.group_size < 1:
            raise _coconut.ValueError("group size must be >= 1; not %r" % (self.group_size,))
        self.fillvalue = fillvalue
        return self
    def __iter__(self):
        iterator = _coconut.iter(self.iter)
        loop = True
        while loop:
            group = []
            for _ in _coconut.range(self.group_size):
                try:
                    group.append(_coconut.next(iterator))
                except _coconut.StopIteration:
                    loop = False
                    break
            if group:
                if not loop and self.fillvalue is not _coconut_sentinel:
                    while _coconut.len(group) < self.group_size:
                        group.append(self.fillvalue)
                yield _coconut.tuple(group)
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return (_coconut.len(self.iter) + self.group_size - 1) // self.group_size
    def __repr__(self):
        return "groupsof(" + _coconut.repr(self.group_size) + ", " + _coconut.repr(self.iter) + (", fillvalue=" + _coconut.repr(self.fillvalue) if self.fillvalue is not _coconut_sentinel else "") + ")"
    def __reduce__(self):
        return (self.__class__, (self.group_size, self.iter))
    def __copy__(self):
        return self.__class__(self.group_size, self.get_new_iter())
class recursive_generator(_coconut_base_callable):
    """Decorator that memoizes a generator (or any function that returns an iterator).
    Particularly useful for recursive generators, which may require recursive_generator to function properly."""
    __slots__ = ("func", "reit_store")
    def __init__(self, func):
        self.func = func
        self.reit_store = {}
    def __call__(self, *args, **kwargs):
        key = (0, args, _coconut.frozenset(kwargs.items()))
        try:
            _coconut.hash(key)
        except _coconut.TypeError:
            try:
                key = (1, _coconut.pickle.dumps(key, -1))
            except _coconut.Exception:
                raise _coconut.TypeError("recursive_generator() requires function arguments to be hashable or pickleable") from None
        reit = self.reit_store.get(key)
        if reit is None:
            reit = _coconut_reiterable(self.func(*args, **kwargs))
            self.reit_store[key] = reit
        return reit
    def __repr__(self):
        return "recursive_generator(%r)" % (self.func,)
    def __reduce__(self):
        return (self.__class__, (self.func,))
class _coconut_FunctionMatchErrorContext(_coconut_baseclass):
    __slots__ = ("exc_class", "taken")
    _threadlocal_ns = _coconut.threading.local()
    def __init__(self, exc_class):
        self.exc_class = exc_class
        self.taken = False
    @classmethod
    def get_contexts(cls):
        return cls._threadlocal_ns.__dict__.setdefault("contexts", [])
    def __enter__(self):
        self.get_contexts().append(self)
    def __exit__(self, type, value, traceback):
        self.get_contexts().pop()
    def __reduce__(self):
        return (self.__class__, (self.exc_class,))
def _coconut_get_function_match_error():
    contexts = _coconut_FunctionMatchErrorContext.get_contexts()
    if not contexts:
        return _coconut_MatchError
    ctx = contexts[-1]
    if ctx.taken:
        return _coconut_MatchError
    ctx.taken = True
    return ctx.exc_class
class _coconut_base_pattern_func(_coconut_base_callable):
    _coconut_is_match = True
    def __init__(self, *funcs):
        self.FunctionMatchError = _coconut.type(_coconut_py_str("MatchError"), (_coconut_MatchError,), {})
        self.patterns = []
        self.__doc__ = None
        self.__name__ = None
        self.__qualname__ = None
        for func in funcs:
            self.add_pattern(func)
    def add_pattern(self, func):
        if _coconut.isinstance(func, _coconut_base_pattern_func):
            self.patterns += func.patterns
        else:
            self.patterns.append(func)
        self.__doc__ = _coconut.getattr(func, "__doc__", self.__doc__)
        self.__name__ = _coconut.getattr(func, "__name__", self.__name__)
        self.__qualname__ = _coconut.getattr(func, "__qualname__", self.__qualname__)
    def __call__(self, *args, **kwargs):
        for func in self.patterns[:-1]:
            try:
                with _coconut_FunctionMatchErrorContext(self.FunctionMatchError):
                    return func(*args, **kwargs)
            except self.FunctionMatchError:
                pass
        return self.patterns[-1](*args, **kwargs)
    def _coconut_tco_func(self, *args, **kwargs):
        for func in self.patterns[:-1]:
            try:
                with _coconut_FunctionMatchErrorContext(self.FunctionMatchError):
                    return func(*args, **kwargs)
            except self.FunctionMatchError:
                pass
        return _coconut_tail_call(self.patterns[-1], *args, **kwargs)
    def __repr__(self):
        return "addpattern(%r)(*%r)" % (self.patterns[0], self.patterns[1:])
    def __reduce__(self):
        return (self.__class__, _coconut.tuple(self.patterns))
def _coconut_mark_as_match(base_func):
    base_func._coconut_is_match = True
    return base_func
def addpattern(base_func, *add_funcs, **kwargs):
    """Decorator to add new cases to a pattern-matching function (where the new case is checked last).

    Pass allow_any_func=True to allow any object as the base_func rather than just pattern-matching functions.
    If add_funcs are passed, addpattern(base_func, add_func) is equivalent to addpattern(base_func)(add_func).
    """
    allow_any_func = kwargs.pop("allow_any_func", False)
    if not allow_any_func and not _coconut.getattr(base_func, "_coconut_is_match", False):
        _coconut.warnings.warn("Possible misuse of addpattern with non-pattern-matching function " + _coconut.repr(base_func) + " (pass allow_any_func=True to dismiss)", _coconut_CoconutWarning, 2)
    if kwargs:
        raise _coconut.TypeError("addpattern() got unexpected keyword arguments " + _coconut.repr(kwargs))
    if add_funcs:
        return _coconut_base_pattern_func(base_func, *add_funcs)
    return _coconut_partial(_coconut_base_pattern_func, base_func)
_coconut_addpattern = addpattern
class _coconut_complex_partial(_coconut_base_callable):
    __slots__ = ("func", "_argdict", "_arglen", "_pos_kwargs", "_stargs", "keywords", "__name__")
    def __init__(self, _coconut_func, _coconut_argdict, _coconut_arglen, _coconut_pos_kwargs, *args, **kwargs):
        self.func = _coconut_func
        self._argdict = _coconut_argdict
        self._arglen = _coconut_arglen
        self._pos_kwargs = _coconut_pos_kwargs
        self._stargs = args
        self.keywords = kwargs
        self.__name__ = _coconut.getattr(_coconut_func, "__name__", None)
    def __reduce__(self):
        return (self.__class__, (self.func, self._argdict, self._arglen, self._pos_kwargs) + self._stargs, {"keywords": self.keywords})
    @property
    def args(self):
        return _coconut.tuple(self._argdict.get(i) for i in _coconut.range(self._arglen)) + self._stargs
    @property
    def required_nargs(self):
        return self._arglen - _coconut.len(self._argdict) + len(self._pos_kwargs)
    def __call__(self, *args, **kwargs):
        callargs = []
        argind = 0
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                callargs.append(self._argdict[i])
            elif argind >= _coconut.len(args):
                raise _coconut.TypeError("expected at least " + _coconut.str(self.required_nargs) + " argument(s) to " + _coconut.repr(self))
            else:
                callargs.append(args[argind])
                argind += 1
        for k in self._pos_kwargs:
            if k in kwargs:
                raise _coconut.TypeError(_coconut.repr(k) + " is an invalid keyword argument for " + _coconut.repr(self))
            elif argind >= _coconut.len(args):
                raise _coconut.TypeError("expected at least " + _coconut.str(self.required_nargs) + " argument(s) to " + _coconut.repr(self))
            else:
                kwargs[k] = args[argind]
                argind += 1
        callargs += self._stargs
        callargs += args[argind:]
        callkwargs = self.keywords.copy()
        callkwargs.update(kwargs)
        return self.func(*callargs, **callkwargs)
    def __repr__(self):
        args = []
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                args.append(_coconut.repr(self._argdict[i]))
            else:
                args.append("?")
        for arg in self._stargs:
            args.append(_coconut.repr(arg))
        for k in self._pos_kwargs:
            args.append(k + "=?")
        for k, v in self.keywords.items():
            args.append(k + "=" + _coconut.repr(v))
        return "%r$(%s)" % (self.func, ", ".join(args))
def consume(iterable, keep_last=0):
    """consume(iterable, keep_last) fully exhausts iterable and returns the last keep_last elements."""
    return _coconut.collections.deque(iterable, maxlen=keep_last)
class starmap(_coconut_baseclass, _coconut.itertools.starmap):
    __slots__ = ("func", "iter")
    __doc__ = getattr(_coconut.itertools.starmap, "__doc__", "starmap(func, iterable) = (func(*args) for args in iterable)")
    def __new__(cls, function, iterable):
        self = _coconut.itertools.starmap.__new__(cls, function, iterable)
        self.func = function
        self.iter = iterable
        return self
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self.func, _coconut_iter_getitem(self.iter, index))
        return self.func(*_coconut_iter_getitem(self.iter, index))
    def __reversed__(self):
        return self.__class__(self.func, *_coconut_reversed(self.iter))
    def __len__(self):
        if not _coconut.isinstance(self.iter, _coconut.abc.Sized):
            return _coconut.NotImplemented
        return _coconut.len(self.iter)
    def __repr__(self):
        return "starmap(%r, %s)" % (self.func, _coconut.repr(self.iter))
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __copy__(self):
        self.iter = _coconut_reiterable(self.iter)
        return self.__class__(self.func, self.iter)
    def __iter__(self):
        return _coconut.iter(_coconut.itertools.starmap(self.func, self.iter))
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self.func, func), self.iter)
class multiset(_coconut.collections.Counter):
    __slots__ = ()
    __doc__ = getattr(_coconut.collections.Counter, "__doc__", "multiset is a version of set that counts the number of times each element is added.")
    def add(self, item):
        """Add an element to a multiset."""
        self[item] += 1
    def remove(self, item, **kwargs):
        """Remove an element from a multiset; it must be a member."""
        allow_missing = kwargs.pop("allow_missing", False)
        if kwargs:
            raise _coconut.TypeError("multiset.remove() got unexpected keyword arguments " + _coconut.repr(kwargs))
        item_count = self[item]
        if item_count > 0:
            self[item] = item_count - 1
            if item_count - 1 <= 0:
                del self[item]
        elif not allow_missing:
            raise _coconut.KeyError(item)
    def discard(self, item):
        """Remove an element from a multiset if it is a member."""
        return self.remove(item, allow_missing=True)
    def isdisjoint(self, other):
        """Return True if two multisets have a null intersection."""
        return not self & other
    def __xor__(self, other):
        return self - other | other - self
    def __ixor__(self, other):
        right = other - self
        self -= other
        self |= right
        return self
    def count(self, item):
        """Return the number of times an element occurs in a multiset.
        Equivalent to multiset[item], but additionally verifies the count is non-negative."""
        result = self[item]
        if result < 0:
            raise _coconut.ValueError("multiset has negative count for " + _coconut.repr(item))
        return result
    def __fmap__(self, func):
        return self.__class__(_coconut.dict((func(obj), num) for obj, num in self.items()))
    def __add__(self, other):
        out = self.copy()
        out += other
        return out
    def __and__(self, other):
        out = self.copy()
        out &= other
        return out
    def __or__(self, other):
        out = self.copy()
        out |= other
        return out
    def __sub__(self, other):
        out = self.copy()
        out -= other
        return out
    def __pos__(self):
        return self.__class__(_coconut.super(_coconut_multiset, self).__pos__())
    def __neg__(self):
        return self.__class__(_coconut.super(_coconut_multiset, self).__neg__())
_coconut.abc.MutableSet.register(multiset)
def _coconut_base_makedata(data_type, args, from_fmap=False, fallback_to_init=False):
    if _coconut.hasattr(data_type, "_make") and _coconut.issubclass(data_type, _coconut.tuple):
        return data_type._make(args)
    if _coconut.issubclass(data_type, (_coconut.range, _coconut.abc.Iterator)):
        return args
    if _coconut.issubclass(data_type, _coconut.str):
        return "".join(args)
    if fallback_to_init or _coconut.issubclass(data_type, _coconut.fmappables):
        return data_type(args)
    if from_fmap:
        raise _coconut.TypeError("no known __fmap__ implementation for " + _coconut.repr(data_type) + " (pass fallback_to_init=True to fall back on __init__ and __iter__)")
    raise _coconut.TypeError("no known makedata implementation for " + _coconut.repr(data_type) + " (pass fallback_to_init=True to fall back on __init__)")
def makedata(data_type, *args, **kwargs):
    """Construct an object of the given data_type containing the given arguments."""
    fallback_to_init = kwargs.pop("fallback_to_init", False)
    if kwargs:
        raise _coconut.TypeError("makedata() got unexpected keyword arguments " + _coconut.repr(kwargs))
    return _coconut_base_makedata(data_type, args, fallback_to_init=fallback_to_init)
class _coconut_amap(_coconut_baseclass):
    __slots__ = ("func", "aiter")
    def __init__(self, func, aiter):
        self.func = func
        self.aiter = aiter
    def __reduce__(self):
        return (self.__class__, (self.func, self.aiter))
    def __repr__(self):
        return "fmap(" + _coconut.repr(self.func) + ", " + _coconut.repr(self.aiter) + ")"
    def __aiter__(self):
        return self
    async def __anext__(self):
        return self.func(await self.aiter.__anext__())
def fmap(func, obj, **kwargs):
    """fmap(func, obj) creates a copy of obj with func applied to its contents.

    Supports:
    * Coconut data types
    * `str`, `dict`, `list`, `tuple`, `set`, `frozenset`, `bytes`, `bytearray`
    * `dict` (maps over .items())
    * asynchronous iterables
    * numpy arrays (uses np.vectorize)
    * pandas objects (uses .apply)

    Override by defining obj.__fmap__(func).
    """
    starmap_over_mappings = kwargs.pop("starmap_over_mappings", False)
    fallback_to_init = kwargs.pop("fallback_to_init", False)
    if kwargs:
        raise _coconut.TypeError("fmap() got unexpected keyword arguments " + _coconut.repr(kwargs))
    obj_fmap = _coconut.getattr(obj, "__fmap__", None)
    if obj_fmap is not None:
        try:
            result = obj_fmap(func)
        except _coconut.NotImplementedError:
            pass
        else:
            if result is not _coconut.NotImplemented:
                return result
    obj_module = _coconut_get_base_module(obj)
    if obj_module in _coconut.xarray_modules:
        return _coconut_fmap(func, _coconut_xarray_to_pandas(obj)).to_xarray()
    if obj_module in _coconut.pandas_modules:
        if obj.ndim <= 1:
            return obj.apply(func)
        return obj.apply(func, axis=obj.ndim-1)
    if obj_module in _coconut.jax_numpy_modules:
        import jax.numpy as jnp
        return jnp.vectorize(func)(obj)
    if obj_module in _coconut.numpy_modules:
        return _coconut.numpy.vectorize(func)(obj)
    obj_aiter = _coconut.getattr(obj, "__aiter__", None)
    if obj_aiter is not None and _coconut_amap is not None:
        try:
            aiter = obj_aiter()
        except _coconut.NotImplementedError:
            pass
        else:
            if aiter is not _coconut.NotImplemented:
                return _coconut_amap(func, aiter)
    if _coconut.isinstance(obj, _coconut.abc.Mapping):
        mapped_obj = (_coconut_starmap if starmap_over_mappings else _coconut_map)(func, obj.items())
    else:
        mapped_obj = _coconut_map(func, obj)
    return _coconut_base_makedata(obj.__class__, mapped_obj, from_fmap=True, fallback_to_init=fallback_to_init)
def memoize(*args, **kwargs):
    """Decorator that memoizes a function, preventing it from being recomputed
    if it is called multiple times with the same arguments."""
    if not kwargs and _coconut.len(args) == 1 and _coconut.callable(args[0]):
        return _coconut_memoize_helper()(args[0])
    if _coconut.len(kwargs) == 1 and "user_function" in kwargs and _coconut.callable(kwargs["user_function"]):
        return _coconut_memoize_helper()(kwargs["user_function"])
    return _coconut_memoize_helper(*args, **kwargs)
memoize.RECURSIVE = _coconut_Sentinel()
def _coconut_memoize_helper(maxsize=None, typed=False):
    if maxsize is memoize.RECURSIVE:
        def memoizer(func):
            """memoize(...)"""
            inside = [False]
            cache = {}
            @_coconut_wraps(func)
            def memoized_func(*args, **kwargs):
                if typed:
                    key = (_coconut.tuple((x, _coconut.type(x)) for x in args), _coconut.tuple((k, _coconut.type(k), v, _coconut.type(v)) for k, v in kwargs.items()))
                else:
                    key = (args, _coconut.tuple(kwargs.items()))
                got = cache.get(key, _coconut_sentinel)
                if got is not _coconut_sentinel:
                    return got
                outer_inside, inside[0] = inside[0], True
                try:
                    got = func(*args, **kwargs)
                    cache[key] = got
                    return got
                finally:
                    inside[0] = outer_inside
                    if not inside[0]:
                        cache.clear()
            memoized_func.__module__ = _coconut.getattr(func, "__module__", None)
            memoized_func.__name__ = _coconut.getattr(func, "__name__", None)
            memoized_func.__qualname__ = _coconut.getattr(func, "__qualname__", None)
            return memoized_func
        return memoizer
    else:
        return _coconut.functools.lru_cache(maxsize, typed)
def _coconut_call_set_names(cls): pass
class override(_coconut_baseclass):
    """Declare a method in a subclass as an override of a parent class method.
    Enforces at runtime that the parent class has such a method to be overwritten."""
    __slots__ = ("func",)
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        self_func_get = _coconut.getattr(self.func, "__get__", None)
        if self_func_get is not None:
            if objtype is None:
                return self_func_get(obj)
            else:
                return self_func_get(obj, objtype)
        if obj is None:
            return self.func
        return _coconut.types.MethodType(self.func, obj)
    def __set_name__(self, obj, name):
        if not _coconut.hasattr(_coconut.super(obj, obj), name):
            raise _coconut.RuntimeError(obj.__name__ + "." + name + " marked with @override but not overriding anything")
    def __reduce__(self):
        return (self.__class__, (self.func,))
def reveal_type(obj):
    """Special function to get MyPy to print the type of the given expression.
    At runtime, reveal_type is the identity function."""
    return obj
def reveal_locals():
    """Special function to get MyPy to print the type of the current locals.
    At runtime, reveal_locals always returns None."""
    pass
def _coconut_dict_merge(*dicts, **kwargs):
    for_func = kwargs.pop("for_func", False)
    assert not kwargs, "error with internal Coconut function _coconut_dict_merge (you should report this at https://github.com/evhub/coconut/issues/new)"
    newdict = {}
    prevlen = 0
    for d in dicts:
        newdict.update(d)
        if for_func:
            if _coconut.len(newdict) != prevlen + _coconut.len(d):
                raise _coconut.TypeError("multiple values for the same keyword argument")
            prevlen = _coconut.len(newdict)
    return newdict
def ident(x, **kwargs):
    """The identity function. Generally equivalent to x => x. Useful in point-free programming.
    Accepts one keyword-only argument, side_effect, which specifies a function to call on the argument before it is returned."""
    side_effect = kwargs.pop("side_effect", None)
    if kwargs:
        raise _coconut.TypeError("ident() got unexpected keyword arguments " + _coconut.repr(kwargs))
    if side_effect is not None:
        side_effect(x)
    return x
call = _coconut.operator.call
def safe_call(_coconut_f, /, *args, **kwargs):
    """safe_call is a version of call that catches any Exceptions and
    returns an Expected containing either the result or the error.

    Equivalent to:
        def safe_call(f, /, *args, **kwargs):
            try:
                return Expected(f(*args, **kwargs))
            except Exception as err:
                return Expected(error=err)
    """
    try:
        return _coconut_Expected(_coconut_f(*args, **kwargs))
    except _coconut.Exception as err:
        return _coconut_Expected(error=err)
class Expected(_coconut.collections.namedtuple("Expected", ("result", "error"))):
    '''Coconut's Expected built-in is a Coconut data that represents a value
    that may or may not be an error, similar to Haskell's Either.

    Effectively equivalent to:
        data Expected[T](result: T? = None, error: BaseException? = None):
            def __bool__(self) -> bool:
                return self.error is None
            def __fmap__[U](self, func: T -> U) -> Expected[U]:
                """Maps func over the result if it exists.

                __fmap__ should be used directly only when fmap is not available (e.g. when consuming an Expected in vanilla Python).
                """
                return self.__class__(func(self.result)) if self else self
            def and_then[U](self, func: T -> Expected[U]) -> Expected[U]:
                """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
                Implements a monadic bind. Equivalent to fmap ..> .join()."""
                return self |> fmap$(func) |> .join()
            def join(self: Expected[Expected[T]]) -> Expected[T]:
                """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
                if not self:
                    return self
                if not self.result `isinstance` Expected:
                    raise TypeError("Expected.join() requires an Expected[Expected[_]]")
                return self.result
            def map_error(self, func: BaseException -> BaseException) -> Expected[T]:
                """Maps func over the error if it exists."""
                return self if self else self.__class__(error=func(self.error))
            def handle(self, err_type, handler: BaseException -> T) -> Expected[T]:
                """Recover from the given err_type by calling handler on the error to determine the result."""
                if not self and isinstance(self.error, err_type):
                    return self.__class__(handler(self.error))
                return self
            def expect_error(self, *err_types: BaseException) -> Expected[T]:
                """Raise any errors that do not match the given error types."""
                if not self and not isinstance(self.error, err_types):
                    raise self.error
                return self
            def unwrap(self) -> T:
                """Unwrap the result or raise the error."""
                if not self:
                    raise self.error
                return self.result
            def or_else[U](self, func: BaseException -> Expected[U]) -> Expected[T | U]:
                """Return self if no error, otherwise return the result of evaluating func on the error."""
                return self if self else func(self.error)
            def result_or_else[U](self, func: BaseException -> U) -> T | U:
                """Return the result if it exists, otherwise return the result of evaluating func on the error."""
                return self.result if self else func(self.error)
            def result_or[U](self, default: U) -> T | U:
                """Return the result if it exists, otherwise return the default.

                Since .result_or() completely silences errors, it is highly recommended that you
                call .expect_error() first to explicitly declare what errors you are okay silencing.
                """
                return self.result if self else default
    '''
    __slots__ = ()
    _coconut_is_data = True
    __match_args__ = ("result", "error")
    _coconut_data_defaults = {0: None, 1: None}
    def __add__(self, other): return _coconut.NotImplemented
    def __mul__(self, other): return _coconut.NotImplemented
    def __rmul__(self, other): return _coconut.NotImplemented
    __ne__ = _coconut.object.__ne__
    def __eq__(self, other):
        return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)
    def __hash__(self):
        return _coconut.tuple.__hash__(self) ^ hash(self.__class__)
    def __new__(cls, result=_coconut_sentinel, error=None):
        if result is not _coconut_sentinel and error is not None:
            raise _coconut.TypeError("Expected cannot have both a result and an error")
        if result is _coconut_sentinel and error is None:
            raise _coconut.TypeError("Expected must have either a result or an error")
        if result is _coconut_sentinel:
            result = None
        return _coconut.tuple.__new__(cls, (result, error))
    def __bool__(self):
        return self.error is None
    def __fmap__(self, func):
        """Maps func over the result if it exists.

        __fmap__ should be used directly only when fmap is not available (e.g. when consuming an Expected in vanilla Python).
        """
        return self.__class__(func(self.result)) if self else self
    def and_then(self, func):
        """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
        Implements a monadic bind. Equivalent to fmap ..> .join()."""
        return self.__fmap__(func).join()
    def join(self):
        """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
        if not self:
            return self
        if not _coconut.isinstance(self.result, _coconut_Expected):
            raise _coconut.TypeError("Expected.join() requires an Expected[Expected[_]]")
        return self.result
    def map_error(self, func):
        """Maps func over the error if it exists."""
        return self if self else self.__class__(error=func(self.error))
    def handle(self, err_type, handler):
        """Recover from the given err_type by calling handler on the error to determine the result."""
        if not self and _coconut.isinstance(self.error, err_type):
            return self.__class__(handler(self.error))
        return self
    def expect_error(self, *err_types):
        """Raise any errors that do not match the given error types."""
        if not self and not _coconut.isinstance(self.error, err_types):
            raise self.error
        return self
    def unwrap(self):
        """Unwrap the result or raise the error."""
        if not self:
            raise self.error
        return self.result
    def or_else(self, func):
        """Return self if no error, otherwise return the result of evaluating func on the error."""
        if self:
            return self
        got = func(self.error)
        if not _coconut.isinstance(got, _coconut_Expected):
            raise _coconut.TypeError("Expected.or_else() requires a function that returns an Expected")
        return got
    def result_or_else(self, func):
        """Return the result if it exists, otherwise return the result of evaluating func on the error."""
        return self.result if self else func(self.error)
    def result_or(self, default):
        """Return the result if it exists, otherwise return the default.

        Since .result_or() completely silences errors, it is highly recommended that you
        call .expect_error() first to explicitly declare what errors you are okay silencing.
        """
        return self.result if self else default
class flip(_coconut_base_callable):
    """Given a function, return a new function with inverse argument order.
    If nargs is passed, only the first nargs arguments are reversed."""
    __slots__ = ("func", "nargs")
    def __init__(self, func, nargs=None):
        self.func = func
        if nargs is None:
            self.nargs = None
        else:
            self.nargs = _coconut.operator.index(nargs)
            if self.nargs < 0:
                raise _coconut.ValueError("flip: nargs cannot be negative")
    def __reduce__(self):
        return (self.__class__, (self.func, self.nargs))
    def __call__(self, *args, **kwargs):
        if self.nargs is None:
            return self.func(*args[::-1], **kwargs)
        if self.nargs == 0:
            return self.func(*args, **kwargs)
        return self.func(*(args[self.nargs-1::-1] + args[self.nargs:]), **kwargs)
    def __repr__(self):
        return "flip(%r%s)" % (self.func, "" if self.nargs is None else ", " + _coconut.repr(self.nargs))
class const(_coconut_base_callable):
    """Create a function that, whatever its arguments, just returns the given value."""
    __slots__ = ("value",)
    def __init__(self, value):
        self.value = value
    def __reduce__(self):
        return (self.__class__, (self.value,))
    def __call__(self, *args, **kwargs):
        return self.value
    def __repr__(self):
        return "const(%s)" % (_coconut.repr(self.value),)
class _coconut_lifted(_coconut_base_callable):
    __slots__ = ("apart", "func", "func_args", "func_kwargs")
    def __init__(self, apart, func, func_args, func_kwargs):
        self.apart = apart
        self.func = func
        self.func_args = func_args
        self.func_kwargs = func_kwargs
    def __reduce__(self):
        return (self.__class__, (self.apart, self.func, self.func_args, self.func_kwargs))
    def __call__(self, *args, **kwargs):
        if self.apart:
            return self.func(*(f(x) for f, x in _coconut_zip(self.func_args, args, strict=True)), **_coconut_py_dict((k, self.func_kwargs[k](kwargs[k])) for k in self.func_kwargs.keys() | kwargs.keys()))
        else:
            return self.func(*(g(*args, **kwargs) for g in self.func_args), **_coconut_py_dict((k, h(*args, **kwargs)) for k, h in self.func_kwargs.items()))
    def __repr__(self):
        return "lift%s(%r)(%s%s)" % (self.func, ("_apart" if self.apart else ""), ", ".join(_coconut.repr(g) for g in self.func_args), ", ".join(k + "=" + _coconut.repr(h) for k, h in self.func_kwargs.items()))
class lift(_coconut_base_callable):
    """Lift a function up so that all of its arguments are functions that all take the same arguments.

    For a binary function f(x, y) and two unary functions g(z) and h(z), lift works as the S' combinator:
        lift(f)(g, h)(z) == f(g(z), h(z))

    In general, lift is equivalent to:
        def lift(f) = ((*func_args, **func_kwargs) => (*args, **kwargs) => (
            f(*(g(*args, **kwargs) for g in func_args), **{k: h(*args, **kwargs) for k, h in func_kwargs.items()}))
        )

    lift also supports a shortcut form such that lift(f, *func_args, **func_kwargs) is equivalent to lift(f)(*func_args, **func_kwargs).
    """
    __slots__ = ("func",)
    _apart = False
    def __new__(cls, func, *func_args, **func_kwargs):
        self = _coconut.super(_coconut_lift, cls).__new__(cls)
        self.func = func
        if func_args or func_kwargs:
            self = self(*func_args, **func_kwargs)
        return self
    def __reduce__(self):
        return (self.__class__, (self.func,))
    def __repr__(self):
        return "lift%s(%r)" % (("_apart" if self._apart else ""), self.func)
    def __call__(self, *func_args, **func_kwargs):
        return _coconut_lifted(self._apart, self.func, func_args, func_kwargs)
class lift_apart(lift):
    """Lift a function up so that all of its arguments are functions that each take separate arguments.

    For a binary function f(x, y) and two unary functions g(z) and h(z), lift_apart works as the D2 combinator:
        lift_apart(f)(g, h)(z, w) == f(g(z), h(w))

    In general, lift_apart is equivalent to:
        def lift_apart(func) = (*func_args, **func_kwargs) => (*args, **kwargs) => func(
            *(f(x) for f, x in zip(func_args, args, strict=True)),
            **{k: func_kwargs[k](kwargs[k]) for k in func_kwargs.keys() | kwargs.keys()},
        )

    lift_apart also supports a shortcut form such that lift_apart(f, *func_args, **func_kwargs) is equivalent to lift_apart(f)(*func_args, **func_kwargs).
    """
    _apart = True
def all_equal(iterable, to=_coconut_sentinel):
    """For a given iterable, check whether all elements in that iterable are equal to each other.
    If 'to' is passed, check that all the elements are equal to that value.

    Supports numpy arrays. Assumes transitivity and 'x != y' being equivalent to 'not (x == y)'.
    """
    iterable_module = _coconut_get_base_module(iterable)
    if iterable_module in _coconut.numpy_modules:
        if iterable_module in _coconut.pandas_modules:
            iterable = iterable.to_numpy()
        elif iterable_module in _coconut.xarray_modules:
            iterable = _coconut_xarray_to_numpy(iterable)
        return not _coconut.len(iterable) or (iterable == (iterable[0] if to is _coconut_sentinel else to)).all()
    first_item = to
    for item in iterable:
        if first_item is _coconut_sentinel:
            first_item = item
        elif first_item != item:
            return False
    return True
def mapreduce(key_value_func, iterable, **kwargs):
    """Map key_value_func over iterable, then collect the values into a dictionary of lists keyed by the keys.

    If reduce_func is passed, instead of collecting the values into lists, reduce over
    the values for each key with reduce_func, effectively implementing a MapReduce operation.

    If collect_in is passed, initialize the collection from .
    """
    collect_in = kwargs.pop("collect_in", None)
    reduce_func = kwargs.pop("reduce_func", None if collect_in is None else False)
    reduce_func_init = kwargs.pop("reduce_func_init", _coconut_sentinel)
    if reduce_func_init is not _coconut_sentinel and not reduce_func:
        raise _coconut.TypeError("reduce_func_init requires reduce_func")
    map_using = kwargs.pop("map_using", _coconut.map)
    if kwargs:
        raise _coconut.TypeError("mapreduce()/collectby() got unexpected keyword arguments " + _coconut.repr(kwargs))
    collection = collect_in if collect_in is not None else _coconut.collections.defaultdict(_coconut.list) if reduce_func is None else {}
    for key, val in map_using(key_value_func, iterable):
        if reduce_func is None:
            collection[key].append(val)
        else:
            old_val = collection.get(key, reduce_func_init)
            if old_val is not _coconut_sentinel:
                if reduce_func is False:
                    raise _coconut.ValueError("mapreduce()/collectby() got duplicate key " + repr(key) + " with reduce_func=False")
                val = reduce_func(old_val, val)
            collection[key] = val
    return collection
def _coconut_parallel_mapreduce(mapreduce_func, map_cls, *args, **kwargs):
    if "map_using" in kwargs:
        raise _coconut.TypeError("redundant map_using argument to process/thread mapreduce/collectby")
    kwargs["map_using"] = _coconut.functools.partial(map_cls, stream=True, ordered=kwargs.pop("ordered", False), chunksize=kwargs.pop("chunksize", 1))
    with map_cls.multiple_sequential_calls(max_workers=kwargs.pop("max_workers", None)):
        return mapreduce_func(*args, **kwargs)
mapreduce.using_processes = _coconut_partial(_coconut_parallel_mapreduce, mapreduce, process_map)
mapreduce.using_threads = _coconut_partial(_coconut_parallel_mapreduce, mapreduce, thread_map)
def collectby(key_func, iterable, value_func=None, **kwargs):
    """Collect the items in iterable into a dictionary of lists keyed by key_func(item).

    If value_func is passed, collect value_func(item) into each list instead of item.

    If reduce_func is passed, instead of collecting the items into lists, reduce over
    the items for each key with reduce_func, effectively implementing a MapReduce operation.

    If map_using is passed, calculate key_func and value_func by mapping them over
    the iterable using map_using as map. Useful with process_map/thread_map.
    """
    return _coconut_mapreduce(_coconut_lifted(False, _coconut_comma_op, (key_func, _coconut_ident if value_func is None else value_func), {}), iterable, **kwargs)
collectby.using_processes = _coconut_partial(_coconut_parallel_mapreduce, collectby, process_map)
collectby.using_threads = _coconut_partial(_coconut_parallel_mapreduce, collectby, thread_map)
def _namedtuple_of(**kwargs):
    """Construct an anonymous namedtuple of the given keyword arguments."""
    return _coconut_mk_anon_namedtuple(kwargs.keys(), of_kwargs=kwargs)
def _coconut_mk_anon_namedtuple(fields, types=None, of_kwargs={}, of_args=()):
    if types is None:
        NT = _coconut.collections.namedtuple("_namedtuple_of", fields)
    else:
        NT = _coconut.typing.NamedTuple("_namedtuple_of", [(f, t) for f, t in _coconut.zip(fields, types)])
    _coconut.copyreg.pickle(NT, lambda nt: (_coconut_mk_anon_namedtuple, (nt._fields, types, nt._asdict())))
    if of_kwargs or of_args:
        return NT(*of_args, **of_kwargs)
    else:
        return NT
def _coconut_ndim(arr):
    arr_mod = _coconut_get_base_module(arr)
    if (arr_mod in _coconut.numpy_modules or _coconut.hasattr(arr.__class__, "__matconcat__")) and _coconut.hasattr(arr, "ndim"):
        return arr.ndim
    if arr_mod in _coconut.xarray_modules:
        return 2
    if not _coconut.isinstance(arr, _coconut.abc.Sequence) or _coconut.isinstance(arr, (_coconut.str, _coconut.bytes)):
        return 0
    if _coconut.len(arr) == 0:
        return 1
    arr_dim = 1
    inner_arr = arr[0]
    if inner_arr == arr:
        return 0
    while _coconut.isinstance(inner_arr, _coconut.abc.Sequence):
        arr_dim += 1
        if _coconut.len(inner_arr) < 1:
            break
        new_inner_arr = inner_arr[0]
        if new_inner_arr == inner_arr:
            break
        inner_arr = new_inner_arr
    return arr_dim
def _coconut_expand_arr(arr, new_dims):
    if (_coconut_get_base_module(arr) in _coconut.numpy_modules or _coconut.hasattr(arr.__class__, "__matconcat__")) and _coconut.hasattr(arr, "reshape"):
        return arr.reshape((1,) * new_dims + arr.shape)
    for _ in _coconut.range(new_dims):
        arr = [arr]
    return arr
def _coconut_concatenate(arrs, axis):
    for a in arrs:
        if _coconut.hasattr(a.__class__, "__matconcat__"):
            return a.__class__.__matconcat__(arrs, axis=axis)
    arr_modules = [_coconut_get_base_module(a) for a in arrs]
    if any(mod in _coconut.xarray_modules for mod in arr_modules):
        return _coconut_concatenate([(_coconut_xarray_to_pandas(a) if mod in _coconut.xarray_modules else a) for a, mod in _coconut.zip(arrs, arr_modules)], axis).to_xarray()
    if any(mod in _coconut.pandas_modules for mod in arr_modules):
        import pandas
        return pandas.concat(arrs, axis=axis)
    if any(mod in _coconut.jax_numpy_modules for mod in arr_modules):
        import jax.numpy
        return jax.numpy.concatenate(arrs, axis=axis)
    if any(mod in _coconut.numpy_modules for mod in arr_modules):
        return _coconut.numpy.concatenate(arrs, axis=axis)
    if not axis:
        return _coconut.list(_coconut.itertools.chain.from_iterable(arrs))
    return [_coconut_concatenate(rows, axis - 1) for rows in _coconut.zip(*arrs)]
def _coconut_arr_concat_op(dim, *arrs):
    """Coconut multi-dimensional array concatenation operator."""
    arr_dims = [_coconut_ndim(a) for a in arrs]
    arrs = [_coconut_expand_arr(a, dim - d) if d < dim else a for a, d in _coconut.zip(arrs, arr_dims)]
    arr_dims.append(dim)
    max_arr_dim = _coconut.max(arr_dims)
    return _coconut_concatenate(arrs, max_arr_dim - dim)
def _coconut_call_or_coefficient(func, *args):
    if _coconut.callable(func):
        return func(*args)
    if not _coconut.isinstance(func, (_coconut.int, _coconut.float, _coconut.complex)) and _coconut_get_base_module(func) not in _coconut.numpy_modules:
        raise _coconut.TypeError("first object in implicit function application and coefficient syntax must be Callable, int, float, complex, or numpy")
    func = func
    for x in args:
        func = func * x
    return func
class _coconut_SupportsAdd(_coconut.typing.Protocol):
    """Coconut (+) Protocol. Equivalent to:

        class SupportsAdd[T, U, V](Protocol):
            def __add__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __add__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((+) in a typing context is a Protocol)")
class _coconut_SupportsMinus(_coconut.typing.Protocol):
    """Coconut (-) Protocol. Equivalent to:

        class SupportsMinus[T, U, V](Protocol):
            def __sub__(self: T, other: U) -> V:
                raise NotImplementedError
            def __neg__(self: T) -> V:
                raise NotImplementedError
    """
    def __sub__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((-) in a typing context is a Protocol)")
    def __neg__(self):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((-) in a typing context is a Protocol)")
class _coconut_SupportsMul(_coconut.typing.Protocol):
    """Coconut (*) Protocol. Equivalent to:

        class SupportsMul[T, U, V](Protocol):
            def __mul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mul__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((*) in a typing context is a Protocol)")
class _coconut_SupportsPow(_coconut.typing.Protocol):
    """Coconut (**) Protocol. Equivalent to:

        class SupportsPow[T, U, V](Protocol):
            def __pow__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __pow__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((**) in a typing context is a Protocol)")
class _coconut_SupportsTruediv(_coconut.typing.Protocol):
    """Coconut (/) Protocol. Equivalent to:

        class SupportsTruediv[T, U, V](Protocol):
            def __truediv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __truediv__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((/) in a typing context is a Protocol)")
class _coconut_SupportsFloordiv(_coconut.typing.Protocol):
    """Coconut (//) Protocol. Equivalent to:

        class SupportsFloordiv[T, U, V](Protocol):
            def __floordiv__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __floordiv__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((//) in a typing context is a Protocol)")
class _coconut_SupportsMod(_coconut.typing.Protocol):
    """Coconut (%) Protocol. Equivalent to:

        class SupportsMod[T, U, V](Protocol):
            def __mod__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __mod__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((%) in a typing context is a Protocol)")
class _coconut_SupportsAnd(_coconut.typing.Protocol):
    """Coconut (&) Protocol. Equivalent to:

        class SupportsAnd[T, U, V](Protocol):
            def __and__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __and__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((&) in a typing context is a Protocol)")
class _coconut_SupportsXor(_coconut.typing.Protocol):
    """Coconut (^) Protocol. Equivalent to:

        class SupportsXor[T, U, V](Protocol):
            def __xor__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __xor__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((^) in a typing context is a Protocol)")
class _coconut_SupportsOr(_coconut.typing.Protocol):
    """Coconut (|) Protocol. Equivalent to:

        class SupportsOr[T, U, V](Protocol):
            def __or__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __or__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((|) in a typing context is a Protocol)")
class _coconut_SupportsLshift(_coconut.typing.Protocol):
    """Coconut (<<) Protocol. Equivalent to:

        class SupportsLshift[T, U, V](Protocol):
            def __lshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __lshift__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((<<) in a typing context is a Protocol)")
class _coconut_SupportsRshift(_coconut.typing.Protocol):
    """Coconut (>>) Protocol. Equivalent to:

        class SupportsRshift[T, U, V](Protocol):
            def __rshift__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __rshift__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((>>) in a typing context is a Protocol)")
class _coconut_SupportsMatmul(_coconut.typing.Protocol):
    """Coconut (@) Protocol. Equivalent to:

        class SupportsMatmul[T, U, V](Protocol):
            def __matmul__(self: T, other: U) -> V:
                raise NotImplementedError(...)
    """
    def __matmul__(self, other):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((@) in a typing context is a Protocol)")
class _coconut_SupportsInv(_coconut.typing.Protocol):
    """Coconut (~) Protocol. Equivalent to:

        class SupportsInv[T, V](Protocol):
            def __invert__(self: T) -> V:
                raise NotImplementedError(...)
    """
    def __invert__(self):
        raise _coconut.NotImplementedError("Protocol methods cannot be called at runtime ((~) in a typing context is a Protocol)")
@_coconut_wraps(_coconut.functools.reduce)
def reduce(function, iterable, initial=_coconut_sentinel):
    if initial is _coconut_sentinel:
        return _coconut.functools.reduce(function, iterable)
    return _coconut.functools.reduce(function, iterable, initial)
class takewhile(_coconut.itertools.takewhile):
    __slots__ = ()
    __doc__ = _coconut.itertools.takewhile.__doc__
    def __new__(cls, predicate, iterable):
        return _coconut.itertools.takewhile.__new__(cls, predicate, iterable)
class dropwhile(_coconut.itertools.dropwhile):
    __slots__ = ()
    __doc__ = _coconut.itertools.dropwhile.__doc__
    def __new__(cls, predicate, iterable):
        return _coconut.itertools.dropwhile.__new__(cls, predicate, iterable)
async def async_map(async_func, *iters, strict=False):
    """Map async_func over iters asynchronously using anyio."""
    import anyio
    results = []
    async def store_func_in_of(i, args):
        got = await async_func(*args)
        results.extend([None] * (1 + i - _coconut.len(results)))
        results[i] = got
    async with anyio.create_task_group() as nursery:
        for i, args in _coconut.enumerate(_coconut_zip(*iters, strict=strict)):
            nursery.start_soon(store_func_in_of, i, args)
    return results
def prepattern(base_func, **kwargs):
    """DEPRECATED: use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func, base_func, **kwargs)
    return pattern_prepender
def datamaker(data_type):
    """DEPRECATED: use makedata instead."""
    return _coconut_partial(makedata, data_type)
of, parallel_map, concurrent_map, recursive_iterator = call, process_map, thread_map, recursive_generator
_coconut_self_match_types = (bool, bytearray, bytes, dict, float, frozenset, int, py_int, list, set, str, py_str, tuple)
TYPE_CHECKING, _coconut_Expected, _coconut_MatchError, _coconut_cartesian_product, _coconut_count, _coconut_cycle, _coconut_enumerate, _coconut_flatten, _coconut_fmap, _coconut_filter, _coconut_groupsof, _coconut_ident, _coconut_lift, _coconut_map, _coconut_mapreduce, _coconut_multiset, _coconut_range, _coconut_reiterable, _coconut_reversed, _coconut_scan, _coconut_starmap, _coconut_tee, _coconut_windowsof, _coconut_zip, _coconut_zip_longest = False, Expected, MatchError, cartesian_product, count, cycle, enumerate, flatten, fmap, filter, groupsof, ident, lift, map, mapreduce, multiset, range, reiterable, reversed, scan, starmap, tee, windowsof, zip, zip_longest

# Compiled Coconut: -----------------------------------------------------------



import asyncio  #12 (line in Coconut source)
import json  #13 (line in Coconut source)
import threading  #14 (line in Coconut source)
import webbrowser  #15 (line in Coconut source)
from collections import Counter  #16 (line in Coconut source)
from pathlib import Path  #17 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #18 (line in Coconut source)
    from typing import TYPE_CHECKING  #18 (line in Coconut source)
else:  #18 (line in Coconut source)
    try:  #18 (line in Coconut source)
        TYPE_CHECKING = _coconut.typing.TYPE_CHECKING  #18 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #18 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #18 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #18 (line in Coconut source)
    from typing import Any  #18 (line in Coconut source)
else:  #18 (line in Coconut source)
    try:  #18 (line in Coconut source)
        Any = _coconut.typing.Any  #18 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #18 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #18 (line in Coconut source)

from yggdrasil_lm.core.edges import Edge  #20 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #21 (line in Coconut source)
from yggdrasil_lm.observability import explain_run  #22 (line in Coconut source)

if TYPE_CHECKING:  #24 (line in Coconut source)
    from yggdrasil_lm.core.executor import ExecutionContext  #25 (line in Coconut source)
    from yggdrasil_lm.core.executor import TraceEvent  #25 (line in Coconut source)

# Top-level import so get_type_hints() can resolve WebSocket annotations when
# Coconut injects `from __future__ import annotations` into compiled output.
try:  #29 (line in Coconut source)
    from fastapi import WebSocket  # noqa: F401  #30 (line in Coconut source)
except ImportError:  #31 (line in Coconut source)
    pass  #32 (line in Coconut source)


_STATIC_DIR = Path(__file__).parent / "static"  #35 (line in Coconut source)

_RUNTIME_EVENT_TYPES = {"pause", "resume", "retry", "validation", "permission_denied", "checkpoint", "transaction", "approval_task", "lease", "schedule", "migration",}  #37 (line in Coconut source)


def _event_to_dict(event: "TraceEvent") -> dict[str, Any]:  #52 (line in Coconut source)
    """Convert a TraceEvent dataclass to a JSON-serializable dict."""  #53 (line in Coconut source)
    return {"event_type": event.event_type, "event_id": event.event_id, "parent_event_id": event.parent_event_id, "session_id": event.session_id, "node_id": event.node_id, "node_name": event.node_name, "timestamp": event.timestamp.isoformat(), "duration_ms": event.duration_ms, "payload": event.payload}  #54 (line in Coconut source)



def _node_to_dict(node: Any) -> dict[str, Any]:  #67 (line in Coconut source)
    data = node.model_dump(mode="json")  #68 (line in Coconut source)
    data["is_valid"] = node.is_valid  #69 (line in Coconut source)
    return data  #70 (line in Coconut source)



def _edge_to_dict(edge: Edge) -> dict[str, Any]:  #73 (line in Coconut source)
    data = edge.model_dump(mode="json")  #74 (line in Coconut source)
    data["is_valid"] = edge.is_valid  #75 (line in Coconut source)
    return data  #76 (line in Coconut source)



async def _store_to_snapshot(store: GraphStore) -> dict[str, Any]:  #79 (line in Coconut source)
    nodes = [_node_to_dict(node) for node in await store.list_nodes(only_valid=False)]  #80 (line in Coconut source)
    edges = [_edge_to_dict(edge) for edge in await store.list_edges(only_valid=False)]  #81 (line in Coconut source)

    nodes_by_type: dict[str, list[dict[str, Any]]] = {}  #83 (line in Coconut source)
    edges_by_type: dict[str, list[dict[str, Any]]] = {}  #84 (line in Coconut source)
    active_node_count = 0  #85 (line in Coconut source)
    active_edge_count = 0  #86 (line in Coconut source)

    for node in nodes:  #88 (line in Coconut source)
        node_type = str(node.get("node_type", "unknown"))  #89 (line in Coconut source)
        nodes_by_type.setdefault(node_type, []).append(node)  #90 (line in Coconut source)
        if node.get("is_valid"):  #91 (line in Coconut source)
            active_node_count += 1  #92 (line in Coconut source)

    for edge in edges:  #94 (line in Coconut source)
        edge_type = str(edge.get("edge_type", "unknown"))  #95 (line in Coconut source)
        edges_by_type.setdefault(edge_type, []).append(edge)  #96 (line in Coconut source)
        if edge.get("is_valid"):  #97 (line in Coconut source)
            active_edge_count += 1  #98 (line in Coconut source)

    return {"summary": {"node_count": len(nodes), "active_node_count": active_node_count, "edge_count": len(edges), "active_edge_count": active_edge_count, "node_type_counts": {key: len(value) for key, value in sorted(nodes_by_type.items())}, "edge_type_counts": {key: len(value) for key, value in sorted(edges_by_type.items())}}, "nodes": nodes, "edges": edges, "nodes_by_type": {key: sorted(value, key=lambda item: (item.get("name", ""), item.get("node_id", ""))) for key, value in sorted(nodes_by_type.items())}, "edges_by_type": {key: sorted(value, key=lambda item: (item.get("src_id", ""), item.get("dst_id", ""))) for key, value in sorted(edges_by_type.items())}}  #100 (line in Coconut source)



def _latest_event(events: list[dict[str, Any]], event_type: str) -> dict[str, Any] | None:  #126 (line in Coconut source)
    for event in reversed(events):  #127 (line in Coconut source)
        if event.get("event_type") == event_type:  #128 (line in Coconut source)
            return event  #129 (line in Coconut source)
    return None  #130 (line in Coconut source)



def _summarize_events(events: list[dict[str, Any]], *, session_id: str="", query: str="", finalized: bool=False, paused: bool=False,) -> dict[str, Any]:  #133 (line in Coconut source)
    counts = Counter((str(event.get("event_type", "unknown")) for event in events))  #141 (line in Coconut source)
    tool_errors = [event for event in events if event.get("event_type") == "tool_result" and event.get("payload", {}).get("success") is False]  #142 (line in Coconut source)
    fatal_errors = [event for event in events if event.get("event_type") == "error"]  #147 (line in Coconut source)
    low_conf_routes = [event for event in events if event.get("event_type") == "routing" and isinstance(event.get("payload", {}).get("confidence"), (int, float)) and float(event["payload"]["confidence"]) < 0.7]  #151 (line in Coconut source)
    validation_failures = [event for event in events if event.get("event_type") == "validation" and event.get("payload", {}).get("success") is False]  #157 (line in Coconut source)
    permission_denials = [event for event in events if event.get("event_type") == "permission_denied"]  #162 (line in Coconut source)
    latest_pause = _latest_event(events, "pause")  #163 (line in Coconut source)
    latest_approval = _latest_event(events, "approval_task")  #164 (line in Coconut source)
    latest_permission = _latest_event(events, "permission_denied")  #165 (line in Coconut source)
    latest_checkpoint = _latest_event(events, "checkpoint")  #166 (line in Coconut source)
    runtime_events = [event for event in events if event.get("event_type") in _RUNTIME_EVENT_TYPES]  #167 (line in Coconut source)

    current_node_id = ""  #169 (line in Coconut source)
    current_node_name = ""  #170 (line in Coconut source)
    if events:  #171 (line in Coconut source)
        current_node_id = str(events[-1].get("node_id", ""))  #172 (line in Coconut source)
        current_node_name = str(events[-1].get("node_name", ""))  #173 (line in Coconut source)

    if paused:  #175 (line in Coconut source)
        status = "paused"  #176 (line in Coconut source)
    elif fatal_errors:  #177 (line in Coconut source)
        status = "error"  #178 (line in Coconut source)
    elif finalized and (tool_errors or validation_failures or permission_denials):  #179 (line in Coconut source)
        status = "completed_with_issues"  #180 (line in Coconut source)
    elif finalized:  #181 (line in Coconut source)
        status = "completed"  #182 (line in Coconut source)
    elif counts:  #183 (line in Coconut source)
        status = "running"  #184 (line in Coconut source)
    else:  #185 (line in Coconut source)
        status = "waiting"  #186 (line in Coconut source)

    return {"status": status, "finalized": finalized, "session_id": session_id, "query": query, "current_node_id": current_node_id, "current_node_name": current_node_name, "selected_event_id": events[-1].get("event_id") if events else None, "counts": dict(sorted(counts.items())), "event_count": len(events), "error_count": len(tool_errors) + len(validation_failures) + len(permission_denials) + len(fatal_errors), "fatal_error_count": len(fatal_errors), "warning_count": len(low_conf_routes), "low_confidence_route_count": len(low_conf_routes), "pause_count": counts.get("pause", 0), "approval_count": counts.get("approval_task", 0), "checkpoint_count": counts.get("checkpoint", 0), "schedule_count": counts.get("schedule", 0), "runtime_event_count": len(runtime_events), "latest_pause": latest_pause, "latest_approval_task": latest_approval, "latest_permission_denied": latest_permission, "latest_checkpoint": latest_checkpoint}  #188 (line in Coconut source)



@_coconut_tco  #214 (line in Coconut source)
def _ctx_summary(ctx: "ExecutionContext", *, finalized: bool=False) -> dict[str, Any]:  #214 (line in Coconut source)
    return _coconut_tail_call(_summarize_events, [_event_to_dict(event) for event in ctx.trace], session_id=ctx.session_id, query=ctx.query, finalized=finalized, paused=ctx.is_paused())  #215 (line in Coconut source)



class VizServer():  #224 (line in Coconut source)
    """Self-contained visualizer server for a single execution session.

    Lifecycle:
        server = VizServer(port=7331)
        await server.start()          # starts uvicorn in a background thread
        server.open_browser()
        server.push_event(event)      # called by the event hook
        server.finalize(ctx)          # marks run complete, sends full snapshot
        await server.stop()
    """  #234 (line in Coconut source)

    def __init__(self, port: int=7331, open_browser: bool=True):  #236 (line in Coconut source)
        self.port = port  #237 (line in Coconut source)
        self.open_browser = open_browser  #238 (line in Coconut source)
        self._app = None  #239 (line in Coconut source)
        self._server = None  #240 (line in Coconut source)
        self._thread: threading.Thread | None = None  #241 (line in Coconut source)
        self._connections: list[Any] = []  # list of WebSocket connections  #242 (line in Coconut source)
        self._loop: asyncio.AbstractEventLoop | None = None  #243 (line in Coconut source)
        self._started = asyncio.Event()  #244 (line in Coconut source)
        self._metadata: dict[str, Any] = {}  #245 (line in Coconut source)
        self._summary: dict[str, Any] | None = None  #246 (line in Coconut source)
        self._finalized_snapshot: dict[str, Any] | None = None  #247 (line in Coconut source)
        self._event_log: list[dict[str, Any]] = []  # replay buffer for late-joining clients  #248 (line in Coconut source)
        self._store: GraphStore | None = None  #249 (line in Coconut source)
        self._graph_snapshot: dict[str, Any] | None = None  #250 (line in Coconut source)
        self._graph_refresh_in_flight = False  #251 (line in Coconut source)
        self._run_explanation: dict[str, Any] | None = None  #252 (line in Coconut source)

# ------------------------------------------------------------------
# Build the FastAPI app
# ------------------------------------------------------------------


    def _build_app(self) -> Any:  #258 (line in Coconut source)
        try:  #259 (line in Coconut source)
            from fastapi import FastAPI  #260 (line in Coconut source)
            from fastapi import WebSocket  #260 (line in Coconut source)
            from fastapi import WebSocketDisconnect  #260 (line in Coconut source)
            from fastapi.responses import HTMLResponse  #261 (line in Coconut source)
            from fastapi.staticfiles import StaticFiles  #262 (line in Coconut source)
        except ImportError as e:  #263 (line in Coconut source)
            raise ImportError("FastAPI is required for the browser trace visualizer. Install it with: pip install 'yggdrasil[viz]'") from e  #264 (line in Coconut source)

        app = FastAPI(title="Yggdrasil Trace Visualizer", docs_url=None, redoc_url=None)  #269 (line in Coconut source)
        app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")  #270 (line in Coconut source)

        @app.get("/", response_class=HTMLResponse)  #272 (line in Coconut source)
        async def index():  #273 (line in Coconut source)
            html_path = _STATIC_DIR / "index.html"  #274 (line in Coconut source)
            return HTMLResponse(content=html_path.read_text(encoding="utf-8"))  #275 (line in Coconut source)


        @app.get("/health")  #277 (line in Coconut source)
        async def health():  #278 (line in Coconut source)
            return {"status": "ok"}  #279 (line in Coconut source)


        @app.post("/explain")  #281 (line in Coconut source)
        async def explain(body: dict[str, Any]):  #282 (line in Coconut source)
            from fastapi.responses import JSONResponse  #283 (line in Coconut source)
            session_id = body.get("session_id", "")  #284 (line in Coconut source)
            stored_session = self._metadata.get("session_id", "")  #285 (line in Coconut source)
            if session_id and stored_session and session_id != stored_session:  #286 (line in Coconut source)
                return JSONResponse(status_code=404, content={"error": "session_id '{_coconut_format_0}' not found; active session is '{_coconut_format_1}'".format(_coconut_format_0=(session_id), _coconut_format_1=(stored_session))})  #287 (line in Coconut source)
            if self._run_explanation is None:  #291 (line in Coconut source)
                return JSONResponse(status_code=404, content={"error": "No explanation available yet; run has not been finalized"})  #292 (line in Coconut source)
            return self._run_explanation  #296 (line in Coconut source)


        @app.websocket("/ws")  #298 (line in Coconut source)
        async def websocket_endpoint(ws: WebSocket):  #299 (line in Coconut source)
            await ws.accept()  #300 (line in Coconut source)
            self._connections.append(ws)  #301 (line in Coconut source)
# Send current state to late-joining browsers so they sync up
            if self._metadata:  #303 (line in Coconut source)
                try:  #304 (line in Coconut source)
                    await ws.send_json({"type": "meta", "data": self._metadata})  #305 (line in Coconut source)
                except Exception:  #306 (line in Coconut source)
                    pass  #307 (line in Coconut source)
            if self._summary:  #308 (line in Coconut source)
                try:  #309 (line in Coconut source)
                    await ws.send_json({"type": "summary", "data": self._summary})  #310 (line in Coconut source)
                except Exception:  #311 (line in Coconut source)
                    pass  #312 (line in Coconut source)
# Replay any events emitted before this browser connected
            for event_msg in list(self._event_log):  #314 (line in Coconut source)
                try:  #315 (line in Coconut source)
                    await ws.send_json(event_msg)  #316 (line in Coconut source)
                except Exception:  #317 (line in Coconut source)
                    break  #318 (line in Coconut source)
            if self._graph_snapshot:  #319 (line in Coconut source)
                try:  #320 (line in Coconut source)
                    await ws.send_json({"type": "graph_state", "data": self._graph_snapshot})  #321 (line in Coconut source)
                except Exception:  #322 (line in Coconut source)
                    pass  #323 (line in Coconut source)
            if self._finalized_snapshot:  #324 (line in Coconut source)
                try:  #325 (line in Coconut source)
                    await ws.send_json({"type": "finalize", "data": self._finalized_snapshot})  #326 (line in Coconut source)
                except Exception:  #327 (line in Coconut source)
                    pass  #328 (line in Coconut source)
            try:  #329 (line in Coconut source)
                while True:  #330 (line in Coconut source)
# Keep alive; client sends pings
                    await ws.receive_text()  #332 (line in Coconut source)
            except WebSocketDisconnect:  #333 (line in Coconut source)
                pass  #334 (line in Coconut source)
            finally:  #335 (line in Coconut source)
                if ws in self._connections:  #336 (line in Coconut source)
                    self._connections.remove(ws)  #337 (line in Coconut source)


        return app  #339 (line in Coconut source)

# ------------------------------------------------------------------
# Start / stop
# ------------------------------------------------------------------


    async def start(self) -> None:  #345 (line in Coconut source)
        """Start the uvicorn server in a daemon thread."""  #346 (line in Coconut source)
        try:  #347 (line in Coconut source)
            import uvicorn  #348 (line in Coconut source)
        except ImportError as e:  #349 (line in Coconut source)
            raise ImportError("uvicorn is required for the browser trace visualizer. Install it with: pip install 'yggdrasil[viz]'") from e  #350 (line in Coconut source)

        self._app = self._build_app()  #355 (line in Coconut source)

        config = uvicorn.Config(self._app, host="127.0.0.1", port=self.port, log_level="error", loop="asyncio")  #357 (line in Coconut source)
        self._server = uvicorn.Server(config)  #364 (line in Coconut source)

        loop_ready = threading.Event()  # daemon loop is up; _loop is set  #366 (line in Coconut source)
        bind_ready = threading.Event()  # uvicorn has bound to the port  #367 (line in Coconut source)

        def run():  #369 (line in Coconut source)
            loop = asyncio.new_event_loop()  #370 (line in Coconut source)
            asyncio.set_event_loop(loop)  #371 (line in Coconut source)
# Capture the daemon loop so push_event schedules on the right loop
# (the one that owns the WebSocket connections).
            self._loop = loop  #374 (line in Coconut source)
            loop_ready.set()  #375 (line in Coconut source)

            async def _serve():  #377 (line in Coconut source)
# Start serving in the background so we can poll server.started
# before signalling bind_ready.  ready.set() used to fire before
# serve() even ran, leaving a race window where the browser
# would try to connect before the socket was bound.
                serve_task = asyncio.create_task(self._server.serve())  #382 (line in Coconut source)
                while not self._server.started:  #383 (line in Coconut source)
                    await asyncio.sleep(0.01)  #384 (line in Coconut source)
                bind_ready.set()  #385 (line in Coconut source)
                await serve_task  #386 (line in Coconut source)


            loop.run_until_complete(_serve())  #388 (line in Coconut source)


        self._thread = threading.Thread(target=run, daemon=True)  #390 (line in Coconut source)
        self._thread.start()  #391 (line in Coconut source)

# Wait for the daemon loop to start, then for uvicorn to bind.
        loop_ready.wait(timeout=5.0)  #394 (line in Coconut source)
        bind_ready.wait(timeout=5.0)  #395 (line in Coconut source)

        if self.open_browser:  #397 (line in Coconut source)
            self.launch_browser()  #398 (line in Coconut source)


    async def stop(self) -> None:  #400 (line in Coconut source)
        """Signal the server to shut down."""  #401 (line in Coconut source)
        if self._server:  #402 (line in Coconut source)
            self._server.should_exit = True  #403 (line in Coconut source)


    def launch_browser(self) -> None:  #405 (line in Coconut source)
        webbrowser.open("http://127.0.0.1:{_coconut_format_0}".format(_coconut_format_0=(self.port)))  #406 (line in Coconut source)

# ------------------------------------------------------------------
# Event streaming
# ------------------------------------------------------------------


    def set_metadata(self, *, session_id: str, query: str) -> None:  #412 (line in Coconut source)
        self._metadata = {"session_id": session_id, "query": query}  #413 (line in Coconut source)
        self._summary = _summarize_events(self._event_log_as_events(), session_id=session_id, query=query, finalized=False)  #414 (line in Coconut source)
        if self._loop and self._loop.is_running():  #420 (line in Coconut source)
            asyncio.run_coroutine_threadsafe(self._broadcast({"type": "meta", "data": self._metadata}), self._loop)  #421 (line in Coconut source)
            if self._summary:  #425 (line in Coconut source)
                asyncio.run_coroutine_threadsafe(self._broadcast({"type": "summary", "data": self._summary}), self._loop)  #426 (line in Coconut source)


    def attach_store(self, store: GraphStore) -> None:  #431 (line in Coconut source)
        self._store = store  #432 (line in Coconut source)
        if self._loop and self._loop.is_running():  #433 (line in Coconut source)
            asyncio.run_coroutine_threadsafe(self._refresh_graph_snapshot(), self._loop)  #434 (line in Coconut source)


    def refresh_graph_state(self) -> None:  #436 (line in Coconut source)
        if self._store and self._loop and self._loop.is_running() and not self._graph_refresh_in_flight:  #437 (line in Coconut source)
            asyncio.run_coroutine_threadsafe(self._refresh_graph_snapshot(), self._loop)  #438 (line in Coconut source)


    def push_event(self, event: "TraceEvent", ctx: "ExecutionContext") -> None:  #440 (line in Coconut source)
        """Sync entry point called by the GraphExecutor event hook."""  #441 (line in Coconut source)
        msg = {"type": "event", "data": _event_to_dict(event)}  #442 (line in Coconut source)
        self._event_log.append(msg)  #443 (line in Coconut source)
        is_fatal = event.event_type == "error"  #444 (line in Coconut source)
        self._summary = _ctx_summary(ctx, finalized=is_fatal)  #445 (line in Coconut source)
        if self._loop and self._loop.is_running():  #446 (line in Coconut source)
            asyncio.run_coroutine_threadsafe(self._broadcast(msg), self._loop)  #447 (line in Coconut source)
            if self._summary:  #448 (line in Coconut source)
                asyncio.run_coroutine_threadsafe(self._broadcast({"type": "summary", "data": self._summary}), self._loop)  #449 (line in Coconut source)
            self.refresh_graph_state()  #453 (line in Coconut source)
            if is_fatal:  #454 (line in Coconut source)
                asyncio.run_coroutine_threadsafe(self.finalize(ctx), self._loop)  #455 (line in Coconut source)


    async def push_event_async(self, event: "TraceEvent", ctx: "ExecutionContext") -> None:  #457 (line in Coconut source)
        """Async variant (called when hook is awaited)."""  #458 (line in Coconut source)
        msg = {"type": "event", "data": _event_to_dict(event)}  #459 (line in Coconut source)
        self._event_log.append(msg)  #460 (line in Coconut source)
        is_fatal = event.event_type == "error"  #461 (line in Coconut source)
        self._summary = _ctx_summary(ctx, finalized=is_fatal)  #462 (line in Coconut source)
        await self._broadcast(msg)  #463 (line in Coconut source)
        if self._summary:  #464 (line in Coconut source)
            await self._broadcast({"type": "summary", "data": self._summary})  #465 (line in Coconut source)
        await self._refresh_graph_snapshot()  #466 (line in Coconut source)
        if is_fatal:  #467 (line in Coconut source)
            await self.finalize(ctx)  #468 (line in Coconut source)


    async def finalize(self, ctx: "ExecutionContext", store: GraphStore | None=None) -> None:  #470 (line in Coconut source)
        """Send the full trace snapshot once execution completes."""  #471 (line in Coconut source)
        snapshot_store = store or self._store  #472 (line in Coconut source)
        graph_state = await _store_to_snapshot(snapshot_store) if snapshot_store else None  #473 (line in Coconut source)
        if graph_state is not None:  #474 (line in Coconut source)
            self._graph_snapshot = graph_state  #475 (line in Coconut source)
        import dataclasses as _dc  #476 (line in Coconut source)
        self._run_explanation = _dc.asdict(explain_run(ctx))  #477 (line in Coconut source)
        snapshot = {"session_id": ctx.session_id, "query": ctx.query, "hop_count": ctx.hop_count, "events": [_event_to_dict(e) for e in ctx.trace], "summary": _ctx_summary(ctx, finalized=True), "graph_state": graph_state}  #478 (line in Coconut source)
        self._summary = snapshot["summary"]  #486 (line in Coconut source)
        self._finalized_snapshot = snapshot  #487 (line in Coconut source)
        msg = {"type": "finalize", "data": snapshot}  #488 (line in Coconut source)
        if self._loop and self._loop.is_running():  #489 (line in Coconut source)
# Called from the main event loop — schedule broadcast on the
# server's own daemon loop to avoid cross-loop WebSocket issues.
            asyncio.run_coroutine_threadsafe(self._broadcast({"type": "summary", "data": self._summary}), self._loop)  #492 (line in Coconut source)
            asyncio.run_coroutine_threadsafe(self._broadcast(msg), self._loop)  #496 (line in Coconut source)
# Yield briefly so the daemon loop can process the broadcast.
            await asyncio.sleep(0.1)  #498 (line in Coconut source)
        else:  #499 (line in Coconut source)
            await self._broadcast({"type": "summary", "data": self._summary})  #500 (line in Coconut source)
            await self._broadcast(msg)  #501 (line in Coconut source)


    async def _refresh_graph_snapshot(self) -> None:  #503 (line in Coconut source)
        if not self._store or self._graph_refresh_in_flight:  #504 (line in Coconut source)
            return  #505 (line in Coconut source)
        self._graph_refresh_in_flight = True  #506 (line in Coconut source)
        try:  #507 (line in Coconut source)
            snapshot = await _store_to_snapshot(self._store)  #508 (line in Coconut source)
            self._graph_snapshot = snapshot  #509 (line in Coconut source)
            await self._broadcast({"type": "graph_state", "data": snapshot})  #510 (line in Coconut source)
        finally:  #511 (line in Coconut source)
            self._graph_refresh_in_flight = False  #512 (line in Coconut source)


    async def _broadcast(self, msg: dict[str, Any]) -> None:  #514 (line in Coconut source)
        if not self._connections:  #515 (line in Coconut source)
            return  #516 (line in Coconut source)
        payload = json.dumps(msg, default=str)  #517 (line in Coconut source)
        dead: list[Any] = []  #518 (line in Coconut source)
        for ws in list(self._connections):  #519 (line in Coconut source)
            try:  #520 (line in Coconut source)
                await ws.send_text(payload)  #521 (line in Coconut source)
            except Exception:  #522 (line in Coconut source)
                dead.append(ws)  #523 (line in Coconut source)
        for ws in dead:  #524 (line in Coconut source)
            if ws in self._connections:  #525 (line in Coconut source)
                self._connections.remove(ws)  #526 (line in Coconut source)


    def _event_log_as_events(self) -> list[dict[str, Any]]:  #528 (line in Coconut source)
        return [message["data"] for message in self._event_log if message.get("type") == "event"]  #529 (line in Coconut source)


# ---------------------------------------------------------------------------
# serve_trace() — post-run entry point
# ---------------------------------------------------------------------------


async def serve_trace(ctx: "ExecutionContext", *, store: GraphStore | None=None, port: int=7331, open_browser: bool=True, wait: bool=True, wait_seconds: int=0,) -> None:  #536 (line in Coconut source)
    """Open a browser tab showing the full post-run trace.

    Args:
        ctx:          ExecutionContext returned by executor.run().
        port:         Local port to bind (default 7331).
        open_browser: Open the default browser automatically (default True).
        wait:         Block until Ctrl-C if True. Set to False in scripts.
        wait_seconds: If > 0 and wait=True, automatically stop after N seconds.

    Example:
        ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
        await serve_trace(ctx)
    """  #557 (line in Coconut source)
    server = VizServer(port=port, open_browser=open_browser)  #558 (line in Coconut source)
    await server.start()  #559 (line in Coconut source)
    if store is not None:  #560 (line in Coconut source)
        server.attach_store(store)  #561 (line in Coconut source)
    server.set_metadata(session_id=ctx.session_id, query=ctx.query)  #562 (line in Coconut source)
    await server.finalize(ctx, store=store)  #563 (line in Coconut source)

    print("\nYggdrasil Trace Visualizer running at http://127.0.0.1:{_coconut_format_0}".format(_coconut_format_0=(port)))  #565 (line in Coconut source)
    print("Press Ctrl-C to stop.\n")  #566 (line in Coconut source)

    if wait:  #568 (line in Coconut source)
        try:  #569 (line in Coconut source)
            if wait_seconds > 0:  #570 (line in Coconut source)
                await asyncio.sleep(wait_seconds)  #571 (line in Coconut source)
            else:  #572 (line in Coconut source)
                await asyncio.Event().wait()  # block forever  #573 (line in Coconut source)
        except (KeyboardInterrupt, asyncio.CancelledError):  #574 (line in Coconut source)
            pass  #575 (line in Coconut source)

    await server.stop()  #577 (line in Coconut source)


# ---------------------------------------------------------------------------
# live_trace() — context manager for streaming during execution
# ---------------------------------------------------------------------------


class _LiveTraceCtx():  #584 (line in Coconut source)
    """Returned by live_trace() — attach the executor inside the 'async with' block."""  #585 (line in Coconut source)

    def __init__(self, server: VizServer):  #587 (line in Coconut source)
        self._server = server  #588 (line in Coconut source)
        self._ctx: "ExecutionContext | None" = None  #589 (line in Coconut source)


    def attach(self, executor: Any, ctx: "ExecutionContext") -> None:  #591 (line in Coconut source)
        """Wire the executor's event hook to stream events via WebSocket."""  #592 (line in Coconut source)
        self._ctx = ctx  #593 (line in Coconut source)
        self._server.set_metadata(session_id=ctx.session_id, query=ctx.query)  #594 (line in Coconut source)
        executor.add_event_hook(self._server.push_event)  #595 (line in Coconut source)


    @property  #597 (line in Coconut source)
    @_coconut_tco  #598 (line in Coconut source)
    def url(self) -> str:  #598 (line in Coconut source)
        return _coconut_tail_call("http://127.0.0.1:{_coconut_format_0}".format, _coconut_format_0=(self._server.port))  #599 (line in Coconut source)



class live_trace():  #602 (line in Coconut source)
    """Async context manager: start the visualizer, stream events during a run.

    Usage:
        async with live_trace(executor) as viz:
            ctx = await executor.run(entry_node_id=agent.node_id, query="hello")
        # Browser tab stays open; press Ctrl-C to exit

    Or with custom port and no auto-wait:
        async with live_trace(executor, port=8080, wait=False) as viz:
            ctx = await executor.run(...)
        await serve_trace(ctx, port=8080, wait=True)
    """  #614 (line in Coconut source)

    def __init__(self, executor: Any, *, port: int=7331, open_browser: bool=True, wait: bool=True, wait_seconds: int=0,):  #616 (line in Coconut source)
        self._executor = executor  #625 (line in Coconut source)
        self._port = port  #626 (line in Coconut source)
        self._open_browser = open_browser  #627 (line in Coconut source)
        self._wait = wait  #628 (line in Coconut source)
        self._wait_seconds = wait_seconds  #629 (line in Coconut source)
        self._server: VizServer | None = None  #630 (line in Coconut source)
        self._ctx_wrapper: _LiveTraceCtx | None = None  #631 (line in Coconut source)


    async def __aenter__(self) -> _LiveTraceCtx:  #633 (line in Coconut source)
        self._server = VizServer(port=self._port, open_browser=self._open_browser)  #634 (line in Coconut source)
        await self._server.start()  #635 (line in Coconut source)
        self._server.attach_store(self._executor.store)  #636 (line in Coconut source)
        self._ctx_wrapper = _LiveTraceCtx(self._server)  #637 (line in Coconut source)

# Monkey-patch executor.run to auto-attach on first call
        _orig_run = self._executor.run  #640 (line in Coconut source)
        _wrapper = self  #641 (line in Coconut source)

        async def _patched_run(entry_node_id, query, **kwargs):  #643 (line in Coconut source)
            ctx = await _orig_run(entry_node_id=entry_node_id, query=query, **kwargs)  #644 (line in Coconut source)
            _wrapper._ctx_wrapper._ctx = ctx  #645 (line in Coconut source)
            await _wrapper._server.finalize(ctx, store=_wrapper._executor.store)  #646 (line in Coconut source)
            return ctx  #647 (line in Coconut source)

# Register event hook before run so live events stream

        self._executor.add_event_hook(self._server.push_event)  #650 (line in Coconut source)
        self._executor._patched_run = _patched_run  #651 (line in Coconut source)
        self._executor.run = _patched_run  # type: ignore[method-assign]  #652 (line in Coconut source)
        self._executor._orig_run = _orig_run  #653 (line in Coconut source)

        print("\nYggdrasil Trace Visualizer running at http://127.0.0.1:{_coconut_format_0}".format(_coconut_format_0=(self._port)))  #655 (line in Coconut source)
        return self._ctx_wrapper  #656 (line in Coconut source)


    async def __aexit__(self, *_) -> None:  #658 (line in Coconut source)
# Restore original run
        if hasattr(self._executor, "_orig_run"):  #660 (line in Coconut source)
            self._executor.run = self._executor._orig_run  #661 (line in Coconut source)

        if self._wait and self._server:  #663 (line in Coconut source)
            print("Press Ctrl-C to stop the visualizer.\n")  #664 (line in Coconut source)
            try:  #665 (line in Coconut source)
                if self._wait_seconds > 0:  #666 (line in Coconut source)
                    await asyncio.sleep(self._wait_seconds)  #667 (line in Coconut source)
                else:  #668 (line in Coconut source)
                    await asyncio.Event().wait()  #669 (line in Coconut source)
            except (KeyboardInterrupt, asyncio.CancelledError):  #670 (line in Coconut source)
                pass  #671 (line in Coconut source)
            await self._server.stop()  #672 (line in Coconut source)
# When wait=False the caller is responsible for keeping the process alive;
# the uvicorn daemon thread stays running until the process exits.
