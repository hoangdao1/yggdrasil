"""Main benchmark runner.

Runs each benchmark task through three systems:
  1. graph-agent          — ClaudeCodeExecutor (or AnthropicBackend fallback)
  2. baseline-single      — one `claude --print` call with full context
  3. baseline-multi       — sequential `claude --print` calls, one per agent role

Prints per-task comparison tables and a cross-task summary.

Usage:
    # Run all tasks, all systems
    python -m benchmarks.run_all

    # Run a specific task
    python -m benchmarks.run_all --task simple_qa

    # Run only specific systems (comma-separated)
    python -m benchmarks.run_all --systems graph,single

    # Save results to CSV
    python -m benchmarks.run_all --output results.csv

    # Choose model
    python -m benchmarks.run_all --model claude-haiku-4-5-20251001

    # Set working directory for file-tool tasks
    python -m benchmarks.run_all --cwd /path/to/repo

    # Run multiple repetitions and average
    python -m benchmarks.run_all --reps 3
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

from benchmarks.baseline import run_baseline_multi, run_baseline_single
from benchmarks.graph_runner import run_graph_agent
from benchmarks.metrics import RunMetrics, print_summary, print_table, save_csv
from benchmarks.tasks import ALL_TASKS, TASK_MAP, BenchmarkTask

# Default working directory for file-tool tasks is the repo root
_REPO_ROOT = str(Path(__file__).parent.parent)


# ---------------------------------------------------------------------------
# Per-run dispatcher
# ---------------------------------------------------------------------------

async def run_task(
    task: BenchmarkTask,
    systems: list[str],
    model: str,
    cwd: str,
) -> list[RunMetrics]:
    """Run one task across all requested systems. Returns one RunMetrics per system."""
    results: list[RunMetrics] = []

    # Run systems sequentially to avoid rate-limit spikes when tasks are large.
    # (Concurrent system runs on a single large task can exhaust a 5-hour quota.)
    runners: list[tuple[str, Any]] = []
    if "graph"  in systems: runners.append(("graph-agent",    run_graph_agent(task, model=model, cwd=cwd)))
    if "single" in systems: runners.append(("baseline-single", run_baseline_single(task, model=model, cwd=cwd)))
    if "multi"  in systems: runners.append(("baseline-multi",  run_baseline_multi(task, model=model, cwd=cwd)))

    for label, coro in runners:
        try:
            out = await coro
            results.append(out)
        except Exception as exc:
            results.append(RunMetrics(
                system=label,
                task_id=task.id,
                task_name=task.name,
                wall_ms=0,
                agent_calls=0,
                num_turns=0,
                tool_calls=0,
                system_prompt_chars=0,
                output_chars=0,
                error=f"uncaught exception: {exc}",
            ))

    return results


# ---------------------------------------------------------------------------
# Repetition averaging
# ---------------------------------------------------------------------------

def _average_metrics(runs: list[RunMetrics]) -> RunMetrics:
    """Average numeric fields across multiple repetitions of the same (system, task)."""
    if len(runs) == 1:
        return runs[0]

    def _avg(vals: list) -> float | None:
        non_none = [v for v in vals if v is not None]
        return sum(non_none) / len(non_none) if non_none else None

    def _avg_int(vals: list) -> int:
        non_none = [v for v in vals if v is not None]
        return round(sum(non_none) / len(non_none)) if non_none else 0

    # Use last successful run for non-numeric fields
    base = runs[-1]
    errors = [r.error for r in runs if r.error]

    return RunMetrics(
        system=base.system,
        task_id=base.task_id,
        task_name=f"{base.task_name} (avg×{len(runs)})",
        wall_ms=_avg([r.wall_ms for r in runs]) or 0.0,
        agent_calls=_avg_int([r.agent_calls for r in runs]),
        num_turns=_avg_int([r.num_turns for r in runs]),
        tool_calls=_avg_int([r.tool_calls for r in runs]),
        system_prompt_chars=_avg_int([r.system_prompt_chars for r in runs]),
        output_chars=_avg_int([r.output_chars for r in runs]),
        hops=_avg_int([r.hops for r in runs if r.hops is not None]) or None,
        context_nodes_injected=_avg_int([r.context_nodes_injected for r in runs if r.context_nodes_injected is not None]) or None,
        tools_composed=_avg_int([r.tools_composed for r in runs if r.tools_composed is not None]) or None,
        cost_usd=_avg([r.cost_usd for r in runs]),
        passed_eval=sum(r.passed_eval for r in runs) >= len(runs) // 2 + 1,
        error=errors[0] if errors else None,
        output=base.output,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(args: argparse.Namespace) -> None:
    # Resolve tasks
    if args.task:
        task_ids = [t.strip() for t in args.task.split(",")]
        tasks = []
        for tid in task_ids:
            if tid not in TASK_MAP:
                print(f"Unknown task: {tid!r}. Available: {list(TASK_MAP)}", file=sys.stderr)
                sys.exit(1)
            tasks.append(TASK_MAP[tid])
    else:
        tasks = list(ALL_TASKS)

    # Resolve systems
    valid_systems = {"graph", "single", "multi"}
    requested_systems = [s.strip() for s in args.systems.split(",")]
    for s in requested_systems:
        if s not in valid_systems:
            print(f"Unknown system: {s!r}. Choose from {valid_systems}", file=sys.stderr)
            sys.exit(1)

    print(f"Model:   {args.model}")
    print(f"Systems: {requested_systems}")
    print(f"Tasks:   {[t.id for t in tasks]}")
    print(f"Reps:    {args.reps}")
    print(f"CWD:     {args.cwd}")

    all_results: list[RunMetrics] = []

    for task in tasks:
        print(f"\n{'='*60}")
        print(f"Task: {task.name}")
        print(f"{'='*60}")

        # Collect repetitions
        rep_buckets: dict[str, list[RunMetrics]] = {}  # system → [RunMetrics]

        for rep in range(args.reps):
            if args.reps > 1:
                print(f"  Rep {rep + 1}/{args.reps}...")
            rep_results = await run_task(task, requested_systems, args.model, args.cwd)
            for m in rep_results:
                rep_buckets.setdefault(m.system, []).append(m)

        # Average across reps
        task_results = [_average_metrics(bucket) for bucket in rep_buckets.values()]
        all_results.extend(task_results)

        print_table(task_results, task.name)

    print_summary(all_results)

    if args.output:
        save_csv(all_results, args.output)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark graph-agent against headless Claude Code baselines"
    )
    parser.add_argument(
        "--task", default="",
        help="Comma-separated task IDs to run (default: all). "
             f"Available: {list(TASK_MAP)}",
    )
    parser.add_argument(
        "--systems", default="graph,single,multi",
        help="Comma-separated systems to run: graph,single,multi (default: all)",
    )
    parser.add_argument(
        "--model", default="claude-sonnet-4-6",
        help="Model name to use for all systems (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--reps", type=int, default=1,
        help="Number of repetitions per (task, system) pair; results are averaged (default: 1)",
    )
    parser.add_argument(
        "--output", default="",
        help="Optional path to write results CSV",
    )
    parser.add_argument(
        "--cwd", default=_REPO_ROOT,
        help=f"Working directory for file-tool tasks (default: {_REPO_ROOT})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(_parse_args()))
