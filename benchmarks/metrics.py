"""Benchmark result types and reporting utilities."""

from __future__ import annotations

import csv
import io
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RunMetrics:
    """All measurements for one (system, task) run."""

    # Identity
    system: str          # "graph-agent" | "baseline-single" | "baseline-multi"
    task_id: str
    task_name: str

    # Timing
    wall_ms: float       # total wall-clock time (ms)

    # Depth / breadth of LLM usage
    agent_calls: int     # how many distinct LLM agents were invoked
    num_turns: int       # total LLM message turns across all agents
    tool_calls: int      # total tool invocations

    # Context load (proxy for token efficiency)
    system_prompt_chars: int   # total chars across all system prompts injected
    output_chars: int          # total chars in final answer

    # Graph-agent–specific (None for baselines)
    hops: int | None = None
    context_nodes_injected: int | None = None   # distinct ContextNodes used
    tools_composed: int | None = None           # tools discovered via graph edges

    # Cost (populated from CLI JSON output when available)
    cost_usd: float | None = None

    # Quality
    passed_eval: bool = False
    error: str | None = None

    # Raw output (not printed in table, used for eval)
    output: str = field(default="", repr=False)


# ---------------------------------------------------------------------------
# Table formatting
# ---------------------------------------------------------------------------

_COL_WIDTHS = {
    "system":               24,
    "wall_ms":              10,
    "agent_calls":           6,
    "num_turns":             6,
    "tool_calls":            6,
    "system_prompt_chars":  10,
    "output_chars":          8,
    "hops":                  5,
    "ctx_nodes":             5,
    "cost_usd":              9,
    "eval":                  5,
}

_HEADERS = [
    ("system",              "System"),
    ("wall_ms",             "Wall(ms)"),
    ("agent_calls",         "Agents"),
    ("num_turns",           "Turns"),
    ("tool_calls",          "Tools"),
    ("system_prompt_chars", "SysPrompt"),
    ("output_chars",        "OutChars"),
    ("hops",                "Hops"),
    ("ctx_nodes",           "CtxN"),
    ("cost_usd",            "Cost$"),
    ("eval",                "Pass"),
]


def _fmt_row(m: RunMetrics) -> dict[str, str]:
    return {
        "system":              m.system,
        "wall_ms":             f"{m.wall_ms:.0f}",
        "agent_calls":         str(m.agent_calls),
        "num_turns":           str(m.num_turns),
        "tool_calls":          str(m.tool_calls),
        "system_prompt_chars": str(m.system_prompt_chars),
        "output_chars":        str(m.output_chars),
        "hops":                str(m.hops) if m.hops is not None else "-",
        "ctx_nodes":           str(m.context_nodes_injected) if m.context_nodes_injected is not None else "-",
        "cost_usd":            f"${m.cost_usd:.4f}" if m.cost_usd is not None else "-",
        "eval":                "yes" if m.passed_eval else "NO",
    }


def print_table(results: list[RunMetrics], task_name: str) -> None:
    """Print a fixed-width comparison table for one task's results."""
    sep_char = "─"

    header_row = {k: label for k, label in _HEADERS}
    rows = [_fmt_row(m) for m in results]

    # Compute column widths from data
    widths: dict[str, int] = {}
    for key, label in _HEADERS:
        widths[key] = max(len(label), max((len(r[key]) for r in rows), default=0))

    def _bar(left: str, mid: str, right: str, fill: str = sep_char) -> str:
        parts = [fill * (widths[k] + 2) for k, _ in _HEADERS]
        return left + mid.join(parts) + right

    def _row(cells: dict[str, str]) -> str:
        parts = [f" {cells[k]:<{widths[k]}} " for k, _ in _HEADERS]
        return "│" + "│".join(parts) + "│"

    print(f"\nTask: {task_name}")
    print(_bar("┌", "┬", "┐"))
    print(_row(header_row))
    print(_bar("├", "┼", "┤"))
    for r in rows:
        err = results[rows.index(r)].error
        print(_row(r))
        if err:
            print(f"│  ⚠ error: {err[:80]}")
    print(_bar("└", "┴", "┘"))


def print_summary(all_results: list[RunMetrics]) -> None:
    """Print per-system averages across all tasks."""
    from collections import defaultdict

    by_system: dict[str, list[RunMetrics]] = defaultdict(list)
    for r in all_results:
        if r.error is None:
            by_system[r.system].append(r)

    print("\n=== Summary (averages across all tasks, excluding errors) ===")
    fmt = "{:<26} {:>10} {:>8} {:>8} {:>12} {:>8}"
    print(fmt.format("System", "Wall(ms)", "Turns", "Tools", "SysPrompt", "Pass%"))
    print("-" * 76)
    for system, ms in sorted(by_system.items()):
        n = len(ms)
        print(fmt.format(
            system,
            f"{sum(m.wall_ms for m in ms) / n:.0f}",
            f"{sum(m.num_turns for m in ms) / n:.1f}",
            f"{sum(m.tool_calls for m in ms) / n:.1f}",
            f"{sum(m.system_prompt_chars for m in ms) / n:.0f}",
            f"{100 * sum(m.passed_eval for m in ms) / n:.0f}%",
        ))


def save_csv(all_results: list[RunMetrics], path: str) -> None:
    """Write all results to a CSV file."""
    if not all_results:
        return
    fieldnames = list(asdict(all_results[0]).keys())
    fieldnames.remove("output")  # skip raw output

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row = asdict(r)
            del row["output"]
            writer.writerow(row)

    print(f"\nResults saved to {path}")
