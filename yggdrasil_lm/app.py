"""Beginner-friendly builder API for yggdrasil.

This module keeps the core graph primitives available while offering a smaller,
task-oriented surface for first-time users and code-generation tools.
"""

from __future__ import annotations

from typing import Any

from yggdrasil_lm.backends.llm import AnthropicBackend, LLMBackend, OpenAIBackend
from yggdrasil_lm.core.edges import Edge
from yggdrasil_lm.core.executor import GraphExecutor
from yggdrasil_lm.core.nodes import AgentNode, ContextNode, PromptNode, ToolNode, TransformNode
from yggdrasil_lm.core.store import GraphStore, NetworkXGraphStore
from yggdrasil_lm.tools.registry import ToolRegistry, default_registry

NodeRef = AgentNode | ToolNode | ContextNode | PromptNode | TransformNode | str
END_NODE = "__END__"


def create_agent(
    name: str,
    *,
    description: str = "",
    model: str = "claude-sonnet-4-6",
    system_prompt: str = "",
    routing_table: dict[str, str] | None = None,
    max_iterations: int = 10,
    **kwargs: Any,
) -> AgentNode:
    """Create an AgentNode with beginner-friendly defaults."""
    return AgentNode(
        name=name,
        description=description,
        model=model,
        system_prompt=system_prompt,
        routing_table=routing_table or {"default": END_NODE},
        max_iterations=max_iterations,
        **kwargs,
    )


def create_tool(
    name: str,
    *,
    callable_ref: str,
    description: str = "",
    input_schema: dict[str, Any] | None = None,
    output_schema: dict[str, Any] | None = None,
    is_async: bool = True,
    **kwargs: Any,
) -> ToolNode:
    """Create a ToolNode with sane defaults."""
    return ToolNode(
        name=name,
        description=description,
        callable_ref=callable_ref,
        input_schema=input_schema or {"type": "object", "properties": {}},
        output_schema=output_schema or {},
        is_async=is_async,
        **kwargs,
    )


def create_transform(
    name: str,
    *,
    callable_ref: str,
    description: str = "",
    input_keys: list[str] | None = None,
    output_key: str = "",
    is_async: bool = True,
    **kwargs: Any,
) -> TransformNode:
    """Create a TransformNode — a pure-Python data reshape step with no LLM."""
    return TransformNode(
        name=name,
        description=description,
        callable_ref=callable_ref,
        input_keys=input_keys or [],
        output_key=output_key,
        is_async=is_async,
        **kwargs,
    )


def create_context(
    name: str,
    content: str,
    *,
    description: str = "",
    **kwargs: Any,
) -> ContextNode:
    """Create a ContextNode."""
    return ContextNode(name=name, content=content, description=description, **kwargs)


def create_prompt(
    name: str,
    template: str,
    *,
    description: str = "",
    **kwargs: Any,
) -> PromptNode:
    """Create a PromptNode."""
    return PromptNode(name=name, template=template, description=description, **kwargs)


def create_executor(
    store: GraphStore,
    *,
    provider: str | None = None,
    backend: LLMBackend | None = None,
    **backend_kwargs: Any,
) -> GraphExecutor:
    """Create a GraphExecutor from a small set of backend profiles.

    Args:
        store: Graph storage backend.
        provider: One of "anthropic", "claude-code", "compatible", "openai",
            "openai-compatible", or None.
        backend: Explicit backend instance. Takes precedence over provider.
        **backend_kwargs: Passed to the backend constructor when provider is set.
    """
    if backend is not None:
        return GraphExecutor(store, backend=backend)
    if provider is None:
        return GraphExecutor(store)

    provider_key = provider.strip().lower()
    if provider_key == "anthropic":
        return GraphExecutor(store, backend=AnthropicBackend(**backend_kwargs))
    if provider_key in {"claude-code", "claude_code", "claudecode"}:
        from yggdrasil_lm.backends.claude_code import ClaudeCodeExecutor

        return ClaudeCodeExecutor(store, **backend_kwargs)
    if provider_key in {"openai", "openai-compatible", "compatible"}:
        return GraphExecutor(store, backend=OpenAIBackend(**backend_kwargs))
    raise ValueError(
        f"Unknown provider: {provider!r}. Use 'anthropic', 'claude-code', "
        "'compatible', or pass backend=..."
    )


class GraphApp:
    """Thin builder facade for the yggdrasil runtime.

    This class keeps the low-level graph primitives available, but presents them
    in a sequence that is easier to teach:
    1. create nodes
    2. connect them
    3. register tool implementations
    4. run the graph
    """

    def __init__(
        self,
        *,
        store: GraphStore | None = None,
        executor: GraphExecutor | None = None,
        provider: str | None = None,
        backend: LLMBackend | None = None,
        tool_registry: ToolRegistry | None = None,
        **backend_kwargs: Any,
    ) -> None:
        self.store = store or NetworkXGraphStore()
        self._executor = executor
        self._provider = provider
        self._backend = backend
        self._backend_kwargs = backend_kwargs
        self.tool_registry = tool_registry or default_registry

    @property
    def executor(self) -> GraphExecutor:
        """Lazily create the executor when it is first needed."""
        if self._executor is None:
            self._executor = create_executor(
                self.store,
                provider=self._provider,
                backend=self._backend,
                **self._backend_kwargs,
            )
        return self._executor

    async def add_agent(self, name: str, **kwargs: Any) -> AgentNode:
        agent = create_agent(name, **kwargs)
        await self.store.upsert_node(agent)
        return agent

    async def add_tool(
        self,
        name: str,
        *,
        fn: Any | None = None,
        attach: bool = False,
        agent: AgentNode | str | None = None,
        **kwargs: Any,
    ) -> ToolNode:
        tool = create_tool(name, **kwargs)
        await self.store.upsert_node(tool)
        if fn is not None:
            self.register_tool(tool.callable_ref, fn)
        if attach:
            if agent is None:
                raise ValueError("agent=... is required when attach=True")
            await self.connect_tool(agent, tool)
        return tool

    async def add_transform(
        self,
        name: str,
        *,
        fn: Any | None = None,
        **kwargs: Any,
    ) -> TransformNode:
        transform = create_transform(name, **kwargs)
        await self.store.upsert_node(transform)
        if fn is not None:
            self.executor.register_tool(transform.callable_ref, fn)
        return transform

    async def add_context(self, name: str, content: str, **kwargs: Any) -> ContextNode:
        ctx = create_context(name, content, **kwargs)
        await self.store.upsert_node(ctx)
        return ctx

    async def add_prompt(self, name: str, template: str, **kwargs: Any) -> PromptNode:
        prompt = create_prompt(name, template, **kwargs)
        await self.store.upsert_node(prompt)
        return prompt

    def register_tool(self, callable_ref: str, fn: Any) -> None:
        self.executor.register_tool(callable_ref, fn)

    def use_default_tools(self) -> None:
        self.tool_registry.attach(self.executor)

    async def connect_tool(
        self,
        agent: AgentNode | str,
        tool: ToolNode | str,
        *,
        weight: float | None = None,
        **kwargs: Any,
    ) -> Edge:
        return await self.store.attach_tool(
            self._node_id(agent),
            self._node_id(tool),
            weight=weight,
            **kwargs,
        )

    async def connect_context(
        self,
        agent: AgentNode | str,
        context: ContextNode | str,
        *,
        weight: float | None = None,
        **kwargs: Any,
    ) -> Edge:
        return await self.store.attach_context(
            self._node_id(agent),
            self._node_id(context),
            weight=weight,
            **kwargs,
        )

    async def connect_prompt(
        self,
        agent: AgentNode | str,
        prompt: PromptNode | str,
        **kwargs: Any,
    ) -> Edge:
        edge = Edge.has_prompt(self._node_id(agent), self._node_id(prompt), **kwargs)
        await self.store.upsert_edge(edge)
        return edge

    async def delegate(
        self,
        src_agent: AgentNode | str,
        dst_agent: AgentNode | str,
        **kwargs: Any,
    ) -> Edge:
        edge = Edge.delegates_to(self._node_id(src_agent), self._node_id(dst_agent), **kwargs)
        await self.store.upsert_edge(edge)
        return edge

    async def run(
        self,
        entry_node: AgentNode | str,
        query: str,
        *,
        strategy: str = "sequential",
        **kwargs: Any,
    ):
        return await self.executor.run(
            entry_node_id=self._node_id(entry_node),
            query=query,
            strategy=strategy,
            **kwargs,
        )

    def _node_id(self, node: NodeRef) -> str:
        if isinstance(node, str):
            return node
        return node.node_id


__all__ = [
    "GraphApp",
    "create_agent",
    "create_context",
    "create_executor",
    "create_prompt",
    "create_tool",
    "create_transform",
]
