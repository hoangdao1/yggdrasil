#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x44d7cf56

# Compiled with Coconut version 3.2.0

"""Terminal display layer for yggdrasil execution traces.

This is the canonical home for functions that render a trace to a terminal.
They have side effects (print to stdout) and return None.

Canonical imports:
    from yggdrasil_lm.trace_ui import inspect_trace  # Rich tree UI
    from yggdrasil_lm.trace_ui import print_trace    # plain-text fallback

Functions:
    inspect_trace() — Rich terminal tree with full detail: agent configs,
                      context previews, tool I/O, routing decisions, timing.
                      Falls back to print_trace() when `rich` is not installed.
    print_trace()   — Plain-text trace dump. CI-safe; no dependencies beyond
                      the core package.

Layers:
    yggdrasil.trace_ui       — terminal display (this module)
    yggdrasil.observability  — data API: explain_run, explain_routing, explain_composition
    yggdrasil.viz            — browser UI: serve_trace, live_trace

Usage:
    from yggdrasil_lm.trace_ui import inspect_trace

    ctx = await executor.run(entry_node_id, query)
    inspect_trace(ctx)

    # Compact mode (no context/output previews)
    inspect_trace(ctx, verbose=False)

    # Write to file
    inspect_trace(ctx, file="trace.html", format="html")
    inspect_trace(ctx, file="trace.txt",  format="text")

    # CI / plain-text fallback
    from yggdrasil_lm.trace_ui import print_trace
    print_trace(ctx)
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



import json  #40 (line in Coconut source)
import sys  #41 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #42 (line in Coconut source)
    from typing import IO  #42 (line in Coconut source)
else:  #42 (line in Coconut source)
    try:  #42 (line in Coconut source)
        IO = _coconut.typing.IO  #42 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #42 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #42 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #42 (line in Coconut source)
    from typing import Any  #42 (line in Coconut source)
else:  #42 (line in Coconut source)
    try:  #42 (line in Coconut source)
        Any = _coconut.typing.Any  #42 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #42 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #42 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #42 (line in Coconut source)
    from typing import Literal  #42 (line in Coconut source)
else:  #42 (line in Coconut source)
    try:  #42 (line in Coconut source)
        Literal = _coconut.typing.Literal  #42 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #42 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #42 (line in Coconut source)

from yggdrasil_lm.core.executor import ExecutionContext  # noqa: F401  #44 (line in Coconut source)
from yggdrasil_lm.core.executor import TraceEvent  # noqa: F401  #44 (line in Coconut source)
from yggdrasil_lm.core.executor import print_trace  # noqa: F401  #44 (line in Coconut source)

__all__ = ["inspect_trace", "print_trace"]  #46 (line in Coconut source)

try:  #48 (line in Coconut source)
    from rich import box  #49 (line in Coconut source)
    from rich.columns import Columns  #50 (line in Coconut source)
    from rich.console import Console  #51 (line in Coconut source)
    from rich.panel import Panel  #52 (line in Coconut source)
    from rich.rule import Rule  #53 (line in Coconut source)
    from rich.syntax import Syntax  #54 (line in Coconut source)
    from rich.table import Table  #55 (line in Coconut source)
    from rich.text import Text  #56 (line in Coconut source)
    from rich.tree import Tree  #57 (line in Coconut source)
    _RICH = True  #58 (line in Coconut source)
except ImportError:  #59 (line in Coconut source)
    _RICH = False  #60 (line in Coconut source)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def inspect_trace(ctx: ExecutionContext | list[TraceEvent], *, verbose: bool=True, file: str | None=None, format: Literal["terminal", "html", "text"]="terminal",) -> None:  #67 (line in Coconut source)
    """Render the execution trace as a rich terminal UI.

    Args:
        ctx:     ExecutionContext or raw list[TraceEvent].
        verbose: When True (default), shows full context content and complete
                 tool inputs/outputs. When False, truncates to one-liners.
        file:    Optional path to write output. Supports .html and .txt.
        format:  "terminal" (default), "html", or "text".
    """  #82 (line in Coconut source)
    if not _RICH:  #83 (line in Coconut source)
        print_trace(ctx)  #84 (line in Coconut source)
        return  #85 (line in Coconut source)

    _coconut_case_match_to_0 = ctx  #87 (line in Coconut source)
    _coconut_case_match_check_0 = False  #87 (line in Coconut source)
    _coconut_match_temp_0 = _coconut.getattr(ExecutionContext, "_coconut_is_data", False) or _coconut.isinstance(ExecutionContext, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "_coconut_is_data", False) for _coconut_x in ExecutionContext)  # type: ignore  #87 (line in Coconut source)
    _coconut_case_match_check_0 = True  #87 (line in Coconut source)
    if _coconut_case_match_check_0:  #87 (line in Coconut source)
        _coconut_case_match_check_0 = False  #87 (line in Coconut source)
        if not _coconut_case_match_check_0:  #87 (line in Coconut source)
            if (_coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, ExecutionContext)):  #87 (line in Coconut source)
                _coconut_match_temp_1 = _coconut.len(_coconut_case_match_to_0) <= _coconut.max(0, _coconut.len(_coconut_case_match_to_0.__match_args__)) and _coconut.all(i in _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {}) and _coconut_case_match_to_0[i] == _coconut.getattr(_coconut_case_match_to_0, "_coconut_data_defaults", {})[i] for i in _coconut.range(0, _coconut.len(_coconut_case_match_to_0.__match_args__))) if _coconut.hasattr(_coconut_case_match_to_0, "__match_args__") else _coconut.len(_coconut_case_match_to_0) == 0  # type: ignore  #87 (line in Coconut source)
                if _coconut_match_temp_1:  #87 (line in Coconut source)
                    _coconut_case_match_check_0 = True  #87 (line in Coconut source)

        if not _coconut_case_match_check_0:  #87 (line in Coconut source)
            if (not _coconut_match_temp_0) and (_coconut.isinstance(_coconut_case_match_to_0, ExecutionContext)):  #87 (line in Coconut source)
                _coconut_case_match_check_0 = True  #87 (line in Coconut source)
            if _coconut_case_match_check_0:  #87 (line in Coconut source)
                _coconut_case_match_check_0 = False  #87 (line in Coconut source)
                if not _coconut_case_match_check_0:  #87 (line in Coconut source)
                    if _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #87 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #87 (line in Coconut source)

                if not _coconut_case_match_check_0:  #87 (line in Coconut source)
                    if not _coconut.type(_coconut_case_match_to_0) in _coconut_self_match_types:  #87 (line in Coconut source)
                        _coconut_match_temp_2 = _coconut.getattr(ExecutionContext, '__match_args__', ())  # type: _coconut.typing.Any  # type: ignore  #87 (line in Coconut source)
                        if not _coconut.isinstance(_coconut_match_temp_2, _coconut.tuple):  #87 (line in Coconut source)
                            raise _coconut.TypeError("ExecutionContext.__match_args__ must be a tuple")  #87 (line in Coconut source)
                        if _coconut.len(_coconut_match_temp_2) < 0:  #87 (line in Coconut source)
                            raise _coconut.TypeError("too many positional args in class match (pattern requires 0; 'ExecutionContext' only supports %s)" % (_coconut.len(_coconut_match_temp_2),))  #87 (line in Coconut source)
                        _coconut_case_match_check_0 = True  #87 (line in Coconut source)




    if _coconut_case_match_check_0:  #87 (line in Coconut source)
        events = ctx.trace  #89 (line in Coconut source)
        session_id = ctx.session_id  #90 (line in Coconut source)
        query = ctx.query  #91 (line in Coconut source)
        hop_count = ctx.hop_count  #92 (line in Coconut source)
    if not _coconut_case_match_check_0:  #93 (line in Coconut source)
        _coconut_case_match_check_0 = True  #93 (line in Coconut source)
        if _coconut_case_match_check_0:  #93 (line in Coconut source)
            events = ctx  #94 (line in Coconut source)
            session_id = events[0].session_id if events else "?"  #95 (line in Coconut source)
            query = ""  #96 (line in Coconut source)
            hop_count = sum((1 for e in events if e.event_type == "hop"))  #97 (line in Coconut source)

# Build console for chosen output destination
    if file:  #100 (line in Coconut source)
        _fmt = format  #101 (line in Coconut source)
        with open(file, "w", encoding="utf-8") as fh:  #102 (line in Coconut source)
            if _fmt == "html":  #103 (line in Coconut source)
                console = Console(file=fh, record=True, force_terminal=False, width=120)  #104 (line in Coconut source)
            else:  #105 (line in Coconut source)
                console = Console(file=fh, force_terminal=False, no_color=True, width=120)  #106 (line in Coconut source)
            _render_session(console, events, session_id, query, hop_count, verbose)  #107 (line in Coconut source)
            if _fmt == "html":  #108 (line in Coconut source)
                fh.write(console.export_html())  #109 (line in Coconut source)
        print("Trace written to {_coconut_format_0}".format(_coconut_format_0=(file)), file=sys.stderr)  #110 (line in Coconut source)
        return  #111 (line in Coconut source)
    else:  #112 (line in Coconut source)
        console = Console(highlight=True)  #113 (line in Coconut source)

    _render_session(console, events, session_id, query, hop_count, verbose)  #115 (line in Coconut source)


# ---------------------------------------------------------------------------
# Session renderer
# ---------------------------------------------------------------------------


_AGENT_COLOR = "bold cyan"  #122 (line in Coconut source)
_TOOL_COLOR = "bold yellow"  #123 (line in Coconut source)
_RESULT_OK = "green"  #124 (line in Coconut source)
_RESULT_ERR = "bold red"  #125 (line in Coconut source)
_ROUTING_COLOR = "magenta"  #126 (line in Coconut source)
_CTX_COLOR = "blue"  #127 (line in Coconut source)
_DIM = "dim"  #128 (line in Coconut source)
_HOP_COLOR = "bold white"  #129 (line in Coconut source)


def _render_session(console: Console, events: list[TraceEvent], session_id: str, query: str, hop_count: int, verbose: bool,) -> None:  #132 (line in Coconut source)
    """Top-level renderer: header → tree → summary."""  #140 (line in Coconut source)

# ── Header ──────────────────────────────────────────────────────────────
    console.print()  #143 (line in Coconut source)
    console.rule("[bold]Session[/bold] [dim]{_coconut_format_0}[/dim]".format(_coconut_format_0=(session_id[:8])), style="cyan")  #144 (line in Coconut source)
    if query:  #148 (line in Coconut source)
        console.print("[dim]Query:[/dim] {_coconut_format_0}\n".format(_coconut_format_0=(query)))  #149 (line in Coconut source)

# ── Build parent→children index ─────────────────────────────────────────
    children: dict[str | None, list[TraceEvent]] = {}  #152 (line in Coconut source)
    for e in events:  #153 (line in Coconut source)
        children.setdefault(e.parent_event_id, []).append(e)  #154 (line in Coconut source)

# ── Render top-level events (hops) ───────────────────────────────────────
    for root in children.get(None, []):  #157 (line in Coconut source)
        _render_event(console, root, children, verbose, depth=0)  #158 (line in Coconut source)

# ── Summary ─────────────────────────────────────────────────────────────
    _render_summary(console, events, hop_count)  #161 (line in Coconut source)
    console.print()  #162 (line in Coconut source)


# ---------------------------------------------------------------------------
# Event renderer (recursive)
# ---------------------------------------------------------------------------


def _fmt_ms(ms: int | None) -> str:  #169 (line in Coconut source)
    """Return a plain (no markup) timing string, or empty string."""  #170 (line in Coconut source)
    if ms is None:  #171 (line in Coconut source)
        return ""  #172 (line in Coconut source)
    return "{_coconut_format_0}ms".format(_coconut_format_0=(ms)) if ms < 1000 else "{_coconut_format_0:.1f}s".format(_coconut_format_0=(ms / 1000))  #173 (line in Coconut source)



def _truncate(s: str, n: int) -> str:  #176 (line in Coconut source)
    return s[:n] + "…" if len(s) > n else s  #177 (line in Coconut source)



@_coconut_tco  #180 (line in Coconut source)
def _json_panel(data: dict | str, title: str, color: str, verbose: bool) -> Any:  #180 (line in Coconut source)
    """Return a Syntax panel for JSON data, or a dim one-liner when not verbose."""  #181 (line in Coconut source)
    raw = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else data  #182 (line in Coconut source)
    if not verbose:  #183 (line in Coconut source)
        one = raw.replace("\n", " ")  #184 (line in Coconut source)
        return _coconut_tail_call(Text, "{_coconut_format_0}: {_coconut_format_1}".format(_coconut_format_0=(title), _coconut_format_1=(_truncate(one, 80))), style="dim")  #185 (line in Coconut source)
    return _coconut_tail_call(Panel, Syntax(raw, "json", theme="monokai", word_wrap=True), title=title, border_style=color, expand=False, padding=(0, 1))  #186 (line in Coconut source)



def _render_event(console: Console, event: TraceEvent, children: dict[str | None, list[TraceEvent]], verbose: bool, depth: int, tree: Tree | None=None,) -> None:  #195 (line in Coconut source)
    """Recursively render one event, attaching children to a rich Tree node."""  #203 (line in Coconut source)
    t = event.event_type  #204 (line in Coconut source)
    p = event.payload  #205 (line in Coconut source)
    pad = "  " * depth  #206 (line in Coconut source)

    _coconut_case_match_to_1 = t  #208 (line in Coconut source)
    _coconut_case_match_check_1 = False  #208 (line in Coconut source)
    if _coconut_case_match_to_1 == "hop":  #208 (line in Coconut source)
        _coconut_case_match_check_1 = True  #208 (line in Coconut source)
    if _coconut_case_match_check_1:  #208 (line in Coconut source)
        node_type = p.get("node_type", "").split(".")[-1].upper()  #211 (line in Coconut source)
        hop_num = p.get("hop", "")  #212 (line in Coconut source)
        label = Text()  #213 (line in Coconut source)
        label.append("HOP {_coconut_format_0}  ".format(_coconut_format_0=(hop_num)), style=_HOP_COLOR)  #214 (line in Coconut source)
        label.append("{_coconut_format_0}  ".format(_coconut_format_0=(node_type)), style=_DIM)  #215 (line in Coconut source)
        label.append(event.node_name, style=_AGENT_COLOR)  #216 (line in Coconut source)
        ms = _fmt_ms(event.duration_ms)  #217 (line in Coconut source)
        if ms:  #218 (line in Coconut source)
            label.append("  {_coconut_format_0}".format(_coconut_format_0=(ms)), style=_DIM)  #219 (line in Coconut source)

        branch = Tree(label)  #221 (line in Coconut source)
        for child in children.get(event.event_id, []):  #222 (line in Coconut source)
            _render_event(console, child, children, verbose, depth=0, tree=branch)  #223 (line in Coconut source)

        if tree:  #225 (line in Coconut source)
            tree.add(branch)  #226 (line in Coconut source)
        else:  #227 (line in Coconut source)
            console.print(branch)  #228 (line in Coconut source)
            console.print()  #229 (line in Coconut source)

# ── agent_start ─────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #232 (line in Coconut source)
        if _coconut_case_match_to_1 == "agent_start":  #232 (line in Coconut source)
            _coconut_case_match_check_1 = True  #232 (line in Coconut source)
        if _coconut_case_match_check_1:  #232 (line in Coconut source)
            model = p.get("model", "?")  #233 (line in Coconut source)
            tools = p.get("tools", [])  #234 (line in Coconut source)
            ctx_l = p.get("context", [])  #235 (line in Coconut source)
            ctx_scores = p.get("context_scores", [])  #236 (line in Coconut source)

# Header row
            header = Text()  #239 (line in Coconut source)
            header.append("AGENT  ", style=_AGENT_COLOR)  #240 (line in Coconut source)
            header.append(event.node_name, style="bold")  #241 (line in Coconut source)
            header.append("  [{_coconut_format_0}]".format(_coconut_format_0=(model)), style=_DIM)  #242 (line in Coconut source)
            node = tree.add(header) if tree else None  #243 (line in Coconut source)

# Tools row
            if tools:  #246 (line in Coconut source)
                tool_text = Text()  #247 (line in Coconut source)
                tool_text.append("  tools  ", style=_DIM)  #248 (line in Coconut source)
                tool_text.append(", ".join(tools), style=_TOOL_COLOR)  #249 (line in Coconut source)
                if node:  #250 (line in Coconut source)
                    node.add(tool_text)  #251 (line in Coconut source)
                else:  #252 (line in Coconut source)
                    console.print("{_coconut_format_0}  {_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(tool_text)))  #253 (line in Coconut source)
            else:  #254 (line in Coconut source)
                dim = Text("  tools  none", style=_DIM)  #255 (line in Coconut source)
                if node:  #256 (line in Coconut source)
                    node.add(dim)  #257 (line in Coconut source)

# Context row
            if ctx_l:  #260 (line in Coconut source)
                ctx_text = Text()  #261 (line in Coconut source)
                ctx_text.append("  context  ", style=_DIM)  #262 (line in Coconut source)
                ctx_text.append(", ".join(ctx_l), style=_CTX_COLOR)  #263 (line in Coconut source)
                if node:  #264 (line in Coconut source)
                    node.add(ctx_text)  #265 (line in Coconut source)
            if node and verbose and ctx_scores:  #266 (line in Coconut source)
                rows = [("{_coconut_format_0}: score={_coconut_format_1} ".format(_coconut_format_0=(item.get('name')), _coconut_format_1=(item.get('score'))) + "source={_coconut_format_0} hops={_coconut_format_1}".format(_coconut_format_0=(item.get('source')), _coconut_format_1=(item.get('hops')))) for item in ctx_scores]  #267 (line in Coconut source)
                node.add(Text("  ranked  " + " | ".join(rows), style=_DIM))  #272 (line in Coconut source)

# Children (context_inject, tool_call, agent_end, routing)
            for child in children.get(event.event_id, []):  #275 (line in Coconut source)
                _render_event(console, child, children, verbose, depth=depth, tree=node or tree)  #276 (line in Coconut source)

# ── context_inject ──────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #279 (line in Coconut source)
        if _coconut_case_match_to_1 == "context_inject":  #279 (line in Coconut source)
            _coconut_case_match_check_1 = True  #279 (line in Coconut source)
        if _coconut_case_match_check_1:  #279 (line in Coconut source)
            names = p.get("context_names", [])  #280 (line in Coconut source)
            count = p.get("count", 0)  #281 (line in Coconut source)
            selected = p.get("selected_contexts", [])  #282 (line in Coconut source)
            label = Text()  #283 (line in Coconut source)
            label.append("  CONTEXT  ", style=_CTX_COLOR)  #284 (line in Coconut source)
            label.append("{_coconut_format_0} node{_coconut_format_1}  ".format(_coconut_format_0=(count), _coconut_format_1=('s' if count != 1 else '')), style=_DIM)  #285 (line in Coconut source)
            label.append(", ".join(names), style=_CTX_COLOR)  #286 (line in Coconut source)
            if tree:  #287 (line in Coconut source)
                node = tree.add(label)  #288 (line in Coconut source)
                if verbose and selected:  #289 (line in Coconut source)
                    for item in selected:  #290 (line in Coconut source)
                        details = (("{_coconut_format_0}  score={_coconut_format_1}  ".format(_coconut_format_0=(item.get('name')), _coconut_format_1=(item.get('score'))) + "source={_coconut_format_0}  hops={_coconut_format_1}  ".format(_coconut_format_0=(item.get('source')), _coconut_format_1=(item.get('hops'))) + "tokens={_coconut_format_0}".format(_coconut_format_0=(item.get('token_count')))))  #291 (line in Coconut source)
                        node.add(Text(details, style=_DIM))  #296 (line in Coconut source)
                        reasons = item.get("reasons") or []  #297 (line in Coconut source)
                        if reasons:  #298 (line in Coconut source)
                            node.add(Text("reasons: " + ", ".join(reasons), style=_DIM))  #299 (line in Coconut source)
            else:  #300 (line in Coconut source)
                console.print("{_coconut_format_0}{_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(label)))  #301 (line in Coconut source)

# ── tool_call ────────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #304 (line in Coconut source)
        if _coconut_case_match_to_1 == "tool_call":  #304 (line in Coconut source)
            _coconut_case_match_check_1 = True  #304 (line in Coconut source)
        if _coconut_case_match_check_1:  #304 (line in Coconut source)
            inp = p.get("input", {})  #305 (line in Coconut source)
            ref = p.get("callable_ref", "")  #306 (line in Coconut source)
            label = Text()  #307 (line in Coconut source)
            label.append("  TOOL CALL  ", style=_TOOL_COLOR)  #308 (line in Coconut source)
            label.append(event.node_name, style="bold yellow")  #309 (line in Coconut source)
            if ref:  #310 (line in Coconut source)
                label.append("  [{_coconut_format_0}]".format(_coconut_format_0=(ref)), style=_DIM)  #311 (line in Coconut source)

            node = tree.add(label) if tree else None  #313 (line in Coconut source)

# Input panel
            inp_widget = _json_panel(inp, "input", "yellow", verbose)  #316 (line in Coconut source)
            if node:  #317 (line in Coconut source)
                node.add(inp_widget)  #318 (line in Coconut source)
            else:  #319 (line in Coconut source)
                console.print(inp_widget)  #320 (line in Coconut source)

# Children (tool_result)
            for child in children.get(event.event_id, []):  #323 (line in Coconut source)
                _render_event(console, child, children, verbose, depth=depth, tree=node or tree)  #324 (line in Coconut source)

# ── tool_result ─────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #327 (line in Coconut source)
        if _coconut_case_match_to_1 == "tool_result":  #327 (line in Coconut source)
            _coconut_case_match_check_1 = True  #327 (line in Coconut source)
        if _coconut_case_match_check_1:  #327 (line in Coconut source)
            success = p.get("success", True)  #328 (line in Coconut source)
            summary = p.get("output_summary", "")  #329 (line in Coconut source)
            ms = _fmt_ms(event.duration_ms)  #330 (line in Coconut source)
            color = _RESULT_OK if success else _RESULT_ERR  #331 (line in Coconut source)
            status = "ok" if success else "ERROR"  #332 (line in Coconut source)

            label = Text()  #334 (line in Coconut source)
            label.append("  TOOL RESULT  ", style=color)  #335 (line in Coconut source)
            label.append(event.node_name, style="bold")  #336 (line in Coconut source)
            label.append("  {_coconut_format_0}  ".format(_coconut_format_0=(status)), style=color)  #337 (line in Coconut source)
            if ms:  #338 (line in Coconut source)
                label.append("  {_coconut_format_0}".format(_coconut_format_0=(ms)), style=_DIM)  #339 (line in Coconut source)

            node = tree.add(label) if tree else None  #341 (line in Coconut source)

# Output preview
            out_text = Text(_truncate(summary, 200) if not verbose else summary, style=_DIM)  #344 (line in Coconut source)
            if node:  #345 (line in Coconut source)
                node.add(out_text)  #346 (line in Coconut source)
            elif verbose:  #347 (line in Coconut source)
                console.print(out_text)  #348 (line in Coconut source)

# ── agent_end ────────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #351 (line in Coconut source)
        if _coconut_case_match_to_1 == "agent_end":  #351 (line in Coconut source)
            _coconut_case_match_check_1 = True  #351 (line in Coconut source)
        if _coconut_case_match_check_1:  #351 (line in Coconut source)
            summary = p.get("text_summary", "")  #352 (line in Coconut source)
            intent = p.get("intent", "default")  #353 (line in Coconut source)
            iters = p.get("iterations", 1)  #354 (line in Coconut source)
            ms = _fmt_ms(event.duration_ms)  #355 (line in Coconut source)

            label = Text()  #357 (line in Coconut source)
            label.append("  AGENT END  ", style=_AGENT_COLOR)  #358 (line in Coconut source)
            label.append("intent=".format(), style=_DIM)  #359 (line in Coconut source)
            label.append(intent, style="bold magenta")  #360 (line in Coconut source)
            if iters > 1:  #361 (line in Coconut source)
                label.append("  iters={_coconut_format_0}".format(_coconut_format_0=(iters)), style=_DIM)  #362 (line in Coconut source)
            if ms:  #363 (line in Coconut source)
                label.append("  {_coconut_format_0}".format(_coconut_format_0=(ms)), style=_DIM)  #364 (line in Coconut source)

            node = tree.add(label) if tree else None  #366 (line in Coconut source)

            if summary:  #368 (line in Coconut source)
                out_text = Text('  "{_coconut_format_0}"'.format(_coconut_format_0=(_truncate(summary, 300 if verbose else 100))), style=_DIM)  #369 (line in Coconut source)
                if node:  #370 (line in Coconut source)
                    node.add(out_text)  #371 (line in Coconut source)
                else:  #372 (line in Coconut source)
                    console.print(out_text)  #373 (line in Coconut source)

# ── routing ──────────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #376 (line in Coconut source)
        if _coconut_case_match_to_1 == "routing":  #376 (line in Coconut source)
            _coconut_case_match_check_1 = True  #376 (line in Coconut source)
        if _coconut_case_match_check_1:  #376 (line in Coconut source)
            intent = p.get("intent", "default")  #377 (line in Coconut source)
            next_id = p.get("next_node_id") or "__END__"  #378 (line in Coconut source)
            conf = p.get("confidence")  #379 (line in Coconut source)

            label = Text()  #381 (line in Coconut source)
            label.append("  ROUTING  ", style=_ROUTING_COLOR)  #382 (line in Coconut source)
            label.append(intent, style="bold magenta")  #383 (line in Coconut source)
            label.append(" → ", style=_DIM)  #384 (line in Coconut source)
            label.append(next_id, style="cyan")  #385 (line in Coconut source)
            if conf is not None:  #386 (line in Coconut source)
                conf_style = _RESULT_ERR if conf < 0.7 else _DIM  #387 (line in Coconut source)
                label.append("  conf={_coconut_format_0:.0%}".format(_coconut_format_0=(conf)), style=conf_style)  #388 (line in Coconut source)

            if tree:  #390 (line in Coconut source)
                tree.add(label)  #391 (line in Coconut source)
            else:  #392 (line in Coconut source)
                console.print("{_coconut_format_0}{_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(label)))  #393 (line in Coconut source)

# ── subgraph_enter ───────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #396 (line in Coconut source)
        if _coconut_case_match_to_1 == "subgraph_enter":  #396 (line in Coconut source)
            _coconut_case_match_check_1 = True  #396 (line in Coconut source)
        if _coconut_case_match_check_1:  #396 (line in Coconut source)
            label = Text()  #397 (line in Coconut source)
            label.append("  SUBGRAPH ↓  ", style="bold blue")  #398 (line in Coconut source)
            label.append(event.node_name)  #399 (line in Coconut source)
            label.append("  entry={_coconut_format_0}".format(_coconut_format_0=(p.get('entry_node_id', '')[:8])), style=_DIM)  #400 (line in Coconut source)
            node = tree.add(label) if tree else None  #401 (line in Coconut source)
            for child in children.get(event.event_id, []):  #402 (line in Coconut source)
                _render_event(console, child, children, verbose, depth=depth, tree=node or tree)  #403 (line in Coconut source)

# ── subgraph_exit ────────────────────────────────────────────────────
    if not _coconut_case_match_check_1:  #406 (line in Coconut source)
        if _coconut_case_match_to_1 == "subgraph_exit":  #406 (line in Coconut source)
            _coconut_case_match_check_1 = True  #406 (line in Coconut source)
        if _coconut_case_match_check_1:  #406 (line in Coconut source)
            label = Text()  #407 (line in Coconut source)
            label.append("  SUBGRAPH ↑  ", style="bold blue")  #408 (line in Coconut source)
            label.append(event.node_name)  #409 (line in Coconut source)
            label.append("  {_coconut_format_0}".format(_coconut_format_0=(_fmt_ms(event.duration_ms))), style=_DIM)  #410 (line in Coconut source)
            if tree:  #411 (line in Coconut source)
                tree.add(label)  #412 (line in Coconut source)
            else:  #413 (line in Coconut source)
                console.print("{_coconut_format_0}{_coconut_format_1}".format(_coconut_format_0=(pad), _coconut_format_1=(label)))  #414 (line in Coconut source)


# ---------------------------------------------------------------------------
# Summary panel
# ---------------------------------------------------------------------------


def _render_summary(console: Console, events: list[TraceEvent], hop_count: int,) -> None:  #421 (line in Coconut source)
    agent_ends = [e for e in events if e.event_type == "agent_end"]  #426 (line in Coconut source)
    tool_calls = [e for e in events if e.event_type == "tool_call"]  #427 (line in Coconut source)
    tool_results = [e for e in events if e.event_type == "tool_result"]  #428 (line in Coconut source)
    ctx_injects = [e for e in events if e.event_type == "context_inject"]  #429 (line in Coconut source)
    routings = [e for e in events if e.event_type == "routing"]  #430 (line in Coconut source)

    total_ms = sum((e.duration_ms for e in agent_ends if e.duration_ms is not None))  #432 (line in Coconut source)
    tool_errors = sum((1 for e in tool_results if not e.payload.get("success", True)))  #433 (line in Coconut source)
    ctx_nodes = sum((e.payload.get("count", 0) for e in ctx_injects))  #434 (line in Coconut source)
    low_conf = [e for e in routings if e.payload.get("confidence") is not None and e.payload["confidence"] < 0.7]  #435 (line in Coconut source)

# Stats table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))  #441 (line in Coconut source)
    table.add_column(style="dim")  #442 (line in Coconut source)
    table.add_column(style="bold")  #443 (line in Coconut source)

    table.add_row("Hops", str(hop_count))  #445 (line in Coconut source)
    table.add_row("Agent calls", str(len(agent_ends)))  #446 (line in Coconut source)
    table.add_row("Tool calls", str(len(tool_calls)))  #447 (line in Coconut source)
    table.add_row("Tool errors", "[red]{_coconut_format_0}[/red]".format(_coconut_format_0=(tool_errors)) if tool_errors else "0")  #448 (line in Coconut source)
    table.add_row("Context nodes", str(ctx_nodes))  #449 (line in Coconut source)
    table.add_row("Routing steps", str(len(routings)))  #450 (line in Coconut source)
    if low_conf:  #451 (line in Coconut source)
        table.add_row("Low-conf routes", "[yellow]{_coconut_format_0}[/yellow]".format(_coconut_format_0=(len(low_conf))))  #452 (line in Coconut source)
    if total_ms:  #456 (line in Coconut source)
        table.add_row("Total agent time", "{_coconut_format_0}ms".format(_coconut_format_0=(total_ms)) if total_ms < 1000 else "{_coconut_format_0:.1f}s".format(_coconut_format_0=(total_ms / 1000)))  #457 (line in Coconut source)

# Agents used
    agents_seen: list[str] = []  #463 (line in Coconut source)
    seen_ids: set[str] = set()  #464 (line in Coconut source)
    for e in events:  #465 (line in Coconut source)
        if e.event_type == "agent_start" and e.node_id not in seen_ids:  #466 (line in Coconut source)
            agents_seen.append(e.node_name or e.node_id[:8])  #467 (line in Coconut source)
            seen_ids.add(e.node_id)  #468 (line in Coconut source)
    if agents_seen:  #469 (line in Coconut source)
        table.add_row("Agents", ", ".join(agents_seen))  #470 (line in Coconut source)

# Tools used
    tools_seen = list(dict.fromkeys((e.node_name for e in tool_calls)))  #473 (line in Coconut source)
    if tools_seen:  #474 (line in Coconut source)
        table.add_row("Tools used", ", ".join(tools_seen))  #475 (line in Coconut source)

    console.rule(style="dim")  #477 (line in Coconut source)
    console.print(Panel(table, title="[bold]Execution Summary[/bold]", border_style="dim", expand=False))  #478 (line in Coconut source)
