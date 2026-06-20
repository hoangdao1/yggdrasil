#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xfde019c7

# Compiled with Coconut version 3.2.0

"""Agent composition and graph execution engine.

Key components:
- AgentComposer  — discovers an agent's tools/context/prompt by traversing edges
- ComposedAgent  — assembled runtime configuration for a single agent invocation
- ExecutionContext — shared mutable state that flows through the graph during a run
- GraphExecutor  — dispatches nodes and follows routing edges to traverse the graph
- TraceEvent     — structured, typed execution event for full observability
- print_trace()  — render a session trace as a human-readable execution tree

Execution strategies:
- sequential  : DFS — run node, route to next, repeat (default for chains)
- parallel    : BFS fan-out — gather all DELEGATES_TO targets concurrently
- topological : DAG waves — graphlib.TopologicalSorter for explicit pipelines
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



import asyncio  #17 (line in Coconut source)
import graphlib  #18 (line in Coconut source)
import inspect  #19 (line in Coconut source)
import json  #20 (line in Coconut source)
import logging  #21 (line in Coconut source)
import re  #22 (line in Coconut source)
import time  #23 (line in Coconut source)
import uuid  #24 (line in Coconut source)
from collections import deque  #25 (line in Coconut source)
from dataclasses import dataclass  #26 (line in Coconut source)
from dataclasses import field  #26 (line in Coconut source)
from datetime import datetime  #27 (line in Coconut source)
from datetime import timedelta  #27 (line in Coconut source)
from datetime import timezone  #27 (line in Coconut source)
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
if _coconut.typing.TYPE_CHECKING:  #28 (line in Coconut source)
    from typing import Literal  #28 (line in Coconut source)
else:  #28 (line in Coconut source)
    try:  #28 (line in Coconut source)
        Literal = _coconut.typing.Literal  #28 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #28 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #28 (line in Coconut source)

from yggdrasil_lm.backends.llm import LLMBackend  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import ToolResult  #30 (line in Coconut source)
from yggdrasil_lm.backends.llm import default_backend  #30 (line in Coconut source)
from yggdrasil_lm.core.edges import Edge  #31 (line in Coconut source)
from yggdrasil_lm.core.edges import EdgeType  #31 (line in Coconut source)
from yggdrasil_lm.core.nodes import AgentNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ApprovalNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import AnyNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ConstraintRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ContextNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import DecisionRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import DecisionTable  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ExecutionPolicy  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import GraphNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import NodeType  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import PromptNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ReasonerNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import RouteRule  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import SchemaNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import ToolNode  #32 (line in Coconut source)
from yggdrasil_lm.core.nodes import TransformNode  #32 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #50 (line in Coconut source)
from yggdrasil_lm.core.store import _cosine  #50 (line in Coconut source)
from yggdrasil_lm.core.store import _normalize  #50 (line in Coconut source)


# ---------------------------------------------------------------------------
# TraceEvent — structured, typed execution event
# ---------------------------------------------------------------------------

EventType = Literal["agent_start", "agent_end", "tool_call", "tool_result", "routing", "context_inject", "hop", "subgraph_enter", "subgraph_exit", "pause", "resume", "retry", "validation", "permission_denied", "checkpoint", "transaction", "approval_task", "lease", "schedule", "migration", "error",]  #57 (line in Coconut source)

_log = logging.getLogger(__name__)  #81 (line in Coconut source)

# Type alias for multimodal query content (mirrors the Anthropic Messages API).
# A plain str is treated as a single text block.  A list follows the Anthropic
# content-block schema: {"type": "text", "text": "..."} or
# {"type": "image", "source": {"type": "base64"|"url", ...}}.
QueryContent = str | list[dict[str, Any]]  #87 (line in Coconut source)


@_coconut_tco  #90 (line in Coconut source)
def _query_text(query: QueryContent) -> str:  #90 (line in Coconut source)
    """Extract the plain-text portion of a query for routing and context scoring."""  #91 (line in Coconut source)
    _coconut_case_match_to_0 = query  #92 (line in Coconut source)
    _coconut_case_match_check_0 = False  #92 (line in Coconut source)
    _coconut_match_temp_0 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #92 (line in Coconut source)
    _coconut_case_match_check_0 = True  #92 (line in Coconut source)
    if _coconut_case_match_check_0:  #92 (line in Coconut source)
        _coconut_case_match_check_0 = False  #92 (line in Coconut source)
        if not _coconut_case_match_check_0:  #92 (line in Coconut source)
            if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #92 (line in Coconut source)
                _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #92 (line in Coconut source)
                if _coconut_match_temp_1:  #92 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #92 (line in Coconut source)

        if not _coconut_case_match_check_0:  #92 (line in Coconut source)
            if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #92 (line in Coconut source)
                _coconut_case_match_check_0 = True  #92 (line in Coconut source)
            if _coconut_case_match_check_0:  #92 (line in Coconut source)
                _coconut_case_match_check_0 = False  #92 (line in Coconut source)
                if not _coconut_case_match_check_0:  #92 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #92 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #92 (line in Coconut source)

                if not _coconut_case_match_check_0:  #92 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #92 (line in Coconut source)
                        _coconut_match_temp_2 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #92 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #92 (line in Coconut source)
                            raise _coconut.TypeError("str.__match_args__ must be a tuple")  #92 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_2) < 0:  #92 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #92 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #92 (line in Coconut source)




    if _coconut_case_match_check_0:  #92 (line in Coconut source)
        return query  #94 (line in Coconut source)
    if not _coconut_case_match_check_0:  #95 (line in Coconut source)
        _coconut_case_match_check_0 = True  #95 (line in Coconut source)
        if _coconut_case_match_check_0:  #95 (line in Coconut source)
            return _coconut_tail_call(" ".join, (block.get("text", "") for block in query if block.get("type") == "text"))  #96 (line in Coconut source)



@dataclass  #99 (line in Coconut source)
class TraceEvent():  #100 (line in Coconut source)
    """A single typed event in the execution trace.

    Events form a tree via parent_event_id:
    - agent_start spawns child events (context_inject, tool_call, tool_result, routing)
    - agent_end closes the agent_start span with duration_ms
    - hop records sequential graph traversal steps

    Payload keys per event_type:
    - agent_start:     model, tools (list[str]), context (list[str]), query
    - agent_end:       text_summary (str), intent (str), iterations (int)
    - tool_call:       tool_name (str), callable_ref (str), input (dict)
    - tool_result:     tool_name (str), output_summary (str), success (bool)
    - routing:         intent (str), next_node_id (str|None), confidence (float|None)
    - context_inject:  context_names (list[str]), count (int)
    - hop:             hop (int), node_type (str), summary (str)
    - subgraph_enter:  entry_node_id (str)
    - subgraph_exit:   exit_node_id (str), summary (str)
    """  #118 (line in Coconut source)

    event_type: EventType  #120 (line in Coconut source)
    session_id: str  #121 (line in Coconut source)
    node_id: str  #122 (line in Coconut source)
    node_name: str  #123 (line in Coconut source)
    timestamp: datetime  #124 (line in Coconut source)
    payload: dict[str, Any]  #125 (line in Coconut source)
    event_id: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #126 (line in Coconut source)
    parent_event_id: str | None = None  #127 (line in Coconut source)
    duration_ms: int | None = None  #128 (line in Coconut source)


# ---------------------------------------------------------------------------
# RoutingDecision — white-box routing result
# ---------------------------------------------------------------------------

class RoutingDecision(_coconut.collections.namedtuple("RoutingDecision", ('agent_id', 'reason', 'confidence'))):  #135 (line in Coconut source)
    """LLM routing decision with explicit reasoning and confidence.

    Returned by GraphExecutor.route() / plan() so callers can inspect and
    debug every dispatch choice before (or instead of) executing.
    """  #140 (line in Coconut source)

    __slots__ = ()  #142 (line in Coconut source)
    _coconut_is_data = True  #142 (line in Coconut source)
    __match_args__ = ('agent_id', 'reason', 'confidence')  #142 (line in Coconut source)
    def __add__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    def __mul__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    def __rmul__(self, other): return _coconut.NotImplemented  #142 (line in Coconut source)
    __ne__ = _coconut.object.__ne__  #142 (line in Coconut source)
    def __eq__(self, other):  #142 (line in Coconut source)
        return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)  #142 (line in Coconut source)
    def __hash__(self):  #142 (line in Coconut source)
        return _coconut.tuple.__hash__(self) ^ _coconut.hash(self.__class__)  #142 (line in Coconut source)
    @property  #142 (line in Coconut source)
    def low_confidence_warning(self) -> str | None:  #143 (line in Coconut source)
        """Non-None when confidence is below 0.7."""  #144 (line in Coconut source)
        if self.confidence < 0.7:  #145 (line in Coconut source)
            return (("Low-confidence routing ({_coconut_format_0:.0%}) — ".format(_coconut_format_0=(self.confidence)) + "consider specifying the agent explicitly."))  #146 (line in Coconut source)
        return None  #150 (line in Coconut source)


# ---------------------------------------------------------------------------
# AgentResult — structured execution envelope
# ---------------------------------------------------------------------------


@dataclass  #157 (line in Coconut source)
class AgentResult():  #158 (line in Coconut source)
    """Execution envelope returned by GraphExecutor.execute()."""  #159 (line in Coconut source)

    routed_to: str  #161 (line in Coconut source)
    reason: str  #162 (line in Coconut source)
    confidence: float  #163 (line in Coconut source)
    context_injected: list[str]  #164 (line in Coconut source)
    result: str  #165 (line in Coconut source)
    low_confidence_warning: str | None = None  #166 (line in Coconut source)


@dataclass  #169 (line in Coconut source)
class WorkflowPause():  #170 (line in Coconut source)
    """Represents a paused workflow waiting for external input or approval."""  #171 (line in Coconut source)

    reason: str  #173 (line in Coconut source)
    node_id: str  #174 (line in Coconut source)
    node_name: str = ""  #175 (line in Coconut source)
    token: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #176 (line in Coconut source)
    waiting_for: str | None = None  #177 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #178 (line in Coconut source)


@dataclass  #181 (line in Coconut source)
class ApprovalTask():  #182 (line in Coconut source)
    """Inbox item created by an ApprovalNode."""  #183 (line in Coconut source)

    task_id: str  #185 (line in Coconut source)
    node_id: str  #186 (line in Coconut source)
    token: str  #187 (line in Coconut source)
    status: str = "pending"  #188 (line in Coconut source)
    assignees: list[str] = field(default_factory=list)  #189 (line in Coconut source)
    assigned_to: str | None = None  #190 (line in Coconut source)
    waiting_for: str | None = None  #191 (line in Coconut source)
    due_at: datetime | None = None  #192 (line in Coconut source)
    escalation_target: str | None = None  #193 (line in Coconut source)
    created_at: datetime = field(default_factory=lambda _=None: datetime.now(timezone.utc))  #194 (line in Coconut source)
    resolved_at: datetime | None = None  #195 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #196 (line in Coconut source)


@dataclass  #199 (line in Coconut source)
class WorkflowState():  #200 (line in Coconut source)
    """Typed workflow state carried between nodes."""  #201 (line in Coconut source)

    data: dict[str, Any] = field(default_factory=dict)  #203 (line in Coconut source)
    schema: dict[str, Any] = field(default_factory=dict)  #204 (line in Coconut source)
    status: str = "running"  #205 (line in Coconut source)
    graph_version: str = "v1"  #206 (line in Coconut source)
    pending_pause: WorkflowPause | None = None  #207 (line in Coconut source)
    inbox: dict[str, ApprovalTask] = field(default_factory=dict)  #208 (line in Coconut source)
    idempotency_cache: dict[str, Any] = field(default_factory=dict)  #209 (line in Coconut source)
    metadata: dict[str, Any] = field(default_factory=dict)  #210 (line in Coconut source)


# ---------------------------------------------------------------------------
# ExecutionContext — flows through the graph during a run
# ---------------------------------------------------------------------------

@dataclass  #217 (line in Coconut source)
class ExecutionContext():  #218 (line in Coconut source)
    """Shared mutable state for a single graph traversal.

    Every node reads from and writes to this object.
    The trace list records the full execution history as structured TraceEvent
    objects so callers can inspect, render, or replay exactly what happened.
    """  #224 (line in Coconut source)

    query: QueryContent  #226 (line in Coconut source)
    session_id: str = field(default_factory=lambda _=None: str(uuid.uuid4()))  #227 (line in Coconut source)
    outputs: dict[str, Any] = field(default_factory=dict)  #228 (line in Coconut source)
    trace: list[TraceEvent] = field(default_factory=list)  #229 (line in Coconut source)
    max_hops: int = 20  #230 (line in Coconut source)
    hop_count: int = 0  #231 (line in Coconut source)

    extra_messages: list[dict[str, Any]] = field(default_factory=list)  #233 (line in Coconut source)
    state: WorkflowState = field(default_factory=WorkflowState)  #234 (line in Coconut source)
    allowed_tools: set[str] | None = None  #235 (line in Coconut source)
    _active_subgraphs: list[str] = field(default_factory=list)  #236 (line in Coconut source)

    def is_paused(self) -> bool:  #238 (line in Coconut source)
        return self.state.status == "paused"  #239 (line in Coconut source)


    def snapshot(self) -> dict[str, Any]:  #241 (line in Coconut source)
        """Serialize the execution context for durable checkpointing."""  #242 (line in Coconut source)
        return {"query": self.query, "session_id": self.session_id, "outputs": self.outputs, "trace": [{"event_type": event.event_type, "session_id": event.session_id, "node_id": event.node_id, "node_name": event.node_name, "timestamp": event.timestamp.isoformat(), "payload": event.payload, "event_id": event.event_id, "parent_event_id": event.parent_event_id, "duration_ms": event.duration_ms} for event in self.trace], "max_hops": self.max_hops, "hop_count": self.hop_count, "extra_messages": self.extra_messages, "state": {"data": self.state.data, "schema": self.state.schema, "status": self.state.status, "graph_version": self.state.graph_version, "pending_pause": None if self.state.pending_pause is None else {"reason": self.state.pending_pause.reason, "node_id": self.state.pending_pause.node_id, "node_name": self.state.pending_pause.node_name, "token": self.state.pending_pause.token, "waiting_for": self.state.pending_pause.waiting_for, "metadata": self.state.pending_pause.metadata}, "inbox": {task_id: {"task_id": task.task_id, "node_id": task.node_id, "token": task.token, "status": task.status, "assignees": task.assignees, "assigned_to": task.assigned_to, "waiting_for": task.waiting_for, "due_at": task.due_at.isoformat() if task.due_at else None, "escalation_target": task.escalation_target, "created_at": task.created_at.isoformat(), "resolved_at": task.resolved_at.isoformat() if task.resolved_at else None, "metadata": task.metadata} for task_id, task in self.state.inbox.items()}, "idempotency_cache": self.state.idempotency_cache, "metadata": self.state.metadata}, "allowed_tools": sorted(self.allowed_tools) if self.allowed_tools is not None else None}  #243 (line in Coconut source)


    @classmethod  #300 (line in Coconut source)
    @_coconut_tco  #301 (line in Coconut source)
    def from_snapshot(cls, data: dict[str, Any]) -> "ExecutionContext":  #301 (line in Coconut source)
        """Restore an execution context from snapshot data."""  #302 (line in Coconut source)
        raw_state = data.get("state", {})  #303 (line in Coconut source)
        pending_pause = raw_state.get("pending_pause")  #304 (line in Coconut source)
        state = WorkflowState(data=raw_state.get("data", {}), schema=raw_state.get("schema", {}), status=raw_state.get("status", "running"), graph_version=raw_state.get("graph_version", "v1"), pending_pause=(WorkflowPause(reason=pending_pause.get("reason", ""), node_id=pending_pause.get("node_id", ""), node_name=pending_pause.get("node_name", ""), token=pending_pause.get("token", str(uuid.uuid4())), waiting_for=pending_pause.get("waiting_for"), metadata=pending_pause.get("metadata", {})) if pending_pause else None), inbox={task_id: ApprovalTask(task_id=item.get("task_id", task_id), node_id=item.get("node_id", ""), token=item.get("token", str(uuid.uuid4())), status=item.get("status", "pending"), assignees=item.get("assignees", []), assigned_to=item.get("assigned_to"), waiting_for=item.get("waiting_for"), due_at=(datetime.fromisoformat(item["due_at"]) if item.get("due_at") else None), escalation_target=item.get("escalation_target"), created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.now(timezone.utc), resolved_at=(datetime.fromisoformat(item["resolved_at"]) if item.get("resolved_at") else None), metadata=item.get("metadata", {})) for task_id, item in raw_state.get("inbox", {}).items()}, idempotency_cache=raw_state.get("idempotency_cache", {}), metadata=raw_state.get("metadata", {}))  #305 (line in Coconut source)
        return _coconut_tail_call(cls, query=data.get("query", ""), session_id=data.get("session_id", str(uuid.uuid4())), outputs=data.get("outputs", {}), trace=[TraceEvent(event_type=item["event_type"], session_id=item.get("session_id", data.get("session_id", "")), node_id=item.get("node_id", ""), node_name=item.get("node_name", ""), timestamp=datetime.fromisoformat(item["timestamp"]), payload=item.get("payload", {}), event_id=item.get("event_id", str(uuid.uuid4())), parent_event_id=item.get("parent_event_id"), duration_ms=item.get("duration_ms")) for item in data.get("trace", [])], max_hops=data.get("max_hops", 20), hop_count=data.get("hop_count", 0), extra_messages=data.get("extra_messages", []), state=state, allowed_tools=set(data["allowed_tools"]) if data.get("allowed_tools") is not None else None)  #347 (line in Coconut source)


# ---------------------------------------------------------------------------
# Context navigation
# ---------------------------------------------------------------------------


@dataclass  #377 (line in Coconut source)
class ContextSelection():  #378 (line in Coconut source)
    """A scored, explainable context selection produced by ContextNavigator."""  #379 (line in Coconut source)

    context: ContextNode  #381 (line in Coconut source)
    score: float  #382 (line in Coconut source)
    source: str  #383 (line in Coconut source)
    hops: int = 0  #384 (line in Coconut source)
    path: list[str] = field(default_factory=list)  #385 (line in Coconut source)
    reasons: list[str] = field(default_factory=list)  #386 (line in Coconut source)
    token_count: int = 0  #387 (line in Coconut source)


@dataclass  #390 (line in Coconut source)
class ContextNavigator():  #391 (line in Coconut source)
    """Graph-native context retrieval with expansion, reranking, and budgeting."""  #392 (line in Coconut source)

    max_hops: int = 2  #394 (line in Coconut source)
    max_context_nodes: int = 8  #395 (line in Coconut source)
    max_context_tokens: int = 4000  #396 (line in Coconut source)
    semantic_top_k: int = 12  #397 (line in Coconut source)
    per_source_limit: int = 2  #398 (line in Coconut source)
    expansion_edge_types: tuple[EdgeType, ...] = (EdgeType.NEXT, EdgeType.SIMILAR_TO, EdgeType.MENTIONS, EdgeType.COVERS, EdgeType.PRODUCES)  #399 (line in Coconut source)
    path_decay: float = 0.85  #406 (line in Coconut source)
    tag_weight: float = 0.15  #407 (line in Coconut source)
    priority_weight: float = 0.1  #408 (line in Coconut source)
    recency_weight: float = 0.1  #409 (line in Coconut source)
    provenance_weight: float = 0.15  #410 (line in Coconut source)
    stale_fact_penalty: float = 0.4  #411 (line in Coconut source)
    exclude_stale_facts: bool = True  #412 (line in Coconut source)

    async def navigate(self, store: GraphStore, agent_node: AgentNode, *, query: str | None=None, embedder: Any=None, session_id: str | None=None,) -> list[ContextSelection]:  #414 (line in Coconut source)
        """Select context for an agent using graph traversal and token budgeting."""  #423 (line in Coconut source)
        direct_edges = await store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_CONTEXT)  #424 (line in Coconut source)
        direct_context_edges: dict[str, Edge] = {}  #425 (line in Coconut source)
        seed_map: dict[str, ContextSelection] = {}  #426 (line in Coconut source)

        query_vec: list[float] | None = None  #428 (line in Coconut source)
        if query and embedder:  #429 (line in Coconut source)
            query_vec = _normalize(await embedder.embed_text(query))  #430 (line in Coconut source)

        for edge in direct_edges:  #432 (line in Coconut source)
            node = await store.get_node(edge.dst_id)  #433 (line in Coconut source)
            if not isinstance(node, ContextNode) or not node.is_valid:  #434 (line in Coconut source)
                continue  #435 (line in Coconut source)
            if self.exclude_stale_facts and not node.is_fact_valid:  #436 (line in Coconut source)
                continue  #437 (line in Coconut source)
            direct_context_edges[node.node_id] = edge  #438 (line in Coconut source)
            selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=edge, source="attached", hops=0, path=[agent_node.node_id, node.node_id], path_weight=edge.weight, session_id=session_id)  #439 (line in Coconut source)
            seed_map[node.node_id] = selection  #450 (line in Coconut source)

        if query_vec is not None:  #452 (line in Coconut source)
            semantic_hits = await store.vector_search(query_vec, node_types=[NodeType.CONTEXT,], top_k=self.semantic_top_k)  #453 (line in Coconut source)
            for rank, (node, _score) in enumerate(semantic_hits):  #458 (line in Coconut source)
                if not isinstance(node, ContextNode) or node.node_id in seed_map or not node.is_valid:  #459 (line in Coconut source)
                    continue  #460 (line in Coconut source)
                if self.exclude_stale_facts and not node.is_fact_valid:  #461 (line in Coconut source)
                    continue  #462 (line in Coconut source)
                selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(node.node_id), source="semantic", hops=0, path=[node.node_id,], path_weight=max(0.5, 1.0 - rank * 0.03), session_id=session_id)  #463 (line in Coconut source)
                seed_map[node.node_id] = selection  #474 (line in Coconut source)

        if session_id:  #476 (line in Coconut source)
            runtime_nodes = await store.list_nodes(node_type=NodeType.CONTEXT, group_id=session_id)  #477 (line in Coconut source)
            for node in runtime_nodes:  #478 (line in Coconut source)
                if not isinstance(node, ContextNode):  #479 (line in Coconut source)
                    continue  #480 (line in Coconut source)
                if node.attributes.get("origin") != "runtime":  #481 (line in Coconut source)
                    continue  #482 (line in Coconut source)
                selection = self._score_context(node, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(node.node_id), source="runtime", hops=0, path=[node.node_id,], path_weight=1.0, session_id=session_id)  #483 (line in Coconut source)
                existing = seed_map.get(node.node_id)  #494 (line in Coconut source)
                if existing is None or selection.score > existing.score:  #495 (line in Coconut source)
                    seed_map[node.node_id] = selection  #496 (line in Coconut source)

        expanded = await self._expand_contexts(store, list(seed_map.values()), query=query, query_vec=query_vec, direct_context_edges=direct_context_edges, session_id=session_id)  #498 (line in Coconut source)

        ranked = sorted(expanded.values(), key=lambda s: s.score, reverse=True)  #507 (line in Coconut source)
        return self._pack_contexts(ranked)  #508 (line in Coconut source)


    async def _expand_contexts(self, store: GraphStore, seeds: list[ContextSelection], *, query: str | None, query_vec: list[float] | None, direct_context_edges: dict[str, Edge], session_id: str | None,) -> dict[str, ContextSelection]:  #510 (line in Coconut source)
        candidates: dict[str, ContextSelection] = {seed.context.node_id: seed for seed in seeds}  #520 (line in Coconut source)
        frontier: deque[tuple[AnyNode, int, list[str], float, str]] = deque(((seed.context, 0, list(seed.path), 1.0, seed.source) for seed in seeds))  #521 (line in Coconut source)
        seen_paths: set[tuple[str, int]] = set()  #525 (line in Coconut source)

        while frontier:  #527 (line in Coconut source)
            current, hops, path, path_weight, origin = frontier.popleft()  #528 (line in Coconut source)
            if hops >= self.max_hops:  #529 (line in Coconut source)
                continue  #530 (line in Coconut source)
            key = (current.node_id, hops)  #531 (line in Coconut source)
            if key in seen_paths:  #532 (line in Coconut source)
                continue  #533 (line in Coconut source)
            seen_paths.add(key)  #534 (line in Coconut source)

            for edge in await store.get_edges(current.node_id, direction="both"):  #536 (line in Coconut source)
                if edge.edge_type not in self.expansion_edge_types:  #537 (line in Coconut source)
                    continue  #538 (line in Coconut source)
                neighbor_id = edge.dst_id if edge.src_id == current.node_id else edge.src_id  #539 (line in Coconut source)
                neighbor = await store.get_node(neighbor_id)  #540 (line in Coconut source)
                if neighbor is None or not neighbor.is_valid:  #541 (line in Coconut source)
                    continue  #542 (line in Coconut source)

                next_path = path + [neighbor_id,]  #544 (line in Coconut source)
                next_weight = path_weight * max(edge.weight, 0.1)  #545 (line in Coconut source)
                next_hops = hops + 1  #546 (line in Coconut source)

                if isinstance(neighbor, ContextNode):  #548 (line in Coconut source)
                    if self.exclude_stale_facts and not neighbor.is_fact_valid:  #549 (line in Coconut source)
                        continue  #550 (line in Coconut source)
                    selection = self._score_context(neighbor, query=query, query_vec=query_vec, direct_edge=direct_context_edges.get(neighbor.node_id), source="{_coconut_format_0}+graph".format(_coconut_format_0=(origin)), hops=next_hops, path=next_path, path_weight=next_weight, session_id=session_id)  #551 (line in Coconut source)
                    existing = candidates.get(neighbor.node_id)  #562 (line in Coconut source)
                    if existing is None or selection.score > existing.score:  #563 (line in Coconut source)
                        candidates[neighbor.node_id] = selection  #564 (line in Coconut source)

                frontier.append((neighbor, next_hops, next_path, next_weight, origin))  #566 (line in Coconut source)

        return candidates  #568 (line in Coconut source)


    def _pack_contexts(self, ranked: list[ContextSelection]) -> list[ContextSelection]:  #570 (line in Coconut source)
        packed: list[ContextSelection] = []  #571 (line in Coconut source)
        total_tokens = 0  #572 (line in Coconut source)
        per_source: dict[str, int] = {}  #573 (line in Coconut source)

        for selection in ranked:  #575 (line in Coconut source)
            source_key = selection.context.source or selection.source or "unknown"  #576 (line in Coconut source)
            if per_source.get(source_key, 0) >= self.per_source_limit:  #577 (line in Coconut source)
                continue  #578 (line in Coconut source)
            if len(packed) >= self.max_context_nodes:  #579 (line in Coconut source)
                break  #580 (line in Coconut source)
            if packed and total_tokens + selection.token_count > self.max_context_tokens:  #581 (line in Coconut source)
                continue  #582 (line in Coconut source)

            packed.append(selection)  #584 (line in Coconut source)
            total_tokens += selection.token_count  #585 (line in Coconut source)
            per_source[source_key] = per_source.get(source_key, 0) + 1  #586 (line in Coconut source)

        return packed  #588 (line in Coconut source)


    @_coconut_tco  #590 (line in Coconut source)
    def _score_context(self, ctx: ContextNode, *, query: str | None, query_vec: list[float] | None, direct_edge: Edge | None, source: str, hops: int, path: list[str], path_weight: float, session_id: str | None,) -> ContextSelection:  #590 (line in Coconut source)
        semantic = 0.5  #603 (line in Coconut source)
        if query_vec is not None and ctx.embedding:  #604 (line in Coconut source)
            semantic = max(0.0, _cosine(query_vec, ctx.embedding))  #605 (line in Coconut source)

        direct_affinity = direct_edge.weight if direct_edge is not None else 0.5  #607 (line in Coconut source)
        path_bonus = (self.path_decay**hops) * max(path_weight, 0.1)  #608 (line in Coconut source)
        priority_bonus = ctx.priority * self.priority_weight  #609 (line in Coconut source)
        tag_bonus = self._tag_overlap_bonus(query, ctx)  #610 (line in Coconut source)
        recency_bonus = self._recency_bonus(ctx)  #611 (line in Coconut source)
        provenance_bonus = self.provenance_weight if ctx.attributes.get("origin") == "runtime" else 0.0  #612 (line in Coconut source)
        if session_id and ctx.group_id == session_id:  #613 (line in Coconut source)
            provenance_bonus += self.provenance_weight  #614 (line in Coconut source)

        score = semantic * direct_affinity * path_bonus  #616 (line in Coconut source)
        score += priority_bonus + tag_bonus + recency_bonus + provenance_bonus  #617 (line in Coconut source)
        if not ctx.is_fact_valid:  #618 (line in Coconut source)
            score -= self.stale_fact_penalty  #619 (line in Coconut source)

        reasons = ["semantic={_coconut_format_0:.2f}".format(_coconut_format_0=(semantic)), "affinity={_coconut_format_0:.2f}".format(_coconut_format_0=(direct_affinity)), "hops={_coconut_format_0}".format(_coconut_format_0=(hops))]  #621 (line in Coconut source)
        if priority_bonus:  #626 (line in Coconut source)
            reasons.append("priority+={_coconut_format_0:.2f}".format(_coconut_format_0=(priority_bonus)))  #627 (line in Coconut source)
        if tag_bonus:  #628 (line in Coconut source)
            reasons.append("tags+={_coconut_format_0:.2f}".format(_coconut_format_0=(tag_bonus)))  #629 (line in Coconut source)
        if recency_bonus:  #630 (line in Coconut source)
            reasons.append("recent+={_coconut_format_0:.2f}".format(_coconut_format_0=(recency_bonus)))  #631 (line in Coconut source)
        if provenance_bonus:  #632 (line in Coconut source)
            reasons.append("runtime+={_coconut_format_0:.2f}".format(_coconut_format_0=(provenance_bonus)))  #633 (line in Coconut source)
        if not ctx.is_fact_valid:  #634 (line in Coconut source)
            reasons.append("stale-={_coconut_format_0:.2f}".format(_coconut_format_0=(self.stale_fact_penalty)))  #635 (line in Coconut source)

        return _coconut_tail_call(ContextSelection, context=ctx, score=score, source=source, hops=hops, path=path, reasons=reasons, token_count=self._estimate_tokens(ctx))  #637 (line in Coconut source)


    @_coconut_tco  #647 (line in Coconut source)
    def _estimate_tokens(self, ctx: ContextNode) -> int:  #647 (line in Coconut source)
        if ctx.token_count > 0:  #648 (line in Coconut source)
            return ctx.token_count  #649 (line in Coconut source)
        content = ctx.content or ""  #650 (line in Coconut source)
        return _coconut_tail_call(max, 1, len(content.split()) + len(content) // 12)  #651 (line in Coconut source)


    def _tag_overlap_bonus(self, query: str | None, ctx: ContextNode) -> float:  #653 (line in Coconut source)
        if not query or not ctx.tags:  #654 (line in Coconut source)
            return 0.0  #655 (line in Coconut source)
        query_lower = query.lower()  #656 (line in Coconut source)
        overlap = sum((1 for tag in ctx.tags if tag.lower() in query_lower))  #657 (line in Coconut source)
        return overlap * self.tag_weight  #658 (line in Coconut source)


    def _recency_bonus(self, ctx: ContextNode) -> float:  #660 (line in Coconut source)
        age_s = (datetime.now(timezone.utc) - ctx.valid_at).total_seconds()  #661 (line in Coconut source)
        if age_s <= 3600:  #662 (line in Coconut source)
            return self.recency_weight  #663 (line in Coconut source)
        if age_s <= 86400:  #664 (line in Coconut source)
            return self.recency_weight / 2  #665 (line in Coconut source)
        return 0.0  #666 (line in Coconut source)


# ---------------------------------------------------------------------------
# ComposedAgent — runtime snapshot of an agent's composition
# ---------------------------------------------------------------------------


@dataclass  #673 (line in Coconut source)
class ComposedAgent():  #674 (line in Coconut source)
    """The fully-resolved runtime configuration for one AgentNode invocation.

    Built by AgentComposer.compose() via graph traversal — not hardcoded.
    """  #678 (line in Coconut source)

    agent_node: AgentNode  #680 (line in Coconut source)
    tools: list[ToolNode]  #681 (line in Coconut source)
    context: list[ContextNode]  #682 (line in Coconut source)
    context_selection: list[ContextSelection]  #683 (line in Coconut source)
    prompt: PromptNode | None  #684 (line in Coconut source)
    delegates: list[AgentNode]  #685 (line in Coconut source)

    @_coconut_tco  #687 (line in Coconut source)
    def build_system_prompt(self, **prompt_vars: Any) -> str:  #687 (line in Coconut source)
        """Assemble the system prompt from the prompt template + context nodes.

        Image context nodes (content_type == "image") are excluded here — they
        are injected as multimodal content blocks in the user message instead.
        """  #692 (line in Coconut source)
        parts: list[str] = []  #693 (line in Coconut source)

        if self.prompt:  #695 (line in Coconut source)
            parts.append(self.prompt.render(**prompt_vars))  #696 (line in Coconut source)
        elif self.agent_node.system_prompt:  #697 (line in Coconut source)
            parts.append(self.agent_node.system_prompt)  #698 (line in Coconut source)

        text_context = [ctx for ctx in self.context if ctx.content_type != "image"]  #700 (line in Coconut source)
        if text_context:  #701 (line in Coconut source)
            parts.append("\n\n## Relevant Context\n")  #702 (line in Coconut source)
            for ctx in text_context:  #703 (line in Coconut source)
                header = "### {_coconut_format_0}".format(_coconut_format_0=(ctx.name)) if ctx.name else "###"  #704 (line in Coconut source)
                if ctx.source:  #705 (line in Coconut source)
                    header += " (source: {_coconut_format_0})".format(_coconut_format_0=(ctx.source))  #706 (line in Coconut source)
                parts.append("{_coconut_format_0}\n{_coconut_format_1}".format(_coconut_format_0=(header), _coconut_format_1=(ctx.content)))  #707 (line in Coconut source)

        return _coconut_tail_call("\n".join, parts)  #709 (line in Coconut source)


    def build_image_context_blocks(self) -> list[dict[str, Any]]:  #711 (line in Coconut source)
        """Return Anthropic-format image blocks for image context nodes."""  #712 (line in Coconut source)
        blocks: list[dict[str, Any]] = []  #713 (line in Coconut source)
        for ctx in self.context:  #714 (line in Coconut source)
            if ctx.content_type != "image":  #715 (line in Coconut source)
                continue  #716 (line in Coconut source)
            source_type = ctx.attributes.get("image_source", "url")  #717 (line in Coconut source)
            if source_type == "base64":  #718 (line in Coconut source)
                media_type = ctx.attributes.get("media_type", "image/jpeg")  #719 (line in Coconut source)
                blocks.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": ctx.content}})  #720 (line in Coconut source)
            else:  #724 (line in Coconut source)
                blocks.append({"type": "image", "source": {"type": "url", "url": ctx.content}})  #725 (line in Coconut source)
        return blocks  #729 (line in Coconut source)


    def build_tool_schemas(self) -> list[dict[str, Any]]:  #731 (line in Coconut source)
        """Return tool definitions for all composed tools (backend-agnostic format)."""  #732 (line in Coconut source)
        return [t.to_tool_schema() for t in self.tools]  #733 (line in Coconut source)


    def explain(self) -> dict[str, Any]:  #735 (line in Coconut source)
        """Return a structured explanation of the composed runtime agent."""  #736 (line in Coconut source)
        prompt_source = "none"  #737 (line in Coconut source)
        prompt_name = ""  #738 (line in Coconut source)
        if self.prompt is not None:  #739 (line in Coconut source)
            prompt_source = "prompt_node"  #740 (line in Coconut source)
            prompt_name = self.prompt.name  #741 (line in Coconut source)
        elif self.agent_node.system_prompt:  #742 (line in Coconut source)
            prompt_source = "agent_node"  #743 (line in Coconut source)

        return {"agent": {"node_id": self.agent_node.node_id, "name": self.agent_node.name, "model": self.agent_node.model}, "prompt": {"source": prompt_source, "name": prompt_name}, "tools": [{"node_id": tool.node_id, "name": tool.name, "callable_ref": tool.callable_ref, "description": tool.description} for tool in self.tools], "context": [{"node_id": selection.context.node_id, "name": selection.context.name, "source": selection.source, "score": round(selection.score, 4), "hops": selection.hops, "path": selection.path, "reasons": selection.reasons, "token_count": selection.token_count} for selection in self.context_selection], "delegates": [{"node_id": delegate.node_id, "name": delegate.name} for delegate in self.delegates]}  #745 (line in Coconut source)


# ---------------------------------------------------------------------------
# AgentComposer — discovers composition from the graph
# ---------------------------------------------------------------------------


class AgentComposer():  #791 (line in Coconut source)
    """Assembles an agent's runtime configuration by traversing graph edges.

    This is the architectural core: composition IS traversal.
    Adding a tool to an agent = upsert_edge(HAS_TOOL, agent, tool). No code change.

    Pass an Embedder instance to enable query-time context re-ranking: context nodes
    are scored by edge.weight * cosine(query, ctx) + priority_bonus instead of
    static edge weight alone.
    """  #800 (line in Coconut source)

    def __init__(self, store: GraphStore, embedder: Any=None, context_navigator: ContextNavigator | None=None,) -> None:  #802 (line in Coconut source)
        self.store = store  #808 (line in Coconut source)
        self._embedder = embedder  #809 (line in Coconut source)
        self._context_navigator = context_navigator or ContextNavigator()  #810 (line in Coconut source)


    async def compose(self, agent_node: AgentNode, query: str | None=None, session_id: str | None=None,) -> ComposedAgent:  #812 (line in Coconut source)
        node_id = agent_node.node_id  #818 (line in Coconut source)

        tool_edges = await self.store.get_edges(node_id, edge_type=EdgeType.HAS_TOOL)  #820 (line in Coconut source)
        tool_edges.sort(key=lambda e: e.weight, reverse=True)  #821 (line in Coconut source)
        raw_tool_nodes = await asyncio.gather(*[self.store.get_node(e.dst_id) for e in tool_edges])  #822 (line in Coconut source)
        tools: list[ToolNode] = [n for n in raw_tool_nodes if isinstance(n, ToolNode) and n.is_valid]  #823 (line in Coconut source)

        context_selection = await self._context_navigator.navigate(self.store, agent_node, query=query, embedder=self._embedder, session_id=session_id)  #827 (line in Coconut source)
        context = [selection.context for selection in context_selection]  #834 (line in Coconut source)

        prompt_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.HAS_PROMPT)  #836 (line in Coconut source)
        prompt = next((n for n in prompt_nodes if isinstance(n, PromptNode)), None)  #837 (line in Coconut source)

        delegate_nodes = await self.store.neighbors(node_id, edge_type=EdgeType.DELEGATES_TO)  #839 (line in Coconut source)
        delegates = [n for n in delegate_nodes if isinstance(n, AgentNode) and n.is_valid]  #840 (line in Coconut source)

        return ComposedAgent(agent_node=agent_node, tools=tools, context=context, context_selection=context_selection, prompt=prompt, delegates=delegates)  #842 (line in Coconut source)


# ---------------------------------------------------------------------------
# Router prompt templates
# ---------------------------------------------------------------------------


_ROUTER_SYSTEM = ('You are a routing classifier. Respond with a single valid JSON object and nothing else.')  #856 (line in Coconut source)

_ROUTER_TEMPLATE = """\
Select the best agent for this task.

Available agents:
{agent_list}

Task: {query}

Respond with JSON only:
{{"agent": "<id>", "reason": "<one sentence explaining why>", "confidence": <0.0-1.0>}}"""  #870 (line in Coconut source)

_INTENT_TEMPLATE = """\
Given this agent output, select the best routing intent.

Available intents:
{intents}
- default

Agent output:
{text}

Respond with JSON only:
{{"intent": "<selected>", "reason": "<brief reason>"}}"""  #883 (line in Coconut source)


# ---------------------------------------------------------------------------
# ExecutionOptions — security and tenancy controls for run()
# ---------------------------------------------------------------------------

class ExecutionOptions(_coconut.collections.namedtuple("ExecutionOptions", ('allowed_tools',))):  #890 (line in Coconut source)
    """Runtime controls for GraphExecutor.run()."""  #891 (line in Coconut source)


    __slots__ = ()  #894 (line in Coconut source)
    _coconut_is_data = True  #894 (line in Coconut source)
    __match_args__ = ('allowed_tools',)  #894 (line in Coconut source)
    def __add__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    def __mul__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    def __rmul__(self, other): return _coconut.NotImplemented  #894 (line in Coconut source)
    __ne__ = _coconut.object.__ne__  #894 (line in Coconut source)
    def __eq__(self, other):  #894 (line in Coconut source)
        return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)  #894 (line in Coconut source)
    def __hash__(self):  #894 (line in Coconut source)
        return _coconut.tuple.__hash__(self) ^ _coconut.hash(self.__class__)  #894 (line in Coconut source)
    def __new__(_coconut_cls, allowed_tools=None):  #894 (line in Coconut source)
        return _coconut.tuple.__new__(_coconut_cls, (allowed_tools,))  #894 (line in Coconut source)
    _coconut_data_defaults = {0: __new__.__defaults__[0]}  # type: ignore  #894 (line in Coconut source)
@dataclass  #894 (line in Coconut source)
class ResumeReadiness():  #895 (line in Coconut source)
    """Diagnosis of whether a checkpointed/paused context is safe to resume."""  #896 (line in Coconut source)

    status: str  #898 (line in Coconut source)
    is_paused: bool  #899 (line in Coconut source)
    is_stale: bool  #900 (line in Coconut source)
    last_event_at: datetime | None  #901 (line in Coconut source)
    seconds_since_last_event: float | None  #902 (line in Coconut source)
    available: list[str]  #903 (line in Coconut source)
    unrecoverable: list[str]  #904 (line in Coconut source)

    @property  #906 (line in Coconut source)
    def ok(self) -> bool:  #907 (line in Coconut source)
        """True when nothing blocks an automatic resume."""  #908 (line in Coconut source)
        return not self.is_stale and not self.unrecoverable  #909 (line in Coconut source)


# ---------------------------------------------------------------------------
# GraphExecutor — dispatches nodes and traverses the graph
# ---------------------------------------------------------------------------


class GraphExecutor():  #916 (line in Coconut source)
    """Executes a query by traversing the agent graph.

    Node dispatch is based on node_type:
    - AGENT   → compose + LLM call + tool handling + routing
    - TOOL    → call registered Python callable
    - CONTEXT → return content (passive)
    - GRAPH   → recursive sub-graph execution
    - PROMPT  → render template (usually consumed by AGENT, not executed directly)
    """  #925 (line in Coconut source)

    def __init__(self, store: GraphStore, composer: AgentComposer | None=None, backend: LLMBackend | None=None, embedder: Any=None, context_navigator: ContextNavigator | None=None, router_model: str="claude-haiku-4-5-20251001",) -> None:  #927 (line in Coconut source)
        self.store = store  #936 (line in Coconut source)
        self.composer = composer or AgentComposer(store, embedder=embedder, context_navigator=context_navigator)  #937 (line in Coconut source)
        self._backend = backend or default_backend()  #940 (line in Coconut source)
        self._router_model = router_model  #941 (line in Coconut source)

        self._tool_fns: dict[str, Any] = {}  #943 (line in Coconut source)
        self._event_hooks: list[Callable[[TraceEvent, ExecutionContext], Any]] = []  #944 (line in Coconut source)


    def register_tool(self, callable_ref: str, fn: Any) -> None:  #946 (line in Coconut source)
        """Register a callable under its dotted ref string."""  #947 (line in Coconut source)
        self._tool_fns[callable_ref] = fn  #948 (line in Coconut source)


    def add_event_hook(self, fn: Callable[[TraceEvent, ExecutionContext], Any]) -> None:  #950 (line in Coconut source)
        """Register a callback invoked for every emitted event."""  #951 (line in Coconut source)
        self._event_hooks.append(fn)  #952 (line in Coconut source)

# ------------------------------------------------------------------
# Trace emission helper
# ------------------------------------------------------------------


    def _emit(self, ctx: ExecutionContext, event_type: EventType, node_id: str, node_name: str, payload: dict[str, Any], event_id: str | None=None, parent_event_id: str | None=None, duration_ms: int | None=None,) -> TraceEvent:  #958 (line in Coconut source)
        """Create and append a TraceEvent to ctx.trace. Returns the event."""  #969 (line in Coconut source)
        event = TraceEvent(event_type=event_type, session_id=ctx.session_id, node_id=node_id, node_name=node_name, timestamp=datetime.now(timezone.utc), payload=payload, event_id=event_id or str(uuid.uuid4()), parent_event_id=parent_event_id, duration_ms=duration_ms)  #970 (line in Coconut source)
        ctx.trace.append(event)  #981 (line in Coconut source)
        for hook in getattr(self, "_event_hooks", []):  #982 (line in Coconut source)
            hook_result = hook(event, ctx)  #983 (line in Coconut source)
            if asyncio.iscoroutine(hook_result):  #984 (line in Coconut source)
                asyncio.create_task(hook_result)  #985 (line in Coconut source)
        return event  #986 (line in Coconut source)

# ------------------------------------------------------------------
# Public entry points
# ------------------------------------------------------------------


    async def run(self, entry_node_id: str, query: QueryContent, strategy: str="sequential", max_hops: int=20, extra_messages: list[dict[str, Any]] | None=None, execution_context: ExecutionContext | None=None, state: dict[str, Any] | None=None, allowed_tools: list[str] | None=None, options: ExecutionOptions | None=None, **kwargs: Any,) -> ExecutionContext:  #992 (line in Coconut source)
        """Execute a query starting from entry_node_id."""  #1005 (line in Coconut source)
        ctx = execution_context or ExecutionContext(query=query, max_hops=max_hops)  #1006 (line in Coconut source)
        ctx.query = query  #1007 (line in Coconut source)
        ctx.max_hops = max_hops  #1008 (line in Coconut source)
        if extra_messages:  #1009 (line in Coconut source)
            ctx.extra_messages = list(extra_messages)  #1010 (line in Coconut source)
        if state:  #1011 (line in Coconut source)
            ctx.state.data.update(state)  #1012 (line in Coconut source)
        if allowed_tools is not None:  #1013 (line in Coconut source)
            ctx.allowed_tools = set(allowed_tools)  #1014 (line in Coconut source)
        if options is not None and options.allowed_tools is not None:  #1015 (line in Coconut source)
            ctx.allowed_tools = options.allowed_tools  #1016 (line in Coconut source)
        try:  #1017 (line in Coconut source)
            entry = await self.store.get_node(entry_node_id)  #1018 (line in Coconut source)
            if entry is None:  #1019 (line in Coconut source)
                raise ValueError(("Entry node {_coconut_format_0!r} not found in graph store.\n".format(_coconut_format_0=(entry_node_id)) + "Hint: use `agent.node_id` (not `agent.name`) as the entry_node_id,\n" + "or call `await store.list_nodes()` to inspect what is in the store."))  #1020 (line in Coconut source)
            _coconut_case_match_to_1 = strategy  #1025 (line in Coconut source)
            _coconut_case_match_check_1 = False  #1025 (line in Coconut source)
            if _coconut_case_match_to_1 == "sequential":  #1025 (line in Coconut source)
                _coconut_case_match_check_1 = True  #1025 (line in Coconut source)
            if _coconut_case_match_check_1:  #1025 (line in Coconut source)
                await self._run_sequential(entry, ctx)  #1027 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1028 (line in Coconut source)
                if _coconut_case_match_to_1 == "parallel":  #1028 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #1028 (line in Coconut source)
                if _coconut_case_match_check_1:  #1028 (line in Coconut source)
                    await self._run_parallel(entry, ctx)  #1029 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1030 (line in Coconut source)
                if _coconut_case_match_to_1 == "topological":  #1030 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #1030 (line in Coconut source)
                if _coconut_case_match_check_1:  #1030 (line in Coconut source)
                    await self._run_topological(entry_node_id, ctx)  #1031 (line in Coconut source)
            if not _coconut_case_match_check_1:  #1032 (line in Coconut source)
                _coconut_case_match_check_1 = True  #1032 (line in Coconut source)
                if _coconut_case_match_check_1:  #1032 (line in Coconut source)
                    raise ValueError("Unknown strategy: {_coconut_format_0!r}".format(_coconut_format_0=(strategy)))  #1033 (line in Coconut source)
        except Exception as exc:  #1034 (line in Coconut source)
            _log.error("Executor fatal error [session=%s node=%s]: %s", ctx.session_id, entry_node_id, exc, exc_info=True)  #1035 (line in Coconut source)
            self._emit(ctx, "error", entry_node_id, "", payload={"error": str(exc), "error_type": type(exc).__name__})  #1039 (line in Coconut source)
            raise  #1049 (line in Coconut source)

        return ctx  #1051 (line in Coconut source)


    async def resume(self, entry_node_id: str, ctx: ExecutionContext, *, query: QueryContent | None=None, strategy: str="sequential",) -> ExecutionContext:  #1053 (line in Coconut source)
        """Resume a paused workflow context."""  #1061 (line in Coconut source)
        if query is not None:  #1062 (line in Coconut source)
            ctx.query = query  #1063 (line in Coconut source)
        ctx.state.status = "running"  #1064 (line in Coconut source)
        pause = ctx.state.pending_pause  #1065 (line in Coconut source)
        ctx.state.pending_pause = None  #1066 (line in Coconut source)
        if pause is not None:  #1067 (line in Coconut source)
            self._emit(ctx, "resume", pause.node_id, pause.node_name, payload={"token": pause.token, "waiting_for": pause.waiting_for})  #1068 (line in Coconut source)
# If the pause was a pause_before, clear that flag on the node so it
# doesn't immediately re-pause when revisited during the resumed run.
            if pause.reason == "pause_before":  #1077 (line in Coconut source)
                try:  #1078 (line in Coconut source)
                    paused_node = await self.store.get_node(pause.node_id)  #1079 (line in Coconut source)
                    if hasattr(paused_node, "pause_before"):  #1080 (line in Coconut source)
                        paused_node.pause_before = False  #1081 (line in Coconut source)
                        await self.store.upsert_node(paused_node)  #1082 (line in Coconut source)
                except Exception:  #1083 (line in Coconut source)
                    pass  #1084 (line in Coconut source)
        return await self.run(entry_node_id, ctx.query, strategy=strategy, max_hops=ctx.max_hops, execution_context=ctx)  #1085 (line in Coconut source)


    @_coconut_tco  #1093 (line in Coconut source)
    def inspect_resume(self, ctx: ExecutionContext, *, stale_after_seconds: float=1200.0, required_outputs: list[str] | None=None, now: datetime | None=None,) -> ResumeReadiness:  #1093 (line in Coconut source)
        """Diagnose whether ``ctx`` is safe to resume — no side effects."""  #1101 (line in Coconut source)
        last_event_at = max((e.timestamp for e in ctx.trace), default=None)  #1102 (line in Coconut source)
        if last_event_at is None:  #1103 (line in Coconut source)
            seconds_since: float | None = None  #1104 (line in Coconut source)
            is_stale = False  #1105 (line in Coconut source)
        else:  #1106 (line in Coconut source)
            current = now or datetime.now(timezone.utc)  #1107 (line in Coconut source)
            seconds_since = (current - last_event_at).total_seconds()  #1108 (line in Coconut source)
            is_stale = seconds_since > stale_after_seconds  #1109 (line in Coconut source)

        available: list[str] = []  #1111 (line in Coconut source)
        unrecoverable: list[str] = []  #1112 (line in Coconut source)
        for key in required_outputs or []:  #1113 (line in Coconut source)
            if key in ctx.outputs or key in ctx.state.data:  #1114 (line in Coconut source)
                available.append(key)  #1115 (line in Coconut source)
            else:  #1116 (line in Coconut source)
                unrecoverable.append(key)  #1117 (line in Coconut source)

        return _coconut_tail_call(ResumeReadiness, status=ctx.state.status, is_paused=ctx.is_paused(), is_stale=is_stale, last_event_at=last_event_at, seconds_since_last_event=seconds_since, available=available, unrecoverable=unrecoverable)  #1119 (line in Coconut source)


    async def batch(self, agent_node_id: str, items: list[Any], query_fn: Callable[[Any,], str], *, context_fn: Callable[[Any,], str | None] | None=None, reduce_fn: Callable[[list[Any],], Any] | None=None, on_progress: Callable[[Any,], Any] | None=None, concurrency: int=5, checkpoint: bool=True, strategy: str="sequential",) -> Any:  #1129 (line in Coconut source)
        """Run an agent over a list of items with concurrency control."""  #1142 (line in Coconut source)
        import warnings  #1143 (line in Coconut source)
        from yggdrasil_lm.batch import BatchExecutor  #1144 (line in Coconut source)
        with warnings.catch_warnings():  #1145 (line in Coconut source)
            warnings.simplefilter("ignore", DeprecationWarning)  #1146 (line in Coconut source)
            _batch = BatchExecutor(self.store, self, concurrency=concurrency)  #1147 (line in Coconut source)
        return await _batch.run(agent_node_id, items, query_fn, context_fn=context_fn, reduce_fn=reduce_fn, on_progress=on_progress, checkpoint=checkpoint, strategy=strategy)  #1148 (line in Coconut source)


    async def checkpoint_context(self, ctx: ExecutionContext, *, name: str="Execution checkpoint", max_inline_chars: int | None=None,) -> ContextNode:  #1159 (line in Coconut source)
        """Persist a resumable execution snapshot as a runtime context node."""  #1166 (line in Coconut source)
        snap = ctx.snapshot()  #1167 (line in Coconut source)
        if max_inline_chars is not None:  #1168 (line in Coconut source)
            snap = await self._offload_snapshot_blobs(ctx, snap, max_inline_chars)  #1169 (line in Coconut source)
        checkpoint = ContextNode(name=name, description="Serialized execution checkpoint", content=json.dumps(snap, default=str), content_type="json", source="checkpoint", group_id=ctx.session_id, attributes={"origin": "checkpoint", "session_id": ctx.session_id, "graph_version": ctx.state.graph_version})  #1170 (line in Coconut source)
        await self.store.upsert_node(checkpoint)  #1183 (line in Coconut source)
        self._emit(ctx, "checkpoint", checkpoint.node_id, checkpoint.name, payload={"checkpoint_node_id": checkpoint.node_id})  #1184 (line in Coconut source)
        return checkpoint  #1191 (line in Coconut source)


    async def _offload_snapshot_blobs(self, ctx: ExecutionContext, snap: dict[str, Any], max_inline_chars: int,) -> dict[str, Any]:  #1193 (line in Coconut source)
        """Replace oversized top-level snapshot values with blob node refs."""  #1199 (line in Coconut source)
        async def offload(value: Any) -> Any:  #1200 (line in Coconut source)
            try:  #1201 (line in Coconut source)
                encoded = json.dumps(value, default=str)  #1202 (line in Coconut source)
            except (TypeError, ValueError):  #1203 (line in Coconut source)
                return value  #1204 (line in Coconut source)
            if len(encoded) <= max_inline_chars:  #1205 (line in Coconut source)
                return value  #1206 (line in Coconut source)
            blob = ContextNode(name="Checkpoint blob", description="Offloaded checkpoint payload", content=encoded, content_type="json", source="checkpoint", group_id=ctx.session_id, attributes={"origin": "checkpoint_blob", "session_id": ctx.session_id})  #1207 (line in Coconut source)
            await self.store.upsert_node(blob)  #1216 (line in Coconut source)
            return {"$ygg_blob": blob.node_id}  #1217 (line in Coconut source)


        outputs = snap.get("outputs")  #1219 (line in Coconut source)
        if isinstance(outputs, dict):  #1220 (line in Coconut source)
            for key, value in list(outputs.items()):  #1221 (line in Coconut source)
                outputs[key] = await offload(value)  #1222 (line in Coconut source)
        state_data = snap.get("state", {}).get("data")  #1223 (line in Coconut source)
        if isinstance(state_data, dict):  #1224 (line in Coconut source)
            for key, value in list(state_data.items()):  #1225 (line in Coconut source)
                state_data[key] = await offload(value)  #1226 (line in Coconut source)
        return snap  #1227 (line in Coconut source)


    async def load_checkpoint(self, checkpoint_node_id: str) -> ExecutionContext:  #1229 (line in Coconut source)
        """Restore an execution context from a checkpoint node."""  #1230 (line in Coconut source)
        node = await self.store.get_node(checkpoint_node_id)  #1231 (line in Coconut source)
        if not isinstance(node, ContextNode):  #1232 (line in Coconut source)
            raise ValueError("Checkpoint node not found: {_coconut_format_0}".format(_coconut_format_0=(checkpoint_node_id)))  #1233 (line in Coconut source)
        snap = json.loads(node.content)  #1234 (line in Coconut source)
        await self._rehydrate_snapshot_blobs(snap)  #1235 (line in Coconut source)
        return ExecutionContext.from_snapshot(snap)  #1236 (line in Coconut source)


    async def _rehydrate_snapshot_blobs(self, snap: dict[str, Any]) -> None:  #1238 (line in Coconut source)
        """Inverse of ``_offload_snapshot_blobs`` — resolve ``$ygg_blob`` refs."""  #1239 (line in Coconut source)
        async def resolve(value: Any) -> Any:  #1240 (line in Coconut source)
            if isinstance(value, dict) and set(value) == {"$ygg_blob"}:  #1241 (line in Coconut source)
                blob = await self.store.get_node(value["$ygg_blob"])  #1242 (line in Coconut source)
                if not isinstance(blob, ContextNode):  #1243 (line in Coconut source)
                    raise ValueError("Checkpoint blob node missing: {_coconut_format_0}".format(_coconut_format_0=(value['$ygg_blob'])))  #1244 (line in Coconut source)
                return json.loads(blob.content)  #1247 (line in Coconut source)
            return value  #1248 (line in Coconut source)


        outputs = snap.get("outputs")  #1250 (line in Coconut source)
        if isinstance(outputs, dict):  #1251 (line in Coconut source)
            for key, value in list(outputs.items()):  #1252 (line in Coconut source)
                outputs[key] = await resolve(value)  #1253 (line in Coconut source)
        state_data = snap.get("state", {}).get("data")  #1254 (line in Coconut source)
        if isinstance(state_data, dict):  #1255 (line in Coconut source)
            for key, value in list(state_data.items()):  #1256 (line in Coconut source)
                state_data[key] = await resolve(value)  #1257 (line in Coconut source)


    async def resume_from_checkpoint(self, checkpoint_node_id: str, entry_node_id: str, *, query: QueryContent | None=None, strategy: str="sequential",) -> ExecutionContext:  #1259 (line in Coconut source)
        """Load a checkpointed context and resume execution."""  #1267 (line in Coconut source)
        ctx = await self.load_checkpoint(checkpoint_node_id)  #1268 (line in Coconut source)
        return await self.resume(entry_node_id, ctx, query=query, strategy=strategy)  #1269 (line in Coconut source)


    def _resolve_json_path(self, payload: Any, path: str) -> Any:  #1271 (line in Coconut source)
        """Resolve a dotted JSON path against a payload dict."""  #1272 (line in Coconut source)
        current: Any = payload  #1273 (line in Coconut source)
        for part in [p for p in path.split(".") if p]:  #1274 (line in Coconut source)
            _coconut_case_match_to_2 = current  #1275 (line in Coconut source)
            _coconut_case_match_check_2 = False  #1275 (line in Coconut source)
            if _coconut.isinstance(_coconut_case_match_to_2, _coconut.abc.Mapping):  #1275 (line in Coconut source)
                _coconut_case_match_check_2 = True  #1275 (line in Coconut source)
            if _coconut_case_match_check_2 and not (part in current):  #1275 (line in Coconut source)
                _coconut_case_match_check_2 = False  #1275 (line in Coconut source)
            if _coconut_case_match_check_2:  #1275 (line in Coconut source)
                current = current[part]  #1277 (line in Coconut source)
            if not _coconut_case_match_check_2:  #1278 (line in Coconut source)
                _coconut_case_match_check_2 = True  #1278 (line in Coconut source)
                if _coconut_case_match_check_2:  #1278 (line in Coconut source)
                    return None  #1279 (line in Coconut source)
        return current  #1280 (line in Coconut source)


    def _payload_for_source(self, source: str, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> Any:  #1282 (line in Coconut source)
        _coconut_case_match_to_3 = source  #1291 (line in Coconut source)
        _coconut_case_match_check_3 = False  #1291 (line in Coconut source)
        if _coconut_case_match_to_3 == "result":  #1291 (line in Coconut source)
            _coconut_case_match_check_3 = True  #1291 (line in Coconut source)
        if _coconut_case_match_check_3:  #1291 (line in Coconut source)
            return result  #1293 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1294 (line in Coconut source)
            if _coconut_case_match_to_3 == "input":  #1294 (line in Coconut source)
                _coconut_case_match_check_3 = True  #1294 (line in Coconut source)
            if _coconut_case_match_check_3:  #1294 (line in Coconut source)
                return input_payload  #1295 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1296 (line in Coconut source)
            if _coconut_case_match_to_3 == "output":  #1296 (line in Coconut source)
                _coconut_case_match_check_3 = True  #1296 (line in Coconut source)
            if _coconut_case_match_check_3:  #1296 (line in Coconut source)
                return output_payload  #1297 (line in Coconut source)
        if not _coconut_case_match_check_3:  #1298 (line in Coconut source)
            _coconut_case_match_check_3 = True  #1298 (line in Coconut source)
            if _coconut_case_match_check_3:  #1298 (line in Coconut source)
                return state.data  #1299 (line in Coconut source)


    @_coconut_tco  #1301 (line in Coconut source)
    def _compare_values(self, operator: str, left: Any, right: Any) -> bool:  #1301 (line in Coconut source)
        _coconut_case_match_to_4 = operator  #1302 (line in Coconut source)
        _coconut_case_match_check_4 = False  #1302 (line in Coconut source)
        if _coconut_case_match_to_4 == "exists":  #1302 (line in Coconut source)
            _coconut_case_match_check_4 = True  #1302 (line in Coconut source)
        if _coconut_case_match_check_4:  #1302 (line in Coconut source)
            return left is not None  #1304 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1305 (line in Coconut source)
            if _coconut_case_match_to_4 == "truthy":  #1305 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1305 (line in Coconut source)
            if _coconut_case_match_check_4:  #1305 (line in Coconut source)
                return _coconut_tail_call(bool, left)  #1306 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1307 (line in Coconut source)
            if _coconut_case_match_to_4 == "contains":  #1307 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1307 (line in Coconut source)
            if _coconut_case_match_check_4:  #1307 (line in Coconut source)
                return left is not None and right in left  #1308 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1309 (line in Coconut source)
            if _coconut_case_match_to_4 == "not_equals":  #1309 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1309 (line in Coconut source)
            if _coconut_case_match_check_4:  #1309 (line in Coconut source)
                return left != right  #1310 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1311 (line in Coconut source)
            if _coconut_case_match_to_4 == "in":  #1311 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1311 (line in Coconut source)
            if _coconut_case_match_check_4:  #1311 (line in Coconut source)
                return left in right if right is not None else False  #1312 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1313 (line in Coconut source)
            if _coconut_case_match_to_4 == "regex":  #1313 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1313 (line in Coconut source)
            if _coconut_case_match_check_4:  #1313 (line in Coconut source)
                return isinstance(left, str) and isinstance(right, str) and re.search(right, left) is not None  #1314 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1315 (line in Coconut source)
            if _coconut_case_match_to_4 == "gt":  #1315 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1315 (line in Coconut source)
            if _coconut_case_match_check_4:  #1315 (line in Coconut source)
                return left > right  #1316 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1317 (line in Coconut source)
            if _coconut_case_match_to_4 == "gte":  #1317 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1317 (line in Coconut source)
            if _coconut_case_match_check_4:  #1317 (line in Coconut source)
                return left >= right  #1318 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1319 (line in Coconut source)
            if _coconut_case_match_to_4 == "lt":  #1319 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1319 (line in Coconut source)
            if _coconut_case_match_check_4:  #1319 (line in Coconut source)
                return left < right  #1320 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1321 (line in Coconut source)
            if _coconut_case_match_to_4 == "lte":  #1321 (line in Coconut source)
                _coconut_case_match_check_4 = True  #1321 (line in Coconut source)
            if _coconut_case_match_check_4:  #1321 (line in Coconut source)
                return left <= right  #1322 (line in Coconut source)
        if not _coconut_case_match_check_4:  #1323 (line in Coconut source)
            _coconut_case_match_check_4 = True  #1323 (line in Coconut source)
            if _coconut_case_match_check_4:  #1323 (line in Coconut source)
                return left == right  #1324 (line in Coconut source)


    @_coconut_tco  #1326 (line in Coconut source)
    def _evaluate_constraint_rule(self, rule: ConstraintRule, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> bool:  #1326 (line in Coconut source)
        source_data = self._payload_for_source(rule.source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1335 (line in Coconut source)
        left = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1342 (line in Coconut source)
        right = rule.value  #1343 (line in Coconut source)
        if rule.compare_to_source:  #1344 (line in Coconut source)
            compare_data = self._payload_for_source(rule.compare_to_source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1345 (line in Coconut source)
            right = self._resolve_json_path(compare_data, rule.compare_to_path) if rule.compare_to_path else compare_data  #1352 (line in Coconut source)
        return _coconut_tail_call(self._compare_values, rule.operator, left, right)  #1353 (line in Coconut source)


    @_coconut_tco  #1355 (line in Coconut source)
    def _evaluate_route_rule(self, rule: RouteRule, *, result: dict[str, Any], state: WorkflowState,) -> bool:  #1355 (line in Coconut source)
        source_data = state.data if rule.source == "state" else result  #1362 (line in Coconut source)
        return _coconut_tail_call(self._compare_values, rule.operator, self._resolve_json_path(source_data, rule.path) if rule.path else source_data, rule.value)  #1363 (line in Coconut source)


    def _describe_constraint_rule(self, rule: ConstraintRule, *, state: WorkflowState, result: Any=None, input_payload: Any=None, output_payload: Any=None,) -> dict[str, Any]:  #1369 (line in Coconut source)
        source_data = self._payload_for_source(rule.source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1378 (line in Coconut source)
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1385 (line in Coconut source)
        expected = rule.value  #1386 (line in Coconut source)
        if rule.compare_to_source:  #1387 (line in Coconut source)
            compare_data = self._payload_for_source(rule.compare_to_source, state=state, result=result, input_payload=input_payload, output_payload=output_payload)  #1388 (line in Coconut source)
            expected = (self._resolve_json_path(compare_data, rule.compare_to_path) if rule.compare_to_path else compare_data)  #1395 (line in Coconut source)
        matched = self._compare_values(rule.operator, actual, expected)  #1399 (line in Coconut source)
        return {"name": rule.name, "source": rule.source, "path": rule.path, "operator": rule.operator, "actual": actual, "expected": expected, "matched": matched, "compare_to_source": rule.compare_to_source, "compare_to_path": rule.compare_to_path, "message": rule.message}  #1400 (line in Coconut source)


    def _describe_route_rule(self, rule: RouteRule, *, state: WorkflowState, result: dict[str, Any],) -> dict[str, Any]:  #1413 (line in Coconut source)
        source_data = state.data if rule.source == "state" else result  #1420 (line in Coconut source)
        actual = self._resolve_json_path(source_data, rule.path) if rule.path else source_data  #1421 (line in Coconut source)
        matched = self._compare_values(rule.operator, actual, rule.value)  #1422 (line in Coconut source)
        return {"name": rule.name, "source": rule.source, "path": rule.path, "operator": rule.operator, "actual": actual, "expected": rule.value, "matched": matched, "priority": rule.priority, "target_node_id": rule.target_node_id, "pause_on_match": rule.pause_on_match}  #1423 (line in Coconut source)


    async def _validate_constraint_rules(self, node: AgentNode, *, ctx: ExecutionContext, result: Any=None, input_payload: Any=None, output_payload: Any=None, parent_event_id: str | None=None,) -> None:  #1436 (line in Coconut source)
        for rule in node.constraint_rules:  #1446 (line in Coconut source)
            if rule.source in {"result", "output"} and result is None and output_payload is None:  #1447 (line in Coconut source)
                continue  #1448 (line in Coconut source)
            if self._evaluate_constraint_rule(rule, state=ctx.state, result=result, input_payload=input_payload, output_payload=output_payload):  #1449 (line in Coconut source)
                continue  #1456 (line in Coconut source)
            message = rule.message or "Constraint {_coconut_format_0!r} failed".format(_coconut_format_0=(rule.name or rule.path or rule.operator))  #1457 (line in Coconut source)
            self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": False, "error": message, "constraint": rule.name}, parent_event_id=parent_event_id)  #1458 (line in Coconut source)
            raise ValueError(message)  #1466 (line in Coconut source)


    def _evaluate_decision_table(self, table: DecisionTable, *, state: WorkflowState, result: dict[str, Any],) -> DecisionRule | None:  #1468 (line in Coconut source)
        for rule in sorted(table.rules, key=lambda item: item.priority, reverse=True):  #1475 (line in Coconut source)
            if all((self._evaluate_constraint_rule(condition, state=state, result=result) for condition in rule.conditions)):  #1476 (line in Coconut source)
                return rule  #1480 (line in Coconut source)
        return None  #1481 (line in Coconut source)


    async def _pause_execution(self, ctx: ExecutionContext, node: AnyNode, *, reason: str, waiting_for: str | None=None, metadata: dict[str, Any] | None=None,) -> None:  #1483 (line in Coconut source)
        pause = WorkflowPause(reason=reason, node_id=node.node_id, node_name=node.name or "", waiting_for=waiting_for, metadata=metadata or {})  #1492 (line in Coconut source)
        ctx.state.pending_pause = pause  #1499 (line in Coconut source)
        ctx.state.status = "paused"  #1500 (line in Coconut source)
        self._emit(ctx, "pause", node.node_id, node.name or "", payload={"reason": reason, "token": pause.token, "waiting_for": waiting_for, "metadata": pause.metadata})  #1501 (line in Coconut source)


    def _validate_against_schema(self, payload: Any, schema: dict[str, Any], *, label: str,) -> None:  #1514 (line in Coconut source)
        if not schema:  #1521 (line in Coconut source)
            return  #1522 (line in Coconut source)
        schema_type = schema.get("type")  #1523 (line in Coconut source)
        _coconut_case_match_to_5 = schema_type  #1524 (line in Coconut source)
        _coconut_case_match_check_5 = False  #1524 (line in Coconut source)
        if _coconut_case_match_to_5 == "object":  #1524 (line in Coconut source)
            _coconut_case_match_check_5 = True  #1524 (line in Coconut source)
        if _coconut_case_match_check_5:  #1524 (line in Coconut source)
            if not isinstance(payload, dict):  #1526 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be an object".format(_coconut_format_0=(label)))  #1527 (line in Coconut source)
            required = schema.get("required", [])  #1528 (line in Coconut source)
            for key in required:  #1529 (line in Coconut source)
                if key not in payload:  #1530 (line in Coconut source)
                    raise ValueError("{_coconut_format_0} missing required field {_coconut_format_1!r}".format(_coconut_format_0=(label), _coconut_format_1=(key)))  #1531 (line in Coconut source)
            for key, subschema in schema.get("properties", {}).items():  #1532 (line in Coconut source)
                if key in payload:  #1533 (line in Coconut source)
                    self._validate_against_schema(payload[key], subschema, label="{_coconut_format_0}.{_coconut_format_1}".format(_coconut_format_0=(label), _coconut_format_1=(key)))  #1534 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1535 (line in Coconut source)
            if _coconut_case_match_to_5 == "array":  #1535 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1535 (line in Coconut source)
            if _coconut_case_match_check_5:  #1535 (line in Coconut source)
                if not isinstance(payload, list):  #1536 (line in Coconut source)
                    raise ValueError("{_coconut_format_0} must be an array".format(_coconut_format_0=(label)))  #1537 (line in Coconut source)
                for idx, item in enumerate(payload):  #1538 (line in Coconut source)
                    self._validate_against_schema(item, schema.get("items", {}), label="{_coconut_format_0}[{_coconut_format_1}]".format(_coconut_format_0=(label), _coconut_format_1=(idx)))  #1539 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1540 (line in Coconut source)
            if _coconut_case_match_to_5 == "string":  #1540 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1540 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, str)):  #1540 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1540 (line in Coconut source)
            if _coconut_case_match_check_5:  #1540 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a string".format(_coconut_format_0=(label)))  #1541 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1542 (line in Coconut source)
            if _coconut_case_match_to_5 == "integer":  #1542 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1542 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, int)):  #1542 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1542 (line in Coconut source)
            if _coconut_case_match_check_5:  #1542 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be an integer".format(_coconut_format_0=(label)))  #1543 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1544 (line in Coconut source)
            if _coconut_case_match_to_5 == "number":  #1544 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1544 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, (int, float))):  #1544 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1544 (line in Coconut source)
            if _coconut_case_match_check_5:  #1544 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a number".format(_coconut_format_0=(label)))  #1545 (line in Coconut source)
        if not _coconut_case_match_check_5:  #1546 (line in Coconut source)
            if _coconut_case_match_to_5 == "boolean":  #1546 (line in Coconut source)
                _coconut_case_match_check_5 = True  #1546 (line in Coconut source)
            if _coconut_case_match_check_5 and not (not isinstance(payload, bool)):  #1546 (line in Coconut source)
                _coconut_case_match_check_5 = False  #1546 (line in Coconut source)
            if _coconut_case_match_check_5:  #1546 (line in Coconut source)
                raise ValueError("{_coconut_format_0} must be a boolean".format(_coconut_format_0=(label)))  #1547 (line in Coconut source)


    async def _validate_node_schemas(self, node: AnyNode, *, input_payload: Any=None, output_payload: Any=None, ctx: ExecutionContext, parent_event_id: str | None=None,) -> None:  #1549 (line in Coconut source)
        try:  #1558 (line in Coconut source)
            _coconut_case_match_to_6 = node  #1559 (line in Coconut source)
            _coconut_case_match_check_6 = False  #1559 (line in Coconut source)
            _coconut_match_temp_3 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #1559 (line in Coconut source)
            _coconut_case_match_check_6 = True  #1559 (line in Coconut source)
            if _coconut_case_match_check_6:  #1559 (line in Coconut source)
                _coconut_case_match_check_6 = False  #1559 (line in Coconut source)
                if not _coconut_case_match_check_6:  #1559 (line in Coconut source)
                    if (_coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_6, ToolNode)):  #1559 (line in Coconut source)
                        _coconut_match_temp_4 = _coconut.len(_coconut_case_match_to_6) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_6.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {}) and _coconut_case_match_to_6[i] == _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_6.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_6, "__match_args__") else _coconut.len(_coconut_case_match_to_6) == 0  # type: ignore  #1559 (line in Coconut source)
                        if _coconut_match_temp_4:  #1559 (line in Coconut source)
                            _coconut_case_match_check_6 = True  #1559 (line in Coconut source)

                if not _coconut_case_match_check_6:  #1559 (line in Coconut source)
                    if (not _coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_6, ToolNode)):  #1559 (line in Coconut source)
                        _coconut_case_match_check_6 = True  #1559 (line in Coconut source)
                    if _coconut_case_match_check_6:  #1559 (line in Coconut source)
                        _coconut_case_match_check_6 = False  #1559 (line in Coconut source)
                        if not _coconut_case_match_check_6:  #1559 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1559 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1559 (line in Coconut source)

                        if not _coconut_case_match_check_6:  #1559 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1559 (line in Coconut source)
                                _coconut_match_temp_5 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1559 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_5, _coconut.tuple):  #1559 (line in Coconut source)
                                    raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #1559 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_5) < 0:  #1559 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_5),))  #1559 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1559 (line in Coconut source)




            if _coconut_case_match_check_6:  #1559 (line in Coconut source)
                if input_payload is not None:  #1561 (line in Coconut source)
                    self._validate_against_schema(input_payload, node.input_schema, label="tool_input")  #1562 (line in Coconut source)
                if output_payload is not None:  #1563 (line in Coconut source)
                    self._validate_against_schema(output_payload, node.output_schema, label="tool_output")  #1564 (line in Coconut source)
            if not _coconut_case_match_check_6:  #1565 (line in Coconut source)
                _coconut_match_temp_6 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1565 (line in Coconut source)
                _coconut_case_match_check_6 = True  #1565 (line in Coconut source)
                if _coconut_case_match_check_6:  #1565 (line in Coconut source)
                    _coconut_case_match_check_6 = False  #1565 (line in Coconut source)
                    if not _coconut_case_match_check_6:  #1565 (line in Coconut source)
                        if (_coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_6, AgentNode)):  #1565 (line in Coconut source)
                            _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_6) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_6.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {}) and _coconut_case_match_to_6[i] == _coconut.getattr(_coconut_case_match_to_6, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_6.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_6, "__match_args__") else _coconut.len(_coconut_case_match_to_6) == 0  # type: ignore  #1565 (line in Coconut source)
                            if _coconut_match_temp_7:  #1565 (line in Coconut source)
                                _coconut_case_match_check_6 = True  #1565 (line in Coconut source)

                    if not _coconut_case_match_check_6:  #1565 (line in Coconut source)
                        if (not _coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_6, AgentNode)):  #1565 (line in Coconut source)
                            _coconut_case_match_check_6 = True  #1565 (line in Coconut source)
                        if _coconut_case_match_check_6:  #1565 (line in Coconut source)
                            _coconut_case_match_check_6 = False  #1565 (line in Coconut source)
                            if not _coconut_case_match_check_6:  #1565 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1565 (line in Coconut source)
                                    _coconut_case_match_check_6 = True  #1565 (line in Coconut source)

                            if not _coconut_case_match_check_6:  #1565 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_6) in _coconut_self_match_types:  #1565 (line in Coconut source)
                                    _coconut_match_temp_8 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1565 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #1565 (line in Coconut source)
                                        raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1565 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_8) < 0:  #1565 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #1565 (line in Coconut source)
                                    _coconut_case_match_check_6 = True  #1565 (line in Coconut source)




                if _coconut_case_match_check_6:  #1565 (line in Coconut source)
                    state_schema = node.state_schema or ctx.state.schema  #1566 (line in Coconut source)
                    if state_schema:  #1567 (line in Coconut source)
                        self._validate_against_schema(ctx.state.data, state_schema, label="state")  #1568 (line in Coconut source)
                    await self._validate_constraint_rules(node, ctx=ctx, result=output_payload, input_payload=input_payload, output_payload=output_payload, parent_event_id=parent_event_id)  #1569 (line in Coconut source)
            validates = await self.store.get_edges(node.node_id, edge_type=EdgeType.VALIDATES, direction="in")  #1577 (line in Coconut source)
            for edge in validates:  #1578 (line in Coconut source)
                schema_node = await self.store.get_node(edge.src_id)  #1579 (line in Coconut source)
                if not isinstance(schema_node, SchemaNode):  #1580 (line in Coconut source)
                    continue  #1581 (line in Coconut source)
                phase = edge.attributes.get("phase", "output")  #1582 (line in Coconut source)
                payload = output_payload if phase == "output" else input_payload  #1583 (line in Coconut source)
                if payload is not None:  #1584 (line in Coconut source)
                    self._validate_against_schema(payload, schema_node.json_schema, label="{_coconut_format_0}_payload".format(_coconut_format_0=(phase)))  #1585 (line in Coconut source)
        except Exception as exc:  #1586 (line in Coconut source)
            self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": False, "error": str(exc)}, parent_event_id=parent_event_id)  #1587 (line in Coconut source)
            raise  #1595 (line in Coconut source)
        self._emit(ctx, "validation", node.node_id, node.name or "", payload={"success": True}, parent_event_id=parent_event_id)  #1596 (line in Coconut source)

# ------------------------------------------------------------------
# Sequential (DFS)
# ------------------------------------------------------------------


    async def _run_sequential(self, node: AnyNode, ctx: ExecutionContext) -> Any:  #1609 (line in Coconut source)
        if ctx.is_paused():  #1610 (line in Coconut source)
            return None  #1611 (line in Coconut source)
        if ctx.hop_count >= ctx.max_hops:  #1612 (line in Coconut source)
            return None  #1613 (line in Coconut source)
        ctx.hop_count += 1  #1614 (line in Coconut source)

        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={"hop": ctx.hop_count, "node_type": str(node.node_type), "summary": ""})  #1616 (line in Coconut source)

        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)  #1622 (line in Coconut source)
        ctx.outputs[node.node_id] = result  #1623 (line in Coconut source)
        ctx.state.data["_last_node_id"] = node.node_id  #1624 (line in Coconut source)
        ctx.state.data["_last_output"] = result  #1625 (line in Coconut source)

        hop_event.payload["summary"] = _summarise(result)  #1627 (line in Coconut source)

        if ctx.is_paused():  #1629 (line in Coconut source)
            return result  #1630 (line in Coconut source)

        _coconut_case_match_to_7 = node  #1632 (line in Coconut source)
        _coconut_case_match_check_7 = False  #1632 (line in Coconut source)
        _coconut_match_temp_9 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1632 (line in Coconut source)
        _coconut_case_match_check_7 = True  #1632 (line in Coconut source)
        if _coconut_case_match_check_7:  #1632 (line in Coconut source)
            _coconut_case_match_check_7 = False  #1632 (line in Coconut source)
            if not _coconut_case_match_check_7:  #1632 (line in Coconut source)
                _coconut_match_set_name_rt = _coconut_sentinel  #1632 (line in Coconut source)
                if (_coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_7, AgentNode)):  #1632 (line in Coconut source)
                    _coconut_match_temp_10 = _coconut.getattr(_coconut_case_match_to_7, 'routing_table', _coconut_sentinel)  #1632 (line in Coconut source)
                    _coconut_match_temp_11 = _coconut.len(_coconut_case_match_to_7) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {}) and _coconut_case_match_to_7[i] == _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) if _coconut_case_match_to_7.__match_args__[i] not in ('routing_table',)) if _coconut.hasattr(_coconut_case_match_to_7, "__match_args__") else _coconut.len(_coconut_case_match_to_7) == 0  # type: ignore  #1632 (line in Coconut source)
                    if (_coconut_match_temp_10 is not _coconut_sentinel) and (_coconut_match_temp_11):  #1632 (line in Coconut source)
                        _coconut_match_set_name_rt = _coconut_match_temp_10  #1632 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1632 (line in Coconut source)
                if _coconut_case_match_check_7:  #1632 (line in Coconut source)
                    if _coconut_match_set_name_rt is not _coconut_sentinel:  #1632 (line in Coconut source)
                        rt = _coconut_match_set_name_rt  #1632 (line in Coconut source)

            if not _coconut_case_match_check_7:  #1632 (line in Coconut source)
                _coconut_match_set_name_rt = _coconut_sentinel  #1632 (line in Coconut source)
                if (not _coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_7, AgentNode)):  #1632 (line in Coconut source)
                    _coconut_match_temp_13 = _coconut.getattr(_coconut_case_match_to_7, 'routing_table', _coconut_sentinel)  #1632 (line in Coconut source)
                    if _coconut_match_temp_13 is not _coconut_sentinel:  #1632 (line in Coconut source)
                        _coconut_match_set_name_rt = _coconut_match_temp_13  #1632 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1632 (line in Coconut source)
                if _coconut_case_match_check_7:  #1632 (line in Coconut source)
                    _coconut_case_match_check_7 = False  #1632 (line in Coconut source)
                    if not _coconut_case_match_check_7:  #1632 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1632 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1632 (line in Coconut source)

                    if not _coconut_case_match_check_7:  #1632 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1632 (line in Coconut source)
                            _coconut_match_temp_12 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1632 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_12, _coconut.tuple):  #1632 (line in Coconut source)
                                raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1632 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_12) < 0:  #1632 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_12),))  #1632 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1632 (line in Coconut source)


                if _coconut_case_match_check_7:  #1632 (line in Coconut source)
                    if _coconut_match_set_name_rt is not _coconut_sentinel:  #1632 (line in Coconut source)
                        rt = _coconut_match_set_name_rt  #1632 (line in Coconut source)


        if _coconut_case_match_check_7 and not (rt):  #1632 (line in Coconut source)
            _coconut_case_match_check_7 = False  #1632 (line in Coconut source)
        if _coconut_case_match_check_7:  #1632 (line in Coconut source)
            next_id = await self._route(node, result, ctx, parent_event_id=hop_event.event_id)  #1634 (line in Coconut source)
            if next_id and next_id != "__END__":  #1635 (line in Coconut source)
                next_node = await self.store.get_node(next_id)  #1636 (line in Coconut source)
                if next_node:  #1637 (line in Coconut source)
                    return await self._run_sequential(next_node, ctx)  #1638 (line in Coconut source)
        if not _coconut_case_match_check_7:  #1639 (line in Coconut source)
            _coconut_match_temp_14 = _coconut.getattr(ApprovalNode, "_coconut_is_data", False) or _coconut.isinstance(ApprovalNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ApprovalNode)  # type: ignore  #1639 (line in Coconut source)
            _coconut_case_match_check_7 = True  #1639 (line in Coconut source)
            if _coconut_case_match_check_7:  #1639 (line in Coconut source)
                _coconut_case_match_check_7 = False  #1639 (line in Coconut source)
                if not _coconut_case_match_check_7:  #1639 (line in Coconut source)
                    if (_coconut_match_temp_14) and (_coconut.isinstance(_coconut_case_match_to_7, ApprovalNode)):  #1639 (line in Coconut source)
                        _coconut_match_temp_15 = _coconut.len(_coconut_case_match_to_7) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_7.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {}) and _coconut_case_match_to_7[i] == _coconut.getattr(_coconut_case_match_to_7, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_7.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_7, "__match_args__") else _coconut.len(_coconut_case_match_to_7) == 0  # type: ignore  #1639 (line in Coconut source)
                        if _coconut_match_temp_15:  #1639 (line in Coconut source)
                            _coconut_case_match_check_7 = True  #1639 (line in Coconut source)

                if not _coconut_case_match_check_7:  #1639 (line in Coconut source)
                    if (not _coconut_match_temp_14) and (_coconut.isinstance(_coconut_case_match_to_7, ApprovalNode)):  #1639 (line in Coconut source)
                        _coconut_case_match_check_7 = True  #1639 (line in Coconut source)
                    if _coconut_case_match_check_7:  #1639 (line in Coconut source)
                        _coconut_case_match_check_7 = False  #1639 (line in Coconut source)
                        if not _coconut_case_match_check_7:  #1639 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1639 (line in Coconut source)
                                _coconut_case_match_check_7 = True  #1639 (line in Coconut source)

                        if not _coconut_case_match_check_7:  #1639 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_7) in _coconut_self_match_types:  #1639 (line in Coconut source)
                                _coconut_match_temp_16 = _coconut.getattr(ApprovalNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1639 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_16, _coconut.tuple):  #1639 (line in Coconut source)
                                    raise _coconut.TypeError("ApprovalNode.__match_args__ must be a tuple")  #1639 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_16) < 0:  #1639 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ApprovalNode' only supports %s)" % (_coconut.len(_coconut_match_temp_16),))  #1639 (line in Coconut source)
                                _coconut_case_match_check_7 = True  #1639 (line in Coconut source)




            if _coconut_case_match_check_7:  #1639 (line in Coconut source)
                next_id = result.get("next_node_id") if isinstance(result, dict) else None  #1640 (line in Coconut source)
                if next_id and next_id != "__END__":  #1641 (line in Coconut source)
                    next_node = await self.store.get_node(next_id)  #1642 (line in Coconut source)
                    if next_node:  #1643 (line in Coconut source)
                        return await self._run_sequential(next_node, ctx)  #1644 (line in Coconut source)

        return result  #1646 (line in Coconut source)

# ------------------------------------------------------------------
# Parallel (BFS fan-out)
# ------------------------------------------------------------------


    async def _run_parallel(self, node: AnyNode, ctx: ExecutionContext) -> Any:  #1652 (line in Coconut source)
        if ctx.is_paused():  #1653 (line in Coconut source)
            return None  #1654 (line in Coconut source)
        if ctx.hop_count >= ctx.max_hops:  #1655 (line in Coconut source)
            return None  #1656 (line in Coconut source)
        ctx.hop_count += 1  #1657 (line in Coconut source)
        hop_event = self._emit(ctx, "hop", node.node_id, node.name or "", payload={"hop": ctx.hop_count, "node_type": str(node.node_type), "summary": ""})  #1658 (line in Coconut source)
        result = await self._execute_node(node, ctx, parent_event_id=hop_event.event_id)  #1663 (line in Coconut source)
        ctx.outputs[node.node_id] = result  #1664 (line in Coconut source)
        ctx.state.data["_last_node_id"] = node.node_id  #1665 (line in Coconut source)
        ctx.state.data["_last_output"] = result  #1666 (line in Coconut source)
        hop_event.payload["summary"] = _summarise(result)  #1667 (line in Coconut source)

        delegate_edges = await self.store.get_edges(node.node_id, edge_type=EdgeType.DELEGATES_TO)  #1669 (line in Coconut source)
        if not delegate_edges:  #1672 (line in Coconut source)
            return result  #1673 (line in Coconut source)

        delegate_nodes = []  #1675 (line in Coconut source)
        for edge in delegate_edges:  #1676 (line in Coconut source)
            n = await self.store.get_node(edge.dst_id)  #1677 (line in Coconut source)
            if n:  #1678 (line in Coconut source)
                delegate_nodes.append(n)  #1679 (line in Coconut source)

        sub_results = await asyncio.gather(*[self._run_parallel(d, ctx) for d in delegate_nodes])  #1681 (line in Coconut source)

        merged = {"node_result": result, "delegate_results": {d.node_id: r for d, r in zip(delegate_nodes, sub_results)}}  #1685 (line in Coconut source)
        ctx.outputs[node.node_id] = merged  #1691 (line in Coconut source)
        return merged  #1692 (line in Coconut source)

# ------------------------------------------------------------------
# Topological (DAG waves)
# ------------------------------------------------------------------


    async def _run_topological(self, entry_node_id: str, ctx: ExecutionContext) -> None:  #1698 (line in Coconut source)
        """Execute a DAG in topological order using stdlib graphlib."""  #1699 (line in Coconut source)
        dep_map: dict[str, set[str]] = {}  #1700 (line in Coconut source)
        visited: set[str] = set()  #1701 (line in Coconut source)
        queue = [entry_node_id,]  #1702 (line in Coconut source)

        while queue:  #1704 (line in Coconut source)
            nid = queue.pop()  #1705 (line in Coconut source)
            if nid in visited:  #1706 (line in Coconut source)
                continue  #1707 (line in Coconut source)
            visited.add(nid)  #1708 (line in Coconut source)
            edges = await self.store.get_edges(nid, edge_type=EdgeType.DELEGATES_TO)  #1709 (line in Coconut source)
            dep_map.setdefault(nid, set())  #1710 (line in Coconut source)
            for e in edges:  #1711 (line in Coconut source)
                dep_map.setdefault(e.dst_id, set()).add(nid)  #1712 (line in Coconut source)
                if e.dst_id not in visited:  #1713 (line in Coconut source)
                    queue.append(e.dst_id)  #1714 (line in Coconut source)

        for nid in list(dep_map):  #1716 (line in Coconut source)
            node = await self.store.get_node(nid)  #1717 (line in Coconut source)
            if isinstance(node, TransformNode) and node.input_keys:  #1718 (line in Coconut source)
                for key in node.input_keys:  #1719 (line in Coconut source)
                    if key in dep_map:  #1720 (line in Coconut source)
                        dep_map[nid].add(key)  #1721 (line in Coconut source)

        sorter = graphlib.TopologicalSorter(dep_map)  #1723 (line in Coconut source)
        sorter.prepare()  #1724 (line in Coconut source)

        wave = 0  #1726 (line in Coconut source)
        while sorter.is_active():  #1727 (line in Coconut source)
            if ctx.is_paused():  #1728 (line in Coconut source)
                return  #1729 (line in Coconut source)
            if ctx.hop_count >= ctx.max_hops:  #1730 (line in Coconut source)
                return  #1731 (line in Coconut source)
            wave += 1  #1732 (line in Coconut source)
            ready = list(sorter.get_ready())  #1733 (line in Coconut source)
# Skip nodes whose output is already cached in ctx.outputs (resume support:
# re-entering from the main entry skips previously completed nodes).
            already_done = [nid for nid in ready if nid in ctx.outputs]  #1736 (line in Coconut source)
            for nid in already_done:  #1737 (line in Coconut source)
                sorter.done(nid)  #1738 (line in Coconut source)
            ready = [nid for nid in ready if nid not in ctx.outputs]  #1739 (line in Coconut source)
            if not ready:  #1740 (line in Coconut source)
                continue  #1741 (line in Coconut source)
            remaining = max(ctx.max_hops - ctx.hop_count, 0)  #1742 (line in Coconut source)
            if remaining == 0:  #1743 (line in Coconut source)
                return  #1744 (line in Coconut source)
            if len(ready) > remaining:  #1745 (line in Coconut source)
                ready = ready[:remaining]  #1746 (line in Coconut source)
            nodes = list(await asyncio.gather(*[self.store.get_node(nid) for nid in ready]))  #1747 (line in Coconut source)

            hop_events = []  #1749 (line in Coconut source)
            valid_nodes = [(nid, n) for nid, n in zip(ready, nodes) if n is not None]  #1750 (line in Coconut source)
            for nid, n in valid_nodes:  #1751 (line in Coconut source)
                ctx.hop_count += 1  #1752 (line in Coconut source)
                hop_event = self._emit(ctx, "hop", nid, n.name or "", payload={"hop": ctx.hop_count, "node_type": str(n.node_type), "summary": "", "wave": wave})  #1753 (line in Coconut source)
                hop_events.append(hop_event)  #1759 (line in Coconut source)

            t0 = time.monotonic()  #1761 (line in Coconut source)
            results = await asyncio.gather(*[self._execute_node(n, ctx, parent_event_id=he.event_id) for (_, n), he in zip(valid_nodes, hop_events)])  #1762 (line in Coconut source)
            wave_ms = int((time.monotonic() - t0) * 1000)  #1766 (line in Coconut source)

            for (nid, _), result, hop_event in zip(valid_nodes, results, hop_events):  #1768 (line in Coconut source)
# Don't store a paused subgraph's output — it will re-run on resume.
                if not ctx.is_paused():  #1770 (line in Coconut source)
                    ctx.outputs[nid] = result  #1771 (line in Coconut source)
                    ctx.state.data["_last_node_id"] = nid  #1772 (line in Coconut source)
                    ctx.state.data["_last_output"] = result  #1773 (line in Coconut source)
                hop_event.payload["summary"] = _summarise(result)  #1774 (line in Coconut source)
                hop_event.payload["wave_ms"] = wave_ms  #1775 (line in Coconut source)
                sorter.done(nid)  #1776 (line in Coconut source)

# ------------------------------------------------------------------
# Node dispatch
# ------------------------------------------------------------------


    async def _execute_node(self, node: AnyNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #1782 (line in Coconut source)
        _coconut_case_match_to_8 = node  #1788 (line in Coconut source)
        _coconut_case_match_check_8 = False  #1788 (line in Coconut source)
        _coconut_match_temp_17 = _coconut.getattr(AgentNode, "_coconut_is_data", False) or _coconut.isinstance(AgentNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in AgentNode)  # type: ignore  #1788 (line in Coconut source)
        _coconut_case_match_check_8 = True  #1788 (line in Coconut source)
        if _coconut_case_match_check_8:  #1788 (line in Coconut source)
            _coconut_case_match_check_8 = False  #1788 (line in Coconut source)
            if not _coconut_case_match_check_8:  #1788 (line in Coconut source)
                if (_coconut_match_temp_17) and (_coconut.isinstance(_coconut_case_match_to_8, AgentNode)):  #1788 (line in Coconut source)
                    _coconut_match_temp_18 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1788 (line in Coconut source)
                    if _coconut_match_temp_18:  #1788 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1788 (line in Coconut source)

            if not _coconut_case_match_check_8:  #1788 (line in Coconut source)
                if (not _coconut_match_temp_17) and (_coconut.isinstance(_coconut_case_match_to_8, AgentNode)):  #1788 (line in Coconut source)
                    _coconut_case_match_check_8 = True  #1788 (line in Coconut source)
                if _coconut_case_match_check_8:  #1788 (line in Coconut source)
                    _coconut_case_match_check_8 = False  #1788 (line in Coconut source)
                    if not _coconut_case_match_check_8:  #1788 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1788 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1788 (line in Coconut source)

                    if not _coconut_case_match_check_8:  #1788 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1788 (line in Coconut source)
                            _coconut_match_temp_19 = _coconut.getattr(AgentNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1788 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_19, _coconut.tuple):  #1788 (line in Coconut source)
                                raise _coconut.TypeError("AgentNode.__match_args__ must be a tuple")  #1788 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_19) < 0:  #1788 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'AgentNode' only supports %s)" % (_coconut.len(_coconut_match_temp_19),))  #1788 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1788 (line in Coconut source)




        if _coconut_case_match_check_8:  #1788 (line in Coconut source)
            return await self._execute_agent(node, ctx, parent_event_id=parent_event_id)  #1790 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
            _coconut_match_temp_20 = _coconut.getattr(ToolNode, "_coconut_is_data", False) or _coconut.isinstance(ToolNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ToolNode)  # type: ignore  #1791 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1791 (line in Coconut source)
            if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1791 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                    if (_coconut_match_temp_20) and (_coconut.isinstance(_coconut_case_match_to_8, ToolNode)):  #1791 (line in Coconut source)
                        _coconut_match_temp_21 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1791 (line in Coconut source)
                        if _coconut_match_temp_21:  #1791 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1791 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                    if (not _coconut_match_temp_20) and (_coconut.isinstance(_coconut_case_match_to_8, ToolNode)):  #1791 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1791 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1791 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1791 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1791 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1791 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1791 (line in Coconut source)
                                _coconut_match_temp_22 = _coconut.getattr(ToolNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1791 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_22, _coconut.tuple):  #1791 (line in Coconut source)
                                    raise _coconut.TypeError("ToolNode.__match_args__ must be a tuple")  #1791 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_22) < 0:  #1791 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ToolNode' only supports %s)" % (_coconut.len(_coconut_match_temp_22),))  #1791 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1791 (line in Coconut source)




            if _coconut_case_match_check_8:  #1791 (line in Coconut source)
                t0 = time.monotonic()  #1792 (line in Coconut source)
                result = await self._execute_tool(node, ctx)  #1793 (line in Coconut source)
                duration_ms = int((time.monotonic() - t0) * 1000)  #1794 (line in Coconut source)
                self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name, "callable_ref": node.callable_ref, "output_summary": _summarise(result), "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #1795 (line in Coconut source)
                return result  #1806 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1807 (line in Coconut source)
            _coconut_match_temp_23 = _coconut.getattr(ApprovalNode, "_coconut_is_data", False) or _coconut.isinstance(ApprovalNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ApprovalNode)  # type: ignore  #1807 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1807 (line in Coconut source)
            if _coconut_case_match_check_8:  #1807 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1807 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1807 (line in Coconut source)
                    if (_coconut_match_temp_23) and (_coconut.isinstance(_coconut_case_match_to_8, ApprovalNode)):  #1807 (line in Coconut source)
                        _coconut_match_temp_24 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1807 (line in Coconut source)
                        if _coconut_match_temp_24:  #1807 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1807 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1807 (line in Coconut source)
                    if (not _coconut_match_temp_23) and (_coconut.isinstance(_coconut_case_match_to_8, ApprovalNode)):  #1807 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1807 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1807 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1807 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1807 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1807 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1807 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1807 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1807 (line in Coconut source)
                                _coconut_match_temp_25 = _coconut.getattr(ApprovalNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1807 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_25, _coconut.tuple):  #1807 (line in Coconut source)
                                    raise _coconut.TypeError("ApprovalNode.__match_args__ must be a tuple")  #1807 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_25) < 0:  #1807 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ApprovalNode' only supports %s)" % (_coconut.len(_coconut_match_temp_25),))  #1807 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1807 (line in Coconut source)




            if _coconut_case_match_check_8:  #1807 (line in Coconut source)
                return await self._execute_approval(node, ctx, parent_event_id=parent_event_id)  #1808 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1809 (line in Coconut source)
            _coconut_match_temp_26 = _coconut.getattr(ContextNode, "_coconut_is_data", False) or _coconut.isinstance(ContextNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ContextNode)  # type: ignore  #1809 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1809 (line in Coconut source)
            if _coconut_case_match_check_8:  #1809 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1809 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1809 (line in Coconut source)
                    if (_coconut_match_temp_26) and (_coconut.isinstance(_coconut_case_match_to_8, ContextNode)):  #1809 (line in Coconut source)
                        _coconut_match_temp_27 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1809 (line in Coconut source)
                        if _coconut_match_temp_27:  #1809 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1809 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1809 (line in Coconut source)
                    if (not _coconut_match_temp_26) and (_coconut.isinstance(_coconut_case_match_to_8, ContextNode)):  #1809 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1809 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1809 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1809 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1809 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1809 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1809 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1809 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1809 (line in Coconut source)
                                _coconut_match_temp_28 = _coconut.getattr(ContextNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1809 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_28, _coconut.tuple):  #1809 (line in Coconut source)
                                    raise _coconut.TypeError("ContextNode.__match_args__ must be a tuple")  #1809 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_28) < 0:  #1809 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ContextNode' only supports %s)" % (_coconut.len(_coconut_match_temp_28),))  #1809 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1809 (line in Coconut source)




            if _coconut_case_match_check_8:  #1809 (line in Coconut source)
                return node.content  #1810 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1811 (line in Coconut source)
            _coconut_match_temp_29 = _coconut.getattr(GraphNode, "_coconut_is_data", False) or _coconut.isinstance(GraphNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in GraphNode)  # type: ignore  #1811 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1811 (line in Coconut source)
            if _coconut_case_match_check_8:  #1811 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1811 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1811 (line in Coconut source)
                    if (_coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_8, GraphNode)):  #1811 (line in Coconut source)
                        _coconut_match_temp_30 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1811 (line in Coconut source)
                        if _coconut_match_temp_30:  #1811 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1811 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1811 (line in Coconut source)
                    if (not _coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_8, GraphNode)):  #1811 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1811 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1811 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1811 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1811 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1811 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1811 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1811 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1811 (line in Coconut source)
                                _coconut_match_temp_31 = _coconut.getattr(GraphNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1811 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_31, _coconut.tuple):  #1811 (line in Coconut source)
                                    raise _coconut.TypeError("GraphNode.__match_args__ must be a tuple")  #1811 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_31) < 0:  #1811 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'GraphNode' only supports %s)" % (_coconut.len(_coconut_match_temp_31),))  #1811 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1811 (line in Coconut source)




            if _coconut_case_match_check_8:  #1811 (line in Coconut source)
                return await self._execute_subgraph(node, ctx, parent_event_id=parent_event_id)  #1812 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1813 (line in Coconut source)
            _coconut_match_temp_32 = _coconut.getattr(TransformNode, "_coconut_is_data", False) or _coconut.isinstance(TransformNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in TransformNode)  # type: ignore  #1813 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1813 (line in Coconut source)
            if _coconut_case_match_check_8:  #1813 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1813 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1813 (line in Coconut source)
                    if (_coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_8, TransformNode)):  #1813 (line in Coconut source)
                        _coconut_match_temp_33 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1813 (line in Coconut source)
                        if _coconut_match_temp_33:  #1813 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1813 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1813 (line in Coconut source)
                    if (not _coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_8, TransformNode)):  #1813 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1813 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1813 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1813 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1813 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1813 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1813 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1813 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1813 (line in Coconut source)
                                _coconut_match_temp_34 = _coconut.getattr(TransformNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1813 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_34, _coconut.tuple):  #1813 (line in Coconut source)
                                    raise _coconut.TypeError("TransformNode.__match_args__ must be a tuple")  #1813 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_34) < 0:  #1813 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'TransformNode' only supports %s)" % (_coconut.len(_coconut_match_temp_34),))  #1813 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1813 (line in Coconut source)




            if _coconut_case_match_check_8:  #1813 (line in Coconut source)
                return await self._execute_transform(node, ctx, parent_event_id=parent_event_id)  #1814 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1815 (line in Coconut source)
            _coconut_match_temp_35 = _coconut.getattr(ReasonerNode, "_coconut_is_data", False) or _coconut.isinstance(ReasonerNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ReasonerNode)  # type: ignore  #1815 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1815 (line in Coconut source)
            if _coconut_case_match_check_8:  #1815 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1815 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1815 (line in Coconut source)
                    if (_coconut_match_temp_35) and (_coconut.isinstance(_coconut_case_match_to_8, ReasonerNode)):  #1815 (line in Coconut source)
                        _coconut_match_temp_36 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1815 (line in Coconut source)
                        if _coconut_match_temp_36:  #1815 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1815 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1815 (line in Coconut source)
                    if (not _coconut_match_temp_35) and (_coconut.isinstance(_coconut_case_match_to_8, ReasonerNode)):  #1815 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1815 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1815 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1815 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1815 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1815 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1815 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1815 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1815 (line in Coconut source)
                                _coconut_match_temp_37 = _coconut.getattr(ReasonerNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1815 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_37, _coconut.tuple):  #1815 (line in Coconut source)
                                    raise _coconut.TypeError("ReasonerNode.__match_args__ must be a tuple")  #1815 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_37) < 0:  #1815 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ReasonerNode' only supports %s)" % (_coconut.len(_coconut_match_temp_37),))  #1815 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1815 (line in Coconut source)




            if _coconut_case_match_check_8:  #1815 (line in Coconut source)
                return await self._execute_reasoner(node, ctx, parent_event_id=parent_event_id)  #1816 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1817 (line in Coconut source)
            _coconut_match_temp_38 = _coconut.getattr(PromptNode, "_coconut_is_data", False) or _coconut.isinstance(PromptNode, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in PromptNode)  # type: ignore  #1817 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1817 (line in Coconut source)
            if _coconut_case_match_check_8:  #1817 (line in Coconut source)
                _coconut_case_match_check_8 = False  #1817 (line in Coconut source)
                if not _coconut_case_match_check_8:  #1817 (line in Coconut source)
                    if (_coconut_match_temp_38) and (_coconut.isinstance(_coconut_case_match_to_8, PromptNode)):  #1817 (line in Coconut source)
                        _coconut_match_temp_39 = _coconut.len(_coconut_case_match_to_8) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_8.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {}) and _coconut_case_match_to_8[i] == _coconut.getattr(_coconut_case_match_to_8, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_8.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_8, "__match_args__") else _coconut.len(_coconut_case_match_to_8) == 0  # type: ignore  #1817 (line in Coconut source)
                        if _coconut_match_temp_39:  #1817 (line in Coconut source)
                            _coconut_case_match_check_8 = True  #1817 (line in Coconut source)

                if not _coconut_case_match_check_8:  #1817 (line in Coconut source)
                    if (not _coconut_match_temp_38) and (_coconut.isinstance(_coconut_case_match_to_8, PromptNode)):  #1817 (line in Coconut source)
                        _coconut_case_match_check_8 = True  #1817 (line in Coconut source)
                    if _coconut_case_match_check_8:  #1817 (line in Coconut source)
                        _coconut_case_match_check_8 = False  #1817 (line in Coconut source)
                        if not _coconut_case_match_check_8:  #1817 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1817 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1817 (line in Coconut source)

                        if not _coconut_case_match_check_8:  #1817 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_8) in _coconut_self_match_types:  #1817 (line in Coconut source)
                                _coconut_match_temp_40 = _coconut.getattr(PromptNode, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #1817 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_40, _coconut.tuple):  #1817 (line in Coconut source)
                                    raise _coconut.TypeError("PromptNode.__match_args__ must be a tuple")  #1817 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_40) < 0:  #1817 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'PromptNode' only supports %s)" % (_coconut.len(_coconut_match_temp_40),))  #1817 (line in Coconut source)
                                _coconut_case_match_check_8 = True  #1817 (line in Coconut source)




            if _coconut_case_match_check_8:  #1817 (line in Coconut source)
                return node.render()  #1818 (line in Coconut source)
        if not _coconut_case_match_check_8:  #1819 (line in Coconut source)
            _coconut_case_match_check_8 = True  #1819 (line in Coconut source)
            if _coconut_case_match_check_8:  #1819 (line in Coconut source)
                return None  #1820 (line in Coconut source)

# ------------------------------------------------------------------
# Sub-graph execution
# ------------------------------------------------------------------


    _MAX_SUBGRAPH_DEPTH = 16  #1826 (line in Coconut source)

    async def _execute_subgraph(self, node: GraphNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #1828 (line in Coconut source)
        """Run a GraphNode: descend, route to exit, surface result."""  #1834 (line in Coconut source)
        if node.node_id in ctx._active_subgraphs:  #1835 (line in Coconut source)
            chain = " → ".join(ctx._active_subgraphs + [node.node_id,])  #1836 (line in Coconut source)
            raise ValueError("GraphNode cycle detected: {_coconut_format_0}".format(_coconut_format_0=(chain)))  #1837 (line in Coconut source)
        if len(ctx._active_subgraphs) >= self._MAX_SUBGRAPH_DEPTH:  #1838 (line in Coconut source)
            raise ValueError(("GraphNode recursion depth exceeded ".format() + "({_coconut_format_0}) at {_coconut_format_1!r}".format(_coconut_format_0=(self._MAX_SUBGRAPH_DEPTH), _coconut_format_1=(node.name or node.node_id))))  #1839 (line in Coconut source)

        if not node.entry_node_id:  #1844 (line in Coconut source)
            raise ValueError("GraphNode {_coconut_format_0!r} has no entry_node_id.".format(_coconut_format_0=(node.name or node.node_id)))  #1845 (line in Coconut source)
        sub_entry = await self.store.get_node(node.entry_node_id)  #1848 (line in Coconut source)
        if sub_entry is None:  #1849 (line in Coconut source)
            raise ValueError(("GraphNode {_coconut_format_0!r} entry_node_id ".format(_coconut_format_0=(node.name or node.node_id)) + "{_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node.entry_node_id))))  #1850 (line in Coconut source)

        exit_id = node.exit_node_id or node.entry_node_id  #1855 (line in Coconut source)
        sub_query = self._resolve_subgraph_query(node, ctx)  #1856 (line in Coconut source)
        sub_state_overlay = self._resolve_subgraph_state(node, ctx)  #1857 (line in Coconut source)

        self._emit(ctx, "subgraph_enter", node.node_id, node.name or "", payload={"entry_node_id": node.entry_node_id, "exit_node_id": exit_id, "strategy": node.strategy, "scoped": node.scope_outputs}, parent_event_id=parent_event_id)  #1859 (line in Coconut source)

        async def _run_subgraph() -> Any:  #1870 (line in Coconut source)
            if node.scope_outputs:  #1871 (line in Coconut source)
                child = ExecutionContext(query=sub_query, session_id=ctx.session_id, max_hops=max(ctx.max_hops - ctx.hop_count, 1), state=ctx.state, allowed_tools=ctx.allowed_tools, extra_messages=list(ctx.extra_messages), _active_subgraphs=ctx._active_subgraphs + [node.node_id,])  #1872 (line in Coconut source)
                if sub_state_overlay:  #1881 (line in Coconut source)
                    ctx.state.data.update(sub_state_overlay)  #1882 (line in Coconut source)
                await self._dispatch_strategy(node.strategy, sub_entry, child)  #1883 (line in Coconut source)
                ctx.trace.extend(child.trace)  #1884 (line in Coconut source)
                ctx.hop_count += child.hop_count  #1885 (line in Coconut source)
                return child.outputs.get(exit_id)  #1886 (line in Coconut source)
            else:  #1887 (line in Coconut source)
                ctx._active_subgraphs.append(node.node_id)  #1888 (line in Coconut source)
                try:  #1889 (line in Coconut source)
                    if sub_state_overlay:  #1890 (line in Coconut source)
                        ctx.state.data.update(sub_state_overlay)  #1891 (line in Coconut source)
                    if sub_query is not None:  #1892 (line in Coconut source)
                        prev_query = ctx.query  #1893 (line in Coconut source)
                        ctx.query = sub_query  #1894 (line in Coconut source)
                        try:  #1895 (line in Coconut source)
                            await self._dispatch_strategy(node.strategy, sub_entry, ctx)  #1896 (line in Coconut source)
                        finally:  #1897 (line in Coconut source)
                            ctx.query = prev_query  #1898 (line in Coconut source)
                    else:  #1899 (line in Coconut source)
                        await self._dispatch_strategy(node.strategy, sub_entry, ctx)  #1900 (line in Coconut source)
                    return ctx.outputs.get(exit_id)  #1901 (line in Coconut source)
                finally:  #1902 (line in Coconut source)
                    ctx._active_subgraphs.pop()  #1903 (line in Coconut source)


        try:  #1905 (line in Coconut source)
            result = await self._call_with_retry(_run_subgraph, ctx, node=node, policy=node.execution_policy, parent_event_id=parent_event_id)  #1906 (line in Coconut source)
        except Exception as exc:  #1913 (line in Coconut source)
            self._emit(ctx, "subgraph_exit", node.node_id, node.name or "", payload={"exit_node_id": exit_id, "summary": "", "error": str(exc), "error_type": type(exc).__name__}, parent_event_id=parent_event_id)  #1914 (line in Coconut source)
            raise  #1924 (line in Coconut source)

        self._emit(ctx, "subgraph_exit", node.node_id, node.name or "", payload={"exit_node_id": exit_id, "summary": _summarise(result)}, parent_event_id=parent_event_id)  #1926 (line in Coconut source)
        return result  #1931 (line in Coconut source)


    async def _dispatch_strategy(self, strategy: str, entry: AnyNode, ctx: ExecutionContext,) -> None:  #1933 (line in Coconut source)
        _coconut_case_match_to_9 = strategy  #1939 (line in Coconut source)
        _coconut_case_match_check_9 = False  #1939 (line in Coconut source)
        if _coconut_case_match_to_9 == "sequential":  #1939 (line in Coconut source)
            _coconut_case_match_check_9 = True  #1939 (line in Coconut source)
        if _coconut_case_match_check_9:  #1939 (line in Coconut source)
            await self._run_sequential(entry, ctx)  #1941 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1942 (line in Coconut source)
            if _coconut_case_match_to_9 == "parallel":  #1942 (line in Coconut source)
                _coconut_case_match_check_9 = True  #1942 (line in Coconut source)
            if _coconut_case_match_check_9:  #1942 (line in Coconut source)
                await self._run_parallel(entry, ctx)  #1943 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1944 (line in Coconut source)
            if _coconut_case_match_to_9 == "topological":  #1944 (line in Coconut source)
                _coconut_case_match_check_9 = True  #1944 (line in Coconut source)
            if _coconut_case_match_check_9:  #1944 (line in Coconut source)
                await self._run_topological(entry.node_id, ctx)  #1945 (line in Coconut source)
        if not _coconut_case_match_check_9:  #1946 (line in Coconut source)
            _coconut_case_match_check_9 = True  #1946 (line in Coconut source)
            if _coconut_case_match_check_9:  #1946 (line in Coconut source)
                raise ValueError("Unknown sub-graph strategy: {_coconut_format_0!r}".format(_coconut_format_0=(strategy)))  #1947 (line in Coconut source)


    async def resolve_subgraph_inputs(self, node: GraphNode | str, ctx: ExecutionContext | None=None,) -> dict[str, Any]:  #1949 (line in Coconut source)
        """Dry-run a GraphNode's input wiring without executing anything."""  #1954 (line in Coconut source)
        if isinstance(node, str):  #1955 (line in Coconut source)
            resolved = await self.store.get_node(node)  #1956 (line in Coconut source)
            if resolved is None:  #1957 (line in Coconut source)
                raise ValueError("Node {_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node)))  #1958 (line in Coconut source)
            node = resolved  #1959 (line in Coconut source)
        if not isinstance(node, GraphNode):  #1960 (line in Coconut source)
            raise ValueError("resolve_subgraph_inputs expected GraphNode, got {_coconut_format_0}".format(_coconut_format_0=(type(node).__name__)))  #1961 (line in Coconut source)
        if not node.entry_node_id:  #1964 (line in Coconut source)
            raise ValueError("GraphNode {_coconut_format_0!r} has no entry_node_id.".format(_coconut_format_0=(node.name or node.node_id)))  #1965 (line in Coconut source)
        sub_entry = await self.store.get_node(node.entry_node_id)  #1968 (line in Coconut source)
        if sub_entry is None:  #1969 (line in Coconut source)
            raise ValueError(("GraphNode {_coconut_format_0!r} entry_node_id ".format(_coconut_format_0=(node.name or node.node_id)) + "{_coconut_format_0!r} not found in graph store.".format(_coconut_format_0=(node.entry_node_id))))  #1970 (line in Coconut source)
        ctx = ctx or ExecutionContext(query="")  #1974 (line in Coconut source)
        return {"entry_node_id": node.entry_node_id, "exit_node_id": node.exit_node_id or node.entry_node_id, "strategy": node.strategy, "scope_outputs": node.scope_outputs, "query": self._resolve_subgraph_query(node, ctx), "state_overlay": self._resolve_subgraph_state(node, ctx)}  #1975 (line in Coconut source)


    def _resolve_subgraph_query(self, node: GraphNode, ctx: ExecutionContext,) -> QueryContent:  #1984 (line in Coconut source)
        """Build the sub-graph's initial query from input_keys."""  #1989 (line in Coconut source)
        if not node.input_keys:  #1990 (line in Coconut source)
            return ctx.query  #1991 (line in Coconut source)
        parts = [_text_of(ctx.outputs[key]) if key in ctx.outputs else _text_of(ctx.state.data[key]) if key in ctx.state.data else None for key in node.input_keys]  #1992 (line in Coconut source)
        return "\n\n".join((p for p in parts if p)) or _query_text(ctx.query)  #1998 (line in Coconut source)


    def _resolve_subgraph_state(self, node: GraphNode, ctx: ExecutionContext,) -> dict[str, Any]:  #2000 (line in Coconut source)
        """Resolve input_map aliases against parent outputs / state."""  #2005 (line in Coconut source)
        if not node.input_map:  #2006 (line in Coconut source)
            return {}  #2007 (line in Coconut source)
        return {alias: ctx.outputs[source] if source in ctx.outputs else ctx.state.data[source] for alias, source in node.input_map.items() if source in ctx.outputs or source in ctx.state.data}  #2008 (line in Coconut source)

# ------------------------------------------------------------------
# Agent execution
# ------------------------------------------------------------------


    async def _execute_agent(self, node: AgentNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #2018 (line in Coconut source)
        if node.pause_before:  #2024 (line in Coconut source)
            await self._pause_execution(ctx, node, reason="pause_before", waiting_for=node.wait_for_input)  #2025 (line in Coconut source)
            return {"text": "", "intent": "default", "status": "paused"}  #2031 (line in Coconut source)
        t0 = time.monotonic()  #2032 (line in Coconut source)
        composed = await self.composer.compose(node, query=_query_text(ctx.query), session_id=ctx.session_id)  #2033 (line in Coconut source)
        system = composed.build_system_prompt()  #2034 (line in Coconut source)
        tool_defs = composed.build_tool_schemas()  #2035 (line in Coconut source)
        if node.state_schema:  #2036 (line in Coconut source)
            ctx.state.schema = node.state_schema  #2037 (line in Coconut source)
        await self._validate_node_schemas(node, ctx=ctx, parent_event_id=parent_event_id)  #2038 (line in Coconut source)

        agent_event_id = str(uuid.uuid4())  #2044 (line in Coconut source)
        self._emit(ctx, "agent_start", node.node_id, node.name or "", payload={"query": ctx.query, "system": system, "model": node.model, "tools": [t.name for t in composed.tools], "context": [c.name for c in composed.context if c.name], "context_scores": [{"name": s.context.name, "score": round(s.score, 4), "source": s.source, "hops": s.hops} for s in composed.context_selection]}, event_id=agent_event_id, parent_event_id=parent_event_id)  #2045 (line in Coconut source)

        if composed.context:  #2067 (line in Coconut source)
            self._emit(ctx, "context_inject", node.node_id, node.name or "", payload={"context_names": [c.name for c in composed.context if c.name], "count": len(composed.context), "selected_contexts": [{"node_id": s.context.node_id, "name": s.context.name, "score": round(s.score, 4), "source": s.source, "hops": s.hops, "token_count": s.token_count, "path": s.path, "reasons": s.reasons} for s in composed.context_selection]}, parent_event_id=agent_event_id)  #2068 (line in Coconut source)

        messages: list[dict[str, Any]] = list(ctx.extra_messages)  #2090 (line in Coconut source)
        if ctx.state.data:  #2091 (line in Coconut source)
            messages.append({"role": "assistant", "content": "Workflow state:\n{_coconut_format_0}".format(_coconut_format_0=(json.dumps(ctx.state.data, sort_keys=True, default=str)))})  #2092 (line in Coconut source)

        image_ctx_blocks = composed.build_image_context_blocks()  #2097 (line in Coconut source)
        if image_ctx_blocks:  #2098 (line in Coconut source)
            user_content: QueryContent = (list(ctx.query) + image_ctx_blocks if isinstance(ctx.query, list) else [{"type": "text", "text": ctx.query},] + image_ctx_blocks)  #2099 (line in Coconut source)
        else:  #2103 (line in Coconut source)
            user_content = ctx.query  #2104 (line in Coconut source)
        messages.append({"role": "user", "content": user_content})  #2105 (line in Coconut source)

        last_response = None  #2107 (line in Coconut source)
        iterations = 0  #2108 (line in Coconut source)

        for _iteration in range(node.max_iterations):  #2110 (line in Coconut source)
            iterations += 1  #2111 (line in Coconut source)
            policy = node.execution_policy  #2112 (line in Coconut source)
            try:  #2113 (line in Coconut source)
                last_response = await self._call_with_retry(lambda _=None: self._chat_once(node, system, messages, tool_defs), ctx, node=node, policy=policy, parent_event_id=agent_event_id)  #2114 (line in Coconut source)
            except Exception:  #2121 (line in Coconut source)
                raise  #2122 (line in Coconut source)

            if last_response.stop_reason == "end_turn":  #2124 (line in Coconut source)
                intent = await self._infer_intent(last_response.text, node)  #2125 (line in Coconut source)
                result = {"text": last_response.text, "intent": intent}  #2126 (line in Coconut source)
                await self._validate_node_schemas(node, output_payload=result, ctx=ctx, parent_event_id=agent_event_id)  #2127 (line in Coconut source)
                if node.pause_after:  #2133 (line in Coconut source)
                    await self._pause_execution(ctx, node, reason="pause_after", waiting_for=node.wait_for_input, metadata={"result": result})  #2134 (line in Coconut source)
                duration_ms = int((time.monotonic() - t0) * 1000)  #2141 (line in Coconut source)
                self._emit(ctx, "agent_end", node.node_id, node.name or "", payload={"text_summary": _summarise(last_response.text), "full_response": last_response.text, "intent": intent, "iterations": iterations}, parent_event_id=agent_event_id, duration_ms=duration_ms)  #2142 (line in Coconut source)
                return result  #2153 (line in Coconut source)

            if last_response.stop_reason == "tool_use":  #2155 (line in Coconut source)
                tool_results = await self._handle_tool_calls(last_response, node, ctx, parent_event_id=agent_event_id)  #2156 (line in Coconut source)
                messages = self._backend.extend_messages(messages, last_response, tool_results)  #2159 (line in Coconut source)
                continue  #2160 (line in Coconut source)

            break  #2162 (line in Coconut source)

        text = last_response.text if last_response else ""  #2164 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2165 (line in Coconut source)
        self._emit(ctx, "agent_end", node.node_id, node.name or "", payload={"text_summary": _summarise(text), "full_response": text, "intent": "default", "iterations": iterations}, parent_event_id=agent_event_id, duration_ms=duration_ms)  #2166 (line in Coconut source)
        result = {"text": text, "intent": "default"}  #2177 (line in Coconut source)
        await self._validate_node_schemas(node, output_payload=result, ctx=ctx, parent_event_id=agent_event_id)  #2178 (line in Coconut source)
        return result  #2184 (line in Coconut source)


    async def _execute_approval(self, node: ApprovalNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #2186 (line in Coconut source)
        payload = ctx.state.data.get(node.input_key, {})  #2192 (line in Coconut source)
        if isinstance(payload, dict) and "approved" in payload:  #2193 (line in Coconut source)
            approved = bool(payload.get("approved"))  #2194 (line in Coconut source)
            assigned_to = payload.get("assigned_to")  #2195 (line in Coconut source)
            task = next((item for item in ctx.state.inbox.values() if item.node_id == node.node_id and item.status == "pending"), None)  #2196 (line in Coconut source)
            if task is not None:  #2200 (line in Coconut source)
                task.status = "approved" if approved else "rejected"  #2201 (line in Coconut source)
                task.assigned_to = assigned_to or task.assigned_to  #2202 (line in Coconut source)
                task.resolved_at = datetime.now(timezone.utc)  #2203 (line in Coconut source)
            return {"approved": approved, "next_node_id": node.approved_target_id if approved else node.rejected_target_id, "assigned_to": assigned_to}  #2204 (line in Coconut source)

        assigned_to = node.assignees[0] if node.assignees and node.require_assignment else None  #2210 (line in Coconut source)
        task = ApprovalTask(task_id=str(uuid.uuid4()), node_id=node.node_id, token=str(uuid.uuid4()), assignees=list(node.assignees), assigned_to=assigned_to, waiting_for=node.instructions or node.name, due_at=(datetime.now(timezone.utc) + timedelta(seconds=node.sla_seconds) if node.sla_seconds else None), escalation_target=node.escalation_target or None, metadata={"assignment_mode": node.assignment_mode, "input_key": node.input_key})  #2211 (line in Coconut source)
        ctx.state.inbox[task.task_id] = task  #2225 (line in Coconut source)
        self._emit(ctx, "approval_task", node.node_id, node.name or "", payload={"task_id": task.task_id, "assignees": task.assignees, "assigned_to": task.assigned_to, "due_at": task.due_at.isoformat() if task.due_at else None, "escalation_target": task.escalation_target}, parent_event_id=parent_event_id)  #2226 (line in Coconut source)
        if task.due_at and task.escalation_target:  #2240 (line in Coconut source)
            self._emit(ctx, "schedule", node.node_id, node.name or "", payload={"task_id": task.task_id, "due_at": task.due_at.isoformat(), "escalation_target": task.escalation_target}, parent_event_id=parent_event_id)  #2241 (line in Coconut source)
        await self._pause_execution(ctx, node, reason="approval_wait", waiting_for=node.instructions or node.name, metadata={"task_id": task.task_id, "token": task.token})  #2253 (line in Coconut source)
        return {"status": "paused", "task_id": task.task_id, "next_node_id": None}  #2260 (line in Coconut source)


    async def _handle_tool_calls(self, response: Any, agent_node: AgentNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> list[ToolResult]:  #2262 (line in Coconut source)
        """Execute all tool calls in the response and return normalised results."""  #2269 (line in Coconut source)
        tool_edges = await self.store.get_edges(agent_node.node_id, edge_type=EdgeType.HAS_TOOL)  #2270 (line in Coconut source)
        tool_map: dict[str, ToolNode] = {}  #2271 (line in Coconut source)
        for edge in tool_edges:  #2272 (line in Coconut source)
            tn = await self.store.get_node(edge.dst_id)  #2273 (line in Coconut source)
            if tn and isinstance(tn, ToolNode):  #2274 (line in Coconut source)
                tool_map[tn.name] = tn  #2275 (line in Coconut source)

        results: list[ToolResult] = []  #2277 (line in Coconut source)
        for tc in response.tool_calls:  #2278 (line in Coconut source)
            tool_node = tool_map.get(tc.name)  #2279 (line in Coconut source)
            callable_ref = tool_node.callable_ref if tool_node else ""  #2280 (line in Coconut source)

            call_event = self._emit(ctx, "tool_call", tool_node.node_id if tool_node else agent_node.node_id, tc.name, payload={"tool_name": tc.name, "callable_ref": callable_ref, "input": tc.input}, parent_event_id=parent_event_id)  #2282 (line in Coconut source)

            t0 = time.monotonic()  #2294 (line in Coconut source)
            if tool_node is None:  #2295 (line in Coconut source)
                content = "Tool {_coconut_format_0!r} not found.".format(_coconut_format_0=(tc.name))  #2296 (line in Coconut source)
                success = False  #2297 (line in Coconut source)
            else:  #2298 (line in Coconut source)
                try:  #2299 (line in Coconut source)
                    raw = await self._execute_tool(tool_node, ctx, input_data=tc.input)  #2300 (line in Coconut source)
                    await self._materialise_output(tool_node, raw, ctx)  #2301 (line in Coconut source)
                    content = raw if isinstance(raw, str) else str(raw)  #2302 (line in Coconut source)
                    success = True  #2303 (line in Coconut source)
                except Exception as exc:  #2304 (line in Coconut source)
                    content = "Tool error: {_coconut_format_0}".format(_coconut_format_0=(exc))  #2305 (line in Coconut source)
                    success = False  #2306 (line in Coconut source)

            duration_ms = int((time.monotonic() - t0) * 1000)  #2308 (line in Coconut source)

            self._emit(ctx, "tool_result", tool_node.node_id if tool_node else agent_node.node_id, tc.name, payload={"tool_name": tc.name, "output_summary": _summarise(content), "success": success}, parent_event_id=call_event.event_id, duration_ms=duration_ms)  #2310 (line in Coconut source)

            results.append(ToolResult(tool_call_id=tc.id, content=content))  #2323 (line in Coconut source)

        return results  #2325 (line in Coconut source)

# ------------------------------------------------------------------
# Tool execution
# ------------------------------------------------------------------


    def _callable_injection_kwargs(self, fn: Any, ctx: ExecutionContext) -> dict[str, Any]:  #2331 (line in Coconut source)
        """Extra keyword arguments to pass to a tool/transform callable."""  #2332 (line in Coconut source)
        try:  #2333 (line in Coconut source)
            params = inspect.signature(fn).parameters  #2334 (line in Coconut source)
        except (TypeError, ValueError):  #2335 (line in Coconut source)
            return {}  #2336 (line in Coconut source)
        kwargs: dict[str, Any] = {}  #2337 (line in Coconut source)
        if "session_id" in params:  #2338 (line in Coconut source)
            kwargs["session_id"] = ctx.session_id  #2339 (line in Coconut source)
        if "ctx" in params:  #2340 (line in Coconut source)
            kwargs["ctx"] = ctx  #2341 (line in Coconut source)
        if "store" in params:  #2342 (line in Coconut source)
            kwargs["store"] = self.store  #2343 (line in Coconut source)
        return kwargs  #2344 (line in Coconut source)


    async def _execute_tool(self, node: ToolNode, ctx: ExecutionContext, input_data: dict[str, Any] | None=None,) -> Any:  #2346 (line in Coconut source)
        fn = self._tool_fns.get(node.callable_ref)  #2352 (line in Coconut source)
        if fn is None:  #2353 (line in Coconut source)
            raise RuntimeError(("Tool callable not registered: {_coconut_format_0!r}. ".format(_coconut_format_0=(node.callable_ref)) + "Call executor.register_tool(ref, fn) before running."))  #2354 (line in Coconut source)

        payload = input_data or (list(ctx.outputs.values())[-1] if ctx.outputs else {})  #2359 (line in Coconut source)
        runtime_payload = dict(payload) if isinstance(payload, dict) else {"input": payload}  #2360 (line in Coconut source)
        await self._validate_node_schemas(node, input_payload=payload, ctx=ctx)  #2361 (line in Coconut source)
        idempotency_key = self._idempotency_key(node, payload)  #2362 (line in Coconut source)
        if idempotency_key:  #2363 (line in Coconut source)
            if idempotency_key in ctx.state.idempotency_cache:  #2364 (line in Coconut source)
                return ctx.state.idempotency_cache[idempotency_key]  #2365 (line in Coconut source)

        injected = self._callable_injection_kwargs(fn, ctx)  #2367 (line in Coconut source)

        async def invoke() -> Any:  #2369 (line in Coconut source)
            if node.is_async:  #2370 (line in Coconut source)
                return await fn(runtime_payload, **injected)  #2371 (line in Coconut source)
            return await asyncio.to_thread(fn, runtime_payload, **injected)  #2372 (line in Coconut source)


        result = await self._call_with_retry(invoke, ctx, node=node, policy=node.execution_policy)  #2374 (line in Coconut source)
        await self._validate_node_schemas(node, output_payload=result, ctx=ctx)  #2380 (line in Coconut source)
        if idempotency_key:  #2381 (line in Coconut source)
            ctx.state.idempotency_cache[idempotency_key] = result  #2382 (line in Coconut source)
        return result  #2383 (line in Coconut source)


    async def _execute_transform(self, node: TransformNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> Any:  #2385 (line in Coconut source)
        fn = self._tool_fns.get(node.callable_ref)  #2391 (line in Coconut source)
        if fn is None:  #2392 (line in Coconut source)
            raise RuntimeError(("Transform callable not registered: {_coconut_format_0!r}. ".format(_coconut_format_0=(node.callable_ref)) + "Call executor.register_tool(ref, fn) before running."))  #2393 (line in Coconut source)

        if node.input_keys:  #2398 (line in Coconut source)
            input_data: dict[str, Any] = {key: ctx.outputs[key] if key in ctx.outputs else ctx.state.data[key] for key in node.input_keys if key in ctx.outputs or key in ctx.state.data}  #2399 (line in Coconut source)
        elif ctx.outputs:  #2404 (line in Coconut source)
            last = list(ctx.outputs.values())[-1]  #2405 (line in Coconut source)
            input_data = dict(last) if isinstance(last, dict) else {"input": last}  #2406 (line in Coconut source)
        else:  #2407 (line in Coconut source)
            input_data = dict(ctx.state.data)  #2408 (line in Coconut source)

        idempotency_key = self._idempotency_key(node, input_data)  #2410 (line in Coconut source)
        if idempotency_key and idempotency_key in ctx.state.idempotency_cache:  #2411 (line in Coconut source)
            return ctx.state.idempotency_cache[idempotency_key]  #2412 (line in Coconut source)

        t0 = time.monotonic()  #2414 (line in Coconut source)
        injected = self._callable_injection_kwargs(fn, ctx)  #2415 (line in Coconut source)

        async def invoke() -> Any:  #2417 (line in Coconut source)
            if node.is_async:  #2418 (line in Coconut source)
                return await fn(input_data, **injected)  #2419 (line in Coconut source)
            return await asyncio.to_thread(fn, input_data, **injected)  #2420 (line in Coconut source)


        result = await self._call_with_retry(invoke, ctx, node=node, policy=node.execution_policy)  #2422 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2423 (line in Coconut source)

        if node.output_key:  #2425 (line in Coconut source)
            ctx.state.data[node.output_key] = result  #2426 (line in Coconut source)

        self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name, "callable_ref": node.callable_ref, "output_summary": _summarise(result), "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #2428 (line in Coconut source)

        if idempotency_key:  #2443 (line in Coconut source)
            ctx.state.idempotency_cache[idempotency_key] = result  #2444 (line in Coconut source)
        return result  #2445 (line in Coconut source)


    async def _execute_reasoner(self, node: ReasonerNode, ctx: ExecutionContext, parent_event_id: str | None=None,) -> dict[str, Any]:  #2447 (line in Coconut source)
        """Run the symbolic Datalog reasoner over facts from state + the KG."""  #2453 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import Program  #2454 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import Rule  #2454 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import fact_to_dict  #2454 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import parse_program  #2454 (line in Coconut source)
        from yggdrasil_lm.symbolic.datalog import rule_from_obj  #2454 (line in Coconut source)

        rules: list[Rule] = list(parse_program(node.program)) if node.program else []  #2462 (line in Coconut source)
        for raw in node.rules:  #2463 (line in Coconut source)
            rules.extend(rule_from_obj(raw))  #2464 (line in Coconut source)
        program = Program(rules)  #2465 (line in Coconut source)

        facts = await self._gather_reasoner_facts(node, ctx)  #2467 (line in Coconut source)

        t0 = time.monotonic()  #2469 (line in Coconut source)

        @_coconut_tco  #2471 (line in Coconut source)
        def _solve() -> Any:  #2471 (line in Coconut source)
            return _coconut_tail_call(program.solve, facts, with_proof=node.with_proof)  #2472 (line in Coconut source)


        solution = await self._call_with_retry(lambda _=None: asyncio.to_thread(_solve), ctx, node=node, policy=node.execution_policy, parent_event_id=parent_event_id)  #2474 (line in Coconut source)
        duration_ms = int((time.monotonic() - t0) * 1000)  #2481 (line in Coconut source)

        emitted = solution.derived if node.emit_derived_only else solution.facts  #2483 (line in Coconut source)
        if node.query:  #2484 (line in Coconut source)
            wanted = set(node.query)  #2485 (line in Coconut source)
            emitted = {f for f in emitted if f[0] in wanted}  #2486 (line in Coconut source)

        if node.fail_on_empty and not emitted:  #2488 (line in Coconut source)
            raise RuntimeError(("ReasonerNode {_coconut_format_0!r} derived no facts ".format(_coconut_format_0=(node.name or node.node_id)) + "for query {_coconut_format_0}".format(_coconut_format_0=(node.query or '*'))))  #2489 (line in Coconut source)

        result: dict[str, Any] = {"facts": [fact_to_dict(f) for f in sorted(emitted, key=repr)], "fact_count": len(emitted), "input_count": len(facts), "predicates": sorted({f[0] for f in emitted})}  #2494 (line in Coconut source)
        if node.with_proof:  #2500 (line in Coconut source)
            result["proofs"] = [{"fact": fact_to_dict(f), "explanation": solution.explain(f)} for f in sorted(emitted, key=repr) if f in solution.justifications]  #2501 (line in Coconut source)

        if node.output_key:  #2507 (line in Coconut source)
            ctx.state.data[node.output_key] = result  #2508 (line in Coconut source)

        self._emit(ctx, "tool_result", node.node_id, node.name or "", payload={"tool_name": node.name or "reasoner", "node_type": str(node.node_type), "output_summary": _summarise(result), "fact_count": result["fact_count"], "input_count": result["input_count"], "predicates": result["predicates"], "success": True, "duration_ms": duration_ms}, parent_event_id=parent_event_id)  #2510 (line in Coconut source)
        return result  #2527 (line in Coconut source)


    async def _gather_reasoner_facts(self, node: ReasonerNode, ctx: ExecutionContext,) -> list[Any]:  #2529 (line in Coconut source)
        """Collect ground facts for a reasoner from state and the knowledge graph."""  #2534 (line in Coconut source)
        src = node.fact_source  #2535 (line in Coconut source)
        facts: list[Any] = []  #2536 (line in Coconut source)

        if src.state_keys:  #2538 (line in Coconut source)
            for key in src.state_keys:  #2539 (line in Coconut source)
                val = ctx.state.data.get(key)  #2540 (line in Coconut source)
                if isinstance(val, list):  #2541 (line in Coconut source)
                    facts.extend(val)  #2542 (line in Coconut source)
                elif val is not None:  #2543 (line in Coconut source)
                    facts.append(val)  #2544 (line in Coconut source)
        else:  #2545 (line in Coconut source)
            if ctx.outputs:  #2546 (line in Coconut source)
                last = list(ctx.outputs.values())[-1]  #2547 (line in Coconut source)
                if isinstance(last, list):  #2548 (line in Coconut source)
                    facts.extend(last)  #2549 (line in Coconut source)
                elif isinstance(last, dict) and isinstance(last.get("facts"), list):  #2550 (line in Coconut source)
                    facts.extend(last["facts"])  #2551 (line in Coconut source)
            if isinstance(ctx.state.data.get("facts"), list):  #2552 (line in Coconut source)
                facts.extend(ctx.state.data["facts"])  #2553 (line in Coconut source)

        if src.edge_types:  #2555 (line in Coconut source)
            name_cache: dict[str, str] = {}  #2556 (line in Coconut source)

            async def _label(node_id: str) -> str:  #2558 (line in Coconut source)
                if node_id in name_cache:  #2559 (line in Coconut source)
                    return name_cache[node_id]  #2560 (line in Coconut source)
                if not src.use_node_names:  #2561 (line in Coconut source)
                    name_cache[node_id] = node_id  #2562 (line in Coconut source)
                    return node_id  #2563 (line in Coconut source)
                n = await self.store.get_node(node_id)  #2564 (line in Coconut source)
                label = (n.name if n and n.name else node_id)  #2565 (line in Coconut source)
                name_cache[node_id] = label  #2566 (line in Coconut source)
                return label  #2567 (line in Coconut source)


            for etype in src.edge_types:  #2569 (line in Coconut source)
                try:  #2570 (line in Coconut source)
                    edge_type = EdgeType(etype)  #2571 (line in Coconut source)
                except ValueError:  #2572 (line in Coconut source)
                    edge_type = None  #2573 (line in Coconut source)
                edges = await self.store.list_edges(edge_type=edge_type) if edge_type else []  #2574 (line in Coconut source)
                if edge_type is None:  #2575 (line in Coconut source)
                    edges = [e for e in await self.store.list_edges() if str(e.edge_type) == etype]  #2576 (line in Coconut source)
                pred = etype.lower()  #2577 (line in Coconut source)
                for e in edges:  #2578 (line in Coconut source)
                    facts.append((pred, await _label(e.src_id), await _label(e.dst_id)))  #2579 (line in Coconut source)

        if src.include_node_facts:  #2581 (line in Coconut source)
            for n in await self.store.list_nodes():  #2582 (line in Coconut source)
                label = n.name if (src.use_node_names and n.name) else n.node_id  #2583 (line in Coconut source)
                facts.append((str(n.node_type), label))  #2584 (line in Coconut source)

        return facts  #2586 (line in Coconut source)


    async def _chat_once(self, node: AgentNode, system: str, messages: list[dict[str, Any]], tool_defs: list[dict[str, Any]],) -> Any:  #2588 (line in Coconut source)
        return await self._backend.chat(model=node.model, system=system, messages=messages, tools=tool_defs)  #2595 (line in Coconut source)


    async def _call_with_retry(self, fn: Callable[[], Any], ctx: ExecutionContext, *, node: AnyNode, policy: ExecutionPolicy, parent_event_id: str | None=None,) -> Any:  #2602 (line in Coconut source)
        attempts = max(1, policy.retry_policy.max_attempts)  #2611 (line in Coconut source)
        delay = max(0.0, policy.retry_policy.backoff_seconds)  #2612 (line in Coconut source)
        last_exc: Exception | None = None  #2613 (line in Coconut source)
        for attempt in range(1, attempts + 1):  #2614 (line in Coconut source)
            try:  #2615 (line in Coconut source)
                if policy.timeout_seconds:  #2616 (line in Coconut source)
                    return await asyncio.wait_for(fn(), timeout=policy.timeout_seconds)  #2617 (line in Coconut source)
                return await fn()  #2618 (line in Coconut source)
            except Exception as exc:  #2619 (line in Coconut source)
                last_exc = exc  #2620 (line in Coconut source)
                if attempt >= attempts:  #2621 (line in Coconut source)
                    break  #2622 (line in Coconut source)
                self._emit(ctx, "retry", node.node_id, node.name or "", payload={"attempt": attempt, "max_attempts": attempts, "error": str(exc)}, parent_event_id=parent_event_id)  #2623 (line in Coconut source)
                if delay > 0:  #2631 (line in Coconut source)
                    await asyncio.sleep(delay)  #2632 (line in Coconut source)
                    delay *= max(policy.retry_policy.backoff_multiplier, 1.0)  #2633 (line in Coconut source)
        assert last_exc is not None  #2634 (line in Coconut source)
        raise last_exc  #2635 (line in Coconut source)


    @_coconut_tco  #2637 (line in Coconut source)
    def _idempotency_key(self, node: ToolNode, payload: Any) -> str:  #2637 (line in Coconut source)
        template = node.execution_policy.idempotency_key  #2638 (line in Coconut source)
        if template == "":  #2639 (line in Coconut source)
            return ""  #2640 (line in Coconut source)
        if template == "auto":  #2641 (line in Coconut source)
            return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(json.dumps(payload, sort_keys=True, default=str)))  #2642 (line in Coconut source)
        if isinstance(payload, dict) and template in payload:  #2643 (line in Coconut source)
            return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(payload[template]))  #2644 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0}:{_coconut_format_1}".format, _coconut_format_0=(node.node_id), _coconut_format_1=(template))  #2645 (line in Coconut source)

# ------------------------------------------------------------------
# Output materialisation
# ------------------------------------------------------------------


    async def _materialise_output(self, source_node: AnyNode, output: Any, ctx: ExecutionContext,) -> ContextNode:  #2651 (line in Coconut source)
        """Write execution output back into the graph as a ContextNode."""  #2657 (line in Coconut source)
        from yggdrasil_lm.core.nodes import ContextNode  #2658 (line in Coconut source)
        from yggdrasil_lm.core.edges import Edge  #2659 (line in Coconut source)

        content = output if isinstance(output, str) else str(output)  #2661 (line in Coconut source)
        ctx_node = ContextNode(name="Output of {_coconut_format_0}".format(_coconut_format_0=(source_node.name)), description="Auto-materialised output from {_coconut_format_0} node".format(_coconut_format_0=(source_node.node_type)), content=content, source="node:{_coconut_format_0}".format(_coconut_format_0=(source_node.node_id)), group_id=ctx.session_id, attributes={"origin": "runtime", "session_id": ctx.session_id, "source_node_id": source_node.node_id})  #2662 (line in Coconut source)
        await self.store.upsert_node(ctx_node)  #2674 (line in Coconut source)
        await self.store.upsert_edge(Edge.produces(src_id=source_node.node_id, dst_id=ctx_node.node_id))  #2675 (line in Coconut source)
        ctx.outputs[ctx_node.node_id] = content  #2678 (line in Coconut source)
        return ctx_node  #2679 (line in Coconut source)

# ------------------------------------------------------------------
# Routing
# ------------------------------------------------------------------


    async def _route(self, node: AgentNode, result: dict[str, Any], ctx: ExecutionContext, parent_event_id: str | None=None,) -> str | None:  #2685 (line in Coconut source)
        if node.decision_table is not None:  #2692 (line in Coconut source)
            decision = self._evaluate_decision_table(node.decision_table, state=ctx.state, result=result)  #2693 (line in Coconut source)
            if decision is not None:  #2694 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": decision.name or "decision_table", "next_node_id": None if decision.target_node_id == "__END__" else decision.target_node_id, "confidence": 1.0, "mode": "decision_table"}, parent_event_id=parent_event_id)  #2695 (line in Coconut source)
                return decision.target_node_id  #2708 (line in Coconut source)
            if node.decision_table.strict:  #2709 (line in Coconut source)
                target = node.decision_table.default_target_id  #2710 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": node.decision_table.default_intent, "next_node_id": None if target == "__END__" else target, "confidence": 1.0, "mode": "decision_table"}, parent_event_id=parent_event_id)  #2711 (line in Coconut source)
                return target  #2724 (line in Coconut source)
        for rule in sorted(node.route_rules, key=lambda r: r.priority, reverse=True):  #2725 (line in Coconut source)
            if self._evaluate_route_rule(rule, result=result, state=ctx.state):  #2726 (line in Coconut source)
                if rule.pause_on_match:  #2727 (line in Coconut source)
                    await self._pause_execution(ctx, node, reason=rule.name or "route_rule_pause", waiting_for=node.wait_for_input, metadata={"rule": rule.name, "target": rule.target_node_id})  #2728 (line in Coconut source)
                self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": rule.name or "route_rule", "next_node_id": None if rule.target_node_id == "__END__" else rule.target_node_id, "confidence": 1.0, "mode": "deterministic"}, parent_event_id=parent_event_id)  #2735 (line in Coconut source)
                return rule.target_node_id  #2748 (line in Coconut source)
        intent = result.get("intent", "default")  #2749 (line in Coconut source)
        next_id = node.routing_table.get(intent) or node.routing_table.get("default", "__END__")  #2750 (line in Coconut source)

        self._emit(ctx, "routing", node.node_id, node.name or "", payload={"intent": intent, "next_node_id": next_id if next_id != "__END__" else None, "confidence": None, "mode": "llm"}, parent_event_id=parent_event_id)  #2752 (line in Coconut source)

        return next_id  #2761 (line in Coconut source)


    async def _infer_intent(self, text: str, node: AgentNode) -> str:  #2763 (line in Coconut source)
        """Classify routing intent from agent output text."""  #2764 (line in Coconut source)
        if not node.routing_table:  #2765 (line in Coconut source)
            return "default"  #2766 (line in Coconut source)
        intents = [intent for intent in node.routing_table if intent != "default"]  #2767 (line in Coconut source)
        if not intents:  #2768 (line in Coconut source)
            return "default"  #2769 (line in Coconut source)

        keyword_intent = self._infer_intent_keywords(text, node)  #2771 (line in Coconut source)
        if keyword_intent != "default":  #2772 (line in Coconut source)
            return keyword_intent  #2773 (line in Coconut source)

        if self._backend is None:  #2775 (line in Coconut source)
            return "default"  #2776 (line in Coconut source)

        prompt = _INTENT_TEMPLATE.format(intents="\n".join(("- {_coconut_format_0}".format(_coconut_format_0=(intent)) for intent in intents)), text=text[:2000])  #2778 (line in Coconut source)
        try:  #2782 (line in Coconut source)
            response = await self._backend.chat(model=self._router_model, system=_ROUTER_SYSTEM, messages=[{"role": "user", "content": prompt},], tools=[])  #2783 (line in Coconut source)
            data = json.loads(response.text.strip())  #2789 (line in Coconut source)
            return str(data.get("intent", "default"))  #2790 (line in Coconut source)
        except Exception:  #2791 (line in Coconut source)
            return "default"  #2792 (line in Coconut source)


    def _infer_intent_keywords(self, text: str, node: AgentNode) -> str:  #2794 (line in Coconut source)
        """Keyword-based intent fallback (no LLM call)."""  #2795 (line in Coconut source)
        text_lower = text.lower()  #2796 (line in Coconut source)
        for intent in node.routing_table:  #2797 (line in Coconut source)
            if intent != "default" and intent.lower() in text_lower:  #2798 (line in Coconut source)
                return intent  #2799 (line in Coconut source)
        return "default"  #2800 (line in Coconut source)

# ------------------------------------------------------------------
# White-box routing: plan + execute (two-phase dispatch)
# ------------------------------------------------------------------


    async def route(self, query: str, candidates: list[AgentNode] | None=None,) -> RoutingDecision:  #2806 (line in Coconut source)
        """LLM-based router: pick the best AgentNode for *query*."""  #2811 (line in Coconut source)
        if candidates is None:  #2812 (line in Coconut source)
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)  #2813 (line in Coconut source)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]  #2814 (line in Coconut source)

        if not candidates:  #2816 (line in Coconut source)
            raise ValueError("No valid AgentNode candidates found in the store.")  #2817 (line in Coconut source)

        if len(candidates) == 1:  #2819 (line in Coconut source)
            return RoutingDecision(candidates[0].node_id, "Only one agent available.", 1.0)  #2820 (line in Coconut source)

        agent_list = "\n".join(("- {_coconut_format_0}: {_coconut_format_1}".format(_coconut_format_0=(n.node_id), _coconut_format_1=(n.description)) for n in candidates))  #2822 (line in Coconut source)
        prompt = _ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)  #2823 (line in Coconut source)

        try:  #2825 (line in Coconut source)
            response = await self._backend.chat(model=self._router_model, system=_ROUTER_SYSTEM, messages=[{"role": "user", "content": prompt},], tools=[])  #2826 (line in Coconut source)
            data = json.loads(response.text.strip())  #2832 (line in Coconut source)
            return RoutingDecision(str(data["agent"]), str(data.get("reason", "")), float(data.get("confidence", 0.5)))  #2833 (line in Coconut source)
        except Exception:  #2838 (line in Coconut source)
            return RoutingDecision(candidates[0].node_id, "Fallback: router response could not be parsed.", 0.5)  #2839 (line in Coconut source)


    async def plan(self, query: str) -> RoutingDecision:  #2845 (line in Coconut source)
        """Deprecated alias for route()."""  #2846 (line in Coconut source)
        import warnings  #2847 (line in Coconut source)
        warnings.warn('GraphExecutor.plan() is deprecated and will be removed in a future release. Use GraphExecutor.route() instead.', DeprecationWarning, stacklevel=2)  #2848 (line in Coconut source)
        return await self.route(query)  #2854 (line in Coconut source)


    async def execute(self, agent_id: str, query: QueryContent, routing: RoutingDecision | None=None,) -> AgentResult:  #2856 (line in Coconut source)
        """Phase 2 of two-phase dispatch: run *agent_id* and return a structured envelope."""  #2862 (line in Coconut source)
        node = await self.store.get_node(agent_id)  #2863 (line in Coconut source)
        if node is None or not isinstance(node, AgentNode):  #2864 (line in Coconut source)
            raise ValueError("Agent node not found or not an AgentNode: {_coconut_format_0!r}".format(_coconut_format_0=(agent_id)))  #2865 (line in Coconut source)

        composed = await self.composer.compose(node, query=_query_text(query))  #2867 (line in Coconut source)
        context_names = [c.name for c in composed.context if c.name]  #2868 (line in Coconut source)

        ctx = ExecutionContext(query=query)  #2870 (line in Coconut source)
        raw = await self._execute_agent(node, ctx)  #2871 (line in Coconut source)
        text = raw.get("text", "") if isinstance(raw, dict) else str(raw)  #2872 (line in Coconut source)

        decision = routing or RoutingDecision(agent_id, "Direct execution (no routing phase).", 1.0)  #2874 (line in Coconut source)

        return AgentResult(routed_to=agent_id, reason=decision.reason, confidence=decision.confidence, context_injected=context_names, result=text, low_confidence_warning=decision.low_confidence_warning)  #2876 (line in Coconut source)


# ---------------------------------------------------------------------------
# print_trace() — render a session trace as a human-readable execution tree
# ---------------------------------------------------------------------------


def print_trace(ctx: ExecutionContext | list[TraceEvent], *, width: int=72) -> None:  #2890 (line in Coconut source)
    """Print the execution trace as a human-readable tree."""  #2891 (line in Coconut source)
    _coconut_case_match_to_10 = ctx  #2892 (line in Coconut source)
    _coconut_case_match_check_10 = False  #2892 (line in Coconut source)
    _coconut_match_temp_41 = _coconut.getattr(ExecutionContext, "_coconut_is_data", False) or _coconut.isinstance(ExecutionContext, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ExecutionContext)  # type: ignore  #2892 (line in Coconut source)
    _coconut_case_match_check_10 = True  #2892 (line in Coconut source)
    if _coconut_case_match_check_10:  #2892 (line in Coconut source)
        _coconut_case_match_check_10 = False  #2892 (line in Coconut source)
        if not _coconut_case_match_check_10:  #2892 (line in Coconut source)
            if (_coconut_match_temp_41) and (_coconut.isinstance(_coconut_case_match_to_10, ExecutionContext)):  #2892 (line in Coconut source)
                _coconut_match_temp_42 = _coconut.len(_coconut_case_match_to_10) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_10.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_10, "_coconut_data_defaults", {}) and _coconut_case_match_to_10[i] == _coconut.getattr(_coconut_case_match_to_10, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_10.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_10, "__match_args__") else _coconut.len(_coconut_case_match_to_10) == 0  # type: ignore  #2892 (line in Coconut source)
                if _coconut_match_temp_42:  #2892 (line in Coconut source)
                    _coconut_case_match_check_10 = True  #2892 (line in Coconut source)

        if not _coconut_case_match_check_10:  #2892 (line in Coconut source)
            if (not _coconut_match_temp_41) and (_coconut.isinstance(_coconut_case_match_to_10, ExecutionContext)):  #2892 (line in Coconut source)
                _coconut_case_match_check_10 = True  #2892 (line in Coconut source)
            if _coconut_case_match_check_10:  #2892 (line in Coconut source)
                _coconut_case_match_check_10 = False  #2892 (line in Coconut source)
                if not _coconut_case_match_check_10:  #2892 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_10) in _coconut_self_match_types:  #2892 (line in Coconut source)
                        _coconut_case_match_check_10 = True  #2892 (line in Coconut source)

                if not _coconut_case_match_check_10:  #2892 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_10) in _coconut_self_match_types:  #2892 (line in Coconut source)
                        _coconut_match_temp_43 = _coconut.getattr(ExecutionContext, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #2892 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_43, _coconut.tuple):  #2892 (line in Coconut source)
                            raise _coconut.TypeError("ExecutionContext.__match_args__ must be a tuple")  #2892 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_43) < 0:  #2892 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ExecutionContext' only supports %s)" % (_coconut.len(_coconut_match_temp_43),))  #2892 (line in Coconut source)
                        _coconut_case_match_check_10 = True  #2892 (line in Coconut source)




    if _coconut_case_match_check_10:  #2892 (line in Coconut source)
        events = ctx.trace  #2894 (line in Coconut source)
        session_id = ctx.session_id[:8]  #2895 (line in Coconut source)
        query = _query_text(ctx.query)  #2896 (line in Coconut source)
    if not _coconut_case_match_check_10:  #2897 (line in Coconut source)
        _coconut_case_match_check_10 = True  #2897 (line in Coconut source)
        if _coconut_case_match_check_10:  #2897 (line in Coconut source)
            events = ctx  #2898 (line in Coconut source)
            session_id = events[0].session_id[:8] if events else "?"  #2899 (line in Coconut source)
            query = ""  #2900 (line in Coconut source)

    sep = "═" * width  #2902 (line in Coconut source)
    print("\nSession {_coconut_format_0}  {_coconut_format_1!r}".format(_coconut_format_0=(session_id), _coconut_format_1=(query)))  #2903 (line in Coconut source)
    print(sep)  #2904 (line in Coconut source)

    by_id: dict[str, TraceEvent] = {e.event_id: e for e in events}  #2906 (line in Coconut source)
    children: dict[str | None, list[TraceEvent]] = {}  #2907 (line in Coconut source)
    for e in events:  #2908 (line in Coconut source)
        children.setdefault(e.parent_event_id, []).append(e)  #2909 (line in Coconut source)

    def _fmt_ms(ms: int | None) -> str:  #2911 (line in Coconut source)
        return "[{_coconut_format_0}ms]".format(_coconut_format_0=(ms)) if ms is not None else ""  #2912 (line in Coconut source)


    def _render(event: TraceEvent, indent: int) -> None:  #2914 (line in Coconut source)
        pad = "  " * indent  #2915 (line in Coconut source)
        t = event.event_type  #2916 (line in Coconut source)
        p = event.payload  #2917 (line in Coconut source)
        ms = _fmt_ms(event.duration_ms)  #2918 (line in Coconut source)

        _coconut_case_match_to_11 = t  #2920 (line in Coconut source)
        _coconut_case_match_check_11 = False  #2920 (line in Coconut source)
        if _coconut_case_match_to_11 == "hop":  #2920 (line in Coconut source)
            _coconut_case_match_check_11 = True  #2920 (line in Coconut source)
        if _coconut_case_match_check_11:  #2920 (line in Coconut source)
            node_type = p.get("node_type", "").split(".")[-1].upper()  #2922 (line in Coconut source)
            hop_num = p.get("hop", "")  #2923 (line in Coconut source)
            hop_label = "hop {_coconut_format_0}  ".format(_coconut_format_0=(hop_num)) if hop_num else ""  #2924 (line in Coconut source)
            print("{_coconut_format_0}{_coconut_format_1}{_coconut_format_2}  {_coconut_format_3}".format(_coconut_format_0=(pad), _coconut_format_1=(hop_label), _coconut_format_2=(node_type), _coconut_format_3=(event.node_name)))  #2925 (line in Coconut source)
            for child in children.get(event.event_id, []):  #2926 (line in Coconut source)
                _render(child, indent + 1)  #2927 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2929 (line in Coconut source)
            if _coconut_case_match_to_11 == "agent_start":  #2929 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2929 (line in Coconut source)
            if _coconut_case_match_check_11:  #2929 (line in Coconut source)
                tools = ", ".join(p.get("tools", [])) or "none"  #2930 (line in Coconut source)
                ctx_l = p.get("context", [])  #2931 (line in Coconut source)
                ctx_s = "  context: {_coconut_format_0}".format(_coconut_format_0=(', '.join(ctx_l))) if ctx_l else ""  #2932 (line in Coconut source)
                print("{_coconut_format_0}tools: {_coconut_format_1}{_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(tools), _coconut_format_2=(ctx_s)))  #2933 (line in Coconut source)
                if p.get("context_scores"):  #2934 (line in Coconut source)
                    ranked = ["{_coconut_format_0}[{_coconut_format_1}, {_coconut_format_2}, hops={_coconut_format_3}]".format(_coconut_format_0=(item.get('name')), _coconut_format_1=(item.get('score')), _coconut_format_2=(item.get('source')), _coconut_format_3=(item.get('hops'))) for item in p["context_scores"]]  #2935 (line in Coconut source)
                    print("{_coconut_format_0}ranked_context: {_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(' | '.join(ranked))))  #2939 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2940 (line in Coconut source)
                    _render(child, indent)  #2941 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2943 (line in Coconut source)
            if _coconut_case_match_to_11 == "context_inject":  #2943 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2943 (line in Coconut source)
            if _coconut_case_match_check_11:  #2943 (line in Coconut source)
                names = ", ".join(p.get("context_names", [])) or "—"  #2944 (line in Coconut source)
                count = p.get("count", 0)  #2945 (line in Coconut source)
                print("{_coconut_format_0}context_inject  {_coconut_format_1}  ({_coconut_format_2} nodes)".format(_coconut_format_0=(pad), _coconut_format_1=(names), _coconut_format_2=(count)))  #2946 (line in Coconut source)
                for item in p.get("selected_contexts", []):  #2947 (line in Coconut source)
                    reasons = ", ".join(item.get("reasons", []))  #2948 (line in Coconut source)
                    print(("{_coconut_format_0}  selected  {_coconut_format_1}  score={_coconut_format_2}  ".format(_coconut_format_0=(pad), _coconut_format_1=(item.get('name')), _coconut_format_2=(item.get('score'))) + "source={_coconut_format_0}  hops={_coconut_format_1}  ".format(_coconut_format_0=(item.get('source')), _coconut_format_1=(item.get('hops'))) + "tokens={_coconut_format_0}".format(_coconut_format_0=(item.get('token_count')))))  #2949 (line in Coconut source)
                    if reasons:  #2954 (line in Coconut source)
                        print("{_coconut_format_0}    reasons  {_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(reasons)))  #2955 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2957 (line in Coconut source)
            if _coconut_case_match_to_11 == "agent_end":  #2957 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2957 (line in Coconut source)
            if _coconut_case_match_check_11:  #2957 (line in Coconut source)
                summary = p.get("text_summary", "")  #2958 (line in Coconut source)
                intent = p.get("intent", "default")  #2959 (line in Coconut source)
                iters = p.get("iterations", 1)  #2960 (line in Coconut source)
                iter_s = "  iters={_coconut_format_0}".format(_coconut_format_0=(iters)) if iters > 1 else ""  #2961 (line in Coconut source)
                print("{_coconut_format_0}agent_end  {_coconut_format_1!r}  intent={_coconut_format_2}{_coconut_format_3}  {_coconut_format_4}".format(_coconut_format_0=(pad), _coconut_format_1=(summary), _coconut_format_2=(intent), _coconut_format_3=(iter_s), _coconut_format_4=(ms)))  #2962 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2964 (line in Coconut source)
            if _coconut_case_match_to_11 == "tool_call":  #2964 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2964 (line in Coconut source)
            if _coconut_case_match_check_11:  #2964 (line in Coconut source)
                inp = json.dumps(p.get("input", {}), ensure_ascii=False)  #2965 (line in Coconut source)
                inp = inp[:60] + "…" if len(inp) > 60 else inp  #2966 (line in Coconut source)
                print("{_coconut_format_0}tool_call  {_coconut_format_1}  {_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(inp)))  #2967 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2968 (line in Coconut source)
                    _render(child, indent + 1)  #2969 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2971 (line in Coconut source)
            if _coconut_case_match_to_11 == "tool_result":  #2971 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2971 (line in Coconut source)
            if _coconut_case_match_check_11:  #2971 (line in Coconut source)
                status = "ok" if p.get("success") else "err"  #2972 (line in Coconut source)
                summary = p.get("output_summary", "")  #2973 (line in Coconut source)
                print("{_coconut_format_0}tool_result  {_coconut_format_1}  {_coconut_format_2}  {_coconut_format_3!r}  {_coconut_format_4}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(status), _coconut_format_3=(summary), _coconut_format_4=(ms)))  #2974 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2976 (line in Coconut source)
            if _coconut_case_match_to_11 == "routing":  #2976 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2976 (line in Coconut source)
            if _coconut_case_match_check_11:  #2976 (line in Coconut source)
                intent = p.get("intent", "default")  #2977 (line in Coconut source)
                next_id = p.get("next_node_id") or "__END__"  #2978 (line in Coconut source)
                conf = p.get("confidence")  #2979 (line in Coconut source)
                conf_s = "  conf={_coconut_format_0:.0%}".format(_coconut_format_0=(conf)) if conf is not None else ""  #2980 (line in Coconut source)
                print("{_coconut_format_0}routing  {_coconut_format_1} → {_coconut_format_2}{_coconut_format_3}".format(_coconut_format_0=(pad), _coconut_format_1=(intent), _coconut_format_2=(next_id), _coconut_format_3=(conf_s)))  #2981 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2983 (line in Coconut source)
            if _coconut_case_match_to_11 == "subgraph_enter":  #2983 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2983 (line in Coconut source)
            if _coconut_case_match_check_11:  #2983 (line in Coconut source)
                print("{_coconut_format_0}subgraph_enter  {_coconut_format_1}  entry={_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(p.get('entry_node_id', ''))))  #2984 (line in Coconut source)
                for child in children.get(event.event_id, []):  #2985 (line in Coconut source)
                    _render(child, indent + 1)  #2986 (line in Coconut source)

        if not _coconut_case_match_check_11:  #2988 (line in Coconut source)
            if _coconut_case_match_to_11 == "subgraph_exit":  #2988 (line in Coconut source)
                _coconut_case_match_check_11 = True  #2988 (line in Coconut source)
            if _coconut_case_match_check_11:  #2988 (line in Coconut source)
                print("{_coconut_format_0}subgraph_exit   {_coconut_format_1}  {_coconut_format_2}".format(_coconut_format_0=(pad), _coconut_format_1=(event.node_name), _coconut_format_2=(ms)))  #2989 (line in Coconut source)


    total_ms = 0  #2991 (line in Coconut source)
    hops = 0  #2992 (line in Coconut source)
    ends = 0  #2993 (line in Coconut source)
    for event in children.get(None, []):  #2994 (line in Coconut source)
        _render(event, indent=0)  #2995 (line in Coconut source)
        if event.event_type == "hop":  #2996 (line in Coconut source)
            hops += 1  #2997 (line in Coconut source)

    for event in events:  #2999 (line in Coconut source)
        if event.event_type == "agent_end":  #3000 (line in Coconut source)
            ends += 1  #3001 (line in Coconut source)
            if event.duration_ms:  #3002 (line in Coconut source)
                total_ms += event.duration_ms  #3003 (line in Coconut source)

    print(sep)  #3005 (line in Coconut source)
    ms_s = " · {_coconut_format_0}ms".format(_coconut_format_0=(total_ms)) if total_ms else ""  #3006 (line in Coconut source)
    print("Total: {_coconut_format_0} hops · {_coconut_format_1} agent_end events{_coconut_format_2}\n".format(_coconut_format_0=(hops), _coconut_format_1=(ends), _coconut_format_2=(ms_s)))  #3007 (line in Coconut source)


# ---------------------------------------------------------------------------
# Runtime node utilities
# ---------------------------------------------------------------------------


async def get_runtime_nodes(store: GraphStore, session_id: str | None=None, only_valid: bool=True,) -> list[ContextNode]:  #3014 (line in Coconut source)
    """Return runtime-materialised ContextNodes without graph traversal."""  #3019 (line in Coconut source)
    candidates = await store.list_nodes(node_type=NodeType.CONTEXT, group_id=session_id, only_valid=only_valid)  #3020 (line in Coconut source)
    return [n for n in candidates if isinstance(n, ContextNode) and n.attributes.get("origin") == "runtime"]  #3025 (line in Coconut source)



async def cleanup_session(store: GraphStore, session_id: str, hard: bool=False,) -> int:  #3031 (line in Coconut source)
    """Expire (or hard-delete) all runtime nodes from *session_id*."""  #3036 (line in Coconut source)
    nodes = await store.list_nodes(group_id=session_id, only_valid=False)  #3037 (line in Coconut source)
    count = 0  #3038 (line in Coconut source)
    for node in nodes:  #3039 (line in Coconut source)
        in_edges = await store.get_edges(node.node_id, edge_type=EdgeType.PRODUCES, direction="in", only_valid=False)  #3040 (line in Coconut source)
        for edge in in_edges:  #3043 (line in Coconut source)
            if hard:  #3044 (line in Coconut source)
                await store.delete_edge(edge.edge_id)  #3045 (line in Coconut source)
            else:  #3046 (line in Coconut source)
                await store.expire_edge(edge.edge_id)  #3047 (line in Coconut source)

        if hard:  #3049 (line in Coconut source)
            await store.delete_node(node.node_id)  #3050 (line in Coconut source)
        else:  #3051 (line in Coconut source)
            await store.expire_node(node.node_id)  #3052 (line in Coconut source)
        count += 1  #3053 (line in Coconut source)

    return count  #3055 (line in Coconut source)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _summarise(value: Any, max_len: int=200) -> str:  #3062 (line in Coconut source)
    s = value if isinstance(value, str) else str(value)  #3063 (line in Coconut source)
    return s[:max_len] + "…" if len(s) > max_len else s  #3064 (line in Coconut source)



@_coconut_tco  #3067 (line in Coconut source)
def _text_of(value: Any) -> str:  #3067 (line in Coconut source)
    """Best-effort extraction of a string payload from a node output."""  #3068 (line in Coconut source)
    _coconut_case_match_to_12 = value  #3069 (line in Coconut source)
    _coconut_case_match_check_12 = False  #3069 (line in Coconut source)
    if _coconut_case_match_to_12 is None:  #3069 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3069 (line in Coconut source)
    if _coconut_case_match_check_12:  #3069 (line in Coconut source)
        return ""  #3071 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3072 (line in Coconut source)
        _coconut_match_temp_44 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #3072 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3072 (line in Coconut source)
        if _coconut_case_match_check_12:  #3072 (line in Coconut source)
            _coconut_case_match_check_12 = False  #3072 (line in Coconut source)
            if not _coconut_case_match_check_12:  #3072 (line in Coconut source)
                if (_coconut_match_temp_44) and (_coconut.isinstance(_coconut_case_match_to_12, str)):  #3072 (line in Coconut source)
                    _coconut_match_temp_45 = _coconut.len(_coconut_case_match_to_12) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_12.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_12, "_coconut_data_defaults", {}) and _coconut_case_match_to_12[i] == _coconut.getattr(_coconut_case_match_to_12, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_12.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_12, "__match_args__") else _coconut.len(_coconut_case_match_to_12) == 0  # type: ignore  #3072 (line in Coconut source)
                    if _coconut_match_temp_45:  #3072 (line in Coconut source)
                        _coconut_case_match_check_12 = True  #3072 (line in Coconut source)

            if not _coconut_case_match_check_12:  #3072 (line in Coconut source)
                if (not _coconut_match_temp_44) and (_coconut.isinstance(_coconut_case_match_to_12, str)):  #3072 (line in Coconut source)
                    _coconut_case_match_check_12 = True  #3072 (line in Coconut source)
                if _coconut_case_match_check_12:  #3072 (line in Coconut source)
                    _coconut_case_match_check_12 = False  #3072 (line in Coconut source)
                    if not _coconut_case_match_check_12:  #3072 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_12) in _coconut_self_match_types:  #3072 (line in Coconut source)
                            _coconut_case_match_check_12 = True  #3072 (line in Coconut source)

                    if not _coconut_case_match_check_12:  #3072 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_12) in _coconut_self_match_types:  #3072 (line in Coconut source)
                            _coconut_match_temp_46 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #3072 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_46, _coconut.tuple):  #3072 (line in Coconut source)
                                raise _coconut.TypeError("str.__match_args__ must be a tuple")  #3072 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_46) < 0:  #3072 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_46),))  #3072 (line in Coconut source)
                            _coconut_case_match_check_12 = True  #3072 (line in Coconut source)




        if _coconut_case_match_check_12:  #3072 (line in Coconut source)
            return value  #3073 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3074 (line in Coconut source)
        if _coconut.isinstance(_coconut_case_match_to_12, _coconut.abc.Mapping):  #3074 (line in Coconut source)
            _coconut_case_match_check_12 = True  #3074 (line in Coconut source)
        if _coconut_case_match_check_12:  #3074 (line in Coconut source)
            for key in ("text", "output", "result", "content"):  #3075 (line in Coconut source)
                v = value.get(key)  #3076 (line in Coconut source)
                if isinstance(v, str):  #3077 (line in Coconut source)
                    return v  #3078 (line in Coconut source)
            return _coconut_tail_call(str, value)  #3079 (line in Coconut source)
    if not _coconut_case_match_check_12:  #3080 (line in Coconut source)
        _coconut_case_match_check_12 = True  #3080 (line in Coconut source)
        if _coconut_case_match_check_12:  #3080 (line in Coconut source)
            return _coconut_tail_call(str, value)  #3081 (line in Coconut source)
