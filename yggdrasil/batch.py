"""Batch execution engine for yggdrasil.

BatchExecutor provides:
- Dynamic fan-out     — one agent execution per item, all run concurrently
- Concurrency cap     — asyncio.Semaphore limits parallel workers
- Failure isolation   — asyncio.gather(return_exceptions=False) with per-item
                        try/except so one failure never cancels other items
- Progress tracking   — BatchRun / BatchItemResult dataclasses updated live
- Checkpointing       — state persisted as ContextNodes in the graph store so
                        a crash does not lose completed work
- Resume              — reload checkpoint state and skip already-completed items
- Per-item context    — context_fn(item) → str injected per query via
                        GraphExecutor.run(extra_messages=...), no graph mutation
- Map-reduce          — optional reduce_fn folds all successful outputs after
                        the map phase; result stored in BatchRun.reduced_output

Usage::

    batch = BatchExecutor(store, executor, concurrency=5)

    run = await batch.run(
        agent_node_id = agent.node_id,
        items         = documents,
        query_fn      = lambda doc: f"Summarise: {doc['title']}",
        context_fn    = lambda doc: doc["body"],
        reduce_fn     = lambda outputs: "\\n\\n".join(o["text"] for o in outputs),
        on_progress   = lambda r: print(f"{r.progress:.0%} — {r.completed}/{r.total}"),
    )

    print(run.status)            # "completed" | "partial" | "failed"
    print(run.reduced_output)    # combined result if reduce_fn was supplied

    # Inspect per-item failures
    for item_id, result in run.results.items():
        if result.status == BatchStatus.FAILED:
            print(f"  item {item_id}: {result.error}")

    # Resume after a crash (skips COMPLETED items)
    run = await batch.resume(run.run_id, items, query_fn, context_fn=context_fn)
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable

from yggdrasil.core.nodes import ContextNode
from yggdrasil.core.store import GraphStore


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class BatchStatus(StrEnum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    PARTIAL   = "partial"   # some items succeeded, some failed


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class BatchItemResult:
    """Outcome of a single item in a batch run."""

    item_id:    str
    status:     BatchStatus     = BatchStatus.PENDING
    output:     Any             = None
    error:      str | None      = None
    started_at: datetime | None = None
    ended_at:   datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Wall-clock time for this item, or None if not yet finished."""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None


@dataclass
class BatchRun:
    """Live state of a batch execution.

    All properties are computed from the results dict so they are always
    consistent with the underlying per-item state.
    """

    run_id:         str
    agent_id:       str
    total:          int
    results:        dict[str, BatchItemResult] = field(default_factory=dict)
    reduced_output: Any                        = None
    started_at:     datetime                   = field(default_factory=_now)
    ended_at:       datetime | None            = None

    # ---- computed properties ------------------------------------------------

    @property
    def completed(self) -> int:
        return sum(1 for r in self.results.values() if r.status == BatchStatus.COMPLETED)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results.values() if r.status == BatchStatus.FAILED)

    @property
    def pending(self) -> int:
        return sum(1 for r in self.results.values() if r.status == BatchStatus.PENDING)

    @property
    def running(self) -> int:
        return sum(1 for r in self.results.values() if r.status == BatchStatus.RUNNING)

    @property
    def status(self) -> BatchStatus:
        if self.ended_at is None:
            return BatchStatus.RUNNING
        if self.failed == 0:
            return BatchStatus.COMPLETED
        if self.completed == 0:
            return BatchStatus.FAILED
        return BatchStatus.PARTIAL

    @property
    def progress(self) -> float:
        """Fraction of items finished (completed + failed) out of total."""
        if self.total == 0:
            return 1.0
        return (self.completed + self.failed) / self.total

    def successful_outputs(self) -> list[Any]:
        """Outputs of all COMPLETED items in original item order."""
        return [
            r.output
            for r in sorted(self.results.values(), key=lambda r: int(r.item_id))
            if r.status == BatchStatus.COMPLETED
        ]


# ---------------------------------------------------------------------------
# BatchExecutor
# ---------------------------------------------------------------------------

class BatchExecutor:
    """Runs an agent node over a list of items with full batch management.

    Each item is processed by an independent executor.run() call so there is
    no shared mutable state between items.

    Args:
        store:       GraphStore used for checkpointing.
        executor:    GraphExecutor that will run the agent per item.
        concurrency: Maximum number of items processed concurrently.
    """

    def __init__(
        self,
        store:       GraphStore,
        executor:    Any,          # GraphExecutor — typed as Any to avoid circular import
        concurrency: int = 10,
    ) -> None:
        import warnings
        warnings.warn(
            "Constructing BatchExecutor directly is deprecated. "
            "Use executor.batch(...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.store       = store
        self.executor    = executor
        self.concurrency = concurrency

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(
        self,
        agent_node_id: str,
        items: list[Any],
        query_fn: Callable[[Any], str],
        *,
        context_fn:  Callable[[Any], str | None] | None  = None,
        reduce_fn:   Callable[[list[Any]], Any]  | None  = None,
        on_progress: Callable[["BatchRun"], Any] | None  = None,
        checkpoint:  bool = True,
        strategy:    str  = "sequential",
    ) -> BatchRun:
        """Run agent_node over every item concurrently.

        Args:
            agent_node_id: Node ID of the agent to execute for each item.
            items:         Any list — elements are passed to query_fn / context_fn.
            query_fn:      item → query string sent to the agent.
            context_fn:    Optional item → context string prepended to the query
                           as an extra message (per-item context injection with
                           no graph mutation).
            reduce_fn:     Optional — receives all successful outputs after the
                           map phase; result stored in BatchRun.reduced_output.
            on_progress:   Sync or async callback invoked after each item
                           finishes (success or failure).
            checkpoint:    Persist BatchRun and per-item state as ContextNodes.
            strategy:      Execution strategy forwarded to GraphExecutor.run().
        """
        run = BatchRun(
            run_id=str(uuid.uuid4()),
            agent_id=agent_node_id,
            total=len(items),
            results={str(i): BatchItemResult(item_id=str(i)) for i in range(len(items))},
        )

        if checkpoint:
            await self._checkpoint_run(run)

        await self._execute(run, items, query_fn, context_fn, on_progress, checkpoint, strategy)

        run.ended_at = _now()

        if reduce_fn is not None:
            run.reduced_output = reduce_fn(run.successful_outputs())

        if checkpoint:
            await self._checkpoint_run(run)

        return run

    async def resume(
        self,
        run_id: str,
        items: list[Any],
        query_fn: Callable[[Any], str],
        *,
        context_fn:  Callable[[Any], str | None] | None  = None,
        reduce_fn:   Callable[[list[Any]], Any]  | None  = None,
        on_progress: Callable[["BatchRun"], Any] | None  = None,
        strategy:    str = "sequential",
    ) -> BatchRun:
        """Resume a previously checkpointed run, skipping COMPLETED items.

        Items that were RUNNING when the process crashed are treated as PENDING
        and re-executed.

        Args:
            run_id: The BatchRun.run_id from the original run.
            items:  Must be the same list (same length and order) as the original.
        """
        run = await self._load_checkpoint(run_id)

        # Re-run everything that did not successfully complete
        await self._execute(run, items, query_fn, context_fn, on_progress, True, strategy)

        run.ended_at = _now()

        if reduce_fn is not None:
            run.reduced_output = reduce_fn(run.successful_outputs())

        await self._checkpoint_run(run)
        return run

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _execute(
        self,
        run: BatchRun,
        items: list[Any],
        query_fn: Callable[[Any], str],
        context_fn: Callable[[Any], str | None] | None,
        on_progress: Callable[[BatchRun], Any] | None,
        checkpoint: bool,
        strategy: str,
    ) -> None:
        """Fan out execution over all items with a concurrency semaphore."""
        sem = asyncio.Semaphore(self.concurrency)

        async def _process(idx: int, item: Any) -> None:
            item_id = str(idx)
            result  = run.results[item_id]

            # Skip items already completed (resume path)
            if result.status == BatchStatus.COMPLETED:
                return

            result.status     = BatchStatus.RUNNING
            result.started_at = _now()

            if checkpoint:
                await self._checkpoint_item(run.run_id, result)

            try:
                async with sem:
                    query = query_fn(item)

                    extra_messages: list[dict[str, Any]] | None = None
                    if context_fn:
                        ctx_text = context_fn(item)
                        if ctx_text:
                            extra_messages = [{"role": "user", "content": ctx_text}]

                    exec_ctx = await self.executor.run(
                        run.agent_id,
                        query,
                        strategy=strategy,
                        extra_messages=extra_messages,
                    )
                    result.output = exec_ctx.outputs.get(run.agent_id)
                    result.status = BatchStatus.COMPLETED

            except Exception as exc:
                result.status = BatchStatus.FAILED
                result.error  = f"{type(exc).__name__}: {exc}"

            finally:
                result.ended_at = _now()

                if checkpoint:
                    await self._checkpoint_item(run.run_id, result)

                if on_progress is not None:
                    ret = on_progress(run)
                    if asyncio.iscoroutine(ret):
                        await ret

        # return_exceptions=False is safe here because _process never raises —
        # all exceptions are caught inside the try/except block above.
        await asyncio.gather(*[_process(i, item) for i, item in enumerate(items)])

    # ------------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------------

    async def _checkpoint_run(self, run: BatchRun) -> None:
        """Upsert a ContextNode representing the BatchRun's current state."""
        node = ContextNode(
            node_id=_run_node_id(run.run_id),
            name=f"BatchRun {run.run_id[:8]}",
            description=(
                f"Batch: {run.completed}/{run.total} completed, "
                f"{run.failed} failed — {run.status}"
            ),
            content=json.dumps({
                "run_id":     run.run_id,
                "agent_id":   run.agent_id,
                "total":      run.total,
                "completed":  run.completed,
                "failed":     run.failed,
                "status":     run.status,
                "started_at": run.started_at.isoformat(),
                "ended_at":   run.ended_at.isoformat() if run.ended_at else None,
            }),
            content_type="batch_run",
            source=f"agent:{run.agent_id}",
            attributes={"run_id": run.run_id},
        )
        await self.store.upsert_node(node)

    async def _checkpoint_item(self, run_id: str, result: BatchItemResult) -> None:
        """Upsert a ContextNode representing one item's current state."""
        node = ContextNode(
            node_id=_item_node_id(run_id, result.item_id),
            name=f"BatchItem {result.item_id}",
            description=f"Item {result.item_id} — {result.status}",
            content=json.dumps({
                "run_id":     run_id,
                "item_id":    result.item_id,
                "status":     result.status,
                "error":      result.error,
                "started_at": result.started_at.isoformat() if result.started_at else None,
                "ended_at":   result.ended_at.isoformat() if result.ended_at else None,
            }),
            content_type="batch_item",
            source=f"batch_run:{run_id}",
            attributes={"run_id": run_id},
        )
        await self.store.upsert_node(node)

    async def _load_checkpoint(self, run_id: str) -> BatchRun:
        """Reconstruct a BatchRun from its checkpoint nodes in the graph."""
        run_node = await self.store.get_node(_run_node_id(run_id))
        if run_node is None:
            raise ValueError(f"No checkpoint found for run_id={run_id!r}")

        run_data = json.loads(run_node.content)  # type: ignore[union-attr]
        run = BatchRun(
            run_id=run_id,
            agent_id=run_data["agent_id"],
            total=run_data["total"],
            started_at=datetime.fromisoformat(run_data["started_at"]),
            results={str(i): BatchItemResult(item_id=str(i)) for i in range(run_data["total"])},
        )

        # Reload per-item state
        for i in range(run.total):
            item_node = await self.store.get_node(_item_node_id(run_id, str(i)))
            if item_node is None:
                continue
            item_data = json.loads(item_node.content)  # type: ignore[union-attr]
            result = run.results[str(i)]
            result.status = BatchStatus(item_data["status"])
            result.error  = item_data.get("error")
            if item_data.get("started_at"):
                result.started_at = datetime.fromisoformat(item_data["started_at"])
            if item_data.get("ended_at"):
                result.ended_at = datetime.fromisoformat(item_data["ended_at"])
            # Items interrupted mid-run (RUNNING) are treated as PENDING for retry
            if result.status == BatchStatus.RUNNING:
                result.status = BatchStatus.PENDING

        return run


# ---------------------------------------------------------------------------
# Deterministic node ID helpers (UUID v5 so IDs are stable across restarts)
# ---------------------------------------------------------------------------

def _run_node_id(run_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"batch_run:{run_id}"))


def _item_node_id(run_id: str, item_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"batch_item:{run_id}:{item_id}"))
