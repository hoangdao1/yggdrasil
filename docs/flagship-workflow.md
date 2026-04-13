# Flagship Workflow: An Agent System That Changes Over Time

This is the flagship use case for `yggdrasil`.

## Scenario

A support workflow starts simple:

- one intake agent
- one billing playbook
- one normalization tool

Later, policy changes:

- high-value billing disputes must escalate to manager review
- the playbook changes
- the routing policy changes

The application should not need to be conceptually rewritten. The graph should change, and the runtime should be able to explain the result.

## Why `yggdrasil` Fits

This workflow combines:

- graph-defined composition
- workflow state
- explainable context selection
- deterministic routing
- graph evolution over time

## Runnable Example

See:

- [examples/research_pipeline.py](../examples/research_pipeline.py)

That example demonstrates a multi-agent pipeline where an intake agent hands off work to a specialist, showing graph-defined composition and explainable execution.

## What This Shows

The important value is not only that the workflow runs.

The important value is that you can answer:

- what changed?
- why did the system route differently?
- which context was active in version 1 vs version 2?
- which policy change caused the new path?

That is the control-plane story.
