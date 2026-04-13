---
title: Graph State Management
parent: Docs
nav_order: 5
---

# Graph State Management

> This page previously covered the graph-admin lifecycle (revision management,
> config-as-code, snapshot import/export, promotion, rollback). Those features
> have been removed to keep yggdrasil focused on its core thesis as a
> graph-native agent runtime.

## What Still Exists

**Checkpoints** — the executor can persist and restore `ExecutionContext`:

```python
checkpoint = await executor.checkpoint_context(ctx)
restored   = await executor.load_checkpoint(checkpoint.node_id)
resumed    = await executor.resume_from_checkpoint(
    checkpoint.node_id, entry.node_id, query="Continue."
)
```

**Workflow state versioning** — `AgentNode.graph_version` provides a semantic compatibility label for in-flight workflow state. Bump it when a graph change is incompatible with previously checkpointed state.

**Runtime node cleanup** — session-scoped context nodes created during
execution can be enumerated and removed:

```python
from yggdrasil import get_runtime_nodes, cleanup_session

nodes = await get_runtime_nodes(store, ctx.session_id)
await cleanup_session(store, ctx.session_id)
```

## Related Docs

- [Long-running workflows](long-running-workflows.md)
- [Workflow patterns](workflow-patterns.md)
- [Observability](observability.md)
- [API reference](../API_REFERENCE.md)
