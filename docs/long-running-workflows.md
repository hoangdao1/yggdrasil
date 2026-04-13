# Long-Running Workflows

Yggdrasil includes runtime helpers for workflows that must pause, survive restarts, and resume later.

These features build on top of normal graph execution. You still model the workflow as graph nodes and edges, but the runtime can persist operational state around that graph.

Use this when:

- a human approval happens later
- an external callback arrives minutes or hours afterward
- a worker process may restart between steps
- multiple workers need coarse coordination over resumptions

## Core Building Blocks

The long-running workflow model has two main parts:

1. Pause and resume
2. Checkpoints

### Pause And Resume

A workflow can pause because of:

- `pause_before=True`
- `pause_after=True`
- `wait_for_input="..."`
- an `ApprovalNode`
- deterministic routing rules that pause on match

Resume with the same `ExecutionContext` after updating workflow state:

```python
ctx = await executor.run(approval.node_id, "Review this request.")

ctx.state.data["approval"] = {"approved": True, "approver": "mgr-1"}
resumed = await executor.resume(approval.node_id, ctx, query="Continue.")
```

When a paused workflow resumes, the trace records a `resume` event and execution continues with the preserved workflow state.

### Checkpoints

Use checkpoints when the process that paused the run might not be the process that resumes it.

```python
checkpoint = await executor.checkpoint_context(ctx)
restored = await executor.load_checkpoint(checkpoint.node_id)
resumed = await executor.resume(entry.node_id, restored, query="Continue.")
```

Or in one step:

```python
resumed = await executor.resume_from_checkpoint(
    checkpoint.node_id,
    entry.node_id,
    query="Continue.",
)
```

Checkpoint nodes store a serialized `ExecutionContext`.

## Trace And Debugging

Long-running workflows emit richer trace events than a simple request-response run.

Watch for:

- `pause`
- `resume`
- `checkpoint`
- `approval_task`

Use:

- `inspect_trace(ctx)` for terminal inspection
- `serve_trace(ctx, store=executor.store)` for the browser UI
- `explain_run(ctx)` for a structured summary

## Choosing The Right Level

Use the simplest thing that fits:

- use `resume(...)` if the same process keeps the context in memory
- add checkpoints when resumptions may happen later or elsewhere

## Related Docs

- [Workflow patterns](workflow-patterns.md)
- [Observability](observability.md)
- [API reference](../API_REFERENCE.md)
