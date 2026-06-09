# Repo Map

This is a quick navigation guide for contributors and LLM coding tools.

## Top-Level Files

- `README.md`: product overview and first-run path
- `API_REFERENCE.md`: exhaustive reference
- `COMPARISONS.md`: positioning and mental-model comparisons
- `CONTRIBUTING.md`: contributor workflow and design rules

## Package Layout

- `yggdrasil/app.py`: beginner-facing builder/helpers
- `yggdrasil/core/`: nodes, edges, store, executor, and runtime support modules
- `yggdrasil/backends/`: LLM backend adapters
- `yggdrasil/tools/`: built-in tools and registry
- `yggdrasil/exporters/`: trace export
- `yggdrasil/viz/`: browser trace UI

## Where To Put Changes

- New tutorial-friendly API: `yggdrasil/app.py`
- New runtime semantics: `yggdrasil/core/`
- New built-in tool: `yggdrasil/tools/`
- New provider integration: `yggdrasil/backends/`
- New operational docs: `docs/`

## Topic Docs

- `docs/neurosymbolic-reasoning.md`: `ReasonerNode` + the built-in Datalog engine, and why Datalog over a plain Python function
- `docs/explainable-systems.md`: run-time explainability (`explain_run`)
- `docs/observability.md`: tracing and debugging

## Best Entry Points For Reading

1. `yggdrasil/app.py`
2. `yggdrasil/core/nodes.py`
3. `yggdrasil/core/edges.py`
4. `yggdrasil/core/store.py`
5. `yggdrasil/core/executor.py`
