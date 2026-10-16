"""Tests for ClaudeCodeExecutor.

All claude_agent_sdk calls are mocked — no Claude Code CLI required.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yggdrasil_lm import (
    AgentNode,
    ContextNode,
    Edge,
    ExecutionContext,
    NetworkXGraphStore,
    ToolNode,
)
from yggdrasil_lm.backends.claude_code import (
    SESSION_OPTION_NAMES,
    ClaudeCodeAgentError,
    ClaudeCodeExecutor,
    _AgentRunResult,
    _build_mcp_server,
    _json_type_to_python,
    _sdk_tool_schema,
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
        model="claude-haiku-4-5-20251001",
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
    with patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True):
        assert _build_mcp_server(composed, {}) is None


def test_build_mcp_server_returns_none_when_callable_not_registered(tool_node):
    composed = _FakeComposed(tools=[tool_node])
    # tool_fns dict is empty — callable_ref not registered
    with patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True):
        assert _build_mcp_server(composed, {}) is None


def test_build_mcp_server_creates_server_when_tool_registered(tool_node):
    async def fake_echo(input):
        return input.get("message", "")

    composed = _FakeComposed(tools=[tool_node])

    fake_server = MagicMock()
    fake_decorated = MagicMock()

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code.cc_tool", autospec=False) as mock_tool,
        patch(
            "yggdrasil_lm.backends.claude_code.create_sdk_mcp_server",
            return_value=fake_server,
        ) as mock_create,
    ):
        # @cc_tool(name, desc, params) returns a decorator; decorator(fn) returns decorated fn
        mock_tool.return_value = lambda fn: fake_decorated

        server = _build_mcp_server(composed, {tool_node.callable_ref: fake_echo})

    assert server is fake_server
    # The full JSON schema is forwarded, so `required` survives (the SDK's
    # {name: type} shorthand would mark every property required).
    mock_tool.assert_called_once_with(
        tool_node.name,
        tool_node.description,
        tool_node.input_schema,
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
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code.cc_tool", autospec=False) as mock_tool,
        patch(
            "yggdrasil_lm.backends.claude_code.create_sdk_mcp_server",
            return_value=fake_server,
        ),
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
        yield fake_result

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
              new_callable=AsyncMock,
              return_value=_AgentRunResult(text="Hello from Claude Code", tool_calls=0, cost_usd=None)) as mock_q,
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", MagicMock()),
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
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=fake_server),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_sdk_client",
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
        model="claude-haiku-4-5-20251001",
        system_prompt="You are A.",
        routing_table={"hand off": "__END__", "default": "__END__"},
    )
    await store.upsert_node(agent_a)

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
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
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch(
            "yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
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

        with patch(
            "yggdrasil_lm.backends.claude_code.ClaudeAgentOptions",
            side_effect=fake_options,
        ):
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

    with patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", False):
        ex = ClaudeCodeExecutor(store)
        with pytest.raises(ImportError, match="claude-agent-sdk"):
            await ex._execute_agent(agent, MagicMock(query="test"))


@pytest.mark.asyncio
async def test_agent_error_emits_trace_event(store, agent):
    await store.upsert_node(agent)

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
            new_callable=AsyncMock,
            side_effect=ClaudeCodeAgentError("auth", "Not logged in"),
        ),
    ):
        ex = ClaudeCodeExecutor(store)
        ctx = ExecutionContext(query="start")
        with pytest.raises(ClaudeCodeAgentError):
            await ex._execute_agent(agent, ctx)

    errors = [event for event in ctx.trace if event.event_type == "error"]
    assert errors
    assert errors[0].payload["source"] == "claude_code"
    assert errors[0].payload["subtype"] == "auth"


# ---------------------------------------------------------------------------
# pause_before must be honored (this override replaces the base method)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_execute_agent_honors_pause_before(store):
    """A pause_before AgentNode must suspend before any agent work — even the
    entry node of a sub-graph step. Regression: the override previously dropped
    the base GraphExecutor's pause_before gate, so human-review pauses were
    silently skipped under the Claude Code executor."""
    node = AgentNode(
        name="gate", model="claude-haiku-4-5-20251001", system_prompt="s",
        max_iterations=3, pause_before=True, wait_for_input="Approve to continue.",
    )
    await store.upsert_node(node)
    ex = ClaudeCodeExecutor(store)
    ctx = ExecutionContext(query="start")

    # The pause is checked before the SDK guard, so it fires even with no SDK.
    with patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", False):
        result = await ex._execute_agent(node, ctx)

    assert result["status"] == "paused"
    assert ctx.is_paused()
    pause = ctx.state.pending_pause
    assert pause is not None
    assert pause.reason == "pause_before"
    assert pause.waiting_for == "Approve to continue."


# ---------------------------------------------------------------------------
# Tool schemas: optional arguments stay optional
# ---------------------------------------------------------------------------

def test_build_mcp_server_keeps_optional_args_optional():
    """A tool whose schema lists only some properties as required must not be
    advertised as requiring them all."""
    schema = {
        "type": "object",
        "properties": {"path": {"type": "string"}, "dry_run": {"type": "boolean"}},
        "required": ["path"],
    }
    tn = ToolNode(name="t", description="d", callable_ref="r", input_schema=schema)
    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code.cc_tool", autospec=False) as mock_tool,
        patch("yggdrasil_lm.backends.claude_code.create_sdk_mcp_server", return_value=MagicMock()),
    ):
        mock_tool.return_value = lambda fn: MagicMock()
        _build_mcp_server(_FakeComposed(tools=[tn]), {"r": AsyncMock()})
    advertised = mock_tool.call_args.args[2]
    assert advertised["required"] == ["path"]


def test_sdk_tool_schema_shorthand_without_type():
    assert _sdk_tool_schema({"properties": {"x": {"type": "number"}}}) == {"x": float}
    assert _sdk_tool_schema(None) == {"input": str}


# ---------------------------------------------------------------------------
# Session options: isolation, per-node overrides
# ---------------------------------------------------------------------------

def test_session_kwargs_defaults_unchanged(store, agent):
    """With no session options the options built are exactly today's."""
    ex = ClaudeCodeExecutor(store, cwd="/w")
    kw = ex._session_kwargs(agent, "sys", {})
    assert kw == {
        "system_prompt": "sys",
        "allowed_tools": ["Read", "Glob", "Grep", "Bash", "WebSearch"],
        "mcp_servers": None,
        "max_turns": 3,
        "model": "claude-haiku-4-5-20251001",
        "permission_mode": "default",
        "cwd": "/w",
        "env": {"ANTHROPIC_API_KEY": ""},
    }


def test_session_kwargs_isolation_options_passed(store, agent):
    ex = ClaudeCodeExecutor(
        store,
        setting_sources=[],
        skills=[],
        strict_mcp_config=True,
        tools=["Read", "Write"],
        disallowed_tools=["Agent", "Task"],
        env={"ENABLE_CLAUDEAI_MCP_SERVERS": "false"},
    )
    with patch("yggdrasil_lm.backends.claude_code._sdk_option_fields", return_value=None):
        kw = ex._session_kwargs(agent, "sys", {})
    assert kw["setting_sources"] == []
    assert kw["skills"] == []
    assert kw["strict_mcp_config"] is True
    assert kw["tools"] == ["Read", "Write"]
    assert kw["disallowed_tools"] == ["Agent", "Task"]
    assert kw["env"] == {"ENABLE_CLAUDEAI_MCP_SERVERS": "false", "ANTHROPIC_API_KEY": ""}


def test_session_kwargs_api_key_cannot_be_overridden(store, agent):
    ex = ClaudeCodeExecutor(store, env={"ANTHROPIC_API_KEY": "sk-x"})
    assert ex._session_kwargs(agent, "s", {})["env"]["ANTHROPIC_API_KEY"] == ""


def test_session_kwargs_node_overrides_executor(store):
    node = AgentNode(
        name="n", model="claude-haiku-4-5-20251001", max_iterations=7, max_tokens=4000,
        attributes={"claude_code": {
            "effort": "low",
            "disallowed_tools": ["Agent"],
            "env": {"A": 1},
            "max_output_tokens": 12000,
        }},
    )
    ex = ClaudeCodeExecutor(store, effort="high", disallowed_tools=["Agent", "Task"], env={"B": "2"})
    with patch("yggdrasil_lm.backends.claude_code._sdk_option_fields", return_value=None):
        kw = ex._session_kwargs(node, "s", {})
    assert kw["effort"] == "low"
    assert kw["disallowed_tools"] == ["Agent"]
    assert kw["max_turns"] == 7
    assert kw["env"] == {"B": "2", "A": "1", "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "12000",
                         "ANTHROPIC_API_KEY": ""}


def test_session_kwargs_honor_max_tokens(store, agent):
    ex = ClaudeCodeExecutor(store, honor_max_tokens=True)
    assert ex._session_kwargs(agent, "s", {})["env"]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] == str(agent.max_tokens)


def test_session_kwargs_drops_fields_the_sdk_lacks(store, agent):
    """An older SDK is never handed a keyword it would refuse."""
    ex = ClaudeCodeExecutor(store, effort="low", skills=[])
    with patch("yggdrasil_lm.backends.claude_code._sdk_option_fields", return_value={"skills"}):
        kw = ex._session_kwargs(agent, "s", {})
    assert "effort" not in kw
    assert kw["skills"] == []


def test_unknown_session_option_refused(store):
    with pytest.raises(TypeError, match="bogus"):
        ClaudeCodeExecutor(store, bogus=1)


def test_unknown_node_option_refused(store):
    node = AgentNode(name="n", attributes={"claude_code": {"nope": 1}})
    ex = ClaudeCodeExecutor(store)
    with pytest.raises(ValueError, match="nope"):
        ex._session_kwargs(node, "s", {})


def test_session_option_names_cover_isolation():
    for name in ("tools", "disallowed_tools", "setting_sources", "strict_mcp_config",
                 "skills", "agents", "effort", "thinking"):
        assert name in SESSION_OPTION_NAMES


@pytest.mark.asyncio
async def test_execute_agent_passes_session_kwargs(store, agent):
    """The options the SDK receives are the ones _session_kwargs builds."""
    await store.upsert_node(agent)
    captured = {}

    def fake_options(**kw):
        captured.update(kw)
        return MagicMock()

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
              new_callable=AsyncMock,
              return_value=_AgentRunResult(text="ok", tool_calls=0, cost_usd=None)),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", fake_options),
        patch("yggdrasil_lm.backends.claude_code._sdk_option_fields", return_value=None),
    ):
        ex = ClaudeCodeExecutor(store, setting_sources=[], strict_mcp_config=True)
        await ex.run(agent.node_id, "hi")
    assert captured["setting_sources"] == []
    assert captured["strict_mcp_config"] is True


# ---------------------------------------------------------------------------
# agent_end carries the whole closing message
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_end_carries_the_full_closing_message(store, agent):
    """`text_summary` stays a 120-character preview; `full_response` is the whole text,
    and the module flag says so for callers that feature-detect it."""
    from yggdrasil_lm.backends import claude_code
    await store.upsert_node(agent)
    closing = "summary line " * 40          # well past the 120-character preview

    with (
        patch("yggdrasil_lm.backends.claude_code._SDK_AVAILABLE", True),
        patch("yggdrasil_lm.backends.claude_code._build_mcp_server", return_value=None),
        patch("yggdrasil_lm.backends.claude_code.ClaudeAgentOptions", MagicMock()),
        patch(
            "yggdrasil_lm.backends.claude_code.ClaudeCodeExecutor._run_with_query",
            new_callable=AsyncMock,
            return_value=_AgentRunResult(text=closing, tool_calls=0, cost_usd=None),
        ),
    ):
        ex = ClaudeCodeExecutor(store)
        ctx = await ex.run(agent.node_id, "start")

    ends = [e for e in ctx.trace if e.event_type == "agent_end"]
    assert len(ends) == 1
    assert ends[0].payload["full_response"] == closing
    assert ends[0].payload["text_summary"] == closing[:120]
    assert claude_code.AGENT_END_FULL_RESPONSE is True
