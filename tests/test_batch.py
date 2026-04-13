"""Tests for BatchExecutor — batch execution, failure isolation, checkpointing, resume."""

import asyncio
import warnings

import pytest

from yggdrasil.batch import BatchExecutor, BatchRun, BatchStatus, _item_node_id, _run_node_id
from yggdrasil.core.executor import ExecutionContext
from yggdrasil.core.nodes import AgentNode
from yggdrasil.core.store import NetworkXGraphStore

# BatchExecutor direct construction is deprecated in favour of executor.batch().
# These tests exercise the implementation through BatchExecutor directly; suppress
# the warning so test output stays clean.
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


# ---------------------------------------------------------------------------
# Stub executor — no real LLM calls
# ---------------------------------------------------------------------------

class _MockExecutor:
    """Returns a canned output dict per query.  Raises for queries starting with 'FAIL:'."""

    async def run(self, agent_node_id, query, strategy="sequential", extra_messages=None, **kw):
        if query.startswith("FAIL:"):
            raise RuntimeError(f"forced failure: {query}")
        ctx = ExecutionContext(query=query)
        ctx.outputs[agent_node_id] = {"text": f"result:{query}"}
        return ctx


class _SlowExecutor:
    """Records call order to verify concurrency behaviour."""

    def __init__(self, delay: float = 0.05):
        self.delay    = delay
        self.running  = 0
        self.peak     = 0
        self.order: list[str] = []

    async def run(self, agent_node_id, query, strategy="sequential", extra_messages=None, **kw):
        self.running += 1
        self.peak     = max(self.peak, self.running)
        await asyncio.sleep(self.delay)
        self.order.append(query)
        self.running -= 1
        ctx = ExecutionContext(query=query)
        ctx.outputs[agent_node_id] = {"text": f"result:{query}"}
        return ctx


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    return NetworkXGraphStore()


@pytest.fixture
def agent(store):
    node = AgentNode(name="TestAgent")
    return node   # not upserted — BatchExecutor only calls executor.run()


@pytest.fixture
def executor():
    return _MockExecutor()


@pytest.fixture
def batch(store, executor):
    return BatchExecutor(store, executor, concurrency=10)


# ---------------------------------------------------------------------------
# Happy-path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_all_items_succeed(batch, agent):
    items = ["a", "b", "c"]
    run = await batch.run(
        agent.node_id,
        items,
        query_fn=lambda x: x,
    )

    assert run.status    == BatchStatus.COMPLETED
    assert run.completed == 3
    assert run.failed    == 0
    assert run.progress  == 1.0
    assert run.ended_at  is not None


@pytest.mark.asyncio
async def test_outputs_match_items(batch, agent):
    items = ["x", "y"]
    run = await batch.run(agent.node_id, items, query_fn=lambda x: x)

    for i, item in enumerate(items):
        result = run.results[str(i)]
        assert result.status == BatchStatus.COMPLETED
        assert result.output == {"text": f"result:{item}"}


# ---------------------------------------------------------------------------
# Failure isolation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_one_failure_does_not_cancel_others(batch, agent):
    items = ["ok1", "FAIL:bad", "ok2"]
    run = await batch.run(agent.node_id, items, query_fn=lambda x: x)

    assert run.status    == BatchStatus.PARTIAL
    assert run.completed == 2
    assert run.failed    == 1

    assert run.results["0"].status == BatchStatus.COMPLETED
    assert run.results["1"].status == BatchStatus.FAILED
    assert run.results["2"].status == BatchStatus.COMPLETED


@pytest.mark.asyncio
async def test_all_fail(batch, agent):
    items = ["FAIL:1", "FAIL:2"]
    run = await batch.run(agent.node_id, items, query_fn=lambda x: x)

    assert run.status    == BatchStatus.FAILED
    assert run.completed == 0
    assert run.failed    == 2


@pytest.mark.asyncio
async def test_error_message_captured(batch, agent):
    items = ["FAIL:oops"]
    run = await batch.run(agent.node_id, items, query_fn=lambda x: x)

    assert "oops" in run.results["0"].error


# ---------------------------------------------------------------------------
# Timing metadata
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_item_timing_recorded(batch, agent):
    run = await batch.run(agent.node_id, ["a"], query_fn=lambda x: x)
    result = run.results["0"]

    assert result.started_at is not None
    assert result.ended_at   is not None
    assert result.duration_seconds is not None
    assert result.duration_seconds >= 0


# ---------------------------------------------------------------------------
# Progress callback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_progress_callback_called_per_item(batch, agent):
    calls: list[float] = []
    run = await batch.run(
        agent.node_id,
        ["a", "b", "c"],
        query_fn=lambda x: x,
        on_progress=lambda r: calls.append(r.progress),
    )

    assert len(calls) == 3
    assert calls[-1] == 1.0


@pytest.mark.asyncio
async def test_async_progress_callback(batch, agent):
    calls: list[int] = []

    async def cb(r: BatchRun) -> None:
        calls.append(r.completed + r.failed)

    run = await batch.run(agent.node_id, ["a", "b"], query_fn=lambda x: x, on_progress=cb)
    assert len(calls) == 2


# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_checkpoint_run_node_persisted(store, agent):
    batch = BatchExecutor(store, _MockExecutor(), concurrency=2)
    run = await batch.run(agent.node_id, ["a", "b"], query_fn=lambda x: x, checkpoint=True)

    node = await store.get_node(_run_node_id(run.run_id))
    assert node is not None
    assert node.content_type == "batch_run"


@pytest.mark.asyncio
async def test_checkpoint_item_nodes_persisted(store, agent):
    batch = BatchExecutor(store, _MockExecutor(), concurrency=2)
    items = ["x", "y", "z"]
    run   = await batch.run(agent.node_id, items, query_fn=lambda x: x, checkpoint=True)

    for i in range(len(items)):
        node = await store.get_node(_item_node_id(run.run_id, str(i)))
        assert node is not None
        assert node.content_type == "batch_item"


@pytest.mark.asyncio
async def test_no_checkpoint_when_disabled(store, agent):
    batch = BatchExecutor(store, _MockExecutor(), concurrency=2)
    run   = await batch.run(agent.node_id, ["a"], query_fn=lambda x: x, checkpoint=False)

    node = await store.get_node(_run_node_id(run.run_id))
    assert node is None


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_resume_skips_completed_items(store, agent):
    """Simulate a partial run then resume — completed items must not be re-run."""
    items = ["a", "b", "c"]

    class _TrackingExecutor:
        def __init__(self):
            self.calls: list[str] = []

        async def run(self, agent_node_id, query, strategy="sequential", extra_messages=None, **kw):
            self.calls.append(query)
            ctx = ExecutionContext(query=query)
            ctx.outputs[agent_node_id] = {"text": f"result:{query}"}
            return ctx

    tracking = _TrackingExecutor()
    batch = BatchExecutor(store, tracking, concurrency=5)

    # First run — all succeed, all checkpointed
    run = await batch.run(agent.node_id, items, query_fn=lambda x: x, checkpoint=True)
    assert run.completed == 3

    # Clear call log, then resume
    tracking.calls.clear()
    resumed = await batch.resume(run.run_id, items, query_fn=lambda x: x)

    # Nothing should have been re-run
    assert tracking.calls == []
    assert resumed.completed == 3


@pytest.mark.asyncio
async def test_resume_reruns_failed_items(store, agent):
    """Failed items from the first run are retried on resume."""
    items = ["ok", "FAIL:bad"]

    batch = BatchExecutor(store, _MockExecutor(), concurrency=5)
    run   = await batch.run(agent.node_id, items, query_fn=lambda x: x, checkpoint=True)
    assert run.failed == 1

    # Fix the "bad" item by changing the query mapping
    resumed = await batch.resume(
        run.run_id,
        items,
        query_fn=lambda x: "fixed" if x == "FAIL:bad" else x,
    )

    assert resumed.completed == 2
    assert resumed.failed    == 0


@pytest.mark.asyncio
async def test_resume_unknown_run_id_raises(store, agent):
    batch = BatchExecutor(store, _MockExecutor())
    with pytest.raises(ValueError, match="No checkpoint found"):
        await batch.resume("nonexistent-run-id", [], query_fn=lambda x: x)


# ---------------------------------------------------------------------------
# Map-reduce
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reduce_fn_called_with_successful_outputs(batch, agent):
    items = ["a", "b", "FAIL:c"]
    combined: list[Any] = []

    run = await batch.run(
        agent.node_id,
        items,
        query_fn=lambda x: x,
        reduce_fn=lambda outputs: outputs,
    )

    assert run.reduced_output is not None
    assert len(run.reduced_output) == 2   # "c" failed, only a+b in reduce


@pytest.mark.asyncio
async def test_reduce_fn_receives_outputs_in_item_order(batch, agent):
    items = ["first", "second", "third"]
    run = await batch.run(
        agent.node_id,
        items,
        query_fn=lambda x: x,
        reduce_fn=lambda outputs: [o["text"] for o in outputs],
    )

    assert run.reduced_output == [
        "result:first",
        "result:second",
        "result:third",
    ]


# ---------------------------------------------------------------------------
# Concurrency cap
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_concurrency_limit_respected():
    store = NetworkXGraphStore()
    slow  = _SlowExecutor(delay=0.05)
    batch = BatchExecutor(store, slow, concurrency=2)
    agent = AgentNode(name="A")

    await batch.run(agent.node_id, list(range(6)), query_fn=str, checkpoint=False)

    assert slow.peak <= 2


@pytest.mark.asyncio
async def test_concurrency_unlimited_runs_all_in_parallel():
    store = NetworkXGraphStore()
    slow  = _SlowExecutor(delay=0.05)
    batch = BatchExecutor(store, slow, concurrency=100)
    agent = AgentNode(name="A")

    await batch.run(agent.node_id, list(range(6)), query_fn=str, checkpoint=False)

    assert slow.peak == 6


# ---------------------------------------------------------------------------
# Per-item context injection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_context_fn_prepended_as_extra_message():
    store    = NetworkXGraphStore()
    received: list[list | None] = []

    class _CapturingExecutor:
        async def run(self, agent_id, query, strategy="sequential", extra_messages=None, **kw):
            received.append(extra_messages)
            ctx = ExecutionContext(query=query)
            ctx.outputs[agent_id] = {"text": "ok"}
            return ctx

    batch = BatchExecutor(store, _CapturingExecutor(), concurrency=1)
    agent = AgentNode(name="A")

    await batch.run(
        agent.node_id,
        ["item0"],
        query_fn=lambda x: "do task",
        context_fn=lambda x: f"data for {x}",
        checkpoint=False,
    )

    assert received[0] == [{"role": "user", "content": "data for item0"}]


@pytest.mark.asyncio
async def test_no_extra_message_when_context_fn_returns_none():
    store    = NetworkXGraphStore()
    received: list[list | None] = []

    class _CapturingExecutor:
        async def run(self, agent_id, query, strategy="sequential", extra_messages=None, **kw):
            received.append(extra_messages)
            ctx = ExecutionContext(query=query)
            ctx.outputs[agent_id] = {"text": "ok"}
            return ctx

    batch = BatchExecutor(store, _CapturingExecutor(), concurrency=1)
    agent = AgentNode(name="A")

    await batch.run(
        agent.node_id,
        ["item0"],
        query_fn=lambda x: "do task",
        context_fn=lambda x: None,
        checkpoint=False,
    )

    assert received[0] is None


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_empty_items_returns_completed_run(batch, agent):
    run = await batch.run(agent.node_id, [], query_fn=lambda x: x)
    assert run.status    == BatchStatus.COMPLETED
    assert run.total     == 0
    assert run.progress  == 1.0


# ---------------------------------------------------------------------------
# Deprecation warnings
# ---------------------------------------------------------------------------

def test_batch_executor_direct_construction_emits_deprecation_warning(store):
    """Constructing BatchExecutor directly should fire a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="executor.batch()"):
        BatchExecutor(store, _MockExecutor())


@pytest.mark.asyncio
@pytest.mark.filterwarnings("always::DeprecationWarning")
async def test_executor_batch_method_runs_agent(store, agent):
    """executor.batch() is the preferred entry point and must work end-to-end."""
    from yggdrasil.core.executor import GraphExecutor
    executor = GraphExecutor.__new__(GraphExecutor)
    # Patch with mock so no real LLM is needed
    mock = _MockExecutor()
    executor.store = store
    executor._mock = mock

    # Wire executor.batch() through the mock by temporarily replacing run()
    async def _mock_run(entry_node_id, query, **kwargs):
        return await mock.run(entry_node_id, query, **kwargs)

    executor.run = _mock_run  # type: ignore[method-assign]

    # Call via executor.batch() — should NOT emit DeprecationWarning
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        run = await executor.batch(
            agent.node_id,
            ["item-a", "item-b"],
            query_fn=lambda x: f"process {x}",
            checkpoint=False,
        )
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert not deprecations, f"executor.batch() leaked DeprecationWarning: {deprecations}"
    assert run.total == 2
    assert run.status == BatchStatus.COMPLETED
