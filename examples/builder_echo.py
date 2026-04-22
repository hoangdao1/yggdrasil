"""Runnable local example: GraphApp + built-in echo tool.

Run:
    python -m examples.builder_echo
"""

from __future__ import annotations

import asyncio

from yggdrasil_lm import GraphApp, print_trace

from examples._stub_backend import SequenceBackend, end_turn, tool_use


async def run_demo() -> None:
    app = GraphApp(
        backend=SequenceBackend(
            [
                tool_use("call-1", "echo", {"text": "hello from yggdrasil"}),
                end_turn("Finished after calling the echo tool."),
            ]
        )
    )

    agent = await app.add_agent(
        "Assistant",
        system_prompt="Use the echo tool when it helps answer the query.",
    )
    tool = await app.add_tool(
        "echo",
        callable_ref="tools.echo.echo",
        description="Echoes input text",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )

    await app.connect_tool(agent, tool)
    app.use_default_tools()

    ctx = await app.run(agent, "Repeat a short greeting with the tool.")

    print("\n--- Final Output ---")
    print(ctx.outputs[agent.node_id]["text"])
    print("\n--- Trace ---")
    print_trace(ctx)


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
