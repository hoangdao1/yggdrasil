"""Graph-agent runner for benchmarking.

Builds a task-specific graph, executes it via ClaudeCodeExecutor, and
extracts RunMetrics from ctx.trace.

Falls back to GraphExecutor (AnthropicBackend) when the claude-agent-sdk
or Claude CLI is not available.

Usage (standalone):
    python -m benchmarks.graph_runner
"""

from __future__ import annotations

import asyncio
import os
import shutil
import time
from typing import Any

from yggdrasil_lm import AgentNode, ContextNode, Edge, NetworkXGraphStore, ToolNode
from yggdrasil_lm.core.edges import EdgeType
from yggdrasil_lm.core.executor import AgentComposer, ExecutionContext, GraphExecutor
from yggdrasil_lm.core.nodes import PromptNode
from yggdrasil_lm.tools.registry import default_registry

from benchmarks.metrics import RunMetrics
from benchmarks.tasks import BenchmarkTask


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

async def build_graph_for_task(
    task: BenchmarkTask,
    store: NetworkXGraphStore,
    model: str,
) -> str:
    """Build a graph that mirrors the task's agent_roles pipeline.

    Returns the entry agent's node_id.

    Each AgentRole becomes an AgentNode connected to the next via routing_table.
    Tool names map to ToolNode stubs (graph-agent discovers them via HAS_TOOL edges).
    """
    if not task.agent_roles:
        raise ValueError(f"Task {task.id!r} has no agent_roles")

    # Create AgentNodes and PromptNodes for every role
    agent_nodes: list[AgentNode] = []
    for i, role in enumerate(task.agent_roles):
        is_last = (i == len(task.agent_roles) - 1)
        agent = AgentNode(
            name=role.name,
            description=f"{role.name} for task: {task.id}",
            model=model,
            system_prompt=role.system_prompt,
            routing_table={"default": "__END__"} if is_last else {},
            max_iterations=6,
        )
        agent_nodes.append(agent)
        await store.upsert_node(agent)

    # Wire sequential delegation via routing_table on non-last agents
    for i, agent in enumerate(agent_nodes[:-1]):
        next_agent = agent_nodes[i + 1]
        # Update routing_table to point to the next agent
        updated = AgentNode(
            node_id=agent.node_id,
            name=agent.name,
            description=agent.description,
            model=agent.model,
            system_prompt=agent.system_prompt,
            routing_table={
                "synthesis needed": next_agent.node_id,
                "review needed":    next_agent.node_id,
                "default":          next_agent.node_id,
            },
            max_iterations=agent.max_iterations,
        )
        await store.upsert_node(updated)
        await store.upsert_edge(Edge.delegates_to(updated.node_id, next_agent.node_id))

    # Create ToolNodes for each agent's tools and attach via HAS_TOOL edges
    for i, role in enumerate(task.agent_roles):
        agent_id = agent_nodes[i].node_id
        for tool_name in role.tools:
            # Use a placeholder callable_ref — ClaudeCodeExecutor uses allowed_tools
            # (Claude Code built-ins), not Python callables registered here.
            tool = ToolNode(
                name=tool_name,
                description=f"Claude Code built-in: {tool_name}",
                callable_ref=f"claude_code.{tool_name.lower()}",
                input_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            )
            await store.upsert_node(tool)
            await store.upsert_edge(Edge.has_tool(agent_id, tool.node_id))

    return agent_nodes[0].node_id


# ---------------------------------------------------------------------------
# Metric extraction from ExecutionContext
# ---------------------------------------------------------------------------

def _extract_metrics_from_ctx(
    ctx: ExecutionContext,
    task: BenchmarkTask,
    wall_ms: float,
    system_prompt_chars: int,
    cost_usd: float | None,
    error: str | None,
    backend_label: str = "graph-agent-api",
) -> RunMetrics:
    """Convert an ExecutionContext trace into RunMetrics."""
    tool_calls   = sum(1 for e in ctx.trace if e.event_type == "tool_call")
    agent_starts = sum(1 for e in ctx.trace if e.event_type == "agent_start")
    ctx_events   = [e for e in ctx.trace if e.event_type == "context_inject"]
    ctx_nodes    = sum(e.payload.get("count", 0) for e in ctx_events)

    # Count turns: each agent_end payload may have an "iterations" field
    num_turns = sum(
        e.payload.get("iterations", 1)
        for e in ctx.trace
        if e.event_type == "agent_end"
    )
    if num_turns == 0:
        num_turns = max(agent_starts, 1)

    # Gather tool composition info from agent_start payloads
    tools_composed = max(
        (len(e.payload.get("tools", [])) for e in ctx.trace if e.event_type == "agent_start"),
        default=None,
    )

    # Accumulate cost from agent_end payloads (populated by ClaudeCodeExecutor).
    # Falls back to the caller-supplied cost_usd (populated by GraphExecutor API path).
    traced_cost: float | None = None
    for e in ctx.trace:
        if e.event_type == "agent_end":
            c = e.payload.get("cost_usd")
            if c is not None:
                traced_cost = (traced_cost or 0.0) + float(c)
    effective_cost = traced_cost if traced_cost is not None else cost_usd

    # Final output: last agent's text output
    final_output = ""
    for node_id, out in ctx.outputs.items():
        if isinstance(out, dict) and "text" in out:
            final_output = out["text"]

    passed = False
    if not error:
        try:
            passed = task.eval_fn(final_output)
        except Exception:
            pass

    return RunMetrics(
        system=backend_label,
        task_id=task.id,
        task_name=task.name,
        wall_ms=wall_ms,
        agent_calls=agent_starts or len(task.agent_roles),
        num_turns=num_turns,
        tool_calls=tool_calls,
        system_prompt_chars=system_prompt_chars,
        output_chars=len(final_output),
        hops=ctx.hop_count,
        context_nodes_injected=ctx_nodes if ctx_nodes > 0 else None,
        tools_composed=tools_composed,
        cost_usd=effective_cost,
        passed_eval=passed,
        error=error,
        output=final_output,
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_graph_agent(
    task: BenchmarkTask,
    model: str = "claude-sonnet-4-6",
    cwd: str | None = None,
    use_claude_code_backend: bool | None = None,
) -> RunMetrics:
    """Run a benchmark task through graph-agent.

    Automatically selects backend:
    - ClaudeCodeExecutor if claude CLI + claude-agent-sdk are available
    - GraphExecutor (AnthropicBackend) otherwise

    Set use_claude_code_backend=True/False to force a choice.
    """
    store = NetworkXGraphStore()

    # Determine backend
    if use_claude_code_backend is None:
        has_cli = bool(shutil.which("claude"))
        try:
            import claude_agent_sdk  # noqa: F401
            has_sdk = True
        except ImportError:
            has_sdk = False
        use_claude_code_backend = has_cli and has_sdk

    # Build executor
    if use_claude_code_backend:
        from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

        # Collect all tools declared across all roles
        all_allowed_tools = list({t for role in task.agent_roles for t in role.tools})
        # Always add basic Claude Code built-ins
        base_tools = ["Read", "Glob", "Grep", "Bash", "WebSearch"]
        allowed_tools = list(dict.fromkeys(all_allowed_tools + base_tools))

        executor = ClaudeCodeExecutor(
            store,
            allowed_tools=allowed_tools,
            permission_mode="acceptEdits",
            cwd=cwd,
            cli_path=shutil.which("claude"),
        )
        backend_label = "graph-agent-cc"
    else:
        executor = GraphExecutor(store)
        backend_label = "graph-agent-api"

    default_registry.attach(executor)

    # Build graph
    entry_node_id = await build_graph_for_task(task, store, model)

    # Measure system_prompt_chars before running (compose first agent)
    entry_node = await store.get_node(entry_node_id)
    composer = AgentComposer(store)
    composed = await composer.compose(entry_node, query=task.query)
    system_prompt = composed.build_system_prompt()
    # For multi-agent, accumulate all agents' prompts as an approximation
    total_sysprompt_chars = sum(len(r.system_prompt) for r in task.agent_roles)

    # Run
    t0 = time.perf_counter()
    error: str | None = None
    ctx: ExecutionContext | None = None
    try:
        ctx = await executor.run(
            entry_node_id=entry_node_id,
            query=task.query,
            strategy="sequential",
        )
    except Exception as exc:
        error = str(exc)[:300]
    wall_ms = (time.perf_counter() - t0) * 1000

    if ctx is None:
        return RunMetrics(
            system=backend_label,
            task_id=task.id,
            task_name=task.name,
            wall_ms=wall_ms,
            agent_calls=0,
            num_turns=0,
            tool_calls=0,
            system_prompt_chars=total_sysprompt_chars,
            output_chars=0,
            error=error,
        )

    return _extract_metrics_from_ctx(
        ctx=ctx,
        task=task,
        wall_ms=wall_ms,
        system_prompt_chars=total_sysprompt_chars,
        cost_usd=None,  # not yet exposed via the trace
        error=error,
        backend_label=backend_label,
    )


# ---------------------------------------------------------------------------
# Standalone smoke test
# ---------------------------------------------------------------------------

async def _smoke_test() -> None:
    from benchmarks.tasks import SIMPLE_QA_TASK
    print("Running graph-agent (simple Q&A)...")
    m = await run_graph_agent(SIMPLE_QA_TASK)
    print(f"  wall_ms={m.wall_ms:.0f}  hops={m.hops}  turns={m.num_turns}  passed={m.passed_eval}")
    print(f"  output[:200]: {m.output[:200]}")
    if m.error:
        print(f"  error: {m.error}")


if __name__ == "__main__":
    asyncio.run(_smoke_test())
