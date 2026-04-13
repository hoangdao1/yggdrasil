"""Claude Code SDK baselines — same auth path as ClaudeCodeExecutor.

Uses claude_agent_sdk.query() directly (no graph overhead) to implement:

  single_agent  — one SDK query with full context in system prompt
  multi_agent   — N sequential SDK queries, one per AgentRole, passing
                  previous output as context (hand-rolled pipeline)

Metrics extracted from SDK message stream:
  - wall_ms        : wall-clock time
  - num_turns      : from ResultMessage.num_turns
  - cost_usd       : from ResultMessage.total_cost_usd
  - tool_calls     : count of ToolUseBlock across AssistantMessages
  - system_prompt_chars: system prompt size injected

Usage (standalone):
    python -m benchmarks.baseline
"""

from __future__ import annotations

import asyncio
import shutil
import time
from dataclasses import dataclass
from typing import Any

from benchmarks.metrics import RunMetrics
from benchmarks.tasks import BenchmarkTask

_DEFAULT_MODEL = "claude-sonnet-4-6"
_MAX_TURNS     = 8   # conservative cap to avoid burning quota


# ---------------------------------------------------------------------------
# Low-level SDK query
# ---------------------------------------------------------------------------

@dataclass
class _SDKResult:
    text: str
    num_turns: int
    tool_calls: int
    cost_usd: float | None
    wall_ms: float
    error: str | None


async def _sdk_query(
    prompt:        str,
    system_prompt: str,
    allowed_tools: list[str],
    model:         str,
    cwd:           str | None,
    max_turns:     int = _MAX_TURNS,
) -> _SDKResult:
    """Run one headless Claude Code agent call via the SDK.

    Extracts turn count, tool calls, and cost from the message stream.
    """
    try:
        from claude_agent_sdk import (           # type: ignore[import]
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            query as cc_query,
        )
        try:
            from claude_agent_sdk import ToolUseBlock  # type: ignore[import]
        except ImportError:
            ToolUseBlock = None  # type: ignore[assignment]
    except ImportError:
        return _SDKResult(
            text="", num_turns=0, tool_calls=0, cost_usd=None,
            wall_ms=0, error="claude_agent_sdk not installed",
        )

    cli = shutil.which("claude")
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=allowed_tools or [],
        max_turns=max_turns,
        model=model,
        permission_mode="acceptEdits",
        cwd=cwd,
        env={"ANTHROPIC_API_KEY": ""},
        **({"cli_path": cli} if cli else {}),
    )

    tool_call_count = 0
    result_text     = ""
    num_turns       = 0
    cost_usd        = None
    error           = None

    t0 = time.perf_counter()
    try:
        async for msg in cc_query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if ToolUseBlock and isinstance(block, ToolUseBlock):
                        tool_call_count += 1
            elif isinstance(msg, ResultMessage):
                result_text = msg.result or ""
                num_turns   = getattr(msg, "num_turns", 0) or 0
                cost_usd    = getattr(msg, "total_cost_usd", None)
                if getattr(msg, "is_error", False):
                    subtype = getattr(msg, "subtype", "unknown")
                    if subtype == "error_max_turns":
                        # Treat as partial success — we have intermediate output
                        pass
                    else:
                        error = f"sdk error ({subtype}): {result_text[:200]}"
    except Exception as exc:
        error = str(exc)[:300]
    wall_ms = (time.perf_counter() - t0) * 1000

    return _SDKResult(
        text=result_text,
        num_turns=num_turns,
        tool_calls=tool_call_count,
        cost_usd=cost_usd,
        wall_ms=wall_ms,
        error=error,
    )


# ---------------------------------------------------------------------------
# Single-agent baseline
# ---------------------------------------------------------------------------

async def run_baseline_single(
    task:  BenchmarkTask,
    model: str = _DEFAULT_MODEL,
    cwd:   str | None = None,
) -> RunMetrics:
    """One SDK agent call. All pipeline roles collapsed into a single system prompt.

    This is the naive baseline: no multi-agent routing, no graph composition —
    the developer writes one system prompt that covers the entire pipeline.
    """
    all_tools = list({t for role in task.agent_roles for t in role.tools})
    # Add the same base tools graph-agent uses
    base = ["Read", "Glob", "Grep", "Bash", "WebSearch"]
    allowed_tools = list(dict.fromkeys(all_tools + base))

    r = await _sdk_query(
        prompt=task.query,
        system_prompt=task.single_agent_system,
        allowed_tools=allowed_tools,
        model=model,
        cwd=cwd,
    )

    passed = False
    if not r.error:
        try:
            passed = task.eval_fn(r.text)
        except Exception:
            pass

    return RunMetrics(
        system="baseline-single",
        task_id=task.id,
        task_name=task.name,
        wall_ms=r.wall_ms,
        agent_calls=1,
        num_turns=r.num_turns or 1,
        tool_calls=r.tool_calls,
        system_prompt_chars=len(task.single_agent_system),
        output_chars=len(r.text),
        cost_usd=r.cost_usd,
        passed_eval=passed,
        error=r.error,
        output=r.text,
    )


# ---------------------------------------------------------------------------
# Multi-agent baseline
# ---------------------------------------------------------------------------

async def run_baseline_multi(
    task:  BenchmarkTask,
    model: str = _DEFAULT_MODEL,
    cwd:   str | None = None,
) -> RunMetrics:
    """Sequential SDK calls — one per AgentRole.

    Mimics a hand-rolled multi-agent pipeline: each agent gets the previous
    agent's output prepended to its prompt. No routing table, no graph.
    """
    if not task.agent_roles:
        return RunMetrics(
            system="baseline-multi",
            task_id=task.id,
            task_name=task.name,
            wall_ms=0,
            agent_calls=0,
            num_turns=0,
            tool_calls=0,
            system_prompt_chars=0,
            output_chars=0,
            error="no agent roles defined",
        )

    base = ["Read", "Glob", "Grep", "Bash", "WebSearch"]
    total_wall_ms   = 0.0
    total_turns     = 0
    total_tools     = 0
    total_sysprompt = 0
    total_cost      = 0.0
    previous_output = ""
    final_output    = ""
    first_error: str | None = None

    for i, role in enumerate(task.agent_roles):
        prompt = (
            task.query
            if i == 0
            else (
                f"Previous agent output:\n{previous_output}\n\n"
                f"Original task: {task.query}\n\n"
                "Continue from where the previous agent left off."
            )
        )
        allowed_tools = list(dict.fromkeys(role.tools + base))

        r = await _sdk_query(
            prompt=prompt,
            system_prompt=role.system_prompt,
            allowed_tools=allowed_tools,
            model=model,
            cwd=cwd,
        )

        total_wall_ms   += r.wall_ms
        total_turns     += r.num_turns or 1
        total_tools     += r.tool_calls
        total_sysprompt += len(role.system_prompt)
        if r.cost_usd is not None:
            total_cost += r.cost_usd
        previous_output  = r.text
        final_output     = r.text

        if r.error and first_error is None:
            first_error = f"agent {i+1} ({role.name}): {r.error}"

    passed = False
    if not first_error:
        try:
            passed = task.eval_fn(final_output)
        except Exception:
            pass

    return RunMetrics(
        system="baseline-multi",
        task_id=task.id,
        task_name=task.name,
        wall_ms=total_wall_ms,
        agent_calls=len(task.agent_roles),
        num_turns=total_turns,
        tool_calls=total_tools,
        system_prompt_chars=total_sysprompt,
        output_chars=len(final_output),
        cost_usd=total_cost if total_cost > 0 else None,
        passed_eval=passed,
        error=first_error,
        output=final_output,
    )


# ---------------------------------------------------------------------------
# Standalone smoke test
# ---------------------------------------------------------------------------

async def _smoke_test() -> None:
    from benchmarks.tasks import SIMPLE_QA_TASK
    print("Running single-agent baseline (simple Q&A)...")
    m = await run_baseline_single(SIMPLE_QA_TASK)
    print(f"  wall_ms={m.wall_ms:.0f}  turns={m.num_turns}  tools={m.tool_calls}  passed={m.passed_eval}")
    if m.cost_usd is not None:
        print(f"  cost_usd={m.cost_usd:.4f}")
    print(f"  output[:300]: {m.output[:300]}")
    if m.error:
        print(f"  error: {m.error}")


if __name__ == "__main__":
    asyncio.run(_smoke_test())
