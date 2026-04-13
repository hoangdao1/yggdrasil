"""Terminal display layer for yggdrasil execution traces.

This is the canonical home for functions that render a trace to a terminal.
They have side effects (print to stdout) and return None.

Canonical imports:
    from yggdrasil.trace_ui import inspect_trace  # Rich tree UI
    from yggdrasil.trace_ui import print_trace    # plain-text fallback

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
    from yggdrasil.trace_ui import inspect_trace

    ctx = await executor.run(entry_node_id, query)
    inspect_trace(ctx)

    # Compact mode (no context/output previews)
    inspect_trace(ctx, verbose=False)

    # Write to file
    inspect_trace(ctx, file="trace.html", format="html")
    inspect_trace(ctx, file="trace.txt",  format="text")

    # CI / plain-text fallback
    from yggdrasil.trace_ui import print_trace
    print_trace(ctx)
"""

from __future__ import annotations

import json
import sys
from typing import IO, Any, Literal

from yggdrasil.core.executor import ExecutionContext, TraceEvent, print_trace  # noqa: F401

__all__ = ["inspect_trace", "print_trace"]

try:
    from rich import box
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree
    _RICH = True
except ImportError:
    _RICH = False


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def inspect_trace(
    ctx:     ExecutionContext | list[TraceEvent],
    *,
    verbose: bool = True,
    file:    str | None = None,
    format:  Literal["terminal", "html", "text"] = "terminal",
) -> None:
    """Render the execution trace as a rich terminal UI.

    Args:
        ctx:     ExecutionContext or raw list[TraceEvent].
        verbose: When True (default), shows full context content and complete
                 tool inputs/outputs. When False, truncates to one-liners.
        file:    Optional path to write output. Supports .html and .txt.
        format:  "terminal" (default), "html", or "text".
    """
    if not _RICH:
        print_trace(ctx)
        return

    if isinstance(ctx, ExecutionContext):
        events    = ctx.trace
        session_id = ctx.session_id
        query     = ctx.query
        hop_count = ctx.hop_count
    else:
        events    = ctx
        session_id = events[0].session_id if events else "?"
        query     = ""
        hop_count = sum(1 for e in events if e.event_type == "hop")

    # Build console for chosen output destination
    if file:
        _fmt = format
        with open(file, "w", encoding="utf-8") as fh:
            if _fmt == "html":
                console = Console(file=fh, record=True, force_terminal=False, width=120)
            else:
                console = Console(file=fh, force_terminal=False, no_color=True, width=120)
            _render_session(console, events, session_id, query, hop_count, verbose)
            if _fmt == "html":
                fh.write(console.export_html())
        print(f"Trace written to {file}", file=sys.stderr)
        return
    else:
        console = Console(highlight=True)

    _render_session(console, events, session_id, query, hop_count, verbose)


# ---------------------------------------------------------------------------
# Session renderer
# ---------------------------------------------------------------------------

_AGENT_COLOR   = "bold cyan"
_TOOL_COLOR    = "bold yellow"
_RESULT_OK     = "green"
_RESULT_ERR    = "bold red"
_ROUTING_COLOR = "magenta"
_CTX_COLOR     = "blue"
_DIM           = "dim"
_HOP_COLOR     = "bold white"


def _render_session(
    console:    Console,
    events:     list[TraceEvent],
    session_id: str,
    query:      str,
    hop_count:  int,
    verbose:    bool,
) -> None:
    """Top-level renderer: header → tree → summary."""

    # ── Header ──────────────────────────────────────────────────────────────
    console.print()
    console.rule(
        f"[bold]Session[/bold] [dim]{session_id[:8]}[/dim]",
        style="cyan",
    )
    if query:
        console.print(f"[dim]Query:[/dim] {query}\n")

    # ── Build parent→children index ─────────────────────────────────────────
    children: dict[str | None, list[TraceEvent]] = {}
    for e in events:
        children.setdefault(e.parent_event_id, []).append(e)

    # ── Render top-level events (hops) ───────────────────────────────────────
    for root in children.get(None, []):
        _render_event(console, root, children, verbose, depth=0)

    # ── Summary ─────────────────────────────────────────────────────────────
    _render_summary(console, events, hop_count)
    console.print()


# ---------------------------------------------------------------------------
# Event renderer (recursive)
# ---------------------------------------------------------------------------

def _fmt_ms(ms: int | None) -> str:
    """Return a plain (no markup) timing string, or empty string."""
    if ms is None:
        return ""
    return f"{ms}ms" if ms < 1000 else f"{ms/1000:.1f}s"


def _truncate(s: str, n: int) -> str:
    return s[:n] + "…" if len(s) > n else s


def _json_panel(data: dict | str, title: str, color: str, verbose: bool) -> Any:
    """Return a Syntax panel for JSON data, or a dim one-liner when not verbose."""
    raw = json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else data
    if not verbose:
        one = raw.replace("\n", " ")
        return Text(f"{title}: {_truncate(one, 80)}", style="dim")
    return Panel(
        Syntax(raw, "json", theme="monokai", word_wrap=True),
        title=title,
        border_style=color,
        expand=False,
        padding=(0, 1),
    )


def _render_event(
    console:  Console,
    event:    TraceEvent,
    children: dict[str | None, list[TraceEvent]],
    verbose:  bool,
    depth:    int,
    tree:     Tree | None = None,
) -> None:
    """Recursively render one event, attaching children to a rich Tree node."""
    t = event.event_type
    p = event.payload
    pad = "  " * depth

    # ── hop ─────────────────────────────────────────────────────────────────
    if t == "hop":
        node_type = p.get("node_type", "").split(".")[-1].upper()
        hop_num   = p.get("hop", "")
        label     = Text()
        label.append(f"HOP {hop_num}  ", style=_HOP_COLOR)
        label.append(f"{node_type}  ", style=_DIM)
        label.append(event.node_name, style=_AGENT_COLOR)
        ms = _fmt_ms(event.duration_ms)
        if ms:
            label.append(f"  {ms}", style=_DIM)

        branch = Tree(label)
        for child in children.get(event.event_id, []):
            _render_event(console, child, children, verbose, depth=0, tree=branch)

        if tree:
            tree.add(branch)
        else:
            console.print(branch)
            console.print()

    # ── agent_start ─────────────────────────────────────────────────────────
    elif t == "agent_start":
        model  = p.get("model", "?")
        tools  = p.get("tools", [])
        ctx_l  = p.get("context", [])
        ctx_scores = p.get("context_scores", [])

        # Header row
        header = Text()
        header.append("AGENT  ", style=_AGENT_COLOR)
        header.append(event.node_name, style="bold")
        header.append(f"  [{model}]", style=_DIM)
        node = tree.add(header) if tree else None

        # Tools row
        if tools:
            tool_text = Text()
            tool_text.append("  tools  ", style=_DIM)
            tool_text.append(", ".join(tools), style=_TOOL_COLOR)
            if node:
                node.add(tool_text)
            else:
                console.print(f"{pad}  {tool_text}")
        else:
            dim = Text("  tools  none", style=_DIM)
            if node:
                node.add(dim)

        # Context row
        if ctx_l:
            ctx_text = Text()
            ctx_text.append("  context  ", style=_DIM)
            ctx_text.append(", ".join(ctx_l), style=_CTX_COLOR)
            if node:
                node.add(ctx_text)
        if node and verbose and ctx_scores:
            rows = []
            for item in ctx_scores:
                rows.append(
                    f"{item.get('name')}: score={item.get('score')} "
                    f"source={item.get('source')} hops={item.get('hops')}"
                )
            node.add(Text("  ranked  " + " | ".join(rows), style=_DIM))

        # Children (context_inject, tool_call, agent_end, routing)
        for child in children.get(event.event_id, []):
            _render_event(console, child, children, verbose, depth=depth, tree=node or tree)

    # ── context_inject ──────────────────────────────────────────────────────
    elif t == "context_inject":
        names = p.get("context_names", [])
        count = p.get("count", 0)
        selected = p.get("selected_contexts", [])
        label = Text()
        label.append("  CONTEXT  ", style=_CTX_COLOR)
        label.append(f"{count} node{'s' if count != 1 else ''}  ", style=_DIM)
        label.append(", ".join(names), style=_CTX_COLOR)
        if tree:
            node = tree.add(label)
            if verbose and selected:
                for item in selected:
                    details = (
                        f"{item.get('name')}  score={item.get('score')}  "
                        f"source={item.get('source')}  hops={item.get('hops')}  "
                        f"tokens={item.get('token_count')}"
                    )
                    node.add(Text(details, style=_DIM))
                    reasons = item.get("reasons") or []
                    if reasons:
                        node.add(Text("reasons: " + ", ".join(reasons), style=_DIM))
        else:
            console.print(f"{pad}{label}")

    # ── tool_call ────────────────────────────────────────────────────────────
    elif t == "tool_call":
        inp       = p.get("input", {})
        ref       = p.get("callable_ref", "")
        label     = Text()
        label.append("  TOOL CALL  ", style=_TOOL_COLOR)
        label.append(event.node_name, style="bold yellow")
        if ref:
            label.append(f"  [{ref}]", style=_DIM)

        node = tree.add(label) if tree else None

        # Input panel
        inp_widget = _json_panel(inp, "input", "yellow", verbose)
        if node:
            node.add(inp_widget)
        else:
            console.print(inp_widget)

        # Children (tool_result)
        for child in children.get(event.event_id, []):
            _render_event(console, child, children, verbose, depth=depth, tree=node or tree)

    # ── tool_result ─────────────────────────────────────────────────────────
    elif t == "tool_result":
        success = p.get("success", True)
        summary = p.get("output_summary", "")
        ms      = _fmt_ms(event.duration_ms)
        color   = _RESULT_OK if success else _RESULT_ERR
        status  = "ok" if success else "ERROR"

        label = Text()
        label.append("  TOOL RESULT  ", style=color)
        label.append(event.node_name, style="bold")
        label.append(f"  {status}  ", style=color)
        if ms:
            label.append(f"  {ms}", style=_DIM)

        node = tree.add(label) if tree else None

        # Output preview
        out_text = Text(_truncate(summary, 200) if not verbose else summary, style=_DIM)
        if node:
            node.add(out_text)
        elif verbose:
            console.print(out_text)

    # ── agent_end ────────────────────────────────────────────────────────────
    elif t == "agent_end":
        summary = p.get("text_summary", "")
        intent  = p.get("intent", "default")
        iters   = p.get("iterations", 1)
        ms      = _fmt_ms(event.duration_ms)

        label = Text()
        label.append("  AGENT END  ", style=_AGENT_COLOR)
        label.append(f"intent=", style=_DIM)
        label.append(intent, style="bold magenta")
        if iters > 1:
            label.append(f"  iters={iters}", style=_DIM)
        if ms:
            label.append(f"  {ms}", style=_DIM)

        node = tree.add(label) if tree else None

        if summary:
            out_text = Text(f'  "{_truncate(summary, 300 if verbose else 100)}"', style=_DIM)
            if node:
                node.add(out_text)
            else:
                console.print(out_text)

    # ── routing ──────────────────────────────────────────────────────────────
    elif t == "routing":
        intent   = p.get("intent", "default")
        next_id  = p.get("next_node_id") or "__END__"
        conf     = p.get("confidence")

        label = Text()
        label.append("  ROUTING  ", style=_ROUTING_COLOR)
        label.append(intent, style="bold magenta")
        label.append(" → ", style=_DIM)
        label.append(next_id, style="cyan")
        if conf is not None:
            conf_style = _RESULT_ERR if conf < 0.7 else _DIM
            label.append(f"  conf={conf:.0%}", style=conf_style)

        if tree:
            tree.add(label)
        else:
            console.print(f"{pad}{label}")

    # ── subgraph_enter / subgraph_exit ───────────────────────────────────────
    elif t == "subgraph_enter":
        label = Text()
        label.append("  SUBGRAPH ↓  ", style="bold blue")
        label.append(event.node_name)
        label.append(f"  entry={p.get('entry_node_id', '')[:8]}", style=_DIM)
        node = tree.add(label) if tree else None
        for child in children.get(event.event_id, []):
            _render_event(console, child, children, verbose, depth=depth, tree=node or tree)

    elif t == "subgraph_exit":
        label = Text()
        label.append("  SUBGRAPH ↑  ", style="bold blue")
        label.append(event.node_name)
        label.append(f"  {_fmt_ms(event.duration_ms)}", style=_DIM)
        if tree:
            tree.add(label)
        else:
            console.print(f"{pad}{label}")


# ---------------------------------------------------------------------------
# Summary panel
# ---------------------------------------------------------------------------

def _render_summary(
    console:   Console,
    events:    list[TraceEvent],
    hop_count: int,
) -> None:
    agent_ends   = [e for e in events if e.event_type == "agent_end"]
    tool_calls   = [e for e in events if e.event_type == "tool_call"]
    tool_results = [e for e in events if e.event_type == "tool_result"]
    ctx_injects  = [e for e in events if e.event_type == "context_inject"]
    routings     = [e for e in events if e.event_type == "routing"]

    total_ms = sum(
        e.duration_ms for e in agent_ends if e.duration_ms is not None
    )
    tool_errors  = sum(1 for e in tool_results if not e.payload.get("success", True))
    ctx_nodes    = sum(e.payload.get("count", 0) for e in ctx_injects)
    low_conf     = [
        e for e in routings
        if e.payload.get("confidence") is not None and e.payload["confidence"] < 0.7
    ]

    # Stats table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column(style="bold")

    table.add_row("Hops",            str(hop_count))
    table.add_row("Agent calls",     str(len(agent_ends)))
    table.add_row("Tool calls",      str(len(tool_calls)))
    table.add_row("Tool errors",     f"[red]{tool_errors}[/red]" if tool_errors else "0")
    table.add_row("Context nodes",   str(ctx_nodes))
    table.add_row("Routing steps",   str(len(routings)))
    if low_conf:
        table.add_row(
            "Low-conf routes",
            f"[yellow]{len(low_conf)}[/yellow]",
        )
    if total_ms:
        table.add_row(
            "Total agent time",
            f"{total_ms}ms" if total_ms < 1000 else f"{total_ms/1000:.1f}s",
        )

    # Agents used
    agents_seen: list[str] = []
    seen_ids: set[str] = set()
    for e in events:
        if e.event_type == "agent_start" and e.node_id not in seen_ids:
            agents_seen.append(e.node_name or e.node_id[:8])
            seen_ids.add(e.node_id)
    if agents_seen:
        table.add_row("Agents", ", ".join(agents_seen))

    # Tools used
    tools_seen = list(dict.fromkeys(e.node_name for e in tool_calls))
    if tools_seen:
        table.add_row("Tools used", ", ".join(tools_seen))

    console.rule(style="dim")
    console.print(
        Panel(table, title="[bold]Execution Summary[/bold]", border_style="dim", expand=False)
    )
