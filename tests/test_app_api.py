from __future__ import annotations

import pytest

from yggdrasil import GraphApp, create_agent, create_context, create_prompt, create_tool
from yggdrasil.backends.llm import LLMBackend, LLMResponse, ToolCall
from yggdrasil.observability import explain_run
from yggdrasil.trace_ui import inspect_trace, print_trace
from yggdrasil.retrieval import semantic_search


class StubBackend(LLMBackend):
    async def chat(self, model, system, messages, tools, max_tokens=8096) -> LLMResponse:
        return LLMResponse(text="builder ok", tool_calls=[], stop_reason="end_turn")

    def extend_messages(self, messages, response, tool_results):
        return messages


class ToolThenTextBackend(LLMBackend):
    def __init__(self) -> None:
        self.calls = 0

    async def chat(self, model, system, messages, tools, max_tokens=8096) -> LLMResponse:
        self.calls += 1
        if self.calls == 1:
            return LLMResponse(
                text="",
                tool_calls=[ToolCall(id="tc-1", name="echo", input={"text": "hello"})],
                stop_reason="tool_use",
            )
        return LLMResponse(text="done", tool_calls=[], stop_reason="end_turn")

    def extend_messages(self, messages, response, tool_results):
        return messages


@pytest.mark.asyncio
async def test_graph_app_runs_simple_agent():
    app = GraphApp(backend=StubBackend())
    agent = await app.add_agent("Assistant")

    ctx = await app.run(agent, "hello")

    assert ctx.outputs[agent.node_id]["text"] == "builder ok"


@pytest.mark.asyncio
async def test_graph_app_connects_context_and_tool():
    app = GraphApp(backend=StubBackend())
    agent = await app.add_agent("Assistant")
    tool = await app.add_tool(
        "echo",
        callable_ref="yggdrasil.tools.echo.echo",
        input_schema={"type": "object", "properties": {}},
    )
    context = await app.add_context("Fact", "Useful fact")

    tool_edge = await app.connect_tool(agent, tool)
    ctx_edge = await app.connect_context(agent, context, weight=0.8)

    assert tool_edge.src_id == agent.node_id
    assert ctx_edge.weight == 0.8


def test_helper_constructors_create_nodes():
    agent = create_agent("A")
    tool = create_tool("echo", callable_ref="yggdrasil.tools.echo.echo")
    context = create_context("C", "content")
    prompt = create_prompt("P", "You are helpful.")

    assert agent.name == "A"
    assert tool.callable_ref == "yggdrasil.tools.echo.echo"
    assert context.content == "content"
    assert prompt.template == "You are helpful."


def test_preferred_namespaces_are_importable():
    assert callable(inspect_trace)
    assert callable(print_trace)
    assert callable(explain_run)
    assert callable(semantic_search)


@pytest.mark.asyncio
async def test_run_and_explain():
    app = GraphApp(backend=ToolThenTextBackend())
    agent = await app.add_agent("Assistant", system_prompt="Use the echo tool.")
    tool = await app.add_tool(
        "echo",
        callable_ref="yggdrasil.tools.echo.echo",
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
    )
    context = await app.add_context("Playbook", "Escalate duplicate billing to finance.")
    await app.connect_tool(agent, tool)
    await app.connect_context(agent, context, weight=0.9)
    app.use_default_tools()

    ctx = await app.run(agent, "help customer")
    run_summary = explain_run(ctx)

    assert run_summary.tool_calls[0].tool_name == "echo"
    assert run_summary.summary.tool_call_count == 1
