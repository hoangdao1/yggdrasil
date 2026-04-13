"""Tool registry — maps callable_ref strings to Python callables.

Usage:
    registry = ToolRegistry()
    registry.register("mymodule.my_fn", my_fn)

    # Or use the decorator:
    @registry.tool("mymodule.my_fn")
    async def my_fn(input: dict) -> str: ...

    # Attach to executor:
    for ref, fn in registry.items():
        executor.register_tool(ref, fn)

    # Or in one call:
    registry.attach(executor)
"""

from __future__ import annotations

import importlib
from typing import Any, Callable

from yggdrasil.tools.code_exec import run_python
from yggdrasil.tools.echo import echo
from yggdrasil.tools.web_search import search as web_search


class ToolRegistry:
    """Central registry mapping callable_ref strings to Python callables.

    callable_ref format: "module.path.function_name"
    e.g. "yggdrasil.tools.web_search.search"
    """

    def __init__(self) -> None:
        self._registry: dict[str, Callable[..., Any]] = {}

    def register(self, callable_ref: str, fn: Callable[..., Any]) -> None:
        """Register a callable under its dotted ref string."""
        self._registry[callable_ref] = fn

    def tool(self, callable_ref: str) -> Callable:
        """Decorator to register a function."""
        def decorator(fn: Callable) -> Callable:
            self.register(callable_ref, fn)
            return fn
        return decorator

    def get(self, callable_ref: str) -> Callable[..., Any] | None:
        return self._registry.get(callable_ref)

    def items(self):
        return self._registry.items()

    def load(self, callable_ref: str) -> Callable[..., Any]:
        """Load a callable from a dotted import path if not already registered.

        e.g. "yggdrasil.tools.web_search.search" imports
        yggdrasil.tools.web_search and returns its .search attribute.
        """
        if callable_ref in self._registry:
            return self._registry[callable_ref]

        parts = callable_ref.rsplit(".", 1)
        if len(parts) != 2:
            raise ImportError(f"Invalid callable_ref: {callable_ref!r}")
        module_path, fn_name = parts
        module = importlib.import_module(module_path)
        fn = getattr(module, fn_name)
        self.register(callable_ref, fn)
        return fn

    def attach(self, executor: Any) -> None:
        """Register all tools in this registry with a GraphExecutor."""
        for ref, fn in self._registry.items():
            executor.register_tool(ref, fn)

    def __contains__(self, ref: str) -> bool:
        return ref in self._registry

    def __len__(self) -> int:
        return len(self._registry)


# ---------------------------------------------------------------------------
# Global default registry (import and use directly)
# ---------------------------------------------------------------------------

default_registry = ToolRegistry()


# ---------------------------------------------------------------------------
# Built-in tool implementations
# ---------------------------------------------------------------------------

default_registry.register("yggdrasil.tools.web_search.search", web_search)


# ---------------------------------------------------------------------------
# run_python is NOT registered in default_registry.
#
# SECURITY: This tool grants any LLM agent that receives it FULL CODE EXECUTION
# capability on the host machine — no sandbox, no capability restrictions, only
# a timeout. Prompt injection via web search results or file contents can trigger
# arbitrary OS commands.
#
# To opt in explicitly:
#   from yggdrasil.tools.registry import run_python
#   executor.register_tool("yggdrasil.tools.code_exec.run_python", run_python)
# ---------------------------------------------------------------------------
default_registry.register("yggdrasil.tools.echo.echo", echo)
