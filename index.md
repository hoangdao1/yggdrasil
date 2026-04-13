---
title: Home
layout: home
nav_order: 1
---

# Yggdrasil

**A Python framework for graph-native agent orchestration.**

Yggdrasil lets you define, run, and inspect multi-agent workflows as first-class graphs — with deterministic routing, structured tracing, and a built-in visualizer.

![Yggdrasil](images/Yggdrasil.jpg)

## Quick Install

```bash
pip install yggdrasil
```

## Five-Line Example

```python
from yggdrasil import GraphApp

app = GraphApp()
agent = app.create_agent("researcher", model="claude-opus-4-6")
result = await app.run(agent, "Summarize the latest AI papers")
print(result)
```

## Documentation

| Section | Description |
|---|---|
| [Start Here](docs/start-here) | Shortest path to understanding the project |
| [Your First Graph](docs/first-graph) | Beginner tutorial using the builder API |
| [Architecture](docs/architecture) | How the project is layered |
| [Workflow Patterns](docs/workflow-patterns) | Common graph patterns and recipes |
| [Observability](docs/observability) | Tracing, logging, and inspection |
| [Batch Execution](docs/batch-execution) | Running many inputs in parallel |
| [API Reference](api-reference) | Full public API reference |

## Links

- [GitHub](https://github.com/hoangdao1/yggdrasil)
- [Issues](https://github.com/hoangdao1/yggdrasil/issues)
- [Releases](https://github.com/hoangdao1/yggdrasil/releases)
