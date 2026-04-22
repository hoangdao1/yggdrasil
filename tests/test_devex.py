from __future__ import annotations

import pytest

from yggdrasil_lm.backends.llm import default_backend
from yggdrasil_lm.tools.registry import ToolRegistry


def test_tool_registry_loads_builtin_echo_tool():
    registry = ToolRegistry()
    fn = registry.load("tools.echo.echo")
    assert fn.__name__ == "echo"


def test_tool_registry_loads_builtin_web_search_tool():
    registry = ToolRegistry()
    fn = registry.load("tools.web_search.search")
    assert fn.__name__ == "search"


def test_default_backend_requires_explicit_default_setup(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="No default LLM backend is configured"):
        default_backend()
