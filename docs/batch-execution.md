---
title: Batch Execution
parent: Docs
nav_order: 7
---

# Batch Execution

Use `BatchExecutor` when the same graph should run over many items.

This is the right fit for:

- document summarization over a corpus
- evaluating a workflow over many test cases
- enrichment pipelines where each item runs independently
- map-reduce style agent workloads

`BatchExecutor` is built for operational runs, not just a `for` loop around `executor.run(...)`.

It adds:

- bounded concurrency
- per-item failure isolation
- progress callbacks
- checkpointing to the graph store
- resume after interruption
- optional reduce over successful outputs

## Basic Example

```python
from yggdrasil import NetworkXGraphStore, create_executor
from yggdrasil.batch import BatchExecutor


async def run_batch(agent, documents) -> None:
    store = NetworkXGraphStore()
    executor = create_executor(store=store)
    batch = BatchExecutor(store, executor, concurrency=5)

    run = await batch.run(
        agent_node_id=agent.node_id,
        items=documents,
        query_fn=lambda doc: f"Summarize: {doc['title']}",
        context_fn=lambda doc: doc["body"],
    )

    print(run.status)
    print(run.completed, run.failed, run.total)
```

How it works:

- `query_fn(item)` builds the per-item query
- `context_fn(item)` optionally injects per-item context without mutating the graph
- each item runs through its own `executor.run(...)`
- one item failing does not cancel the whole batch

## Progress And Reduce

Use `on_progress` to monitor a long run and `reduce_fn` to combine successful outputs.

```python
run = await batch.run(
    agent_node_id=agent.node_id,
    items=documents,
    query_fn=lambda doc: f"Summarize: {doc['title']}",
    context_fn=lambda doc: doc["body"],
    on_progress=lambda r: print(f"{r.progress:.0%} complete"),
    reduce_fn=lambda outputs: "\n\n".join(o["text"] for o in outputs if "text" in o),
)

print(run.reduced_output)
```

Use `reduce_fn` when:

- each item is independent
- you want one combined result after the map phase
- partial success is acceptable

## Checkpointing And Resume

Checkpointing is enabled by default.

That means batch state is persisted into the graph store as runtime `ContextNode`s, so a process crash does not lose the whole run.

```python
run = await batch.run(
    agent_node_id=agent.node_id,
    items=documents,
    query_fn=lambda doc: f"Summarize: {doc['title']}",
    checkpoint=True,
)

# Later, after a restart:
run = await batch.resume(
    run.run_id,
    documents,
    query_fn=lambda doc: f"Summarize: {doc['title']}",
)
```

Resume behavior:

- completed items are skipped
- items that were still running are treated as pending
- reduced output is recomputed if you pass `reduce_fn` on resume

## Understanding Results

`BatchRun` gives you aggregate state:

- `status`
- `completed`
- `failed`
- `pending`
- `running`
- `progress`
- `reduced_output`

Each item also has a `BatchItemResult`:

- `status`
- `output`
- `error`
- `started_at`
- `ended_at`
- `duration_seconds`

Example:

```python
for item_id, result in run.results.items():
    if result.status == "failed":
        print(item_id, result.error)
```

## When To Use It

Prefer `BatchExecutor` over manual fan-out when you need:

- durable progress
- bounded concurrency
- resumability
- per-item reporting

Prefer normal graph strategies such as `parallel` or `topological` when the parallelism is inside one workflow run rather than across many independent items.

## Related Docs

- [Workflow patterns](workflow-patterns.md)
- [Advanced configuration](advanced-configuration.md)
- [Observability](observability.md)
- [API reference](../API_REFERENCE.md)
