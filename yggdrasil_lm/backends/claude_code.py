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
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from yggdrasil_lm.backends.llm import LLMBackend, LLMResponse, ToolResult, default_backend
from yggdrasil_lm.core.executor import (
    _ROUTER_SYSTEM,
    _ROUTER_TEMPLATE,
    AgentComposer,
    ExecutionContext,
    GraphExecutor,
    RoutingDecision,
    _query_text,
    _summarise,
)
from yggdrasil_lm.core.nodes import AgentNode, ToolNode
from yggdrasil_lm.core.store import GraphStore

# ---------------------------------------------------------------------------
# Optional SDK imports — kept at module level so tests can patch them.
# All are None when claude-agent-sdk is not installed; the executor raises a
# clear ImportError at call time rather than at import time. The type checker
# sees the SDK names; code that runs without the SDK checks _SDK_AVAILABLE.
# ---------------------------------------------------------------------------
if TYPE_CHECKING:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeSDKClient,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        create_sdk_mcp_server,
        tool as cc_tool,
    )

    _SDK_AVAILABLE: bool
else:
    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ClaudeSDKClient,
            ResultMessage,
            TextBlock,
            create_sdk_mcp_server,
            tool as cc_tool,
        )
        try:
            from claude_agent_sdk import ToolUseBlock
        except ImportError:
            ToolUseBlock = None
        _SDK_AVAILABLE = True
    except ImportError:
        AssistantMessage = None
        ClaudeAgentOptions = None
        ClaudeSDKClient = None
        ResultMessage = None
        TextBlock = None
        ToolUseBlock = None
        create_sdk_mcp_server = None
        cc_tool = None
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
    tokens_in: int = 0
    tokens_out: int = 0
    tool_events: list[dict[str, Any]] = field(default_factory=list)


class _ClaudeCodeBootstrapBackend(LLMBackend):
    """Placeholder backend used only to satisfy GraphExecutor initialization."""

    async def chat(
        self,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = 8096,
    ) -> LLMResponse:
        raise RuntimeError("ClaudeCodeExecutor does not use LLMBackend.chat().")

    def extend_messages(
        self,
        messages: list[dict[str, Any]],
        response: LLMResponse,
        tool_results: list[ToolResult],
    ) -> list[dict[str, Any]]:
        raise RuntimeError("ClaudeCodeExecutor does not use LLMBackend.extend_messages().")


class ClaudeCodeAgentError(RuntimeError):
    """Structured error raised when the Claude Code SDK returns a failed result."""

    def __init__(self, subtype: str, result: str) -> None:
        self.subtype = subtype
        self.result = result
        super().__init__(f"Claude Code agent error ({subtype}): {result}")


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


def _validate_tool_args(args: dict[str, Any], schema: dict[str, Any], tool_name: str) -> None:
    if not schema:
        return
    if schema.get("type") == "object" and not isinstance(args, dict):
        raise ValueError(f"{tool_name} input must be an object")
    for key in schema.get("required", []):
        if key not in args:
            raise ValueError(f"{tool_name} input missing required field {key!r}")
    for key, subschema in schema.get("properties", {}).items():
        if key not in args:
            continue
        value = args[key]
        schema_type = subschema.get("type")
        if "enum" in subschema and value not in subschema["enum"]:
            raise ValueError(f"{tool_name}.{key} must be one of {subschema['enum']!r}")
        expected_type = _json_type_to_python(schema_type or "")
        if schema_type == "number":
            ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif schema_type == "integer":
            ok = isinstance(value, int) and not isinstance(value, bool)
        elif schema_type:
            ok = isinstance(value, expected_type)
        else:
            ok = True
        if not ok:
            raise ValueError(f"{tool_name}.{key} must be a {schema_type}")


def _format_tool_content(result: Any) -> str:
    match result:
        case str():
            return result
        case _:
            try:
                return json.dumps(result, default=str, sort_keys=True)
            except TypeError:
                return str(result)


def _extract_tool_event(block: Any) -> dict[str, Any]:
    return {
        "id": getattr(block, "id", None),
        "name": getattr(block, "name", "claude_code_builtin"),
        "input": getattr(block, "input", None),
    }


def _split_tokens(usage: dict[str, Any] | None) -> tuple[int, int]:
    """Reduce an Anthropic-shaped ``usage`` dict to (input, output) token totals.

    Cache-creation and cache-read tokens are input-side, so they fold into the
    input count. Returns (0, 0) when usage is missing (e.g. a non-Claude backend
    or a failed call) so callers can accumulate unconditionally."""
    if not usage:
        return 0, 0
    tokens_in = (
        int(usage.get("input_tokens", 0) or 0)
        + int(usage.get("cache_creation_input_tokens", 0) or 0)
        + int(usage.get("cache_read_input_tokens", 0) or 0)
    )
    tokens_out = int(usage.get("output_tokens", 0) or 0)
    return tokens_in, tokens_out


def _sdk_tool_schema(input_schema: dict[str, Any] | None) -> dict[str, Any]:
    """The schema handed to the Agent SDK's ``tool()`` for one ToolNode.

    A full JSON schema (an object ``type`` plus ``properties``) is passed as-is, so
    its ``required`` list survives. The SDK's ``{name: python_type}`` shorthand marks
    EVERY property required, which made a tool's optional arguments mandatory and got
    a call that left one out refused before the tool ran. Anything else falls back to
    the shorthand, and a tool with no properties takes a single ``input`` string.

    >>> _sdk_tool_schema({"type": "object", "properties": {"a": {"type": "string"}}, "required": []})
    {'type': 'object', 'properties': {'a': {'type': 'string'}}, 'required': []}
    >>> _sdk_tool_schema({"properties": {"n": {"type": "integer"}}})
    {'n': <class 'int'>}
    >>> _sdk_tool_schema({})
    {'input': <class 'str'>}
    """
    schema = input_schema or {}
    if isinstance(schema.get("type"), str) and isinstance(schema.get("properties"), dict):
        return schema
    props = schema.get("properties", {})
    return {
        k: _json_type_to_python(v.get("type", "string"))
        for k, v in props.items()
    } or {"input": str}


# Options a caller may set to shape a session beyond the defaults. Each is passed to
# ClaudeAgentOptions only when set (None means "leave the SDK's default"), and only
# when the installed SDK has the field — an older SDK is not handed a keyword it
# would refuse.
# `agent_end` carries the agent's whole closing message as `full_response` (the
# `text_summary` preview stays 120 characters). Callers feature-detect this flag.
AGENT_END_FULL_RESPONSE: bool = True

SESSION_OPTION_NAMES: tuple[str, ...] = (
    "tools",               # built-in tools the model SEES (allowed_tools only pre-approves)
    "disallowed_tools",    # e.g. ["Agent", "Task"] to stop in-session fan-out
    "setting_sources",     # [] = load no user/project/local settings, CLAUDE.md or memory
    "strict_mcp_config",   # True = only the MCP servers passed here, none from config
    "skills",              # [] = no skills listing
    "agents",              # programmatic sub-agent definitions
    "plugins",
    "add_dirs",
    "effort",
    "thinking",
    "max_thinking_tokens",
    "fallback_model",
)

# The per-node override lives here: ``node.attributes["claude_code"] = {...}``. Keys are
# SESSION_OPTION_NAMES plus ``env`` (merged over the executor's) and
# ``max_output_tokens``. A key set on the node replaces the executor's value.
NODE_OPTIONS_ATTRIBUTE = "claude_code"


def _sdk_option_fields() -> set[str] | None:
    """The field names the installed ClaudeAgentOptions accepts; None when unknown."""
    import dataclasses
    try:
        return {f.name for f in dataclasses.fields(ClaudeAgentOptions)}
    except TypeError:
        return None


def _build_mcp_server(
    composed: Any,
    tool_fns: dict[str, Any],
    on_tool_result: Callable[[ToolNode, dict[str, Any], Any, bool, int], None] | None = None,
) -> Any | None:
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

        param_types = _sdk_tool_schema(tn.input_schema)

        is_async = tn.is_async

        def _make_handler(tool_node: ToolNode, tool_fn: Any, async_fn: bool) -> Any:
            async def handler(args: dict[str, Any]) -> dict[str, Any]:
                t0 = time.monotonic()
                success = False
                result: Any = None
                try:
                    _validate_tool_args(args, tool_node.input_schema, tool_node.name)
                    result = (
                        await tool_fn(args)
                        if async_fn
                        else await asyncio.to_thread(tool_fn, args)
                    )
                    success = True
                    return {"content": [{"type": "text", "text": _format_tool_content(result)}]}
                except Exception as exc:  # noqa: BLE001 — a tool failure goes back to the model
                    result = {"error": str(exc), "tool": tool_node.name}
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": _format_tool_content(result)}],
                    }
                finally:
                    if on_tool_result:
                        duration_ms = int((time.monotonic() - t0) * 1000)
                        on_tool_result(tool_node, args, result, success, duration_ms)
            return handler

        handler_fn = _make_handler(tn, fn, is_async)
        decorated = cc_tool(tn.name, tn.description, param_types)(handler_fn)
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
        env:               Extra environment for every sub-agent, merged under the
                           forced ``ANTHROPIC_API_KEY=""`` (account auth).
        honor_max_tokens:  Pass each node's ``max_tokens`` to Claude Code as
                           ``CLAUDE_CODE_MAX_OUTPUT_TOKENS``. Off by default: Claude
                           Code otherwise ignores the node's budget.
        **session_options: Any of SESSION_OPTION_NAMES, e.g. ``setting_sources=[]``,
                           ``tools=[...]``, ``strict_mcp_config=True``, ``skills=[]``,
                           ``disallowed_tools=["Agent", "Task"]``, ``effort="low"``.
                           A node overrides them with ``attributes["claude_code"]``.
    """

    def __init__(
        self,
        store:              GraphStore,
        composer:           AgentComposer | None = None,
        embedder:           Any = None,
        allowed_tools:      list[str] | None = None,
        extra_mcp_servers:  dict[str, Any] | None = None,
        permission_mode:    str = "default",
        max_budget_usd:     float | None = None,
        cwd:                str | None = None,
        cli_path:           str | None = None,
        env:                dict[str, str] | None = None,
        honor_max_tokens:   bool = False,
        **session_options:  Any,
    ) -> None:
        super().__init__(
            store,
            composer=composer,
            backend=_ClaudeCodeBootstrapBackend(),
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
        self._env             = dict(env or {})
        self._honor_max_tokens = honor_max_tokens
        unknown = set(session_options) - set(SESSION_OPTION_NAMES)
        if unknown:
            raise TypeError(f"unknown Claude Code session option(s): {sorted(unknown)}")
        self._session_options = {k: v for k, v in session_options.items() if v is not None}

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
        from yggdrasil_lm.core.nodes import NodeType

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
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode:
                err = stderr.decode(errors="replace").strip()
                raise RuntimeError(f"Claude Code router failed ({proc.returncode}): {err}")
            text = stdout.decode().strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = "\n".join(
                    line for line in text.splitlines()
                    if not line.startswith("```")
                ).strip()
            data = json.loads(text)
            agent_id = str(data["agent"])
            candidate_ids = {agent.node_id for agent in candidates}
            if agent_id not in candidate_ids:
                raise ValueError(f"Router returned unknown agent id {agent_id!r}")
            return RoutingDecision(
                agent_id=agent_id,
                reason=str(data.get("reason", "")),
                confidence=float(data.get("confidence", 0.5)),
            )
        except Exception as exc:  # noqa: BLE001 — any CLI/parse failure falls back to the first agent
            return RoutingDecision(
                agent_id=candidates[0].node_id,
                reason=f"Fallback: CLI routing failed ({type(exc).__name__}).",
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
        # Honor pause_before, mirroring GraphExecutor._execute_agent. This override
        # replaces the whole method, so without this a human-in-the-loop gate on an
        # AgentNode (including the entry node of a sub-graph step) would be silently
        # skipped under the Claude Code executor and the run would proceed past the
        # intended review point. Suspend before doing any work (no SDK required).
        if node.pause_before:
            await self._pause_execution(
                ctx,
                node,
                reason="pause_before",
                waiting_for=node.wait_for_input,
            )
            return {"text": "", "intent": "default", "status": "paused"}

        if not _SDK_AVAILABLE:
            raise ImportError(
                "claude-agent-sdk is required: pip install 'yggdrasil[claude-code]'"
            )
        if not isinstance(ctx.query, str):
            # The Agent SDK prompt is plain text; dropping the image blocks would
            # answer a different question than the one asked.
            raise TypeError(
                "ClaudeCodeExecutor does not support multimodal queries; pass a plain string"
            )
        prompt = ctx.query

        import time as _time
        t0 = _time.monotonic()

        composed = await self.composer.compose(node, query=_query_text(ctx.query))
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
        mcp_servers: dict[str, Any] = dict(self._extra_mcp)

        bridged_tool_names: set[str] = set()

        def record_mcp_tool_result(
            tool_node: ToolNode,
            args: dict[str, Any],
            result: Any,
            success: bool,
            duration_ms: int,
        ) -> None:
            bridged_tool_names.add(tool_node.name)
            call_event = self._emit(
                ctx, "tool_call", tool_node.node_id, tool_node.name,
                payload={
                    "tool_name": tool_node.name,
                    "callable_ref": tool_node.callable_ref,
                    "input": args,
                    "source": "claude_code_mcp",
                },
                parent_event_id=agent_event_id,
            )
            if success:
                ctx.outputs[tool_node.node_id] = result
            self._emit(
                ctx, "tool_result", tool_node.node_id, tool_node.name,
                payload={
                    "tool_name": tool_node.name,
                    "output_summary": _summarise(_format_tool_content(result)),
                    "success": success,
                    "source": "claude_code_mcp",
                },
                parent_event_id=call_event.event_id,
                duration_ms=duration_ms,
            )

        # Bridge graph-registered ToolNodes as an in-process MCP server
        tool_mcp = _build_mcp_server(composed, self._tool_fns, record_mcp_tool_result)
        if tool_mcp:
            mcp_servers["yggdrasil-tools"] = tool_mcp

        options = ClaudeAgentOptions(**self._session_kwargs(node, system, mcp_servers))

        try:
            run_result: _AgentRunResult = await (
                self._run_with_sdk_client(prompt, options)
                if tool_mcp
                else self._run_with_query(prompt, options)
            )
        except ClaudeCodeAgentError as exc:
            self._emit(
                ctx, "error", node.node_id, node.name or "",
                payload={
                    "source": "claude_code",
                    "subtype": exc.subtype,
                    "message": exc.result,
                },
                parent_event_id=agent_event_id,
            )
            raise
        except Exception as exc:
            self._emit(
                ctx, "error", node.node_id, node.name or "",
                payload={
                    "source": "claude_code",
                    "subtype": type(exc).__name__,
                    "message": str(exc),
                },
                parent_event_id=agent_event_id,
            )
            raise

        # Built-in Claude Code tools do not return structured results through the
        # same in-process bridge, but ToolUseBlock still gives useful call data.
        for tool_event in run_result.tool_events:
            tool_name = str(tool_event.get("name") or "claude_code_builtin")
            if tool_name in bridged_tool_names:
                continue
            call_event = self._emit(
                ctx, "tool_call", node.node_id, node.name or "",
                payload={
                    "tool_name": tool_name,
                    "callable_ref": "",
                    "input": tool_event.get("input"),
                    "tool_call_id": tool_event.get("id"),
                    "source": "claude_code_builtin",
                },
                parent_event_id=agent_event_id,
            )
            self._emit(
                ctx, "tool_result", node.node_id, node.name or "",
                payload={
                    "tool_name": tool_name,
                    "output_summary": "Result handled inside Claude Code.",
                    "success": True,
                    "source": "claude_code_builtin",
                },
                parent_event_id=call_event.event_id,
            )

        intent = await self._infer_intent(run_result.text, node)
        duration_ms = int((_time.monotonic() - t0) * 1000)
        self._emit(
            ctx, "agent_end", node.node_id, node.name or "",
            payload={
                "text_summary": run_result.text[:120],
                "full_response": run_result.text,
                "intent":       intent,
                "iterations":   1,
                "cost_usd":     run_result.cost_usd,
                "tokens_in":    run_result.tokens_in,
                "tokens_out":   run_result.tokens_out,
            },
            parent_event_id=agent_event_id,
            duration_ms=duration_ms,
        )

        return {"text": run_result.text, "intent": intent}

    def _session_kwargs(
        self, node: AgentNode, system: str, mcp_servers: dict[str, Any]
    ) -> dict[str, Any]:
        """The ClaudeAgentOptions keywords for one node's session.

        The executor's session options, overridden key by key by the node's
        ``attributes["claude_code"]``; ``env`` merges instead (node over executor),
        and ``ANTHROPIC_API_KEY`` is always blanked so the CLI uses account auth.
        """
        node_opts = dict((node.attributes or {}).get(NODE_OPTIONS_ATTRIBUTE) or {})
        unknown = set(node_opts) - set(SESSION_OPTION_NAMES) - {"env", "max_output_tokens"}
        if unknown:
            raise ValueError(
                f"node {node.name or node.node_id!r}: unknown {NODE_OPTIONS_ATTRIBUTE} "
                f"option(s) {sorted(unknown)}"
            )
        env: dict[str, str] = {**self._env, **{str(k): str(v) for k, v in (node_opts.pop("env", None) or {}).items()}}
        max_out = node_opts.pop("max_output_tokens", None)
        if max_out is None and self._honor_max_tokens:
            max_out = node.max_tokens
        if max_out:
            env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(int(max_out))
        env["ANTHROPIC_API_KEY"] = ""

        kwargs: dict[str, Any] = {
            "system_prompt": system,
            "allowed_tools": self._allowed_tools,
            "mcp_servers": mcp_servers or None,
            "max_turns": node.max_iterations,
            "model": node.model,
            "permission_mode": self._permission_mode,
            "cwd": self._cwd,
            "env": env,
        }
        if self._max_budget_usd:
            kwargs["max_budget_usd"] = self._max_budget_usd
        if self._cli_path:
            kwargs["cli_path"] = self._cli_path
        session = {**self._session_options, **{k: v for k, v in node_opts.items() if v is not None}}
        known = _sdk_option_fields()
        for key, value in session.items():
            if known is None or key in known:
                kwargs[key] = value
        return kwargs

    # ------------------------------------------------------------------
    # Two execution paths
    # ------------------------------------------------------------------

    async def _run_with_query(self, prompt: str, options: Any) -> _AgentRunResult:
        """Use query() — sufficient when no in-process MCP server is needed."""
        from claude_agent_sdk import query as cc_query

        result_text = ""
        tool_call_count = 0
        cost_usd: float | None = None
        tokens_in = 0
        tokens_out = 0
        tool_events: list[dict[str, Any]] = []

        async for message in cc_query(prompt=prompt, options=options):
            match message:
                case AssistantMessage():
                    for block in message.content:
                        if ToolUseBlock is not None and isinstance(block, ToolUseBlock):
                            tool_call_count += 1
                            tool_events.append(_extract_tool_event(block))
                case ResultMessage():
                    if getattr(message, "is_error", False):
                        subtype = getattr(message, "subtype", "unknown")
                        raise ClaudeCodeAgentError(subtype, message.result or "")
                    result_text = message.result or ""
                    cost_usd = getattr(message, "total_cost_usd", None)
                    tokens_in, tokens_out = _split_tokens(getattr(message, "usage", None))

        return _AgentRunResult(
            text=result_text,
            tool_calls=tool_call_count,
            cost_usd=cost_usd,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tool_events=tool_events,
        )

    async def _run_with_sdk_client(self, prompt: str, options: Any) -> _AgentRunResult:
        """Use ClaudeSDKClient — required for in-process SDK MCP servers."""
        parts: list[str] = []
        tool_call_count = 0
        cost_usd: float | None = None
        tokens_in = 0
        tokens_out = 0
        tool_events: list[dict[str, Any]] = []

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                match message:
                    case AssistantMessage():
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                parts.append(block.text)
                            if ToolUseBlock is not None and isinstance(block, ToolUseBlock):
                                tool_call_count += 1
                                tool_events.append(_extract_tool_event(block))
                    case ResultMessage():
                        if getattr(message, "is_error", False):
                            subtype = getattr(message, "subtype", "unknown")
                            raise ClaudeCodeAgentError(subtype, message.result or "")
                        cost_usd = getattr(message, "total_cost_usd", None)
                        tokens_in, tokens_out = _split_tokens(getattr(message, "usage", None))

        return _AgentRunResult(
            text="\n".join(parts),
            tool_calls=tool_call_count,
            cost_usd=cost_usd,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tool_events=tool_events,
        )
