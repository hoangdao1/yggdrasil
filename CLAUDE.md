# Yggdrasil — Agent Orientation

## Package name

The installed package is `yggdrasil_lm`. Always import from `yggdrasil_lm`, never `yggdrasil`.

```python
from yggdrasil_lm.app import GraphApp
from yggdrasil_lm import AgentNode, ToolNode, Edge, GraphExecutor
```

## Install

```bash
pip install "yggdrasil_lm @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil_lm[anthropic] @ git+..."   # Anthropic backend
pip install "yggdrasil_lm[openai] @ git+..."      # OpenAI-compatible backend
pip install "yggdrasil_lm[dev] @ git+..."         # tests + trace UI
```

Local dev:
```bash
pip install -e ".[anthropic]"
```

## Two API layers — pick one

### Layer 1 — GraphApp (use this first)

`GraphApp` wires the store, executor, and backend automatically. Start here for any new app.

```python
import asyncio
from yggdrasil_lm.app import GraphApp

async def main():
    app = GraphApp()  # reads ANTHROPIC_API_KEY from env
    agent = await app.add_agent("Bot", system_prompt="You are helpful.")
    ctx = await app.run(agent, "Hello")
    print(ctx.outputs[agent.node_id]["text"])

asyncio.run(main())
```

### Layer 2 — Low-level API (use when you need direct control)

```python
from yggdrasil_lm import AgentNode, ToolNode, Edge, NetworkXGraphStore, GraphExecutor
from yggdrasil_lm.core.executor import AgentComposer

store = NetworkXGraphStore()
# build nodes + edges manually, then:
composer = AgentComposer(store)
executor = GraphExecutor(store, composer, backend=backend)
ctx = await executor.run(entry_node_id=agent.node_id, query="Hello", strategy="sequential")
```

## Provider / backend setup

```python
# Anthropic (default) — needs ANTHROPIC_API_KEY
app = GraphApp()
app = GraphApp(provider="anthropic", api_key="sk-ant-...")

# OpenAI or compatible (Ollama, etc.)
app = GraphApp(provider="compatible", api_key="sk-...", base_url="http://localhost:11434/v1")

# Local Claude Code sub-agents (no API key needed)
app = GraphApp(provider="claude-code", cwd="/path/to/project", permission_mode="acceptEdits")
```

## GraphApp key methods

```python
agent  = await app.add_agent("Name", system_prompt="...", model="claude-sonnet-4-6")
tool   = await app.add_tool("name", callable_ref="module.func", description="...", input_schema={...})
ctx_n  = await app.add_context("Name", content="...", description="...")
prompt = await app.add_prompt("Name", template="...", description="...")

await app.connect_tool(agent, tool)        # HAS_TOOL edge
await app.connect_context(agent, ctx_n)    # HAS_CONTEXT edge
await app.connect_prompt(agent, prompt)    # HAS_PROMPT edge
await app.delegate(agent_a, agent_b)       # DELEGATES_TO edge

app.use_default_tools()   # registers built-in web_search, echo, run_python callables

ctx = await app.run(agent, "query")
print(ctx.outputs[agent.node_id]["text"])  # final text output
```

## Multi-agent routing

Route by keywords in the LLM's response. `"__END__"` terminates execution.

```python
researcher = await app.add_agent(
    "Researcher",
    system_prompt="...",
    routing_table={
        "synthesis needed": synthesizer_id,  # matched as lowercase substring
        "default": "__END__",
    },
)
```

To get a node_id before calling `add_agent`, use `create_agent()` from `yggdrasil_lm.app`, then `await store.upsert_node(node)`.

## All operations are async

Every `add_*`, `connect_*`, `run`, `store.upsert_node`, `store.get_node` call is `async`. Always use `await`. Wrap your entry point in `asyncio.run(main())`.

## Reading results

```python
ctx = await app.run(agent, "query")
ctx.outputs[agent.node_id]["text"]    # final text from a specific agent
ctx.trace                              # list of TraceEvent
ctx.hop_count                          # number of agent hops

from yggdrasil_lm import print_trace, explain_run
print_trace(ctx)          # terminal trace
explain_run(ctx, store)   # structured explanation
```

## Examples to copy from

These are all runnable and tested — read before building:

- `examples/builder_echo.py` — simplest GraphApp + tool pattern
- `examples/deterministic_routing.py` — multi-agent hand-off
- `examples/parallel_workers.py` — fan-out execution
- `examples/approval_workflow.py` — human-in-the-loop / ApprovalNode
- `examples/research_pipeline.py` — full low-level API with routing

## Common mistakes

| Mistake | Fix |
|---|---|
| `import yggdrasil` | Use `import yggdrasil_lm` |
| Calling `add_agent(...)` without `await` | All store ops are async |
| Reading `ctx.output` or `ctx.result` | Use `ctx.outputs[agent.node_id]["text"]` |
| Missing `app.use_default_tools()` | Required to register built-in tool callables |
| Forgetting `asyncio.run(main())` | All execution is async |
| Passing `strategy="parallel"` for single-agent | Default `"sequential"` works for all cases |

## Run tests

```bash
pytest                        # all tests
pytest tests/test_app_api.py  # builder API tests
pytest tests/test_examples.py # example smoke tests
```
