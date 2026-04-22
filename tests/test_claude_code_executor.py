"""Tests for ClaudeCodeExecutor.

All claude_agent_sdk calls are mocked — no Claude Code CLI required.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yggdrasil_lm import (
    AgentNode,
    ContextNode,
    Edge,
    NetworkXGraphStore,
    ToolNode,
)
from yggdrasil_lm.backends.claude_code import (
    ClaudeCodeExecutor,
    _AgentRunResult,
    _build_mcp_server,
    _json_type_to_python,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    return NetworkXGraphStore()


@pytest.fixture
def agent():
    return AgentNode(
        name="TestAgent",
        system_prompt="You are a test agent.",
        max_iterations=3,
        routing_table={"default": "__END__"},
    )


@pytest.fixture
def tool_node():
    return ToolNode(
        name="echo",
        description="Echo the input",
        callable_ref="tools.echo.echo",
        input_schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
        is_async=True,
    )


@pytest.fixture
def context_node():
    return ContextNode(
        name="Hint",
        content="Always be concise.",
        priority=1,
    )


# ---------------------------------------------------------------------------
# Unit: _json_type_to_python
# ---------------------------------------------------------------------------

def test_json_type_to_python_known_types():
    assert _json_type_to_python("string")  is str
    assert _json_type_to_python("integer") is int
    assert _json_type_to_python("number")  is float
    assert _json_type_to_python("boolean") is bool
    assert _json_type_to_python("array")   is list
    assert _json_type_to_python("object")  is dict


def test_json_type_to_python_unknown_falls_back_to_str():
    assert _json_type_to_python("null")    is str
    assert _json_type_to_python("unknown") is str


# ---------------------------------------------------------------------------
# Unit: _build_mcp_server
# ---------------------------------------------------------------------------

class _FakeComposed:
    def __init__(self, tools):
        self.tools = tools


def test_build_mcp_server_returns_none_when_no_tools_registered():
    composed = _FakeComposed(tools=[])
    with patch("backends.claude_code._SDK_AVAILABLE", True):
        assert _build_mcp_server(composed, {}) is None


def test_build_mcp_server_returns_none_when_callable_not_registered(tool_node):
    composed = _FakeComposed(tools=[tool_node])
    # tool_fns dict is empty — callable_ref not registered
    with patch("backends.claude_code._SDK_AVAILABLE", True):
        assert _build_mcp_server(composed, {}) is None


def test_build_mcp_server_creates_server_when_tool_registered(tool_node):
    async def fake_echo(input):
        return input.get("message", "")

    composed = _FakeComposed(tools=[tool_node])

    fake_server = MagicMock()
    fake_decorated = MagicMock()

    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code.cc_tool", autospec=False) as mock_tool,
        patch("backends.claude_code.create_sdk_mcp_server", return_value=fake_server) as mock_create,
    ):
        # @cc_tool(name, desc, params) returns a decorator; decorator(fn) returns decorated fn
        mock_tool.return_value = lambda fn: fake_decorated

        server = _build_mcp_server(composed, {tool_node.callable_ref: fake_echo})

    assert server is fake_server
    mock_tool.assert_called_once_with(
        tool_node.name,
        tool_node.description,
        {"message": str},
    )
    mock_create.assert_called_once_with("yggdrasil-tools", tools=[fake_decorated])


def test_build_mcp_server_fallback_param_for_empty_schema():
    """Tools with no declared properties get a single 'input: str' param."""
    tn = ToolNode(
        name="no_schema_tool",
        description="A tool with no schema",
        callable_ref="my.tool",
        input_schema={},
    )
    composed = _FakeComposed(tools=[tn])

    fake_server = MagicMock()
    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code.cc_tool", autospec=False) as mock_tool,
        patch("backends.claude_code.create_sdk_mcp_server", return_value=fake_server),
    ):
        mock_tool.return_value = lambda fn: MagicMock()
        _build_mcp_server(composed, {"my.tool": AsyncMock()})

    mock_tool.assert_called_once_with("no_schema_tool", "A tool with no schema", {"input": str})


# ---------------------------------------------------------------------------
# Unit: ClaudeCodeExecutor.__init__
# ---------------------------------------------------------------------------

def test_executor_init_defaults(store):
    ex = ClaudeCodeExecutor(store)
    assert ex.store is store
    assert ex._backend is None
    assert ex._tool_fns == {}
    assert ex._allowed_tools == ["Read", "Glob", "Grep", "Bash", "WebSearch"]
    assert ex._permission_mode == "default"
    assert ex._cwd is None
    assert ex._max_budget_usd is None


def test_executor_init_custom_options(store):
    ex = ClaudeCodeExecutor(
        store,
        allowed_tools=["Bash"],
        permission_mode="acceptEdits",
        cwd="/tmp",
        max_budget_usd=0.50,
    )
    assert ex._allowed_tools == ["Bash"]
    assert ex._permission_mode == "acceptEdits"
    assert ex._cwd == "/tmp"
    assert ex._max_budget_usd == 0.50


def test_register_tool_populates_tool_fns(store):
    ex = ClaudeCodeExecutor(store)
    fn = AsyncMock()
    ex.register_tool("my.ref", fn)
    assert ex._tool_fns["my.ref"] is fn


# ---------------------------------------------------------------------------
# Integration: _execute_agent via query() path (no ToolNodes)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_execute_agent_query_path(store, agent):
    """When no ToolNodes are attached the lighter query() path is used."""
    await store.upsert_node(agent)

    fake_result = MagicMock()
    fake_result.result = "Hello from Claude Code"

    async def fake_query(prompt, options):
        from claude_agent_sdk import ResultMessage  # type: ignore[import]
        yield fake_result

    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code.ClaudeCodeExecutor._run_with_query",
              new_callable=AsyncMock,
              return_value=_AgentRunResult(text="Hello from Claude Code", tool_calls=0, cost_usd=None)) as mock_q,
        patch("backends.claude_code._build_mcp_server", return_value=None),
        patch("backends.claude_code.ClaudeAgentOptions", MagicMock()),
    ):
        ex = ClaudeCodeExecutor(store)
        ctx = await ex.run(agent.node_id, "say hello")

    mock_q.assert_called_once()
    assert ctx.outputs[agent.node_id]["text"] == "Hello from Claude Code"


# ---------------------------------------------------------------------------
# Integration: _execute_agent via ClaudeSDKClient path (with ToolNodes)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_execute_agent_sdk_client_path(store, agent, tool_node):
    """When ToolNodes are bridged ClaudeSDKClient path is used."""
    await store.upsert_node(agent)
    await store.upsert_node(tool_node)
    await store.upsert_edge(Edge.has_tool(agent.node_id, tool_node.node_id))

    async def fake_echo(input):
        return f"echo: {input}"

    fake_server = MagicMock()

    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code._build_mcp_server", return_value=fake_server),
        patch("backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "backends.claude_code.ClaudeCodeExecutor._run_with_sdk_client",
            new_callable=AsyncMock,
            return_value=_AgentRunResult(text="Tool result via SDK client", tool_calls=0, cost_usd=None),
        ) as mock_sdk,
    ):
        ex = ClaudeCodeExecutor(store)
        ex.register_tool(tool_node.callable_ref, fake_echo)
        ctx = await ex.run(agent.node_id, "use the echo tool")

    mock_sdk.assert_called_once()
    assert ctx.outputs[agent.node_id]["text"] == "Tool result via SDK client"


# ---------------------------------------------------------------------------
# Integration: routing still works after _execute_agent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_routing_between_agents(store):
    """Intent-based routing works identically to GraphExecutor."""
    agent_a = AgentNode(
        name="A",
        system_prompt="You are A.",
        routing_table={"hand off": "__END__", "default": "__END__"},
    )
    await store.upsert_node(agent_a)

    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code._build_mcp_server", return_value=None),
        patch("backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "backends.claude_code.ClaudeCodeExecutor._run_with_query",
            new_callable=AsyncMock,
            return_value=_AgentRunResult(text="I will hand off to the next agent", tool_calls=0, cost_usd=None),
        ),
    ):
        ex = ClaudeCodeExecutor(store)
        ctx = await ex.run(agent_a.node_id, "start")

    output = ctx.outputs[agent_a.node_id]
    assert output["intent"] == "hand off"


# ---------------------------------------------------------------------------
# Integration: context injected into system prompt
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_context_injected_into_system_prompt(store, agent, context_node):
    """ContextNodes attached via HAS_CONTEXT appear in the composed system prompt."""
    await store.upsert_node(agent)
    await store.upsert_node(context_node)
    await store.upsert_edge(Edge.has_context(agent.node_id, context_node.node_id))

    captured_options = {}

    async def capture_run(prompt, options):
        captured_options["system"] = options.system_prompt
        return _AgentRunResult(text="ok", tool_calls=0, cost_usd=None)

    with (
        patch("backends.claude_code._SDK_AVAILABLE", True),
        patch("backends.claude_code._build_mcp_server", return_value=None),
        patch(
            "backends.claude_code.ClaudeCodeExecutor._run_with_query",
            side_effect=capture_run,
        ),
    ):
        # ClaudeAgentOptions is called with system_prompt= so we need to track it
        real_options_calls: list[dict] = []

        def fake_options(**kwargs):
            real_options_calls.append(kwargs)
            obj = MagicMock()
            obj.system_prompt = kwargs.get("system_prompt", "")
            return obj

        with patch("backends.claude_code.ClaudeAgentOptions", side_effect=fake_options):
            ex = ClaudeCodeExecutor(store)
            await ex.run(agent.node_id, "check context")

    assert real_options_calls
    system = real_options_calls[0]["system_prompt"]
    assert "Always be concise." in system


# ---------------------------------------------------------------------------
# Import guard: missing claude-agent-sdk raises ImportError
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_sdk_raises_import_error(store, agent):
    await store.upsert_node(agent)

    with patch("backends.claude_code._SDK_AVAILABLE", False):
        ex = ClaudeCodeExecutor(store)
        with pytest.raises(ImportError, match="claude-agent-sdk"):
            await ex._execute_agent(agent, MagicMock(query="test"))
