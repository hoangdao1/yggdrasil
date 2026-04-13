# Contributing

This project is easiest to work on when we keep the layering clear:

- beginner-facing APIs and docs should optimize for time-to-first-success
- core runtime code should stay explicit and debuggable
- advanced/platform features should build on the core runtime instead of leaking into every example
- the graph should remain the control surface for systems that change over time
- behavior should remain explainable from graph state plus runtime traces

## Start Here

Read these in order:

1. [README.md](README.md)
2. [Start Here](docs/start-here.md)
3. [Architecture](docs/architecture.md)
4. [Repo Map](docs/repo-map.md)

## Repo Map

- `yggdrasil/app.py`: beginner-friendly builder/helpers
- `yggdrasil/core/`: execution engine, nodes, edges, store
- `yggdrasil/backends/`: model backends
- `yggdrasil/tools/`: built-in tool modules and registry
- `yggdrasil/exporters/`: trace export
- `docs/`: tutorials, architecture, operations
- `tests/`: behavior-driven test coverage

## Design Rules

- Keep the low-level graph primitives stable.
- Prefer additive changes over breaking renames on the top-level API.
- When adding a new feature, decide whether it belongs in:
  - beginner API
  - core runtime
  - platform/admin layer
- Ask whether the feature improves one of these:
  - control-plane management of changing systems
  - explainability of runtime behavior
  - safe evolution over time
- Add at least one focused test and one documentation touchpoint for user-facing features.

## Guidance For LLM Coding Tools

LLM agents do better in this repo when changes stay local and explicit.

- Prefer adding a small helper over making `GraphExecutor` more magical.
- Reuse existing node/edge helpers instead of open-coding graph mutations.
- Put importable built-in tools in `yggdrasil/tools/*.py`, not only in the registry.
- Keep docs example-first; reference docs should explain, not teach.

## Common Tasks

### Add a built-in tool

1. Add an importable module in `yggdrasil/tools/`
2. Register it in `yggdrasil/tools/registry.py`
3. Add or update tests
4. Update the relevant tutorial or README example

### Add a new runtime capability

1. Prefer the smallest layer that can own it
2. Add tests around the user-visible behavior
3. Update `docs/architecture.md` if it changes subsystem boundaries
4. Add a short usage example when possible

### Add a new backend

1. Implement the `LLMBackend` contract
2. Add a targeted test for chat + message extension behavior
3. Document backend setup in `docs/choose-backend.md`

## Verification

Typical local verification:

```bash
python3 -m pytest tests -q
```

For a narrower pass during iteration:

```bash
python3 -m pytest tests/test_devex.py tests/test_executor.py -q
```
