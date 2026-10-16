"""Yggdrasil — a knowledge graph where every node is an active agent."""

from __future__ import annotations

END_NODE: str = "__END__"

from typing import TYPE_CHECKING

if TYPE_CHECKING:     # type checkers see the real classes; runtime stays lazy
    from yggdrasil_lm.batch import (
        BatchItemResult as BatchItemResult,
        BatchRun as BatchRun,
        BatchStatus as BatchStatus,
    )
    from yggdrasil_lm.app import (
        GraphApp as GraphApp,
        create_agent as create_agent,
        create_context as create_context,
        create_executor as create_executor,
        create_prompt as create_prompt,
        create_reasoner as create_reasoner,
        create_tool as create_tool,
        create_transform as create_transform,
    )
    from yggdrasil_lm.backends.llm import (
        AnthropicBackend as AnthropicBackend,
        OpenAIBackend as OpenAIBackend,
    )
    from yggdrasil_lm.backends.claude_code import (
        ClaudeCodeExecutor as ClaudeCodeExecutor,
    )
    from yggdrasil_lm.core.nodes import (
        AgentNode as AgentNode,
        ApprovalNode as ApprovalNode,
        ContextNode as ContextNode,
        ExecutionPolicy as ExecutionPolicy,
        FactSource as FactSource,
        GraphNode as GraphNode,
        ReasonerNode as ReasonerNode,
        RetryPolicy as RetryPolicy,
        RouteRule as RouteRule,
        ToolNode as ToolNode,
        TransformNode as TransformNode,
    )
    from yggdrasil_lm.symbolic import (
        Program as Program,
        Solution as Solution,
        fact as fact,
    )
    from yggdrasil_lm.core.edges import (
        Edge as Edge,
        EdgeType as EdgeType,
    )
    from yggdrasil_lm.core.store import (
        GraphStore as GraphStore,
        NetworkXGraphStore as NetworkXGraphStore,
    )
    from yggdrasil_lm.core.executor import (
        ExecutionContext as ExecutionContext,
        ExecutionOptions as ExecutionOptions,
        GraphExecutor as GraphExecutor,
        ResumeReadiness as ResumeReadiness,
        TraceEvent as TraceEvent,
        print_trace as print_trace,
    )
    from yggdrasil_lm.observability import (
        RunExplanation as RunExplanation,
        explain_run as explain_run,
    )
    from yggdrasil_lm.trace_ui import (
        inspect_trace as inspect_trace,
    )
    from yggdrasil_lm.media import (
        ImageBlock as ImageBlock,
        QueryContent as QueryContent,
        image_from_file as image_from_file,
        image_from_url as image_from_url,
        image_from_base64 as image_from_base64,
        build_query as build_query,
    )

# Every public name resolves on first access (PEP 562), so importing a submodule —
# `yggdrasil_lm.core.nodes` in a tool child, say — does not pay for the Claude Agent
# SDK, MCP, the LLM clients, batch or the trace UI. `from yggdrasil_lm import X` and
# `yggdrasil_lm.X` work exactly as before.
_LAZY: dict[str, str] = {
    "BatchItemResult": "yggdrasil_lm.batch", "BatchRun": "yggdrasil_lm.batch",
    "BatchStatus": "yggdrasil_lm.batch",
    "GraphApp": "yggdrasil_lm.app", "create_agent": "yggdrasil_lm.app",
    "create_context": "yggdrasil_lm.app", "create_executor": "yggdrasil_lm.app",
    "create_prompt": "yggdrasil_lm.app", "create_reasoner": "yggdrasil_lm.app",
    "create_tool": "yggdrasil_lm.app", "create_transform": "yggdrasil_lm.app",
    "AnthropicBackend": "yggdrasil_lm.backends.llm", "OpenAIBackend": "yggdrasil_lm.backends.llm",
    "ClaudeCodeExecutor": "yggdrasil_lm.backends.claude_code",
    "AgentNode": "yggdrasil_lm.core.nodes", "ApprovalNode": "yggdrasil_lm.core.nodes",
    "ContextNode": "yggdrasil_lm.core.nodes", "ExecutionPolicy": "yggdrasil_lm.core.nodes",
    "FactSource": "yggdrasil_lm.core.nodes", "GraphNode": "yggdrasil_lm.core.nodes",
    "ReasonerNode": "yggdrasil_lm.core.nodes", "RetryPolicy": "yggdrasil_lm.core.nodes",
    "RouteRule": "yggdrasil_lm.core.nodes", "ToolNode": "yggdrasil_lm.core.nodes",
    "TransformNode": "yggdrasil_lm.core.nodes",
    "Program": "yggdrasil_lm.symbolic", "Solution": "yggdrasil_lm.symbolic",
    "fact": "yggdrasil_lm.symbolic",
    "Edge": "yggdrasil_lm.core.edges", "EdgeType": "yggdrasil_lm.core.edges",
    "GraphStore": "yggdrasil_lm.core.store", "NetworkXGraphStore": "yggdrasil_lm.core.store",
    "ExecutionContext": "yggdrasil_lm.core.executor", "ExecutionOptions": "yggdrasil_lm.core.executor",
    "GraphExecutor": "yggdrasil_lm.core.executor", "ResumeReadiness": "yggdrasil_lm.core.executor",
    "TraceEvent": "yggdrasil_lm.core.executor", "print_trace": "yggdrasil_lm.core.executor",
    "RunExplanation": "yggdrasil_lm.observability", "explain_run": "yggdrasil_lm.observability",
    "inspect_trace": "yggdrasil_lm.trace_ui",
    "ImageBlock": "yggdrasil_lm.media", "QueryContent": "yggdrasil_lm.media",
    "image_from_file": "yggdrasil_lm.media", "image_from_url": "yggdrasil_lm.media",
    "image_from_base64": "yggdrasil_lm.media", "build_query": "yggdrasil_lm.media",
}


def __getattr__(name: str) -> object:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module 'yggdrasil_lm' has no attribute {name!r}")
    import importlib
    value = getattr(importlib.import_module(module), name)
    globals()[name] = value          # resolve once
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY))


__all__ = [
    "GraphApp", "create_agent", "create_context", "create_executor", "create_prompt", "create_reasoner", "create_tool", "create_transform",
    "AnthropicBackend", "OpenAIBackend", "ClaudeCodeExecutor",
    "BatchRun", "BatchItemResult", "BatchStatus",
    "AgentNode", "ApprovalNode", "ContextNode", "ToolNode", "GraphNode", "TransformNode", "ReasonerNode", "FactSource",
    "Program", "Solution", "fact",
    "RetryPolicy", "ExecutionPolicy", "RouteRule",
    "Edge", "EdgeType",
    "END_NODE",
    "GraphStore", "NetworkXGraphStore",
    "GraphExecutor", "ExecutionContext", "ExecutionOptions", "ResumeReadiness", "TraceEvent",
    "explain_run", "RunExplanation",
    "print_trace", "inspect_trace",
    # Multimodal / image helpers
    "ImageBlock", "QueryContent",
    "image_from_file", "image_from_url", "image_from_base64", "build_query",
]
