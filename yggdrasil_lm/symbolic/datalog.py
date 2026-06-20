#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x97ea53cc

# Compiled with Coconut version 3.2.0

"""A small, dependency-free Datalog engine with stratified negation.

This is the symbolic reasoner that powers neurosymbolic pipelines in yggdrasil.
It is deliberately self-contained (pure standard library) so it adds no install
weight and can run inside a :class:`ReasonerNode` with no external solver.

What it supports
----------------
* Positive Datalog with **semi-naive forward chaining to a fixpoint**.
* **Negation as failure** with automatic **stratification** (a rule program that
  cannot be stratified — i.e. recursion through negation — is rejected with a
  clear :class:`StratificationError`).
* **Comparison built-ins** in rule bodies: ``=`` ``==`` ``!=`` ``<`` ``<=``
  ``>`` ``>=`` (e.g. ``adult(?p) :- person(?p, ?age), ?age >= 18``).
* **Safety checking**: every variable in a rule head, in a negated literal and
  in a comparison must be bound by a positive body literal. Unsafe rules are
  rejected at compile time (:class:`UnsafeRuleError`).
* Optional **proof trace** (``solve(..., with_proof=True)``) recording, for each
  derived fact, the rule and the ground body literals that justified it — the
  explainability hook a neural agent can verbalise.

Term & syntax conventions
--------------------------
* A **variable** is written ``?name`` (always prefixed with ``?``).
* A **constant** is a quoted string (``"alice"`` / ``'alice'``), a number
  (``42``, ``3.14``), the literals ``true`` / ``false``, or a bare word
  (``alice``) which is treated as a string constant.
* An **atom** is ``predicate(term, term, ...)``; a 0-arity atom is ``flag()``.
* A **rule** is ``head :- body1, body2, ... .`` (trailing ``.`` optional).
* A **fact** is a rule with an empty (ground) body: ``parent("alice","bob").``
* Comments start with ``#`` or ``%`` and run to end of line.

Facts handed to :meth:`Program.solve` may be given as native tuples
``("parent", "alice", "bob")``, as :func:`fact` results, as ``["parent", ...]``
lists, or as dicts ``{"predicate": "parent", "args": [...]}`` — see
:func:`normalise_fact`.
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



import re  #39 (line in Coconut source)
from dataclasses import dataclass  #40 (line in Coconut source)
from dataclasses import field  #40 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #41 (line in Coconut source)
    from typing import Any  #41 (line in Coconut source)
else:  #41 (line in Coconut source)
    try:  #41 (line in Coconut source)
        Any = _coconut.typing.Any  #41 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #41 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #41 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #41 (line in Coconut source)
    from typing import Iterable  #41 (line in Coconut source)
else:  #41 (line in Coconut source)
    try:  #41 (line in Coconut source)
        Iterable = _coconut.typing.Iterable  #41 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #41 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #41 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #41 (line in Coconut source)
    from typing import Iterator  #41 (line in Coconut source)
else:  #41 (line in Coconut source)
    try:  #41 (line in Coconut source)
        Iterator = _coconut.typing.Iterator  #41 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #41 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #41 (line in Coconut source)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class DatalogError(Exception):  #48 (line in Coconut source)
    """Base class for all errors raised by the Datalog engine."""  #49 (line in Coconut source)


class ParseError(DatalogError):  #52 (line in Coconut source)
    """Raised when a rule program cannot be parsed."""  #53 (line in Coconut source)


class UnsafeRuleError(DatalogError):  #56 (line in Coconut source)
    """Raised when a rule has variables that are not range-restricted."""  #57 (line in Coconut source)


class StratificationError(DatalogError):  #60 (line in Coconut source)
    """Raised when a program recurses through negation (cannot be stratified)."""  #61 (line in Coconut source)


# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

# A ground fact is represented internally as a tuple: (predicate, arg1, arg2, ...)
# where each arg is a plain Python scalar (str | int | float | bool).
GroundFact = tuple[Any, ...]  #70 (line in Coconut source)


@dataclass(frozen=True)  #73 (line in Coconut source)
class Var():  #74 (line in Coconut source)
    """A logic variable, e.g. ``?x``."""  #75 (line in Coconut source)

    name: str  #77 (line in Coconut source)

    @_coconut_tco  # pragma: no cover - cosmetic  #79 (line in Coconut source)
    def __repr__(self) -> str:  # pragma: no cover - cosmetic  #79 (line in Coconut source)
        return _coconut_tail_call("?{_coconut_format_0}".format, _coconut_format_0=(self.name))  #80 (line in Coconut source)



@dataclass(frozen=True)  #83 (line in Coconut source)
class Const():  #84 (line in Coconut source)
    """A constant term (str | int | float | bool)."""  #85 (line in Coconut source)

    value: Any  #87 (line in Coconut source)

    @_coconut_tco  # pragma: no cover - cosmetic  #89 (line in Coconut source)
    def __repr__(self) -> str:  # pragma: no cover - cosmetic  #89 (line in Coconut source)
        return _coconut_tail_call(repr, self.value)  #90 (line in Coconut source)



Term = Var | Const  #93 (line in Coconut source)


@dataclass(frozen=True)  #96 (line in Coconut source)
class Atom():  #97 (line in Coconut source)
    """A predicate applied to terms, e.g. ``parent(?x, "bob")``."""  #98 (line in Coconut source)

    predicate: str  #100 (line in Coconut source)
    terms: tuple[Term, ...] = ()  #101 (line in Coconut source)
    negated: bool = False  #102 (line in Coconut source)

    @property  #104 (line in Coconut source)
    @_coconut_tco  #105 (line in Coconut source)
    def arity(self) -> int:  #105 (line in Coconut source)
        return _coconut_tail_call(len, self.terms)  #106 (line in Coconut source)


    def vars(self) -> set[str]:  #108 (line in Coconut source)
        return {t.name for t in self.terms if isinstance(t, Var)}  #109 (line in Coconut source)

# pragma: no cover - cosmetic
    @_coconut_tco  # pragma: no cover - cosmetic  #111 (line in Coconut source)
    def __repr__(self) -> str:  # pragma: no cover - cosmetic  #111 (line in Coconut source)
        inner = ", ".join((repr(t) for t in self.terms))  #112 (line in Coconut source)
        prefix = "not " if self.negated else ""  #113 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0}{_coconut_format_1}({_coconut_format_2})".format, _coconut_format_0=(prefix), _coconut_format_1=(self.predicate), _coconut_format_2=(inner))  #114 (line in Coconut source)



_COMPARATORS = {"=", "==", "!=", "<", "<=", ">", ">="}  #117 (line in Coconut source)


@dataclass(frozen=True)  #120 (line in Coconut source)
class Comparison():  #121 (line in Coconut source)
    """A comparison built-in body literal, e.g. ``?age >= 18``."""  #122 (line in Coconut source)

    op: str  #124 (line in Coconut source)
    left: Term  #125 (line in Coconut source)
    right: Term  #126 (line in Coconut source)

    def vars(self) -> set[str]:  #128 (line in Coconut source)
        return {t.name for t in (self.left, self.right) if isinstance(t, Var)}  #129 (line in Coconut source)

# pragma: no cover - cosmetic
    @_coconut_tco  # pragma: no cover - cosmetic  #131 (line in Coconut source)
    def __repr__(self) -> str:  # pragma: no cover - cosmetic  #131 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0!r} {_coconut_format_1} {_coconut_format_2!r}".format, _coconut_format_0=(self.left), _coconut_format_1=(self.op), _coconut_format_2=(self.right))  #132 (line in Coconut source)



BodyLiteral = Atom | Comparison  #135 (line in Coconut source)


@dataclass(frozen=True)  #138 (line in Coconut source)
class Rule():  #139 (line in Coconut source)
    """A Horn clause: ``head :- body``. A fact has an empty body."""  #140 (line in Coconut source)

    head: Atom  #142 (line in Coconut source)
    body: tuple[BodyLiteral, ...] = ()  #143 (line in Coconut source)
    name: str = ""  #144 (line in Coconut source)

    @property  #146 (line in Coconut source)
    def is_fact(self) -> bool:  #147 (line in Coconut source)
        return not self.body  #148 (line in Coconut source)

# pragma: no cover - cosmetic
    @_coconut_tco  # pragma: no cover - cosmetic  #150 (line in Coconut source)
    def __repr__(self) -> str:  # pragma: no cover - cosmetic  #150 (line in Coconut source)
        if self.is_fact:  #151 (line in Coconut source)
            return _coconut_tail_call("{_coconut_format_0!r}.".format, _coconut_format_0=(self.head))  #152 (line in Coconut source)
        body = ", ".join((repr(b) for b in self.body))  #153 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0!r} :- {_coconut_format_1}.".format, _coconut_format_0=(self.head), _coconut_format_1=(body))  #154 (line in Coconut source)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


_VAR_RE = re.compile(r"^\?[A-Za-z_][A-Za-z0-9_]*$")  #161 (line in Coconut source)
_ATOM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)$", re.DOTALL)  #162 (line in Coconut source)
_INT_RE = re.compile(r"^[+-]?\d+$")  #163 (line in Coconut source)
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")  #164 (line in Coconut source)


@_coconut_tco  #167 (line in Coconut source)
def _strip_comments(text: str) -> str:  #167 (line in Coconut source)
    out_lines = []  #168 (line in Coconut source)
    for line in text.splitlines():  #169 (line in Coconut source)
# Strip # / % comments, but not inside quotes.
        in_quote: str | None = None  #171 (line in Coconut source)
        cut = len(line)  #172 (line in Coconut source)
        for i, ch in enumerate(line):  #173 (line in Coconut source)
            if in_quote:  #174 (line in Coconut source)
                if ch == in_quote:  #175 (line in Coconut source)
                    in_quote = None  #176 (line in Coconut source)
            elif ch in ("'", '"'):  #177 (line in Coconut source)
                in_quote = ch  #178 (line in Coconut source)
            elif ch in ("#", "%"):  #179 (line in Coconut source)
                cut = i  #180 (line in Coconut source)
                break  #181 (line in Coconut source)
        out_lines.append(line[:cut])  #182 (line in Coconut source)
    return _coconut_tail_call("\n".join, out_lines)  #183 (line in Coconut source)



def _split_top_level(text: str, sep: str=",") -> list[str]:  #186 (line in Coconut source)
    """Split on ``sep`` characters that sit at parenthesis/quote depth 0."""  #187 (line in Coconut source)
    parts: list[str] = []  #188 (line in Coconut source)
    depth = 0  #189 (line in Coconut source)
    in_quote: str | None = None  #190 (line in Coconut source)
    buf: list[str] = []  #191 (line in Coconut source)
    for ch in text:  #192 (line in Coconut source)
        if in_quote:  #193 (line in Coconut source)
            buf.append(ch)  #194 (line in Coconut source)
            if ch == in_quote:  #195 (line in Coconut source)
                in_quote = None  #196 (line in Coconut source)
            continue  #197 (line in Coconut source)
        if ch in ("'", '"'):  #198 (line in Coconut source)
            in_quote = ch  #199 (line in Coconut source)
            buf.append(ch)  #200 (line in Coconut source)
            continue  #201 (line in Coconut source)
        if ch == "(":  #202 (line in Coconut source)
            depth += 1  #203 (line in Coconut source)
        elif ch == ")":  #204 (line in Coconut source)
            depth -= 1  #205 (line in Coconut source)
        if ch == sep and depth == 0:  #206 (line in Coconut source)
            parts.append("".join(buf))  #207 (line in Coconut source)
            buf = []  #208 (line in Coconut source)
            continue  #209 (line in Coconut source)
        buf.append(ch)  #210 (line in Coconut source)
    parts.append("".join(buf))  #211 (line in Coconut source)
    return parts  #212 (line in Coconut source)



@_coconut_tco  #215 (line in Coconut source)
def _parse_term(token: str) -> Term:  #215 (line in Coconut source)
    token = token.strip()  #216 (line in Coconut source)
    if not token:  #217 (line in Coconut source)
        raise ParseError("empty term")  #218 (line in Coconut source)
    if token.startswith("?"):  #219 (line in Coconut source)
        if not _VAR_RE.match(token):  #220 (line in Coconut source)
            raise ParseError("invalid variable: {_coconut_format_0!r}".format(_coconut_format_0=(token)))  #221 (line in Coconut source)
        return _coconut_tail_call(Var, token[1:])  #222 (line in Coconut source)
    if (token[0] == '"' and token[-1] == '"' and len(token) >= 2) or (token[0] == "'" and token[-1] == "'" and len(token) >= 2):  #223 (line in Coconut source)
        return _coconut_tail_call(Const, token[1:-1])  #226 (line in Coconut source)
    if _INT_RE.match(token):  #227 (line in Coconut source)
        return _coconut_tail_call(Const, int(token))  #228 (line in Coconut source)
    if _FLOAT_RE.match(token):  #229 (line in Coconut source)
        return _coconut_tail_call(Const, float(token))  #230 (line in Coconut source)
    if token in ("true", "false"):  #231 (line in Coconut source)
        return _coconut_tail_call(Const, token == "true")  #232 (line in Coconut source)
# Bare word -> string constant.
    return _coconut_tail_call(Const, token)  #234 (line in Coconut source)



@_coconut_tco  #237 (line in Coconut source)
def _parse_atom(text: str, *, negated: bool=False) -> Atom:  #237 (line in Coconut source)
    text = text.strip()  #238 (line in Coconut source)
    m = _ATOM_RE.match(text)  #239 (line in Coconut source)
    if not m:  #240 (line in Coconut source)
        raise ParseError("malformed atom: {_coconut_format_0!r} (expected 'pred(args)')".format(_coconut_format_0=(text)))  #241 (line in Coconut source)
    predicate, args_src = m.group(1), m.group(2).strip()  #242 (line in Coconut source)
    if not args_src:  #243 (line in Coconut source)
        return _coconut_tail_call(Atom, predicate=predicate, terms=(), negated=negated)  #244 (line in Coconut source)
    terms = tuple((_parse_term(t) for t in _split_top_level(args_src)))  #245 (line in Coconut source)
    return _coconut_tail_call(Atom, predicate=predicate, terms=terms, negated=negated)  #246 (line in Coconut source)



@_coconut_tco  #249 (line in Coconut source)
def _parse_body_literal(text: str) -> BodyLiteral:  #249 (line in Coconut source)
    text = text.strip()  #250 (line in Coconut source)
# Comparison? look for a top-level comparator surrounded by terms.
# Order matters: check the two-char operators before single-char.
    for op in ("<=", ">=", "==", "!=", "=", "<", ">"):  #253 (line in Coconut source)
# Avoid splitting inside an atom's parens by scanning at depth 0.
        idx = _find_top_level_op(text, op)  #255 (line in Coconut source)
        if idx is not None:  #256 (line in Coconut source)
            left = text[:idx].strip()  #257 (line in Coconut source)
            right = text[idx + len(op):].strip()  #258 (line in Coconut source)
            if left and right and "(" not in left and "(" not in right:  #259 (line in Coconut source)
                return Comparison(op=op, left=_parse_term(left), right=_parse_term(right))  #260 (line in Coconut source)
    if text.startswith("not ") or text.startswith("not(") or text.startswith("!"):  #261 (line in Coconut source)
        rest = text[1:] if text.startswith("!") else text[4:]  #262 (line in Coconut source)
        return _coconut_tail_call(_parse_atom, rest, negated=True)  #263 (line in Coconut source)
    return _coconut_tail_call(_parse_atom, text)  #264 (line in Coconut source)



def _find_top_level_op(text: str, op: str) -> int | None:  #267 (line in Coconut source)
    depth = 0  #268 (line in Coconut source)
    in_quote: str | None = None  #269 (line in Coconut source)
    i = 0  #270 (line in Coconut source)
    n = len(text)  #271 (line in Coconut source)
    while i < n:  #272 (line in Coconut source)
        ch = text[i]  #273 (line in Coconut source)
        if in_quote:  #274 (line in Coconut source)
            if ch == in_quote:  #275 (line in Coconut source)
                in_quote = None  #276 (line in Coconut source)
            i += 1  #277 (line in Coconut source)
            continue  #278 (line in Coconut source)
        if ch in ("'", '"'):  #279 (line in Coconut source)
            in_quote = ch  #280 (line in Coconut source)
            i += 1  #281 (line in Coconut source)
            continue  #282 (line in Coconut source)
        if ch == "(":  #283 (line in Coconut source)
            depth += 1  #284 (line in Coconut source)
        elif ch == ")":  #285 (line in Coconut source)
            depth -= 1  #286 (line in Coconut source)
        elif depth == 0 and text.startswith(op, i):  #287 (line in Coconut source)
# Don't match '=' that is really part of '==', '<=', '>=', '!='.
            if op == "=" and (text[i - 1:i] in ("<", ">", "!", "=") or text[i + 1:i + 2] == "="):  #289 (line in Coconut source)
                i += 1  #290 (line in Coconut source)
                continue  #291 (line in Coconut source)
            if op in ("<", ">") and text[i + 1:i + 2] == "=":  #292 (line in Coconut source)
                i += 1  #293 (line in Coconut source)
                continue  #294 (line in Coconut source)
            return i  #295 (line in Coconut source)
        i += 1  #296 (line in Coconut source)
    return None  #297 (line in Coconut source)



def parse_program(text: str) -> list[Rule]:  #300 (line in Coconut source)
    """Parse a Datalog program (string DSL) into a list of :class:`Rule`."""  #301 (line in Coconut source)
    rules: list[Rule] = []  #302 (line in Coconut source)
# Statements terminate at top-level '.' — but '.' also appears in floats
# (3.14) and inside quotes, so split carefully.
    for stmt in (_split_statements)((_strip_comments)(text)):  #305 (line in Coconut source)
        stmt = stmt.strip()  #306 (line in Coconut source)
        if not stmt:  #307 (line in Coconut source)
            continue  #308 (line in Coconut source)
        if ":-" in stmt:  #309 (line in Coconut source)
            head_src, body_src = stmt.split(":-", 1)  #310 (line in Coconut source)
            head = _parse_atom(head_src)  #311 (line in Coconut source)
            body = tuple((_parse_body_literal(b) for b in _split_top_level(body_src) if b.strip()))  #312 (line in Coconut source)
            rules.append(Rule(head=head, body=body, name=stmt))  #317 (line in Coconut source)
        else:  #318 (line in Coconut source)
            rules.append(Rule(head=_parse_atom(stmt), body=(), name=stmt))  #319 (line in Coconut source)
    return rules  #320 (line in Coconut source)



@_coconut_tco  #323 (line in Coconut source)
def rule_from_obj(obj: Any) -> list[Rule]:  #323 (line in Coconut source)
    """Parse a single rule given as a DSL string or a structured dict.

    Accepted dict shape::

        {"head": "ancestor(?x, ?z)", "body": ["parent(?x, ?y)", "ancestor(?y, ?z)"]}

    ``body`` may be omitted/empty for a fact. Returns a list (a string may parse
    to several rules if it contains multiple statements).
    """  #332 (line in Coconut source)
    _coconut_case_match_to_0 = obj  #333 (line in Coconut source)
    _coconut_case_match_check_0 = False  #333 (line in Coconut source)
    _coconut_match_temp_0 = _coconut.getattr(Rule, "_coconut_is_data", False) or _coconut.isinstance(Rule, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Rule)  # type: ignore  #333 (line in Coconut source)
    _coconut_case_match_check_0 = True  #333 (line in Coconut source)
    if _coconut_case_match_check_0:  #333 (line in Coconut source)
        _coconut_case_match_check_0 = False  #333 (line in Coconut source)
        if not _coconut_case_match_check_0:  #333 (line in Coconut source)
            if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, Rule)):  #333 (line in Coconut source)
                _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #333 (line in Coconut source)
                if _coconut_match_temp_1:  #333 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #333 (line in Coconut source)

        if not _coconut_case_match_check_0:  #333 (line in Coconut source)
            if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, Rule)):  #333 (line in Coconut source)
                _coconut_case_match_check_0 = True  #333 (line in Coconut source)
            if _coconut_case_match_check_0:  #333 (line in Coconut source)
                _coconut_case_match_check_0 = False  #333 (line in Coconut source)
                if not _coconut_case_match_check_0:  #333 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #333 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #333 (line in Coconut source)

                if not _coconut_case_match_check_0:  #333 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #333 (line in Coconut source)
                        _coconut_match_temp_2 = _coconut.getattr(Rule, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #333 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #333 (line in Coconut source)
                            raise _coconut.TypeError("Rule.__match_args__ must be a tuple")  #333 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_2) < 0:  #333 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Rule' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #333 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #333 (line in Coconut source)




    if _coconut_case_match_check_0:  #333 (line in Coconut source)
        return [obj,]  #335 (line in Coconut source)
    if not _coconut_case_match_check_0:  #336 (line in Coconut source)
        _coconut_match_temp_3 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #336 (line in Coconut source)
        _coconut_case_match_check_0 = True  #336 (line in Coconut source)
        if _coconut_case_match_check_0:  #336 (line in Coconut source)
            _coconut_case_match_check_0 = False  #336 (line in Coconut source)
            if not _coconut_case_match_check_0:  #336 (line in Coconut source)
                if (_coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #336 (line in Coconut source)
                    _coconut_match_temp_4 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #336 (line in Coconut source)
                    if _coconut_match_temp_4:  #336 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #336 (line in Coconut source)

            if not _coconut_case_match_check_0:  #336 (line in Coconut source)
                if (not _coconut_match_temp_3) and (_coconut.isinstance(_coconut_case_match_to_0, str)):  #336 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #336 (line in Coconut source)
                if _coconut_case_match_check_0:  #336 (line in Coconut source)
                    _coconut_case_match_check_0 = False  #336 (line in Coconut source)
                    if not _coconut_case_match_check_0:  #336 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #336 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #336 (line in Coconut source)

                    if not _coconut_case_match_check_0:  #336 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #336 (line in Coconut source)
                            _coconut_match_temp_5 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #336 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_5, _coconut.tuple):  #336 (line in Coconut source)
                                raise _coconut.TypeError("str.__match_args__ must be a tuple")  #336 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_5) < 0:  #336 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_5),))  #336 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #336 (line in Coconut source)




        if _coconut_case_match_check_0:  #336 (line in Coconut source)
            return _coconut_tail_call(parse_program, obj)  #337 (line in Coconut source)
    if not _coconut_case_match_check_0:  #338 (line in Coconut source)
        _coconut_match_temp_6 = _coconut.getattr(dict, "_coconut_is_data", False) or _coconut.isinstance(dict, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in dict)  # type: ignore  #338 (line in Coconut source)
        _coconut_case_match_check_0 = True  #338 (line in Coconut source)
        if _coconut_case_match_check_0:  #338 (line in Coconut source)
            _coconut_case_match_check_0 = False  #338 (line in Coconut source)
            if not _coconut_case_match_check_0:  #338 (line in Coconut source)
                if (_coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_0, dict)):  #338 (line in Coconut source)
                    _coconut_match_temp_7 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #338 (line in Coconut source)
                    if _coconut_match_temp_7:  #338 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #338 (line in Coconut source)

            if not _coconut_case_match_check_0:  #338 (line in Coconut source)
                if (not _coconut_match_temp_6) and (_coconut.isinstance(_coconut_case_match_to_0, dict)):  #338 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #338 (line in Coconut source)
                if _coconut_case_match_check_0:  #338 (line in Coconut source)
                    _coconut_case_match_check_0 = False  #338 (line in Coconut source)
                    if not _coconut_case_match_check_0:  #338 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #338 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #338 (line in Coconut source)

                    if not _coconut_case_match_check_0:  #338 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #338 (line in Coconut source)
                            _coconut_match_temp_8 = _coconut.getattr(dict, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #338 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_8, _coconut.tuple):  #338 (line in Coconut source)
                                raise _coconut.TypeError("dict.__match_args__ must be a tuple")  #338 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_8) < 0:  #338 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'dict' only supports %s)" % (_coconut.len(_coconut_match_temp_8),))  #338 (line in Coconut source)
                            _coconut_case_match_check_0 = True  #338 (line in Coconut source)




        if _coconut_case_match_check_0:  #338 (line in Coconut source)
            head = obj.get("head")  #339 (line in Coconut source)
            if not head:  #340 (line in Coconut source)
                raise ParseError("rule dict missing 'head': {_coconut_format_0!r}".format(_coconut_format_0=(obj)))  #341 (line in Coconut source)
            body = obj.get("body") or []  #342 (line in Coconut source)
            if isinstance(body, str):  #343 (line in Coconut source)
                body = [body,]  #344 (line in Coconut source)
            stmt = "{_coconut_format_0} :- {_coconut_format_1}".format(_coconut_format_0=(head), _coconut_format_1=(', '.join(body))) if body else str(head)  #345 (line in Coconut source)
            return _coconut_tail_call(parse_program, stmt)  #346 (line in Coconut source)
    if not _coconut_case_match_check_0:  #347 (line in Coconut source)
        _coconut_case_match_check_0 = True  #347 (line in Coconut source)
        if _coconut_case_match_check_0:  #347 (line in Coconut source)
            raise ParseError("cannot interpret rule: {_coconut_format_0!r}".format(_coconut_format_0=(obj)))  #348 (line in Coconut source)



def _split_statements(text: str) -> list[str]:  #351 (line in Coconut source)
    """Split a program into statements on top-level '.' not inside a float/quote."""  #352 (line in Coconut source)
    stmts: list[str] = []  #353 (line in Coconut source)
    depth = 0  #354 (line in Coconut source)
    in_quote: str | None = None  #355 (line in Coconut source)
    buf: list[str] = []  #356 (line in Coconut source)
    n = len(text)  #357 (line in Coconut source)
    for i, ch in enumerate(text):  #358 (line in Coconut source)
        if in_quote:  #359 (line in Coconut source)
            buf.append(ch)  #360 (line in Coconut source)
            if ch == in_quote:  #361 (line in Coconut source)
                in_quote = None  #362 (line in Coconut source)
            continue  #363 (line in Coconut source)
        if ch in ("'", '"'):  #364 (line in Coconut source)
            in_quote = ch  #365 (line in Coconut source)
            buf.append(ch)  #366 (line in Coconut source)
            continue  #367 (line in Coconut source)
        if ch == "(":  #368 (line in Coconut source)
            depth += 1  #369 (line in Coconut source)
        elif ch == ")":  #370 (line in Coconut source)
            depth -= 1  #371 (line in Coconut source)
        if ch == "." and depth == 0:  #372 (line in Coconut source)
# A '.' between two digits is a decimal point, not a terminator.
            prev = text[i - 1] if i > 0 else ""  #374 (line in Coconut source)
            nxt = text[i + 1] if i + 1 < n else ""  #375 (line in Coconut source)
            if prev.isdigit() and nxt.isdigit():  #376 (line in Coconut source)
                buf.append(ch)  #377 (line in Coconut source)
                continue  #378 (line in Coconut source)
            stmts.append("".join(buf))  #379 (line in Coconut source)
            buf = []  #380 (line in Coconut source)
            continue  #381 (line in Coconut source)
        buf.append(ch)  #382 (line in Coconut source)
    if "".join(buf).strip():  #383 (line in Coconut source)
        stmts.append("".join(buf))  #384 (line in Coconut source)
    return stmts  #385 (line in Coconut source)


# ---------------------------------------------------------------------------
# Fact helpers (public)
# ---------------------------------------------------------------------------


def fact(predicate: str, *args: Any) -> GroundFact:  #392 (line in Coconut source)
    """Build a ground fact tuple: ``fact("parent", "alice", "bob")``."""  #393 (line in Coconut source)
    return (predicate, *args)  #394 (line in Coconut source)



@_coconut_tco  #397 (line in Coconut source)
def normalise_fact(item: Any) -> GroundFact:  #397 (line in Coconut source)
    """Coerce a user-supplied fact into the internal ``(pred, *args)`` tuple.

    Accepts:
      * a tuple/list ``("parent", "alice", "bob")`` / ``["parent", "alice"]``
      * a dict ``{"predicate": "parent", "args": [...]}`` (``terms`` also works)
      * a string in atom syntax ``parent("alice", "bob")`` (must be ground)
    """  #404 (line in Coconut source)
    _coconut_case_match_to_1 = item  #405 (line in Coconut source)
    _coconut_case_match_check_1 = False  #405 (line in Coconut source)
    _coconut_match_temp_9 = _coconut.getattr(str, "_coconut_is_data", False) or _coconut.isinstance(str, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in str)  # type: ignore  #405 (line in Coconut source)
    _coconut_case_match_check_1 = True  #405 (line in Coconut source)
    if _coconut_case_match_check_1:  #405 (line in Coconut source)
        _coconut_case_match_check_1 = False  #405 (line in Coconut source)
        if not _coconut_case_match_check_1:  #405 (line in Coconut source)
            if (_coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_1, str)):  #405 (line in Coconut source)
                _coconut_match_temp_10 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #405 (line in Coconut source)
                if _coconut_match_temp_10:  #405 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #405 (line in Coconut source)

        if not _coconut_case_match_check_1:  #405 (line in Coconut source)
            if (not _coconut_match_temp_9) and (_coconut.isinstance(_coconut_case_match_to_1, str)):  #405 (line in Coconut source)
                _coconut_case_match_check_1 = True  #405 (line in Coconut source)
            if _coconut_case_match_check_1:  #405 (line in Coconut source)
                _coconut_case_match_check_1 = False  #405 (line in Coconut source)
                if not _coconut_case_match_check_1:  #405 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #405 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #405 (line in Coconut source)

                if not _coconut_case_match_check_1:  #405 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #405 (line in Coconut source)
                        _coconut_match_temp_11 = _coconut.getattr(str, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #405 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_11, _coconut.tuple):  #405 (line in Coconut source)
                            raise _coconut.TypeError("str.__match_args__ must be a tuple")  #405 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_11) < 0:  #405 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'str' only supports %s)" % (_coconut.len(_coconut_match_temp_11),))  #405 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #405 (line in Coconut source)




    if _coconut_case_match_check_1:  #405 (line in Coconut source)
        atom = _parse_atom(item)  #407 (line in Coconut source)
        if atom.vars():  #408 (line in Coconut source)
            raise UnsafeRuleError("input fact contains variables: {_coconut_format_0!r}".format(_coconut_format_0=(item)))  #409 (line in Coconut source)
        return (atom.predicate, *(t.value for t in atom.terms))  # type: ignore[union-attr]  #410 (line in Coconut source)
    if not _coconut_case_match_check_1:  #411 (line in Coconut source)
        _coconut_match_temp_12 = _coconut.getattr(dict, "_coconut_is_data", False) or _coconut.isinstance(dict, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in dict)  # type: ignore  #411 (line in Coconut source)
        _coconut_case_match_check_1 = True  #411 (line in Coconut source)
        if _coconut_case_match_check_1:  #411 (line in Coconut source)
            _coconut_case_match_check_1 = False  #411 (line in Coconut source)
            if not _coconut_case_match_check_1:  #411 (line in Coconut source)
                if (_coconut_match_temp_12) and (_coconut.isinstance(_coconut_case_match_to_1, dict)):  #411 (line in Coconut source)
                    _coconut_match_temp_13 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #411 (line in Coconut source)
                    if _coconut_match_temp_13:  #411 (line in Coconut source)
                        _coconut_case_match_check_1 = True  #411 (line in Coconut source)

            if not _coconut_case_match_check_1:  #411 (line in Coconut source)
                if (not _coconut_match_temp_12) and (_coconut.isinstance(_coconut_case_match_to_1, dict)):  #411 (line in Coconut source)
                    _coconut_case_match_check_1 = True  #411 (line in Coconut source)
                if _coconut_case_match_check_1:  #411 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #411 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #411 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #411 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #411 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #411 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #411 (line in Coconut source)
                            _coconut_match_temp_14 = _coconut.getattr(dict, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #411 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_14, _coconut.tuple):  #411 (line in Coconut source)
                                raise _coconut.TypeError("dict.__match_args__ must be a tuple")  #411 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_14) < 0:  #411 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'dict' only supports %s)" % (_coconut.len(_coconut_match_temp_14),))  #411 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #411 (line in Coconut source)




        if _coconut_case_match_check_1:  #411 (line in Coconut source)
            pred = item.get("predicate") or item.get("pred")  #412 (line in Coconut source)
            if not pred:  #413 (line in Coconut source)
                raise DatalogError("fact dict missing 'predicate': {_coconut_format_0!r}".format(_coconut_format_0=(item)))  #414 (line in Coconut source)
            args = item.get("args", item.get("terms", []))  #415 (line in Coconut source)
            return (pred, *args)  #416 (line in Coconut source)
    if not _coconut_case_match_check_1:  #417 (line in Coconut source)
        _coconut_case_match_check_1 = True  #417 (line in Coconut source)
        if _coconut_case_match_check_1:  #417 (line in Coconut source)
            _coconut_case_match_check_1 = False  #417 (line in Coconut source)
            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                _coconut_match_temp_15 = _coconut.getattr(list, "_coconut_is_data", False) or _coconut.isinstance(list, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in list)  # type: ignore  #417 (line in Coconut source)
                _coconut_case_match_check_1 = True  #417 (line in Coconut source)
                if _coconut_case_match_check_1:  #417 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #417 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                        if (_coconut_match_temp_15) and (_coconut.isinstance(_coconut_case_match_to_1, list)):  #417 (line in Coconut source)
                            _coconut_match_temp_16 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #417 (line in Coconut source)
                            if _coconut_match_temp_16:  #417 (line in Coconut source)
                                _coconut_case_match_check_1 = True  #417 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                        if (not _coconut_match_temp_15) and (_coconut.isinstance(_coconut_case_match_to_1, list)):  #417 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #417 (line in Coconut source)
                        if _coconut_case_match_check_1:  #417 (line in Coconut source)
                            _coconut_case_match_check_1 = False  #417 (line in Coconut source)
                            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #417 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #417 (line in Coconut source)

                            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #417 (line in Coconut source)
                                    _coconut_match_temp_17 = _coconut.getattr(list, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #417 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_17, _coconut.tuple):  #417 (line in Coconut source)
                                        raise _coconut.TypeError("list.__match_args__ must be a tuple")  #417 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_17) < 0:  #417 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'list' only supports %s)" % (_coconut.len(_coconut_match_temp_17),))  #417 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #417 (line in Coconut source)





            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                _coconut_match_temp_18 = _coconut.getattr(tuple, "_coconut_is_data", False) or _coconut.isinstance(tuple, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in tuple)  # type: ignore  #417 (line in Coconut source)
                _coconut_case_match_check_1 = True  #417 (line in Coconut source)
                if _coconut_case_match_check_1:  #417 (line in Coconut source)
                    _coconut_case_match_check_1 = False  #417 (line in Coconut source)
                    if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                        if (_coconut_match_temp_18) and (_coconut.isinstance(_coconut_case_match_to_1, tuple)):  #417 (line in Coconut source)
                            _coconut_match_temp_19 = _coconut.len(_coconut_case_match_to_1) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_1.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {}) and _coconut_case_match_to_1[i] == _coconut.getattr(_coconut_case_match_to_1, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_1.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_1, "__match_args__") else _coconut.len(_coconut_case_match_to_1) == 0  # type: ignore  #417 (line in Coconut source)
                            if _coconut_match_temp_19:  #417 (line in Coconut source)
                                _coconut_case_match_check_1 = True  #417 (line in Coconut source)

                    if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                        if (not _coconut_match_temp_18) and (_coconut.isinstance(_coconut_case_match_to_1, tuple)):  #417 (line in Coconut source)
                            _coconut_case_match_check_1 = True  #417 (line in Coconut source)
                        if _coconut_case_match_check_1:  #417 (line in Coconut source)
                            _coconut_case_match_check_1 = False  #417 (line in Coconut source)
                            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                                if _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #417 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #417 (line in Coconut source)

                            if not _coconut_case_match_check_1:  #417 (line in Coconut source)
                                if not _coconut.type(_coconut_case_match_to_1) in _coconut_self_match_types:  #417 (line in Coconut source)
                                    _coconut_match_temp_20 = _coconut.getattr(tuple, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #417 (line in Coconut source)
                                    if not _coconut.isinstance(_coconut_match_temp_20, _coconut.tuple):  #417 (line in Coconut source)
                                        raise _coconut.TypeError("tuple.__match_args__ must be a tuple")  #417 (line in Coconut source)
                                    if _coconut.len(_coconut_match_temp_20) < 0:  #417 (line in Coconut source)
                                        raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'tuple' only supports %s)" % (_coconut.len(_coconut_match_temp_20),))  #417 (line in Coconut source)
                                    _coconut_case_match_check_1 = True  #417 (line in Coconut source)






        if _coconut_case_match_check_1:  #417 (line in Coconut source)
            if not item:  #418 (line in Coconut source)
                raise DatalogError("empty fact")  #419 (line in Coconut source)
            return _coconut_tail_call(tuple, item)  #420 (line in Coconut source)
    if not _coconut_case_match_check_1:  #421 (line in Coconut source)
        _coconut_case_match_check_1 = True  #421 (line in Coconut source)
        if _coconut_case_match_check_1:  #421 (line in Coconut source)
            raise DatalogError("cannot interpret fact: {_coconut_format_0!r}".format(_coconut_format_0=(item)))  #422 (line in Coconut source)



def atoms_to_facts(items: Iterable[Any]) -> set[GroundFact]:  #425 (line in Coconut source)
    """Normalise an iterable of user facts into a set of internal tuples."""  #426 (line in Coconut source)
    return {normalise_fact(i) for i in items}  #427 (line in Coconut source)



def fact_to_dict(f: GroundFact) -> dict[str, Any]:  #430 (line in Coconut source)
    """Render an internal fact tuple as a JSON-friendly dict."""  #431 (line in Coconut source)
    return {"predicate": f[0], "args": list(f[1:])}  #432 (line in Coconut source)


# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------


@dataclass  #439 (line in Coconut source)
class Solution():  #440 (line in Coconut source)
    """The result of running a :class:`Program`.

    Attributes:
        facts: the full deductive closure (input facts + all derived facts).
        derived: only the newly inferred facts (closure minus input facts).
        justifications: when solved ``with_proof=True``, maps each derived fact
            to ``(rule_repr, [ground_body_facts])`` recording why it holds.
    """  #448 (line in Coconut source)

    facts: set[GroundFact]  #450 (line in Coconut source)
    derived: set[GroundFact] = field(default_factory=set)  #451 (line in Coconut source)
    justifications: dict[GroundFact, tuple[str, list[GroundFact]]] = field(default_factory=dict)  #452 (line in Coconut source)

    @_coconut_tco  #454 (line in Coconut source)
    def query(self, predicate: str) -> list[GroundFact]:  #454 (line in Coconut source)
        """All facts (input + derived) with the given predicate."""  #455 (line in Coconut source)
        return _coconut_tail_call(sorted, (f for f in self.facts if f[0] == predicate), key=repr)  #456 (line in Coconut source)


    def as_dicts(self, *, only_derived: bool=False) -> list[dict[str, Any]]:  #458 (line in Coconut source)
        """Render facts as JSON-friendly ``{"predicate", "args"}`` dicts."""  #459 (line in Coconut source)
        src = self.derived if only_derived else self.facts  #460 (line in Coconut source)
        return [fact_to_dict(f) for f in sorted(src, key=repr)]  #461 (line in Coconut source)


    @_coconut_tco  #463 (line in Coconut source)
    def explain(self, f: GroundFact) -> str:  #463 (line in Coconut source)
        """Human-readable, one-line proof for a derived fact (if recorded)."""  #464 (line in Coconut source)
        if f not in self.justifications:  #465 (line in Coconut source)
            return "{_coconut_format_0} (given)".format(_coconut_format_0=(fact_to_dict(f))) if f in self.facts else "(unknown fact)"  #466 (line in Coconut source)
        rule_repr, support = self.justifications[f]  #467 (line in Coconut source)
        because = ", ".join((repr(s) for s in support)) or "(no premises)"  #468 (line in Coconut source)
        return _coconut_tail_call("{_coconut_format_0}{_coconut_format_1} ⟸ {_coconut_format_2}   [rule: {_coconut_format_3}]".format, _coconut_format_0=(f[0]), _coconut_format_1=(f[1:]), _coconut_format_2=(because), _coconut_format_3=(rule_repr))  #469 (line in Coconut source)


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------


class Program():  #476 (line in Coconut source)
    """A compiled, validated, stratified Datalog rule program."""  #477 (line in Coconut source)

    def __init__(self, rules: Iterable[Rule]):  #479 (line in Coconut source)
        self.rules: list[Rule] = list(rules)  #480 (line in Coconut source)
        self._base_facts: set[GroundFact] = set()  #481 (line in Coconut source)
        self._derivation_rules: list[Rule] = []  #482 (line in Coconut source)
        for r in self.rules:  #483 (line in Coconut source)
            if r.is_fact:  #484 (line in Coconut source)
                if r.head.vars():  #485 (line in Coconut source)
                    raise UnsafeRuleError("fact has unbound variables: {_coconut_format_0!r}".format(_coconut_format_0=(r)))  #486 (line in Coconut source)
                self._base_facts.add((r.head.predicate, *(t.value for t in r.head.terms)))  # type: ignore[union-attr]  #487 (line in Coconut source)
            else:  #490 (line in Coconut source)
                self._derivation_rules.append(_compile_rule(r))  #491 (line in Coconut source)
# Predicates that can be *derived* (appear as a rule head).
        self._intensional: set[str] = {r.head.predicate for r in self._derivation_rules}  #493 (line in Coconut source)
        self._strata: list[set[str]] = _stratify(self._derivation_rules, self._intensional)  #494 (line in Coconut source)


    @classmethod  #496 (line in Coconut source)
    @_coconut_tco  #497 (line in Coconut source)
    def parse(cls, text: str) -> "Program":  #497 (line in Coconut source)
        """Compile a program from the string DSL."""  #498 (line in Coconut source)
        return _coconut_tail_call(cls, parse_program(text))  #499 (line in Coconut source)


    @property  #501 (line in Coconut source)
    def strata(self) -> list[set[str]]:  #502 (line in Coconut source)
        """The computed stratification (predicate sets, lowest stratum first)."""  #503 (line in Coconut source)
        return self._strata  #504 (line in Coconut source)


    @_coconut_tco  #506 (line in Coconut source)
    def solve(self, facts: Iterable[Any] | None=None, *, with_proof: bool=False,) -> Solution:  #506 (line in Coconut source)
        """Compute the deductive closure of ``facts`` under this program.

        ``facts`` are normalised via :func:`normalise_fact`, so tuples, dicts,
        lists and atom-syntax strings are all accepted.
        """  #516 (line in Coconut source)
        db: set[GroundFact] = set(self._base_facts)  #517 (line in Coconut source)
        if facts:  #518 (line in Coconut source)
            db |= atoms_to_facts(facts)  #519 (line in Coconut source)
        input_facts = set(db)  #520 (line in Coconut source)
        justifications: dict[GroundFact, tuple[str, list[GroundFact]]] = {}  #521 (line in Coconut source)

# Evaluate stratum by stratum; negation in a stratum only ever refers to
# predicates whose closure is already complete (lower strata), which is
# exactly what stratification guarantees.
        for stratum in self._strata:  #526 (line in Coconut source)
            stratum_rules = [r for r in self._derivation_rules if r.head.predicate in stratum]  #527 (line in Coconut source)
            changed = True  #528 (line in Coconut source)
            while changed:  #529 (line in Coconut source)
                changed = False  #530 (line in Coconut source)
                new_facts: set[GroundFact] = set()  #531 (line in Coconut source)
                for rule in stratum_rules:  #532 (line in Coconut source)
                    for binding, support in _match_body(rule.body, db):  #533 (line in Coconut source)
                        new_fact = _ground_head(rule.head, binding)  #534 (line in Coconut source)
                        if new_fact not in db and new_fact not in new_facts:  #535 (line in Coconut source)
                            new_facts.add(new_fact)  #536 (line in Coconut source)
                            if with_proof and new_fact not in justifications:  #537 (line in Coconut source)
                                justifications[new_fact] = (rule.name or repr(rule), support)  #538 (line in Coconut source)
                if new_facts:  #539 (line in Coconut source)
                    db |= new_facts  #540 (line in Coconut source)
                    changed = True  #541 (line in Coconut source)

        return _coconut_tail_call(Solution, facts=db, derived=db - input_facts, justifications=justifications)  #543 (line in Coconut source)


# ---------------------------------------------------------------------------
# Compilation: safety check + body reordering
# ---------------------------------------------------------------------------


@_coconut_tco  #554 (line in Coconut source)
def _compile_rule(rule: Rule) -> Rule:  #554 (line in Coconut source)
    """Validate range-restriction and reorder the body (positives first).

    Reordering guarantees that by the time a negated literal or comparison is
    evaluated left-to-right, all of its variables are already bound.
    """  #559 (line in Coconut source)
    positives = [b for b in rule.body if isinstance(b, Atom) and not b.negated]  #560 (line in Coconut source)
    others = [b for b in rule.body if not (isinstance(b, Atom) and not b.negated)]  #561 (line in Coconut source)

    positive_vars: set[str] = set()  #563 (line in Coconut source)
    for p in positives:  #564 (line in Coconut source)
        positive_vars |= p.vars()  #565 (line in Coconut source)

# Head safety: every head var must be bound by a positive body literal.
    unbound_head = rule.head.vars() - positive_vars  #568 (line in Coconut source)
    if unbound_head:  #569 (line in Coconut source)
        raise UnsafeRuleError(("unsafe rule {_coconut_format_0!r}: head variable(s) ".format(_coconut_format_0=(rule.name or rule)) + "{_coconut_format_0} not bound by any positive literal".format(_coconut_format_0=(sorted(('?' + v for v in unbound_head))))))  #570 (line in Coconut source)
# Negation/comparison safety.
    for lit in others:  #575 (line in Coconut source)
        unbound = lit.vars() - positive_vars  #576 (line in Coconut source)
        if unbound:  #577 (line in Coconut source)
            kind = "negated literal" if isinstance(lit, Atom) else "comparison"  #578 (line in Coconut source)
            raise UnsafeRuleError(("unsafe rule {_coconut_format_0!r}: {_coconut_format_1} {_coconut_format_2!r} has unbound ".format(_coconut_format_0=(rule.name or rule), _coconut_format_1=(kind), _coconut_format_2=(lit)) + "variable(s) {_coconut_format_0}".format(_coconut_format_0=(sorted(('?' + v for v in unbound))))))  #579 (line in Coconut source)

    return _coconut_tail_call(Rule, head=rule.head, body=(*positives, *others), name=rule.name)  #584 (line in Coconut source)


# ---------------------------------------------------------------------------
# Stratification
# ---------------------------------------------------------------------------


def _stratify(rules: list[Rule], intensional: set[str]) -> list[set[str]]:  #591 (line in Coconut source)
    """Assign each intensional predicate a stratum number.

    Constraint: for a rule with head P,
      * positive body pred Q (intensional) => stratum(P) >= stratum(Q)
      * negated  body pred Q (intensional) => stratum(P) >  stratum(Q)
    A program recursing through negation has no finite assignment -> error.
    """  #598 (line in Coconut source)
    stratum: dict[str, int] = {p: 0 for p in intensional}  #599 (line in Coconut source)
    max_iters = len(intensional) + 1  #600 (line in Coconut source)
    for _ in range(max_iters):  #601 (line in Coconut source)
        changed = False  #602 (line in Coconut source)
        for rule in rules:  #603 (line in Coconut source)
            head_pred = rule.head.predicate  #604 (line in Coconut source)
            for lit in rule.body:  #605 (line in Coconut source)
                if not isinstance(lit, Atom):  #606 (line in Coconut source)
                    continue  #607 (line in Coconut source)
                q = lit.predicate  #608 (line in Coconut source)
                if q not in intensional:  #609 (line in Coconut source)
                    continue  #610 (line in Coconut source)
                required = stratum[q] + (1 if lit.negated else 0)  #611 (line in Coconut source)
                if required > stratum[head_pred]:  #612 (line in Coconut source)
                    stratum[head_pred] = required  #613 (line in Coconut source)
                    changed = True  #614 (line in Coconut source)
        if not changed:  #615 (line in Coconut source)
            break  #616 (line in Coconut source)
    else:  #617 (line in Coconut source)
# Did not converge within the bound -> negative cycle.
        raise StratificationError("program cannot be stratified: recursion through negation detected")  #619 (line in Coconut source)

# Re-verify (a converged-but-violating assignment also means a neg cycle).
    for rule in rules:  #624 (line in Coconut source)
        for lit in rule.body:  #625 (line in Coconut source)
            if isinstance(lit, Atom) and lit.negated and lit.predicate in intensional:  #626 (line in Coconut source)
                if stratum[lit.predicate] >= stratum[rule.head.predicate]:  #627 (line in Coconut source)
                    raise StratificationError(("program cannot be stratified: negated {_coconut_format_0!r} ".format(_coconut_format_0=(lit.predicate)) + "is recursively derived with {_coconut_format_0!r}".format(_coconut_format_0=(rule.head.predicate))))  #628 (line in Coconut source)

    groups: dict[int, set[str]] = {}  #633 (line in Coconut source)
    for pred, s in stratum.items():  #634 (line in Coconut source)
        groups.setdefault(s, set()).add(pred)  #635 (line in Coconut source)
    return [groups[k] for k in sorted(groups)]  #636 (line in Coconut source)


# ---------------------------------------------------------------------------
# Body matching (backtracking join)
# ---------------------------------------------------------------------------


def _match_body(body: tuple[BodyLiteral, ...], db: set[GroundFact],) -> Iterator[tuple[dict[str, Any], list[GroundFact]]]:  #643 (line in Coconut source)
    """Yield ``(binding, support_facts)`` for every way the body unifies with db."""  #647 (line in Coconut source)

    def rec(i: int, binding: dict[str, Any], support: list[GroundFact]) -> Iterator[tuple[dict[str, Any], list[GroundFact]]]:  #649 (line in Coconut source)
        if i == len(body):  #652 (line in Coconut source)
            yield dict(binding), list(support)  #653 (line in Coconut source)
            return  #654 (line in Coconut source)
        lit = body[i]  #655 (line in Coconut source)
        _coconut_case_match_to_2 = lit  #656 (line in Coconut source)
        _coconut_case_match_check_2 = False  #656 (line in Coconut source)
        _coconut_match_temp_21 = _coconut.getattr(Comparison, "_coconut_is_data", False) or _coconut.isinstance(Comparison, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Comparison)  # type: ignore  #656 (line in Coconut source)
        _coconut_case_match_check_2 = True  #656 (line in Coconut source)
        if _coconut_case_match_check_2:  #656 (line in Coconut source)
            _coconut_case_match_check_2 = False  #656 (line in Coconut source)
            if not _coconut_case_match_check_2:  #656 (line in Coconut source)
                if (_coconut_match_temp_21) and (_coconut.isinstance(_coconut_case_match_to_2, Comparison)):  #656 (line in Coconut source)
                    _coconut_match_temp_22 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #656 (line in Coconut source)
                    if _coconut_match_temp_22:  #656 (line in Coconut source)
                        _coconut_case_match_check_2 = True  #656 (line in Coconut source)

            if not _coconut_case_match_check_2:  #656 (line in Coconut source)
                if (not _coconut_match_temp_21) and (_coconut.isinstance(_coconut_case_match_to_2, Comparison)):  #656 (line in Coconut source)
                    _coconut_case_match_check_2 = True  #656 (line in Coconut source)
                if _coconut_case_match_check_2:  #656 (line in Coconut source)
                    _coconut_case_match_check_2 = False  #656 (line in Coconut source)
                    if not _coconut_case_match_check_2:  #656 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #656 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #656 (line in Coconut source)

                    if not _coconut_case_match_check_2:  #656 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #656 (line in Coconut source)
                            _coconut_match_temp_23 = _coconut.getattr(Comparison, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #656 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_23, _coconut.tuple):  #656 (line in Coconut source)
                                raise _coconut.TypeError("Comparison.__match_args__ must be a tuple")  #656 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_23) < 0:  #656 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Comparison' only supports %s)" % (_coconut.len(_coconut_match_temp_23),))  #656 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #656 (line in Coconut source)




        if _coconut_case_match_check_2:  #656 (line in Coconut source)
            if _eval_comparison(lit, binding):  #658 (line in Coconut source)
                yield from rec(i + 1, binding, support)  #659 (line in Coconut source)
            return  #660 (line in Coconut source)
        if not _coconut_case_match_check_2:  #661 (line in Coconut source)
            _coconut_match_temp_24 = _coconut.getattr(Atom, "_coconut_is_data", False) or _coconut.isinstance(Atom, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Atom)  # type: ignore  #661 (line in Coconut source)
            _coconut_case_match_check_2 = True  #661 (line in Coconut source)
            if _coconut_case_match_check_2:  #661 (line in Coconut source)
                _coconut_case_match_check_2 = False  #661 (line in Coconut source)
                if not _coconut_case_match_check_2:  #661 (line in Coconut source)
                    if (_coconut_match_temp_24) and (_coconut.isinstance(_coconut_case_match_to_2, Atom)):  #661 (line in Coconut source)
                        _coconut_match_temp_25 = _coconut.getattr(_coconut_case_match_to_2, 'negated', _coconut_sentinel)  #661 (line in Coconut source)
                        _coconut_match_temp_26 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) if _coconut_case_match_to_2.__match_args__[i] not in ('negated',)) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #661 (line in Coconut source)
                        if (_coconut_match_temp_25 is not _coconut_sentinel) and (_coconut_match_temp_25 is True) and (_coconut_match_temp_26):  #661 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #661 (line in Coconut source)

                if not _coconut_case_match_check_2:  #661 (line in Coconut source)
                    if (not _coconut_match_temp_24) and (_coconut.isinstance(_coconut_case_match_to_2, Atom)):  #661 (line in Coconut source)
                        _coconut_match_temp_28 = _coconut.getattr(_coconut_case_match_to_2, 'negated', _coconut_sentinel)  #661 (line in Coconut source)
                        if (_coconut_match_temp_28 is not _coconut_sentinel) and (_coconut_match_temp_28 is True):  #661 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #661 (line in Coconut source)
                    if _coconut_case_match_check_2:  #661 (line in Coconut source)
                        _coconut_case_match_check_2 = False  #661 (line in Coconut source)
                        if not _coconut_case_match_check_2:  #661 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #661 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #661 (line in Coconut source)

                        if not _coconut_case_match_check_2:  #661 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #661 (line in Coconut source)
                                _coconut_match_temp_27 = _coconut.getattr(Atom, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #661 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_27, _coconut.tuple):  #661 (line in Coconut source)
                                    raise _coconut.TypeError("Atom.__match_args__ must be a tuple")  #661 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_27) < 0:  #661 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Atom' only supports %s)" % (_coconut.len(_coconut_match_temp_27),))  #661 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #661 (line in Coconut source)




            if _coconut_case_match_check_2:  #661 (line in Coconut source)
                ground = _ground_atom(lit, binding)  #662 (line in Coconut source)
                if ground not in db:  # negation as failure  #663 (line in Coconut source)
                    yield from rec(i + 1, binding, support)  #664 (line in Coconut source)
                return  #665 (line in Coconut source)
        if not _coconut_case_match_check_2:  #666 (line in Coconut source)
            _coconut_match_temp_29 = _coconut.getattr(Atom, "_coconut_is_data", False) or _coconut.isinstance(Atom, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Atom)  # type: ignore  #666 (line in Coconut source)
            _coconut_case_match_check_2 = True  #666 (line in Coconut source)
            if _coconut_case_match_check_2:  #666 (line in Coconut source)
                _coconut_case_match_check_2 = False  #666 (line in Coconut source)
                if not _coconut_case_match_check_2:  #666 (line in Coconut source)
                    if (_coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_2, Atom)):  #666 (line in Coconut source)
                        _coconut_match_temp_30 = _coconut.len(_coconut_case_match_to_2) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_2.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {}) and _coconut_case_match_to_2[i] == _coconut.getattr(_coconut_case_match_to_2, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_2.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_2, "__match_args__") else _coconut.len(_coconut_case_match_to_2) == 0  # type: ignore  #666 (line in Coconut source)
                        if _coconut_match_temp_30:  #666 (line in Coconut source)
                            _coconut_case_match_check_2 = True  #666 (line in Coconut source)

                if not _coconut_case_match_check_2:  #666 (line in Coconut source)
                    if (not _coconut_match_temp_29) and (_coconut.isinstance(_coconut_case_match_to_2, Atom)):  #666 (line in Coconut source)
                        _coconut_case_match_check_2 = True  #666 (line in Coconut source)
                    if _coconut_case_match_check_2:  #666 (line in Coconut source)
                        _coconut_case_match_check_2 = False  #666 (line in Coconut source)
                        if not _coconut_case_match_check_2:  #666 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #666 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #666 (line in Coconut source)

                        if not _coconut_case_match_check_2:  #666 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_2) in _coconut_self_match_types:  #666 (line in Coconut source)
                                _coconut_match_temp_31 = _coconut.getattr(Atom, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #666 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_31, _coconut.tuple):  #666 (line in Coconut source)
                                    raise _coconut.TypeError("Atom.__match_args__ must be a tuple")  #666 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_31) < 0:  #666 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Atom' only supports %s)" % (_coconut.len(_coconut_match_temp_31),))  #666 (line in Coconut source)
                                _coconut_case_match_check_2 = True  #666 (line in Coconut source)




            if _coconut_case_match_check_2:  #666 (line in Coconut source)
                for f in db:  #668 (line in Coconut source)
                    if f[0] != lit.predicate or (len(f) - 1) != lit.arity:  #669 (line in Coconut source)
                        continue  #670 (line in Coconut source)
                    nb = _unify(lit.terms, f[1:], binding)  #671 (line in Coconut source)
                    if nb is not None:  #672 (line in Coconut source)
                        support.append(f)  #673 (line in Coconut source)
                        yield from rec(i + 1, nb, support)  #674 (line in Coconut source)
                        support.pop()  #675 (line in Coconut source)


    yield from rec(0, {}, [])  #677 (line in Coconut source)



def _unify(terms: tuple[Term, ...], values: tuple[Any, ...], binding: dict[str, Any]) -> dict[str, Any] | None:  #680 (line in Coconut source)
    nb = binding  #681 (line in Coconut source)
    copied = False  #682 (line in Coconut source)
    for term, value in zip(terms, values):  #683 (line in Coconut source)
        _coconut_case_match_to_3 = term  #684 (line in Coconut source)
        _coconut_case_match_check_3 = False  #684 (line in Coconut source)
        _coconut_match_temp_32 = _coconut.getattr(Const, "_coconut_is_data", False) or _coconut.isinstance(Const, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Const)  # type: ignore  #684 (line in Coconut source)
        _coconut_case_match_check_3 = True  #684 (line in Coconut source)
        if _coconut_case_match_check_3:  #684 (line in Coconut source)
            _coconut_case_match_check_3 = False  #684 (line in Coconut source)
            if not _coconut_case_match_check_3:  #684 (line in Coconut source)
                _coconut_match_set_name_v = _coconut_sentinel  #684 (line in Coconut source)
                if (_coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_3, Const)):  #684 (line in Coconut source)
                    _coconut_match_temp_33 = _coconut.getattr(_coconut_case_match_to_3, 'value', _coconut_sentinel)  #684 (line in Coconut source)
                    _coconut_match_temp_34 = _coconut.len(_coconut_case_match_to_3) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_3.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_3, "_coconut_data_defaults", {}) and _coconut_case_match_to_3[i] == _coconut.getattr(_coconut_case_match_to_3, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_3.__match_args__)) if _coconut_case_match_to_3.__match_args__[i] not in ('value',)) if _coconut.hasattr(_coconut_case_match_to_3, "__match_args__") else _coconut.len(_coconut_case_match_to_3) == 0  # type: ignore  #684 (line in Coconut source)
                    if (_coconut_match_temp_33 is not _coconut_sentinel) and (_coconut_match_temp_34):  #684 (line in Coconut source)
                        _coconut_match_set_name_v = _coconut_match_temp_33  #684 (line in Coconut source)
                        _coconut_case_match_check_3 = True  #684 (line in Coconut source)
                if _coconut_case_match_check_3:  #684 (line in Coconut source)
                    if _coconut_match_set_name_v is not _coconut_sentinel:  #684 (line in Coconut source)
                        v = _coconut_match_set_name_v  #684 (line in Coconut source)

            if not _coconut_case_match_check_3:  #684 (line in Coconut source)
                _coconut_match_set_name_v = _coconut_sentinel  #684 (line in Coconut source)
                if (not _coconut_match_temp_32) and (_coconut.isinstance(_coconut_case_match_to_3, Const)):  #684 (line in Coconut source)
                    _coconut_match_temp_36 = _coconut.getattr(_coconut_case_match_to_3, 'value', _coconut_sentinel)  #684 (line in Coconut source)
                    if _coconut_match_temp_36 is not _coconut_sentinel:  #684 (line in Coconut source)
                        _coconut_match_set_name_v = _coconut_match_temp_36  #684 (line in Coconut source)
                        _coconut_case_match_check_3 = True  #684 (line in Coconut source)
                if _coconut_case_match_check_3:  #684 (line in Coconut source)
                    _coconut_case_match_check_3 = False  #684 (line in Coconut source)
                    if not _coconut_case_match_check_3:  #684 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_3) in _coconut_self_match_types:  #684 (line in Coconut source)
                            _coconut_case_match_check_3 = True  #684 (line in Coconut source)

                    if not _coconut_case_match_check_3:  #684 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_3) in _coconut_self_match_types:  #684 (line in Coconut source)
                            _coconut_match_temp_35 = _coconut.getattr(Const, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #684 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_35, _coconut.tuple):  #684 (line in Coconut source)
                                raise _coconut.TypeError("Const.__match_args__ must be a tuple")  #684 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_35) < 0:  #684 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Const' only supports %s)" % (_coconut.len(_coconut_match_temp_35),))  #684 (line in Coconut source)
                            _coconut_case_match_check_3 = True  #684 (line in Coconut source)


                if _coconut_case_match_check_3:  #684 (line in Coconut source)
                    if _coconut_match_set_name_v is not _coconut_sentinel:  #684 (line in Coconut source)
                        v = _coconut_match_set_name_v  #684 (line in Coconut source)


        if _coconut_case_match_check_3:  #684 (line in Coconut source)
            if v != value:  #686 (line in Coconut source)
                return None  #687 (line in Coconut source)
        if not _coconut_case_match_check_3:  #688 (line in Coconut source)
            _coconut_match_temp_37 = _coconut.getattr(Var, "_coconut_is_data", False) or _coconut.isinstance(Var, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Var)  # type: ignore  #688 (line in Coconut source)
            _coconut_case_match_check_3 = True  #688 (line in Coconut source)
            if _coconut_case_match_check_3:  #688 (line in Coconut source)
                _coconut_case_match_check_3 = False  #688 (line in Coconut source)
                if not _coconut_case_match_check_3:  #688 (line in Coconut source)
                    _coconut_match_set_name_n = _coconut_sentinel  #688 (line in Coconut source)
                    if (_coconut_match_temp_37) and (_coconut.isinstance(_coconut_case_match_to_3, Var)):  #688 (line in Coconut source)
                        _coconut_match_temp_38 = _coconut.getattr(_coconut_case_match_to_3, 'name', _coconut_sentinel)  #688 (line in Coconut source)
                        _coconut_match_temp_39 = _coconut.len(_coconut_case_match_to_3) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_3.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_3, "_coconut_data_defaults", {}) and _coconut_case_match_to_3[i] == _coconut.getattr(_coconut_case_match_to_3, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_3.__match_args__)) if _coconut_case_match_to_3.__match_args__[i] not in ('name',)) if _coconut.hasattr(_coconut_case_match_to_3, "__match_args__") else _coconut.len(_coconut_case_match_to_3) == 0  # type: ignore  #688 (line in Coconut source)
                        if (_coconut_match_temp_38 is not _coconut_sentinel) and (_coconut_match_temp_39):  #688 (line in Coconut source)
                            _coconut_match_set_name_n = _coconut_match_temp_38  #688 (line in Coconut source)
                            _coconut_case_match_check_3 = True  #688 (line in Coconut source)
                    if _coconut_case_match_check_3:  #688 (line in Coconut source)
                        if _coconut_match_set_name_n is not _coconut_sentinel:  #688 (line in Coconut source)
                            n = _coconut_match_set_name_n  #688 (line in Coconut source)

                if not _coconut_case_match_check_3:  #688 (line in Coconut source)
                    _coconut_match_set_name_n = _coconut_sentinel  #688 (line in Coconut source)
                    if (not _coconut_match_temp_37) and (_coconut.isinstance(_coconut_case_match_to_3, Var)):  #688 (line in Coconut source)
                        _coconut_match_temp_41 = _coconut.getattr(_coconut_case_match_to_3, 'name', _coconut_sentinel)  #688 (line in Coconut source)
                        if _coconut_match_temp_41 is not _coconut_sentinel:  #688 (line in Coconut source)
                            _coconut_match_set_name_n = _coconut_match_temp_41  #688 (line in Coconut source)
                            _coconut_case_match_check_3 = True  #688 (line in Coconut source)
                    if _coconut_case_match_check_3:  #688 (line in Coconut source)
                        _coconut_case_match_check_3 = False  #688 (line in Coconut source)
                        if not _coconut_case_match_check_3:  #688 (line in Coconut source)
                            if _coconut.type(_coconut_case_match_to_3) in _coconut_self_match_types:  #688 (line in Coconut source)
                                _coconut_case_match_check_3 = True  #688 (line in Coconut source)

                        if not _coconut_case_match_check_3:  #688 (line in Coconut source)
                            if not _coconut.type(_coconut_case_match_to_3) in _coconut_self_match_types:  #688 (line in Coconut source)
                                _coconut_match_temp_40 = _coconut.getattr(Var, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #688 (line in Coconut source)
                                if not _coconut.isinstance(_coconut_match_temp_40, _coconut.tuple):  #688 (line in Coconut source)
                                    raise _coconut.TypeError("Var.__match_args__ must be a tuple")  #688 (line in Coconut source)
                                if _coconut.len(_coconut_match_temp_40) < 0:  #688 (line in Coconut source)
                                    raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Var' only supports %s)" % (_coconut.len(_coconut_match_temp_40),))  #688 (line in Coconut source)
                                _coconut_case_match_check_3 = True  #688 (line in Coconut source)


                    if _coconut_case_match_check_3:  #688 (line in Coconut source)
                        if _coconut_match_set_name_n is not _coconut_sentinel:  #688 (line in Coconut source)
                            n = _coconut_match_set_name_n  #688 (line in Coconut source)


            if _coconut_case_match_check_3:  #688 (line in Coconut source)
                if n in nb:  #689 (line in Coconut source)
                    if nb[n] != value:  #690 (line in Coconut source)
                        return None  #691 (line in Coconut source)
                else:  #692 (line in Coconut source)
                    if not copied:  #693 (line in Coconut source)
                        nb = dict(nb)  #694 (line in Coconut source)
                        copied = True  #695 (line in Coconut source)
                    nb[n] = value  #696 (line in Coconut source)
    return nb  #697 (line in Coconut source)



def _resolve(term: Term, binding: dict[str, Any]) -> Any:  #700 (line in Coconut source)
    _coconut_case_match_to_4 = term  #701 (line in Coconut source)
    _coconut_case_match_check_4 = False  #701 (line in Coconut source)
    _coconut_match_temp_42 = _coconut.getattr(Const, "_coconut_is_data", False) or _coconut.isinstance(Const, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Const)  # type: ignore  #701 (line in Coconut source)
    _coconut_case_match_check_4 = True  #701 (line in Coconut source)
    if _coconut_case_match_check_4:  #701 (line in Coconut source)
        _coconut_case_match_check_4 = False  #701 (line in Coconut source)
        if not _coconut_case_match_check_4:  #701 (line in Coconut source)
            _coconut_match_set_name_v = _coconut_sentinel  #701 (line in Coconut source)
            if (_coconut_match_temp_42) and (_coconut.isinstance(_coconut_case_match_to_4, Const)):  #701 (line in Coconut source)
                _coconut_match_temp_43 = _coconut.getattr(_coconut_case_match_to_4, 'value', _coconut_sentinel)  #701 (line in Coconut source)
                _coconut_match_temp_44 = _coconut.len(_coconut_case_match_to_4) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_4.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_4, "_coconut_data_defaults", {}) and _coconut_case_match_to_4[i] == _coconut.getattr(_coconut_case_match_to_4, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_4.__match_args__)) if _coconut_case_match_to_4.__match_args__[i] not in ('value',)) if _coconut.hasattr(_coconut_case_match_to_4, "__match_args__") else _coconut.len(_coconut_case_match_to_4) == 0  # type: ignore  #701 (line in Coconut source)
                if (_coconut_match_temp_43 is not _coconut_sentinel) and (_coconut_match_temp_44):  #701 (line in Coconut source)
                    _coconut_match_set_name_v = _coconut_match_temp_43  #701 (line in Coconut source)
                    _coconut_case_match_check_4 = True  #701 (line in Coconut source)
            if _coconut_case_match_check_4:  #701 (line in Coconut source)
                if _coconut_match_set_name_v is not _coconut_sentinel:  #701 (line in Coconut source)
                    v = _coconut_match_set_name_v  #701 (line in Coconut source)

        if not _coconut_case_match_check_4:  #701 (line in Coconut source)
            _coconut_match_set_name_v = _coconut_sentinel  #701 (line in Coconut source)
            if (not _coconut_match_temp_42) and (_coconut.isinstance(_coconut_case_match_to_4, Const)):  #701 (line in Coconut source)
                _coconut_match_temp_46 = _coconut.getattr(_coconut_case_match_to_4, 'value', _coconut_sentinel)  #701 (line in Coconut source)
                if _coconut_match_temp_46 is not _coconut_sentinel:  #701 (line in Coconut source)
                    _coconut_match_set_name_v = _coconut_match_temp_46  #701 (line in Coconut source)
                    _coconut_case_match_check_4 = True  #701 (line in Coconut source)
            if _coconut_case_match_check_4:  #701 (line in Coconut source)
                _coconut_case_match_check_4 = False  #701 (line in Coconut source)
                if not _coconut_case_match_check_4:  #701 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_4) in _coconut_self_match_types:  #701 (line in Coconut source)
                        _coconut_case_match_check_4 = True  #701 (line in Coconut source)

                if not _coconut_case_match_check_4:  #701 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_4) in _coconut_self_match_types:  #701 (line in Coconut source)
                        _coconut_match_temp_45 = _coconut.getattr(Const, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #701 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_45, _coconut.tuple):  #701 (line in Coconut source)
                            raise _coconut.TypeError("Const.__match_args__ must be a tuple")  #701 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_45) < 0:  #701 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Const' only supports %s)" % (_coconut.len(_coconut_match_temp_45),))  #701 (line in Coconut source)
                        _coconut_case_match_check_4 = True  #701 (line in Coconut source)


            if _coconut_case_match_check_4:  #701 (line in Coconut source)
                if _coconut_match_set_name_v is not _coconut_sentinel:  #701 (line in Coconut source)
                    v = _coconut_match_set_name_v  #701 (line in Coconut source)


    if _coconut_case_match_check_4:  #701 (line in Coconut source)
        return v  #703 (line in Coconut source)
    if not _coconut_case_match_check_4:  #704 (line in Coconut source)
        _coconut_match_temp_47 = _coconut.getattr(Var, "_coconut_is_data", False) or _coconut.isinstance(Var, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in Var)  # type: ignore  #704 (line in Coconut source)
        _coconut_case_match_check_4 = True  #704 (line in Coconut source)
        if _coconut_case_match_check_4:  #704 (line in Coconut source)
            _coconut_case_match_check_4 = False  #704 (line in Coconut source)
            if not _coconut_case_match_check_4:  #704 (line in Coconut source)
                _coconut_match_set_name_n = _coconut_sentinel  #704 (line in Coconut source)
                if (_coconut_match_temp_47) and (_coconut.isinstance(_coconut_case_match_to_4, Var)):  #704 (line in Coconut source)
                    _coconut_match_temp_48 = _coconut.getattr(_coconut_case_match_to_4, 'name', _coconut_sentinel)  #704 (line in Coconut source)
                    _coconut_match_temp_49 = _coconut.len(_coconut_case_match_to_4) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_4.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_4, "_coconut_data_defaults", {}) and _coconut_case_match_to_4[i] == _coconut.getattr(_coconut_case_match_to_4, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_4.__match_args__)) if _coconut_case_match_to_4.__match_args__[i] not in ('name',)) if _coconut.hasattr(_coconut_case_match_to_4, "__match_args__") else _coconut.len(_coconut_case_match_to_4) == 0  # type: ignore  #704 (line in Coconut source)
                    if (_coconut_match_temp_48 is not _coconut_sentinel) and (_coconut_match_temp_49):  #704 (line in Coconut source)
                        _coconut_match_set_name_n = _coconut_match_temp_48  #704 (line in Coconut source)
                        _coconut_case_match_check_4 = True  #704 (line in Coconut source)
                if _coconut_case_match_check_4:  #704 (line in Coconut source)
                    if _coconut_match_set_name_n is not _coconut_sentinel:  #704 (line in Coconut source)
                        n = _coconut_match_set_name_n  #704 (line in Coconut source)

            if not _coconut_case_match_check_4:  #704 (line in Coconut source)
                _coconut_match_set_name_n = _coconut_sentinel  #704 (line in Coconut source)
                if (not _coconut_match_temp_47) and (_coconut.isinstance(_coconut_case_match_to_4, Var)):  #704 (line in Coconut source)
                    _coconut_match_temp_51 = _coconut.getattr(_coconut_case_match_to_4, 'name', _coconut_sentinel)  #704 (line in Coconut source)
                    if _coconut_match_temp_51 is not _coconut_sentinel:  #704 (line in Coconut source)
                        _coconut_match_set_name_n = _coconut_match_temp_51  #704 (line in Coconut source)
                        _coconut_case_match_check_4 = True  #704 (line in Coconut source)
                if _coconut_case_match_check_4:  #704 (line in Coconut source)
                    _coconut_case_match_check_4 = False  #704 (line in Coconut source)
                    if not _coconut_case_match_check_4:  #704 (line in Coconut source)
                        if _coconut.type(_coconut_case_match_to_4) in _coconut_self_match_types:  #704 (line in Coconut source)
                            _coconut_case_match_check_4 = True  #704 (line in Coconut source)

                    if not _coconut_case_match_check_4:  #704 (line in Coconut source)
                        if not _coconut.type(_coconut_case_match_to_4) in _coconut_self_match_types:  #704 (line in Coconut source)
                            _coconut_match_temp_50 = _coconut.getattr(Var, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #704 (line in Coconut source)
                            if not _coconut.isinstance(_coconut_match_temp_50, _coconut.tuple):  #704 (line in Coconut source)
                                raise _coconut.TypeError("Var.__match_args__ must be a tuple")  #704 (line in Coconut source)
                            if _coconut.len(_coconut_match_temp_50) < 0:  #704 (line in Coconut source)
                                raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'Var' only supports %s)" % (_coconut.len(_coconut_match_temp_50),))  #704 (line in Coconut source)
                            _coconut_case_match_check_4 = True  #704 (line in Coconut source)


                if _coconut_case_match_check_4:  #704 (line in Coconut source)
                    if _coconut_match_set_name_n is not _coconut_sentinel:  #704 (line in Coconut source)
                        n = _coconut_match_set_name_n  #704 (line in Coconut source)


        if _coconut_case_match_check_4:  #704 (line in Coconut source)
            if n not in binding:  #705 (line in Coconut source)
# Safety checking guarantees this never happens for compiled rules.
                raise UnsafeRuleError("unbound variable ?{_coconut_format_0} at evaluation time".format(_coconut_format_0=(n)))  #707 (line in Coconut source)
            return binding[n]  #708 (line in Coconut source)



def _ground_atom(atom: Atom, binding: dict[str, Any]) -> GroundFact:  #711 (line in Coconut source)
    return (atom.predicate, *(_resolve(t, binding) for t in atom.terms))  #712 (line in Coconut source)



@_coconut_tco  #715 (line in Coconut source)
def _ground_head(head: Atom, binding: dict[str, Any]) -> GroundFact:  #715 (line in Coconut source)
    return _coconut_tail_call(_ground_atom, head, binding)  #716 (line in Coconut source)



def _eval_comparison(cmp: Comparison, binding: dict[str, Any]) -> bool:  #719 (line in Coconut source)
    left = _resolve(cmp.left, binding)  #720 (line in Coconut source)
    right = _resolve(cmp.right, binding)  #721 (line in Coconut source)
    op = cmp.op  #722 (line in Coconut source)
    if op in ("=", "=="):  #723 (line in Coconut source)
        return left == right  #724 (line in Coconut source)
    if op == "!=":  #725 (line in Coconut source)
        return left != right  #726 (line in Coconut source)
    try:  #727 (line in Coconut source)
        if op == "<":  #728 (line in Coconut source)
            return left < right  #729 (line in Coconut source)
        if op == "<=":  #730 (line in Coconut source)
            return left <= right  #731 (line in Coconut source)
        if op == ">":  #732 (line in Coconut source)
            return left > right  #733 (line in Coconut source)
        if op == ">=":  #734 (line in Coconut source)
            return left >= right  #735 (line in Coconut source)
    except TypeError as exc:  #736 (line in Coconut source)
        raise DatalogError("cannot compare {_coconut_format_0!r} {_coconut_format_1} {_coconut_format_2!r}: {_coconut_format_3}".format(_coconut_format_0=(left), _coconut_format_1=(op), _coconut_format_2=(right), _coconut_format_3=(exc))) from exc  #737 (line in Coconut source)
    raise DatalogError("unknown comparison operator: {_coconut_format_0!r}".format(_coconut_format_0=(op)))  #740 (line in Coconut source)
