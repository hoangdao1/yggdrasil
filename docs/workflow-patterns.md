# Workflow Patterns

This guide collects the patterns you will reach for most often once the basic Yggdrasil model clicks.

The first five patterns focus on orchestration structure. The last two show the newer workflow-runtime features: deterministic routing and human-in-the-loop pause / resume.

Shared imports for the examples below:

```python
from yggdrasil import (
    AgentNode,
    Edge,
    GraphExecutor,
    GraphNode,
    NetworkXGraphStore,
    TransformNode,
    create_agent,
    create_transform,
    get_runtime_nodes,
    print_trace,
)
```

## 1. Linear Pipeline

Use a sequential chain when each stage transforms the previous stage's output.

Typical shape:

```text
Extractor -> Validator -> Summarizer
```

Example:

```python
async def linear_pipeline() -> None:
    store = NetworkXGraphStore()

    summarizer = AgentNode(
        name="Summarizer",
        system_prompt="Write a concise summary.",
        routing_table={"default": "__END__"},
    )
    extractor = AgentNode(
        name="Extractor",
        system_prompt="Extract the important facts.",
        routing_table={"default": summarizer.node_id},
    )

    await store.upsert_node(extractor)
    await store.upsert_node(summarizer)

    ctx = await GraphExecutor(store).run(
        entry_node_id=extractor.node_id,
        query="Analyze Q3 earnings.",
        strategy="sequential",
    )
    print_trace(ctx)
```

Use this when:

- each step depends on the previous step
- you want an explicit multi-stage chain
- parallelism is not the main concern

## 2. Supervisor / Worker Fan-Out

Use `DELEGATES_TO` plus `strategy="parallel"` when one agent should delegate independent sub-tasks to multiple workers.

Typical shape:

```text
          -> SentimentWorker
Supervisor -> EntityWorker
          -> TopicWorker
```

Example:

```python
async def fan_out() -> None:
    store = NetworkXGraphStore()

    supervisor = AgentNode(name="Supervisor", system_prompt="Break the work apart.")
    sentiment = AgentNode(name="Sentiment", system_prompt="Analyze sentiment.")
    entities = AgentNode(name="Entities", system_prompt="Extract named entities.")
    topics = AgentNode(name="Topics", system_prompt="Classify the topic.")

    for node in [supervisor, sentiment, entities, topics]:
        await store.upsert_node(node)

    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, sentiment.node_id))
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, entities.node_id))
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, topics.node_id))

    ctx = await GraphExecutor(store).run(
        entry_node_id=supervisor.node_id,
        query="Process this article.",
        strategy="parallel",
    )

    merged = ctx.outputs[supervisor.node_id]
    print(merged["node_result"])
    print(merged["delegate_results"])
```

Use this when:

- workers are independent
- latency matters
- you want one merged result object

## 3. Explicit DAG

Use `strategy="topological"` when execution order should follow dependencies instead of a single chain.

Typical shape:

```text
Ingest -> Analyze -> Validate -> Report
   \-------------------------->/
```

Example:

```python
async def dag_pipeline() -> None:
    store = NetworkXGraphStore()

    ingest = AgentNode(name="Ingest", system_prompt="Load and chunk documents.")
    analyze = AgentNode(name="Analyze", system_prompt="Analyze each chunk.")
    validate = AgentNode(name="Validate", system_prompt="Validate the analysis.")
    report = AgentNode(name="Report", system_prompt="Generate the final report.")

    for node in [ingest, analyze, validate, report]:
        await store.upsert_node(node)

    await store.upsert_edge(Edge.delegates_to(ingest.node_id, analyze.node_id))
    await store.upsert_edge(Edge.delegates_to(analyze.node_id, validate.node_id))
    await store.upsert_edge(Edge.delegates_to(validate.node_id, report.node_id))
    await store.upsert_edge(Edge.delegates_to(ingest.node_id, report.node_id))

    ctx = await GraphExecutor(store).run(
        entry_node_id=ingest.node_id,
        query="Run pipeline.",
        strategy="topological",
    )
    print(ctx.outputs[report.node_id])
```

Use this when:

- multiple stages have strict dependencies
- some waves can run in parallel
- you want the graph shape to be the execution plan

## 4. Reusable Sub-Graphs

Wrap a multi-step workflow in a `GraphNode` when you want to reuse it as a single step inside a larger graph.

Example:

```python
async def nested_workflow() -> None:
    store = NetworkXGraphStore()

    writer = AgentNode(
        name="Writer",
        system_prompt="Write the report.",
        routing_table={"default": "__END__"},
    )
    researcher = AgentNode(
        name="Researcher",
        system_prompt="Find supporting information.",
        routing_table={"default": writer.node_id},
    )

    await store.upsert_node(researcher)
    await store.upsert_node(writer)

    reusable_pipeline = GraphNode(
        name="ResearchAndWrite",
        description="A reusable sub-graph",
        entry_node_id=researcher.node_id,
        exit_node_id=writer.node_id,
    )
    orchestrator = AgentNode(
        name="Orchestrator",
        system_prompt="Start the reusable workflow.",
        routing_table={"default": reusable_pipeline.node_id},
    )

    await store.upsert_node(reusable_pipeline)
    await store.upsert_node(orchestrator)

    ctx = await GraphExecutor(store).run(
        entry_node_id=orchestrator.node_id,
        query="Research quantum computing.",
    )
    print_trace(ctx)
```

Use this when:

- a workflow should be reusable
- you want one graph to embed another
- you want to hide inner complexity behind one node

## 5. Agent-To-Agent Data Passing

All node outputs land in `ExecutionContext.outputs`, so later agents can read earlier results explicitly. For structured workflow state that should outlive a single node result, use `ExecutionContext.state`.

Example:

```python
async def data_passing() -> None:
    store = NetworkXGraphStore()

    writer = AgentNode(
        name="Writer",
        system_prompt="Read prior outputs and produce a final response.",
        routing_table={"default": "__END__"},
    )
    researcher = AgentNode(
        name="Researcher",
        system_prompt="Research the topic first.",
        routing_table={"default": writer.node_id},
    )

    await store.upsert_node(researcher)
    await store.upsert_node(writer)

    ctx = await GraphExecutor(store).run(
        entry_node_id=researcher.node_id,
        query="Summarize the Python async ecosystem.",
    )

    print(ctx.outputs[researcher.node_id])
    print(ctx.outputs[writer.node_id])
```

This is useful when:

- you want explicit handoff between stages
- intermediate outputs matter for debugging
- you need structured state shared across a traversal

## 6. Split / Join With TransformNode

Use `TransformNode` when you need to reshape data between nodes without an LLM. The most common cases are fan-out splitting and fan-in joining.

**Why not use an agent?** An agent costs tokens and non-deterministically formats output. A `TransformNode` is a plain Python function — fast, free, and testable in isolation.

Typical shape:

```text
Splitter (TransformNode)
   → WorkerA
   → WorkerB       ← parallel branches
   → WorkerC
Joiner (TransformNode, input_keys=[A, B, C])
   → Summarizer
```

Example:

```python
def split_items(data: dict) -> dict:
    items = data.get("items", [])
    return {f"bucket_{i}": item for i, item in enumerate(items)}

def join_results(data: dict) -> dict:
    parts = [v.get("text", str(v)) if isinstance(v, dict) else str(v) for v in data.values()]
    return {"merged": "\n".join(sorted(parts))}

async def split_join_pipeline() -> None:
    store = NetworkXGraphStore()

    splitter = create_transform(
        "Splitter",
        callable_ref="myapp.split_items",
        output_key="buckets",
        is_async=False,
    )
    worker_a = create_agent("WorkerA", system_prompt="Process bucket_0.")
    worker_b = create_agent("WorkerB", system_prompt="Process bucket_1.")
    joiner = create_transform(
        "Joiner",
        callable_ref="myapp.join_results",
        input_keys=[worker_a.node_id, worker_b.node_id],  # explicit fan-in
        output_key="joined",
        is_async=False,
    )
    summarizer = create_agent("Summarizer", system_prompt="Summarize the joined results.")

    for node in [splitter, worker_a, worker_b, joiner, summarizer]:
        await store.upsert_node(node)

    # splitter → workers (fan-out)
    await store.upsert_edge(Edge.delegates_to(splitter.node_id, worker_a.node_id))
    await store.upsert_edge(Edge.delegates_to(splitter.node_id, worker_b.node_id))

    # workers → joiner (fan-in — also declared via input_keys above)
    await store.upsert_edge(Edge.delegates_to(worker_a.node_id, joiner.node_id))
    await store.upsert_edge(Edge.delegates_to(worker_b.node_id, joiner.node_id))

    # joiner → summarizer
    await store.upsert_edge(Edge.delegates_to(joiner.node_id, summarizer.node_id))

    executor = GraphExecutor(store)
    executor.register_tool("myapp.split_items", split_items)
    executor.register_tool("myapp.join_results", join_results)

    ctx = await executor.run(
        splitter.node_id,
        "Process items",
        strategy="topological",
        state={"items": ["report_q1", "report_q2"]},
    )

    print(ctx.state.data["joined"])
    print(ctx.outputs[summarizer.node_id]["text"])
```

Key points:

- `input_keys=[worker_a.node_id, worker_b.node_id]` tells the topological executor to wait for both workers before the joiner fires — this is the **guaranteed fan-in**, avoiding the `_last_output` race condition present in unstructured parallel execution
- `output_key` writes the result to `ctx.state.data` so downstream agents can read it from the injected workflow state
- The callable is registered with `executor.register_tool()`, reusing the same registry as `ToolNode`
- Transform steps appear in `print_trace()` as `tool_result` events

Use this when:

- you need to chunk or reshape data before workers run
- you need a deterministic, token-free merge of parallel results
- you want fan-in behavior that is explicit in the graph, not implicit in `_last_output`

## 7. Deterministic Approval Routing

Use `route_rules` when the next step should be selected from workflow state before the LLM gets a vote.

Example:

```python
from yggdrasil import AgentNode, GraphExecutor, NetworkXGraphStore, RouteRule


async def approval_flow() -> None:
    store = NetworkXGraphStore()

    approver = AgentNode(
        name="Approver",
        system_prompt="Review the request and either approve or reject it.",
        routing_table={"default": "__END__"},
    )
    intake = AgentNode(
        name="Intake",
        system_prompt="Classify the incoming request.",
        routing_table={"default": "__END__"},
        route_rules=[
            RouteRule(
                name="needs_approval",
                source="state",
                path="approval.required",
                operator="equals",
                value=True,
                target_node_id=approver.node_id,
                priority=10,
            )
        ],
    )

    await store.upsert_node(intake)
    await store.upsert_node(approver)

    ctx = await GraphExecutor(store).run(
        entry_node_id=intake.node_id,
        query="Start procurement request.",
        state={"approval": {"required": True}},
    )

    print(ctx.outputs[approver.node_id])
```

Use this when:

- branching must be deterministic
- workflow state should override free-form model output
- compliance or approval rules must be auditable

## 8. Human-In-The-Loop Pause / Resume

Use pause / resume when a workflow needs approval or external input between graph steps.

Example:

```python
from yggdrasil import AgentNode, GraphExecutor, NetworkXGraphStore


async def pause_resume() -> None:
    store = NetworkXGraphStore()

    approval = AgentNode(
        name="ApprovalStep",
        system_prompt="Summarize the request for review.",
        routing_table={"default": "__END__"},
        pause_after=True,
        wait_for_input="manager approval",
    )
    await store.upsert_node(approval)

    executor = GraphExecutor(store)
    ctx = await executor.run(approval.node_id, "Approve this expense request.")

    checkpoint = await executor.checkpoint_context(ctx)

    restored = await executor.load_checkpoint(checkpoint.node_id)
    restored.state.data["approval"] = {"approved": True, "approver": "mgr-123"}

    resumed = await executor.resume(approval.node_id, restored, query="Continue.")
    print(resumed.state.data)
```

Use this when:

- a human must review work
- an external system posts the next decision later
- workflows must survive process restarts

## 9. Approval Inbox Nodes

Use `ApprovalNode` when the review step should be explicit in the graph instead of encoded as a paused agent.

```python
from yggdrasil import ApprovalNode, AgentNode, GraphExecutor, NetworkXGraphStore


async def approval_inbox() -> None:
    store = NetworkXGraphStore()

    approved = AgentNode(name="Approved", routing_table={"default": "__END__"})
    rejected = AgentNode(name="Rejected", routing_table={"default": "__END__"})
    approval = ApprovalNode(
        name="ManagerApproval",
        instructions="Manager must approve the request.",
        assignees=["mgr-1"],
        sla_seconds=1800,
        escalation_target="director-on-call",
        approved_target_id=approved.node_id,
        rejected_target_id=rejected.node_id,
    )

    for node in [approved, rejected, approval]:
        await store.upsert_node(node)

    executor = GraphExecutor(store)
    ctx = await executor.run(approval.node_id, "Review request.")

    print(ctx.state.inbox)  # approval tasks live here

    ctx.state.data["approval"] = {"approved": True, "assigned_to": "mgr-1"}
    await executor.resume(approval.node_id, ctx, query="Continue.")
```

Use this when:

- assignees and due dates matter
- approval tasks should be inspectable in workflow state
- approved and rejected paths should be explicit graph edges

## Picking The Right Strategy

- Use `sequential` when the workflow is a chain.
- Use `parallel` when one supervisor fans out to independent workers.
- Use `topological` when dependencies matter and some waves can run concurrently — required when using `TransformNode` with `input_keys` for fan-in joining.

## Related Docs

- [README](../README.md)
- [Your First Graph](first-graph.md)
- [Choose a Backend](choose-backend.md)
- [Observability](observability.md)
- [Advanced configuration](advanced-configuration.md)
- [API reference](../API_REFERENCE.md)
