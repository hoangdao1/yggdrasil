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
sub    = await app.add_subgraph("Pipeline", entry=first_agent, exit=last_agent)

await app.connect_tool(agent, tool)        # HAS_TOOL edge
await app.connect_context(agent, ctx_n)    # HAS_CONTEXT edge
await app.connect_prompt(agent, prompt)    # HAS_PROMPT edge
await app.delegate(agent_a, agent_b)       # DELEGATES_TO edge

app.use_default_tools()   # registers built-in web_search, echo, run_python callables

ctx = await app.run(agent, "query")
print(ctx.outputs[agent.node_id]["text"])  # final text output
```

## Images and visual RAG

### Inline image query

Pass an image alongside the text question using `build_query` from `yggdrasil_lm.media`:

```python
from yggdrasil_lm.media import build_query, image_from_file, image_from_url, image_from_base64

# From a URL
query = build_query("What's in this image?", image_from_url("https://example.com/photo.jpg"))

# From a local file (auto-detects MIME type from extension)
query = build_query("Describe this diagram.", image_from_file("diagram.png"))

# From pre-encoded base64
query = build_query("Analyse this chart.", image_from_base64(b64_str, "image/png"))

ctx = await app.run(agent, query)
```

Multiple images are supported — pass them as additional arguments to `build_query`.

### Visual RAG — persistent image context

Attach an image `ContextNode` to an agent so it is included automatically on every call:

```python
# URL-based
photo = await app.add_image_context("Product photo", url="https://cdn.example.com/p.jpg")

# Local file
diagram = await app.add_image_context("Architecture diagram", path="arch.png")

# Pre-encoded base64
chart = await app.add_image_context("Chart", data=b64_str, media_type="image/png")

await app.connect_context(agent, photo)
ctx = await app.run(agent, "Describe this product.")   # image injected automatically
```

Image context nodes are injected as content blocks in the **user message**, not the system prompt. Text context nodes continue to go into the system prompt.

## Reusable sub-graphs (GraphNode)

Wrap a chain of nodes behind a single `GraphNode` so it can be reused across parents. The sub-graph runs in a child context — inner outputs do not leak into the parent.

```python
sub = await app.add_subgraph(
    "ReviewPipeline",
    entry=extractor,                            # AgentNode or node_id
    exit=critic,                                # output the parent sees (defaults to entry)
    strategy="sequential",                      # | "parallel" | "topological"
    input_map={"product_text": "current_product"},  # parent state → sub-graph state.data
    scope_outputs=True,                         # default — keep inner outputs scoped
)
ctx = await app.run(sub, query="...", state={"current_product": "..."})
ctx.outputs[sub.node_id]["text"]                # exit node's output
```

Errors: a missing `entry_node_id` raises; cycles and recursion depth >16 raise. The whole sub-run can be retried via `execution_policy`.

### Testing sub-graphs hermetically

`yggdrasil_lm.testing` exposes a `StubBackend` plus `end_turn()` / `tool_use()` helpers — pre-recorded responses, zero network. The `GraphApp` exposes two test-friendly entry points:

```python
from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.testing import StubBackend, end_turn

# Dry run: assert wiring (input_map, exit_node_id) without invoking an LLM.
info = await app.dry_run_subgraph(sub, inputs={"raw": "hi"})
assert info["state_overlay"] == {"alias": "hi"}
assert info["exit_node_id"] == critic.node_id

# Replay: run the sub-graph in isolation with canned LLM responses.
backend = StubBackend([end_turn("CLAIM: fast"), end_turn("VERDICT: HYPE")])
app = GraphApp(backend=backend)
ctx = await app.run_subgraph(sub, inputs={"product": "..."}, query="review")
assert "HYPE" in ctx.outputs[sub.node_id]["text"]
assert len(backend.calls) == 2   # backend records each chat() call
```

- `app.run_subgraph(sub, inputs=..., query=..., **run_kwargs)` — runs a `GraphNode` as the top-level entry; `inputs` are merged into `state.data`.
- `app.dry_run_subgraph(sub, inputs=...)` — resolves entry/exit/strategy/query/state-overlay without firing the executor.
- `StubBackend(responses)` — `responses` is a list (returned in order, loops when exhausted) or a callable `(model, system, messages, tools) -> LLMResponse`. The `.calls` attribute records every invocation.

### Record once against a real LLM, replay forever

`RecordingBackend` wraps any real backend and writes each `chat()` call to a JSON fixture; `StubBackend.from_recording(path)` replays the fixture deterministically with no network.

```python
from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.backends.llm import AnthropicBackend
from yggdrasil_lm.testing import RecordingBackend, StubBackend

# First run — hits the real API, writes the fixture
app = GraphApp(backend=RecordingBackend(AnthropicBackend(), "tests/fixtures/critic.json"))
ctx = await app.run(agent, "review this product")

# Subsequent runs — fully offline, byte-identical
app = GraphApp(backend=StubBackend.from_recording("tests/fixtures/critic.json"))
```

Recordings are coupled to prompt text — change the system prompt or model and you must re-record (delete the fixture, run again with the real backend wired up).

### Gating live-LLM tests

`tests/conftest.py` registers a `live_llm` marker. Tests marked with it are skipped by default; set `YGG_LIVE_LLM=1` to run them.

```python
@pytest.mark.live_llm
async def test_critic_flags_hype():
    app = GraphApp()  # real backend
    ...
```

```bash
YGG_LIVE_LLM=1 pytest -m live_llm
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
- `examples/subgraph_reuse.py` — reusable `GraphNode` sub-graph (extractor → critic) run against any backend
- `examples/image_query_and_visual_rag.py` — inline image query and persistent visual RAG

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
