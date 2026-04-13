# Yggdrasil - Observable and Explainable Agent-as-Graph library

Build agent systems as graphs, where agents, tools, context, and workflow state live in one runtime.

`yggdrasil` is a Python framework for graph-native orchestration. The core idea is simple:

- store agents, tools, prompts, and context as graph nodes
- connect them with typed edges
- let the runtime compose and execute that graph at query time

The strongest use case is not just "build an agent."
It is:

- build an agent system that changes over time
- manage that system as graph data
- explain why it behaved the way it did

The intended workflow is:

1. define agents, tools, and context as graph nodes
2. connect them with typed edges
3. run queries through the graph
4. inspect behavior with structured traces and `explain_run`

## Illustration

![Yggdrasil](images/Yggdrasil.jpg)

Yggdrasil is named after the world tree because the project is meant to connect distinct realms of work in one traversable system:

- data and memory
- humans and approvals
- deterministic business logic
- probabilistic reasoning with LLMs
- durable workflow state across all of them

## Start Here

If you are new to the project, use this order:

1. [Start Here](docs/start-here.md)
2. [Your First Graph](docs/first-graph.md)
3. [Choose a Backend](docs/choose-backend.md)
4. [Control Plane Thesis](docs/control-plane-thesis.md)
5. [Explainable Agent Systems](docs/explainable-systems.md)
6. [Flagship Workflow](docs/flagship-workflow.md)
7. [Observability](docs/observability.md)
8. [Visualizer Web UI](docs/visualizer-web-ui.md)

Skip these until later:

- [Advanced configuration](docs/advanced-configuration.md)
- [Batch execution](docs/batch-execution.md)
- [Long-running workflows](docs/long-running-workflows.md)
- [API reference](API_REFERENCE.md)

## Install

Requirements: Python 3.11+

Install directly from Git without cloning:

```bash
pip install "yggdrasil @ git+https://github.com/hoangdao1/yggdrasil.git"
```

Add extras the same way:

```bash
pip install "yggdrasil[anthropic] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[openai] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[embeddings] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[observe] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[neo4j] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[claude-code] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[viz] @ git+https://github.com/hoangdao1/yggdrasil.git"
pip install "yggdrasil[dev] @ git+https://github.com/hoangdao1/yggdrasil.git"
```

Or clone the repo for local development:

```bash
git clone https://github.com/hoangdao1/yggdrasil.git
cd yggdrasil
pip install -e .
```

Add the extras you need:

```bash
pip install -e ".[anthropic]"    # default Anthropic backend
pip install -e ".[openai]"       # OpenAI-compatible backend
pip install -e ".[embeddings]"   # semantic retrieval
pip install -e ".[observe]"      # OpenTelemetry export
pip install -e ".[neo4j]"        # Neo4j graph store
pip install -e ".[claude-code]"  # Claude Code sub-agent backend
pip install -e ".[viz]"          # browser trace visualizer
pip install -e ".[dev]"          # tests + rich trace UI
```

## Fastest Working Example

90% of use cases fit in five lines. The beginner-friendly path uses `GraphApp`, which wires up the store, executor, and backend automatically.

```python
import asyncio
from yggdrasil.app import GraphApp


async def main() -> None:
    app = GraphApp()
    agent = await app.add_agent("Bot", system_prompt="You are a helpful assistant.")
    ctx = await app.run(agent, "What is Python 3.13?")
    print(ctx.outputs[agent.node_id]["text"])


asyncio.run(main())
```

Need tools? Attach the built-ins and go:

```python
import asyncio
from yggdrasil.app import GraphApp


async def main() -> None:
    app = GraphApp()

    agent = await app.add_agent(
        "Researcher",
        system_prompt="You are a technical researcher.",
        model="claude-sonnet-4-6",
    )
    app.use_default_tools()  # registers built-in web_search, echo, run_python

    ctx = await app.run(agent, "What changed in Python 3.13?")
    print(ctx.outputs[agent.node_id]["text"])


asyncio.run(main())
```

See [API reference §2 Builder API](API_REFERENCE.md#2-builder-api) for the full `GraphApp` surface, including `add_tool(fn=..., attach=True, agent=...)`, `add_context`, `add_prompt`, and `delegate`.

## Why This Project Exists

Many agent systems start as prompt-and-tool loops, then become operational systems:

- new policies appear
- review steps are added
- context sources change
- capabilities vary by tenant or environment
- operators need to explain decisions

`yggdrasil` is designed for that phase.

It treats the agent system as something that should be:

- versioned
- diffed
- migrated
- inspected
- explained

## Core Mental Model

Keep these four ideas in mind:

1. Composition is traversal.
   Agents discover tools, prompts, and context by following graph edges.

2. Execution is traversal.
   Running a query is a walk through the graph.

3. Routing is explicit.
   Multi-agent handoff is represented in the graph and resolved by the executor.

4. Outputs can become graph state.
   Runs produce traces and can materialize runtime context.

## API Layers

There are two ways to use the project.

### Beginner API

Use this first. Import from `yggdrasil.app`:

- `GraphApp`
- `create_agent()`
- `create_tool()`
- `create_context()`
- `create_prompt()`
- `create_executor()`

### Low-Level Runtime API

Use this when you need direct control:

- `AgentNode`, `ToolNode`, `ContextNode`, `PromptNode`
- `Edge`
- `NetworkXGraphStore`
- `GraphExecutor`

## What The Project Already Does Well

- dynamic tool and context composition from graph edges
- multi-agent routing
- sequential, fan-out, and DAG execution strategies
- batch execution with concurrency, checkpointing, and resume
- structured traces with terminal and browser views
- typed run explanations with hop summaries, routing decisions, and tool call details
- workflow runtime features such as pause/resume, approvals, and checkpoints

For the browser trace viewer specifically, see [Visualizer Web UI](docs/visualizer-web-ui.md).

## Recommended Learning Path

### Learn the runtime

- [Your First Graph](docs/first-graph.md)
- [Workflow Patterns](docs/workflow-patterns.md)
- [Observability](docs/observability.md)
- [Explainable Agent Systems](docs/explainable-systems.md)
- [Why behavior changed](docs/why-behavior-changed.md)
- [Flagship Workflow](docs/flagship-workflow.md)

### Run practical local examples

- [examples/builder_echo.py](examples/builder_echo.py)
- [examples/deterministic_routing.py](examples/deterministic_routing.py)
- [examples/approval_workflow.py](examples/approval_workflow.py)
- [examples/parallel_workers.py](examples/parallel_workers.py)
- [examples/research_pipeline.py](examples/research_pipeline.py)

### Learn provider setup

- [Choose a Backend](docs/choose-backend.md)
- [Advanced configuration](docs/advanced-configuration.md)

### Learn the platform layer

- [Control Plane Thesis](docs/control-plane-thesis.md)
- [Architecture](docs/architecture.md)
- [Repo map](docs/repo-map.md)

## Contributor Docs

- [Contributing](CONTRIBUTING.md)
- [Architecture](docs/architecture.md)
- [Repo map](docs/repo-map.md)

## Reference Docs

- [API reference](API_REFERENCE.md)

## Project Status

This repo now has a clearer split:

- `README.md`: first-run path
- `docs/`: tutorials, architecture, and operations
- `API_REFERENCE.md`: exhaustive reference
- `yggdrasil/app.py`: beginner-facing builder API
- `yggdrasil/core/`: low-level runtime
