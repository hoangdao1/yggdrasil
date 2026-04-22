"""Claude Code sub-agent backend for GraphExecutor.

Replaces the direct Anthropic Messages API call with a Claude Code Agent SDK
invocation. Each AgentNode runs as a full autonomous Claude Code sub-agent,
with its graph-registered ToolNodes bridged in as an in-process MCP server.

Usage:
    executor = ClaudeCodeExecutor(
        store,
        allowed_tools=["Bash", "Read", "Glob", "Grep", "WebSearch"],
        permission_mode="acceptEdits",
        cwd="/path/to/project",
    )
    default_registry.attach(executor)
    ctx = await executor.run(agent.node_id, "analyse the codebase")

Requirements:
    pip install 'yggdrasil[claude-code]'
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import uuid
from dataclasses import dataclass, field
from typing import Any

from yggdrasil_lm.backends.llm import default_backend
from yggdrasil_lm.core.executor import (
    AgentComposer,
    AgentResult,
    ExecutionContext,
    GraphExecutor,
    RoutingDecision,
    TraceEvent,
    _ROUTER_SYSTEM,
    _ROUTER_TEMPLATE,
)
from yggdrasil_lm.core.nodes import AgentNode
from yggdrasil_lm.core.store import GraphStore

# ---------------------------------------------------------------------------
# Optional SDK imports — kept at module level so tests can patch them.
# All are None when claude-agent-sdk is not installed; the executor raises a
# clear ImportError at call time rather than at import time.
# ---------------------------------------------------------------------------
try:
    from claude_agent_sdk import (                       # type: ignore[import]
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        ResultMessage,
        TextBlock,
        create_sdk_mcp_server,
        tool as cc_tool,
    )
    try:
        from claude_agent_sdk import ToolUseBlock        # type: ignore[import]
    except ImportError:
        ToolUseBlock = None                              # type: ignore[assignment]
    _SDK_AVAILABLE = True
except ImportError:
    AssistantMessage = None                              # type: ignore[assignment,misc]
    ClaudeAgentOptions = None                            # type: ignore[assignment,misc]
    ClaudeSDKClient = None                               # type: ignore[assignment,misc]
    ResultMessage = None                                 # type: ignore[assignment,misc]
    TextBlock = None                                     # type: ignore[assignment,misc]
    ToolUseBlock = None                                  # type: ignore[assignment]
    create_sdk_mcp_server = None                         # type: ignore[assignment]
    cc_tool = None                                       # type: ignore[assignment]
    _SDK_AVAILABLE = False


# ---------------------------------------------------------------------------
# Internal result type for SDK runs
# ---------------------------------------------------------------------------

@dataclass
class _AgentRunResult:
    """Raw data returned from a single Claude Code SDK invocation."""
    text: str
    tool_calls: int
    cost_usd: float | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_type_to_python(type_str: str) -> type:
    return {
        "string":  str,
        "integer": int,
        "number":  float,
        "boolean": bool,
        "array":   list,
        "object":  dict,
    }.get(type_str, str)


def _build_mcp_server(composed: Any, tool_fns: dict) -> Any | None:
    """Wrap each ComposedAgent ToolNode as an in-process Agent SDK MCP tool.

    Returns a server object (from create_sdk_mcp_server) to pass to
    ClaudeAgentOptions.mcp_servers, or None when no tools can be bridged.

    Requires: pip install 'yggdrasil[claude-code]'
    """
    if not _SDK_AVAILABLE:
        raise ImportError(
            "claude-agent-sdk is required for tool bridging: "
            "pip install 'yggdrasil[claude-code]'"
        )

    sdk_tools = []

    for tn in composed.tools:
        fn = tool_fns.get(tn.callable_ref)
        if fn is None:
            continue

        props = tn.input_schema.get("properties", {})
        param_types = {
            k: _json_type_to_python(v.get("type", "string"))
            for k, v in props.items()
        }
        # Fallback for tools that declare no properties
        if not param_types:
            param_types = {"input": str}

        is_async = tn.is_async

        def _make_handler(tool_fn: Any, async_fn: bool) -> Any:
            async def handler(args: dict) -> dict:
                result = (
                    await tool_fn(args)
                    if async_fn
                    else await asyncio.to_thread(tool_fn, args)
                )
                return {"content": [{"type": "text", "text": str(result)}]}
            return handler

        handler = _make_handler(fn, is_async)
        decorated = cc_tool(tn.name, tn.description, param_types)(handler)
        sdk_tools.append(decorated)

    if not sdk_tools:
        return None

    return create_sdk_mcp_server("yggdrasil-tools", tools=sdk_tools)


# ---------------------------------------------------------------------------
# ClaudeCodeExecutor
# ---------------------------------------------------------------------------

class ClaudeCodeExecutor(GraphExecutor):
    """GraphExecutor that runs each AgentNode as a Claude Code sub-agent.

    All graph traversal, routing, context composition, and ToolNode bridging
    work identically to GraphExecutor. Only _execute_agent is replaced: instead
    of driving the Anthropic Messages API directly it spawns a Claude Code
    sub-agent via the Agent SDK.

    Graph-registered ToolNodes are bridged to the sub-agent as an in-process
    MCP server (requires ClaudeSDKClient). When no ToolNodes are present the
    lighter query() path is used instead.

    Args:
        store:             Graph store.
        composer:          AgentComposer instance; auto-created if None.
        embedder:          Optional Embedder for query-time context re-ranking.
        allowed_tools:     Claude Code built-in tools available to sub-agents
                           (default: Read, Glob, Grep, Bash, WebSearch).
        extra_mcp_servers: Additional MCP servers merged into every sub-agent
                           invocation (stdio/http format or SDK server objects).
        permission_mode:   How to handle permission prompts
                           ("default" | "acceptEdits" | "bypassPermissions").
        max_budget_usd:    Optional per-invocation USD budget cap.
        cwd:               Working directory for file operations.
        cli_path:          Path to the Claude Code CLI binary. When set, overrides
                           the bundled CLI inside claude_agent_sdk. Use this to
                           point at your system-installed ``claude`` so sub-agents
                           authenticate via your Claude Code account rather than
                           ANTHROPIC_API_KEY.
    """

    def __init__(
        self,
        store:              GraphStore,
        composer:           AgentComposer | None = None,
        embedder:           Any = None,
        allowed_tools:      list[str] | None = None,
        extra_mcp_servers:  dict | None = None,
        permission_mode:    str = "default",
        max_budget_usd:     float | None = None,
        cwd:                str | None = None,
        cli_path:           str | None = None,
    ) -> None:
        super().__init__(
            store,
            composer=composer,
            backend=default_backend(),
            embedder=embedder,
            router_model="claude-haiku-4-5-20251001",
        )
        self._backend = None   # not used — Agent SDK owns the LLM loop

        self._allowed_tools   = ["Read", "Glob", "Grep", "Bash", "WebSearch"] if allowed_tools is None else allowed_tools
        self._extra_mcp       = extra_mcp_servers or {}
        self._permission_mode = permission_mode
        self._max_budget_usd  = max_budget_usd
        self._cwd             = cwd
        self._cli_path        = cli_path

    # ------------------------------------------------------------------
    # Override: LLM routing (lazily init backend — not used for execution)
    # ------------------------------------------------------------------

    async def route(
        self,
        query: str,
        candidates: list[AgentNode] | None = None,
    ) -> RoutingDecision:
        """Route using the system Claude Code CLI so no API key is needed.

        Calls the CLI with ``--print`` (non-agentic, single response) using the
        same routing prompt as the parent class, but authenticated via the
        Claude Code account instead of ANTHROPIC_API_KEY.
        """
        from yggdrasil_lm.core.store import NodeType

        if candidates is None:
            all_nodes = await self.store.list_nodes(node_type=NodeType.AGENT)
            candidates = [n for n in all_nodes if isinstance(n, AgentNode) and n.is_valid]

        if not candidates:
            raise ValueError("No valid AgentNode candidates found in the store.")

        if len(candidates) == 1:
            return RoutingDecision(
                agent_id=candidates[0].node_id,
                reason="Only one agent available.",
                confidence=1.0,
            )

        cli = self._cli_path or shutil.which("claude")
        if not cli:
            # Fallback to Anthropic backend if no CLI found
            if self._backend is None:
                self._backend = default_backend()
            return await super().route(query, candidates)

        agent_list = "\n".join(f"- {n.node_id}: {n.description}" for n in candidates)
        prompt = f"{_ROUTER_SYSTEM}\n\n{_ROUTER_TEMPLATE.format(agent_list=agent_list, query=query)}"

        proc_env = {**os.environ, "ANTHROPIC_API_KEY": ""}
        try:
            proc = await asyncio.create_subprocess_exec(
                cli, "--print", "--output-format", "text", prompt,
                env=proc_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await proc.communicate()
            text = stdout.decode().strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = "\n".join(
                    line for line in text.splitlines()
                    if not line.startswith("```")
                ).strip()
            data = json.loads(text)
            return RoutingDecision(
                agent_id=str(data["agent"]),
                reason=str(data.get("reason", "")),
                confidence=float(data.get("confidence", 0.5)),
            )
        except Exception:
            return RoutingDecision(
                agent_id=candidates[0].node_id,
                reason="Fallback: CLI routing failed.",
                confidence=0.5,
            )

    # ------------------------------------------------------------------
    # Override: run each AgentNode as a Claude Code sub-agent
    # ------------------------------------------------------------------

    async def _execute_agent(
        self,
        node:            AgentNode,
        ctx:             ExecutionContext,
        parent_event_id: str | None = None,
    ) -> dict[str, Any]:
        if not _SDK_AVAILABLE:
            raise ImportError(
                "claude-agent-sdk is required: pip install 'yggdrasil[claude-code]'"
            )

        import time as _time
        t0 = _time.monotonic()

        composed = await self.composer.compose(node, query=ctx.query)
        system   = composed.build_system_prompt()

        # Emit agent_start so downstream metrics extraction picks up agent counts.
        agent_event_id = str(uuid.uuid4())
        self._emit(
            ctx, "agent_start", node.node_id, node.name or "",
            payload={
                "query":   ctx.query,
                "model":   node.model,
                "tools":   [t.name for t in composed.tools],
                "context": [c.name for c in composed.context if c.name],
            },
            event_id=agent_event_id,
            parent_event_id=parent_event_id,
        )
        if composed.context:
            self._emit(
                ctx, "context_inject", node.node_id, node.name or "",
                payload={
                    "context_names": [c.name for c in composed.context if c.name],
                    "count":         len(composed.context),
                },
                parent_event_id=agent_event_id,
            )

        # Build MCP server map — start with any user-supplied servers
        mcp_servers: dict = dict(self._extra_mcp)

        # Bridge graph-registered ToolNodes as an in-process MCP server
        tool_mcp = _build_mcp_server(composed, self._tool_fns)
        if tool_mcp:
            mcp_servers["yggdrasil-tools"] = tool_mcp

        options = ClaudeAgentOptions(
            system_prompt=system,
            allowed_tools=self._allowed_tools,
            mcp_servers=mcp_servers or None,
            max_turns=node.max_iterations,
            model=node.model,
            permission_mode=self._permission_mode,
            cwd=self._cwd,
            env={"ANTHROPIC_API_KEY": ""},
            **({"max_budget_usd": self._max_budget_usd} if self._max_budget_usd else {}),
            **({"cli_path": self._cli_path} if self._cli_path else {}),
        )

        run_result: _AgentRunResult = await (
            self._run_with_sdk_client(ctx.query, options)
            if tool_mcp
            else self._run_with_query(ctx.query, options)
        )

        # Emit one tool_call trace event per tool invocation so metrics count them.
        for _ in range(run_result.tool_calls):
            self._emit(
                ctx, "tool_call", node.node_id, node.name or "",
                payload={"tool_name": "claude_code_builtin", "callable_ref": ""},
                parent_event_id=agent_event_id,
            )

        intent = await self._infer_intent(run_result.text, node)
        duration_ms = int((_time.monotonic() - t0) * 1000)
        self._emit(
            ctx, "agent_end", node.node_id, node.name or "",
            payload={
                "text_summary": run_result.text[:120],
                "intent":       intent,
                "iterations":   1,
                "cost_usd":     run_result.cost_usd,
            },
            parent_event_id=agent_event_id,
            duration_ms=duration_ms,
        )

        return {"text": run_result.text, "intent": intent}

    # ------------------------------------------------------------------
    # Two execution paths
    # ------------------------------------------------------------------

    async def _run_with_query(self, prompt: str, options: Any) -> _AgentRunResult:
        """Use query() — sufficient when no in-process MCP server is needed."""
        from claude_agent_sdk import query as cc_query  # type: ignore[import]

        result_text = ""
        tool_call_count = 0
        cost_usd: float | None = None

        async for message in cc_query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if ToolUseBlock and isinstance(block, ToolUseBlock):
                        tool_call_count += 1
            elif isinstance(message, ResultMessage):
                if getattr(message, "is_error", False):
                    subtype = getattr(message, "subtype", "unknown")
                    raise RuntimeError(
                        f"Claude Code agent error ({subtype}): {message.result or ''}"
                    )
                result_text = message.result or ""
                cost_usd = getattr(message, "total_cost_usd", None)

        return _AgentRunResult(text=result_text, tool_calls=tool_call_count, cost_usd=cost_usd)

    async def _run_with_sdk_client(self, prompt: str, options: Any) -> _AgentRunResult:
        """Use ClaudeSDKClient — required for in-process SDK MCP servers."""
        parts: list[str] = []
        tool_call_count = 0
        cost_usd: float | None = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            parts.append(block.text)
                        if ToolUseBlock and isinstance(block, ToolUseBlock):
                            tool_call_count += 1
                elif isinstance(message, ResultMessage):
                    if getattr(message, "is_error", False):
                        subtype = getattr(message, "subtype", "unknown")
                        raise RuntimeError(
                            f"Claude Code agent error ({subtype}): {message.result or ''}"
                        )
                    cost_usd = getattr(message, "total_cost_usd", None)

        return _AgentRunResult(
            text="\n".join(parts), tool_calls=tool_call_count, cost_usd=cost_usd
        )
