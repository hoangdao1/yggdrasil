---
title: Your First Graph
parent: Docs
nav_order: 2
---

# Your First Graph

This tutorial uses the beginner-friendly builder API.

## Goal

Create one agent, attach one built-in tool, run one query.

## Example

```python
import asyncio

from yggdrasil import GraphApp


async def main() -> None:
    app = GraphApp(provider="compatible", api_key="sk-...")

    agent = await app.add_agent(
        "Assistant",
        system_prompt="Use the echo tool when it helps.",
    )

    tool = await app.add_tool(
        "echo",
        callable_ref="yggdrasil.tools.echo.echo",
        description="Echoes the input",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )

    await app.connect_tool(agent, tool)
    app.use_default_tools()

    ctx = await app.run(agent, "Use the echo tool to repeat: hello graph")
    print(ctx.outputs[agent.node_id]["text"])


asyncio.run(main())
```

## What Happened

- `GraphApp` created an in-memory graph store and executor
- `add_agent()` inserted an `AgentNode`
- `add_tool()` inserted a `ToolNode`
- `connect_tool()` created the `HAS_TOOL` edge
- `use_default_tools()` registered the built-in Python callable
- `run()` executed the graph starting at that agent

## What To Learn Next

- [Choose a Backend](choose-backend.md)
- [Workflow Patterns](workflow-patterns.md)
- [Observability](observability.md)
