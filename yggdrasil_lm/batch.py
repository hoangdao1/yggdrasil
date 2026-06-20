#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x5a40a494

# Compiled with Coconut version 3.2.0

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
        reduce_fn     = lambda outputs: "\n\n".join(o["text"] for o in outputs),
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

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop, annotations
import sys as _coconut_sys
import os as _coconut_os
_coconut_header_info = ('3.2.0', '311', False)
_coconut_cached__coconut__ = _coconut_sys.modules.get('__coconut__')
_coconut_file_dir = _coconut_os.path.dirname(_coconut_os.path.abspath(__file__))
_coconut_pop_path = False
if _coconut_cached__coconut__ is None or getattr(_coconut_cached__coconut__, "_coconut_header_info", None) != _coconut_header_info and _coconut_os.path.dirname(_coconut_cached__coconut__.__file__ or "") != _coconut_file_dir:  # type: ignore
    if _coconut_cached__coconut__ is not None:
        _coconut_sys.modules['_coconut_cached__coconut__'] = _coconut_cached__coconut__
        del _coconut_sys.modules['__coconut__']
    _coconut_sys.path.insert(0, _coconut_file_dir)
    _coconut_pop_path = True
    _coconut_module_name = _coconut_os.path.splitext(_coconut_os.path.basename(_coconut_file_dir))[0]
    if _coconut_module_name and _coconut_module_name[0].isalpha() and all(c.isalpha() or c.isdigit() for c in _coconut_module_name) and "__init__.py" in _coconut_os.listdir(_coconut_file_dir):  # type: ignore
        _coconut_full_module_name = str(_coconut_module_name + ".__coconut__")  # type: ignore
        import __coconut__ as _coconut__coconut__
        _coconut__coconut__.__name__ = _coconut_full_module_name
        for _coconut_v in vars(_coconut__coconut__).values():  # type: ignore
            if getattr(_coconut_v, "__module__", None) == '__coconut__':  # type: ignore
                try:
                    _coconut_v.__module__ = _coconut_full_module_name
                except AttributeError:
                    _coconut_v_type = type(_coconut_v)  # type: ignore
                    if getattr(_coconut_v_type, "__module__", None) == '__coconut__':  # type: ignore
                        _coconut_v_type.__module__ = _coconut_full_module_name
        _coconut_sys.modules[_coconut_full_module_name] = _coconut__coconut__
from __coconut__ import *
from __coconut__ import _coconut_tail_call, _coconut_tco, _namedtuple_of, _coconut, _coconut_Expected, _coconut_MatchError, _coconut_SupportsAdd, _coconut_SupportsMinus, _coconut_SupportsMul, _coconut_SupportsPow, _coconut_SupportsTruediv, _coconut_SupportsFloordiv, _coconut_SupportsMod, _coconut_SupportsAnd, _coconut_SupportsXor, _coconut_SupportsOr, _coconut_SupportsLshift, _coconut_SupportsRshift, _coconut_SupportsMatmul, _coconut_SupportsInv, _coconut_iter_getitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_star_pipe, _coconut_dubstar_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_back_dubstar_pipe, _coconut_none_pipe, _coconut_none_star_pipe, _coconut_none_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_complex_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_raise, _coconut_mark_as_match, _coconut_reiterable, _coconut_self_match_types, _coconut_dict_merge, _coconut_exec, _coconut_comma_op, _coconut_arr_concat_op, _coconut_mk_anon_namedtuple, _coconut_matmul, _coconut_py_str, _coconut_flatten, _coconut_multiset, _coconut_back_none_pipe, _coconut_back_none_star_pipe, _coconut_back_none_dubstar_pipe, _coconut_forward_none_compose, _coconut_back_none_compose, _coconut_forward_none_star_compose, _coconut_back_none_star_compose, _coconut_forward_none_dubstar_compose, _coconut_back_none_dubstar_compose, _coconut_call_or_coefficient, _coconut_in, _coconut_not_in, _coconut_attritemgetter, _coconut_if_op, _coconut_CoconutWarning
if _coconut_pop_path:
    _coconut_sys.path.pop(0)
try:
    __file__ = _coconut_os.path.abspath(__file__) if __file__ else __file__
except NameError:
    pass
else:
    if __file__ and '__coconut_cache__' in __file__:
        _coconut_file_comps = []
        while __file__:
            __file__, _coconut_file_comp = _coconut_os.path.split(__file__)
            if not _coconut_file_comp:
                _coconut_file_comps.append(__file__)
                break
            if _coconut_file_comp != '__coconut_cache__':
                _coconut_file_comps.append(_coconut_file_comp)
        __file__ = _coconut_os.path.join(*reversed(_coconut_file_comps))

# Compiled Coconut: -----------------------------------------------------------



import asyncio  #42 (line in Coconut source)
import json  #43 (line in Coconut source)
import uuid  #44 (line in Coconut source)
from dataclasses import dataclass  #45 (line in Coconut source)
from dataclasses import field  #45 (line in Coconut source)
from datetime import datetime  #46 (line in Coconut source)
from datetime import timezone  #46 (line in Coconut source)
from enum import StrEnum  #47 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #48 (line in Coconut source)
    from typing import Any  #48 (line in Coconut source)
else:  #48 (line in Coconut source)
    try:  #48 (line in Coconut source)
        Any = _coconut.typing.Any  #48 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #48 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #48 (line in Coconut source)
if _coconut.typing.TYPE_CHECKING:  #48 (line in Coconut source)
    from typing import Callable  #48 (line in Coconut source)
else:  #48 (line in Coconut source)
    try:  #48 (line in Coconut source)
        Callable = _coconut.typing.Callable  #48 (line in Coconut source)
    except _coconut.AttributeError as _coconut_imp_err:  #48 (line in Coconut source)
        raise _coconut.ImportError(_coconut.str(_coconut_imp_err))  #48 (line in Coconut source)

from yggdrasil_lm.core.nodes import ContextNode  #50 (line in Coconut source)
from yggdrasil_lm.core.store import GraphStore  #51 (line in Coconut source)


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class BatchStatus(StrEnum):  #58 (line in Coconut source)
    PENDING = "pending"  #59 (line in Coconut source)
    RUNNING = "running"  #60 (line in Coconut source)
    COMPLETED = "completed"  #61 (line in Coconut source)
    FAILED = "failed"  #62 (line in Coconut source)
    PARTIAL = "partial"  # some items succeeded, some failed  #63 (line in Coconut source)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@_coconut_tco  #70 (line in Coconut source)
def _now() -> datetime:  #70 (line in Coconut source)
    return _coconut_tail_call(datetime.now, timezone.utc)  #71 (line in Coconut source)



@dataclass  #74 (line in Coconut source)
class BatchItemResult():  #75 (line in Coconut source)
    """Outcome of a single item in a batch run."""  #76 (line in Coconut source)

    item_id: str  #78 (line in Coconut source)
    status: BatchStatus = BatchStatus.PENDING  #79 (line in Coconut source)
    output: Any = None  #80 (line in Coconut source)
    error: str | None = None  #81 (line in Coconut source)
    started_at: datetime | None = None  #82 (line in Coconut source)
    ended_at: datetime | None = None  #83 (line in Coconut source)

    @property  #85 (line in Coconut source)
    @_coconut_tco  #86 (line in Coconut source)
    def duration_seconds(self) -> float | None:  #86 (line in Coconut source)
        """Wall-clock time for this item, or None if not yet finished."""  #87 (line in Coconut source)
        if self.started_at and self.ended_at:  #88 (line in Coconut source)
            return _coconut_tail_call((self.ended_at - self.started_at).total_seconds)  #89 (line in Coconut source)
        return None  #90 (line in Coconut source)



@dataclass  #93 (line in Coconut source)
class BatchRun():  #94 (line in Coconut source)
    """Live state of a batch execution.

    All properties are computed from the results dict so they are always
    consistent with the underlying per-item state.
    """  #99 (line in Coconut source)

    run_id: str  #101 (line in Coconut source)
    agent_id: str  #102 (line in Coconut source)
    total: int  #103 (line in Coconut source)
    results: dict[str, BatchItemResult] = field(default_factory=dict)  #104 (line in Coconut source)
    reduced_output: Any = None  #105 (line in Coconut source)
    started_at: datetime = field(default_factory=_now)  #106 (line in Coconut source)
    ended_at: datetime | None = None  #107 (line in Coconut source)

# ---- computed properties ------------------------------------------------

    @property  #111 (line in Coconut source)
    @_coconut_tco  #112 (line in Coconut source)
    def completed(self) -> int:  #112 (line in Coconut source)
        return _coconut_tail_call(sum, (1 for r in self.results.values() if r.status == BatchStatus.COMPLETED))  #113 (line in Coconut source)


    @property  #115 (line in Coconut source)
    @_coconut_tco  #116 (line in Coconut source)
    def failed(self) -> int:  #116 (line in Coconut source)
        return _coconut_tail_call(sum, (1 for r in self.results.values() if r.status == BatchStatus.FAILED))  #117 (line in Coconut source)


    @property  #119 (line in Coconut source)
    @_coconut_tco  #120 (line in Coconut source)
    def pending(self) -> int:  #120 (line in Coconut source)
        return _coconut_tail_call(sum, (1 for r in self.results.values() if r.status == BatchStatus.PENDING))  #121 (line in Coconut source)


    @property  #123 (line in Coconut source)
    @_coconut_tco  #124 (line in Coconut source)
    def running(self) -> int:  #124 (line in Coconut source)
        return _coconut_tail_call(sum, (1 for r in self.results.values() if r.status == BatchStatus.RUNNING))  #125 (line in Coconut source)


    @property  #127 (line in Coconut source)
    def status(self) -> BatchStatus:  #128 (line in Coconut source)
        if self.ended_at is None:  #129 (line in Coconut source)
            return BatchStatus.RUNNING  #130 (line in Coconut source)
        if self.failed == 0:  #131 (line in Coconut source)
            return BatchStatus.COMPLETED  #132 (line in Coconut source)
        if self.completed == 0:  #133 (line in Coconut source)
            return BatchStatus.FAILED  #134 (line in Coconut source)
        return BatchStatus.PARTIAL  #135 (line in Coconut source)


    @property  #137 (line in Coconut source)
    def progress(self) -> float:  #138 (line in Coconut source)
        """Fraction of items finished (completed + failed) out of total."""  #139 (line in Coconut source)
        if self.total == 0:  #140 (line in Coconut source)
            return 1.0  #141 (line in Coconut source)
        return (self.completed + self.failed) / self.total  #142 (line in Coconut source)


    def successful_outputs(self) -> list[Any]:  #144 (line in Coconut source)
        """Outputs of all COMPLETED items in original item order."""  #145 (line in Coconut source)
        return [r.output for r in sorted(self.results.values(), key=lambda r: int(r.item_id)) if r.status == BatchStatus.COMPLETED]  #146 (line in Coconut source)


# ---------------------------------------------------------------------------
# BatchExecutor
# ---------------------------------------------------------------------------


class BatchExecutor():  #157 (line in Coconut source)
    """Runs an agent node over a list of items with full batch management.

    Each item is processed by an independent executor.run() call so there is
    no shared mutable state between items.

    Args:
        store:       GraphStore used for checkpointing.
        executor:    GraphExecutor that will run the agent per item.
        concurrency: Maximum number of items processed concurrently.
    """  #167 (line in Coconut source)

    def __init__(self, store: GraphStore, executor: Any, concurrency: int=10,) -> None:  # GraphExecutor — typed as Any to avoid circular import  #169 (line in Coconut source)
        import warnings  #175 (line in Coconut source)
        warnings.warn('Constructing BatchExecutor directly is deprecated. Use executor.batch(...) instead.', DeprecationWarning, stacklevel=2)  #176 (line in Coconut source)
        self.store = store  #182 (line in Coconut source)
        self.executor = executor  #183 (line in Coconut source)
        self.concurrency = concurrency  #184 (line in Coconut source)

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


    async def run(self, agent_node_id: str, items: list[Any], query_fn: Callable[[Any,], str], *, context_fn: Callable[[Any,], str | None] | None=None, reduce_fn: Callable[[list[Any],], Any] | None=None, on_progress: Callable[["BatchRun",], Any] | None=None, checkpoint: bool=True, strategy: str="sequential",) -> BatchRun:  #190 (line in Coconut source)
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
        """  #217 (line in Coconut source)
        run = BatchRun(run_id=str(uuid.uuid4()), agent_id=agent_node_id, total=len(items), results={str(i): BatchItemResult(item_id=str(i)) for i in range(len(items))})  #218 (line in Coconut source)

        if checkpoint:  #225 (line in Coconut source)
            await self._checkpoint_run(run)  #226 (line in Coconut source)

        await self._execute(run, items, query_fn, context_fn, on_progress, checkpoint, strategy)  #228 (line in Coconut source)

        run.ended_at = _now()  #230 (line in Coconut source)

        if reduce_fn is not None:  #232 (line in Coconut source)
            run.reduced_output = reduce_fn(run.successful_outputs())  #233 (line in Coconut source)

        if checkpoint:  #235 (line in Coconut source)
            await self._checkpoint_run(run)  #236 (line in Coconut source)

        return run  #238 (line in Coconut source)


    async def resume(self, run_id: str, items: list[Any], query_fn: Callable[[Any,], str], *, context_fn: Callable[[Any,], str | None] | None=None, reduce_fn: Callable[[list[Any],], Any] | None=None, on_progress: Callable[["BatchRun",], Any] | None=None, strategy: str="sequential",) -> BatchRun:  #240 (line in Coconut source)
        """Resume a previously checkpointed run, skipping COMPLETED items.

        Items that were RUNNING when the process crashed are treated as PENDING
        and re-executed.

        Args:
            run_id: The BatchRun.run_id from the original run.
            items:  Must be the same list (same length and order) as the original.
        """  #259 (line in Coconut source)
        run = await self._load_checkpoint(run_id)  #260 (line in Coconut source)

# Re-run everything that did not successfully complete
        await self._execute(run, items, query_fn, context_fn, on_progress, True, strategy)  #263 (line in Coconut source)

        run.ended_at = _now()  #265 (line in Coconut source)

        if reduce_fn is not None:  #267 (line in Coconut source)
            run.reduced_output = reduce_fn(run.successful_outputs())  #268 (line in Coconut source)

        await self._checkpoint_run(run)  #270 (line in Coconut source)
        return run  #271 (line in Coconut source)

# ------------------------------------------------------------------
# Internals
# ------------------------------------------------------------------


    async def _execute(self, run: BatchRun, items: list[Any], query_fn: Callable[[Any,], str], context_fn: Callable[[Any,], str | None] | None, on_progress: Callable[[BatchRun,], Any] | None, checkpoint: bool, strategy: str,) -> None:  #277 (line in Coconut source)
        """Fan out execution over all items with a concurrency semaphore."""  #287 (line in Coconut source)
        sem = asyncio.Semaphore(self.concurrency)  #288 (line in Coconut source)

        async def _process(idx: int, item: Any) -> None:  #290 (line in Coconut source)
            item_id = str(idx)  #291 (line in Coconut source)
            result = run.results[item_id]  #292 (line in Coconut source)

# Skip items already completed (resume path)
            if result.status == BatchStatus.COMPLETED:  #295 (line in Coconut source)
                return  #296 (line in Coconut source)

            result.status = BatchStatus.RUNNING  #298 (line in Coconut source)
            result.started_at = _now()  #299 (line in Coconut source)

            if checkpoint:  #301 (line in Coconut source)
                await self._checkpoint_item(run.run_id, result)  #302 (line in Coconut source)

            try:  #304 (line in Coconut source)
                async with sem:  #305 (line in Coconut source)
                    query = query_fn(item)  #306 (line in Coconut source)

                    extra_messages: list[dict[str, Any]] | None = None  #308 (line in Coconut source)
                    if context_fn:  #309 (line in Coconut source)
                        ctx_text = context_fn(item)  #310 (line in Coconut source)
                        if ctx_text:  #311 (line in Coconut source)
                            extra_messages = [{"role": "user", "content": ctx_text},]  #312 (line in Coconut source)

                    exec_ctx = await self.executor.run(run.agent_id, query, strategy=strategy, extra_messages=extra_messages)  #314 (line in Coconut source)
                    result.output = exec_ctx.outputs.get(run.agent_id)  #320 (line in Coconut source)
                    result.status = BatchStatus.COMPLETED  #321 (line in Coconut source)

            except Exception as exc:  #323 (line in Coconut source)
                result.status = BatchStatus.FAILED  #324 (line in Coconut source)
                result.error = "{_coconut_format_0}: {_coconut_format_1}".format(_coconut_format_0=(type(exc).__name__), _coconut_format_1=(exc))  #325 (line in Coconut source)

            finally:  #327 (line in Coconut source)
                result.ended_at = _now()  #328 (line in Coconut source)

                if checkpoint:  #330 (line in Coconut source)
                    await self._checkpoint_item(run.run_id, result)  #331 (line in Coconut source)

                if on_progress is not None:  #333 (line in Coconut source)
                    ret = on_progress(run)  #334 (line in Coconut source)
                    if asyncio.iscoroutine(ret):  #335 (line in Coconut source)
                        await ret  #336 (line in Coconut source)

# return_exceptions=False is safe here because _process never raises —
# all exceptions are caught inside the try/except block above.

        await asyncio.gather(*[_process(i, item) for i, item in enumerate(items)])  #340 (line in Coconut source)

# ------------------------------------------------------------------
# Checkpointing
# ------------------------------------------------------------------


    async def _checkpoint_run(self, run: BatchRun) -> None:  #346 (line in Coconut source)
        """Upsert a ContextNode representing the BatchRun's current state."""  #347 (line in Coconut source)
        node = ContextNode(node_id=_run_node_id(run.run_id), name="BatchRun {_coconut_format_0}".format(_coconut_format_0=(run.run_id[:8])), description=(("Batch: {_coconut_format_0}/{_coconut_format_1} completed, ".format(_coconut_format_0=(run.completed), _coconut_format_1=(run.total)) + "{_coconut_format_0} failed — {_coconut_format_1}".format(_coconut_format_0=(run.failed), _coconut_format_1=(run.status)))), content=json.dumps({"run_id": run.run_id, "agent_id": run.agent_id, "total": run.total, "completed": run.completed, "failed": run.failed, "status": run.status, "started_at": run.started_at.isoformat(), "ended_at": run.ended_at.isoformat() if run.ended_at else None}), content_type="batch_run", source="agent:{_coconut_format_0}".format(_coconut_format_0=(run.agent_id)), attributes={"run_id": run.run_id})  #348 (line in Coconut source)
        await self.store.upsert_node(node)  #369 (line in Coconut source)


    async def _checkpoint_item(self, run_id: str, result: BatchItemResult) -> None:  #371 (line in Coconut source)
        """Upsert a ContextNode representing one item's current state."""  #372 (line in Coconut source)
        node = ContextNode(node_id=_item_node_id(run_id, result.item_id), name="BatchItem {_coconut_format_0}".format(_coconut_format_0=(result.item_id)), description="Item {_coconut_format_0} — {_coconut_format_1}".format(_coconut_format_0=(result.item_id), _coconut_format_1=(result.status)), content=json.dumps({"run_id": run_id, "item_id": result.item_id, "status": result.status, "error": result.error, "started_at": result.started_at.isoformat() if result.started_at else None, "ended_at": result.ended_at.isoformat() if result.ended_at else None}), content_type="batch_item", source="batch_run:{_coconut_format_0}".format(_coconut_format_0=(run_id)), attributes={"run_id": run_id})  #373 (line in Coconut source)
        await self.store.upsert_node(node)  #389 (line in Coconut source)


    async def _load_checkpoint(self, run_id: str) -> BatchRun:  #391 (line in Coconut source)
        """Reconstruct a BatchRun from its checkpoint nodes in the graph."""  #392 (line in Coconut source)
        run_node = await self.store.get_node(_run_node_id(run_id))  #393 (line in Coconut source)
        if run_node is None:  #394 (line in Coconut source)
            raise ValueError("No checkpoint found for run_id={_coconut_format_0!r}".format(_coconut_format_0=(run_id)))  #395 (line in Coconut source)

        run_data = json.loads(run_node.content)  # type: ignore[union-attr]  #397 (line in Coconut source)
        run = BatchRun(run_id=run_id, agent_id=run_data["agent_id"], total=run_data["total"], started_at=datetime.fromisoformat(run_data["started_at"]), results={str(i): BatchItemResult(item_id=str(i)) for i in range(run_data["total"])})  #398 (line in Coconut source)

# Reload per-item state
        for i in range(run.total):  #407 (line in Coconut source)
            item_node = await self.store.get_node(_item_node_id(run_id, str(i)))  #408 (line in Coconut source)
            if item_node is None:  #409 (line in Coconut source)
                continue  #410 (line in Coconut source)
            item_data = json.loads(item_node.content)  # type: ignore[union-attr]  #411 (line in Coconut source)
            result = run.results[str(i)]  #412 (line in Coconut source)
            result.status = BatchStatus(item_data["status"])  #413 (line in Coconut source)
            result.error = item_data.get("error")  #414 (line in Coconut source)
            if item_data.get("started_at"):  #415 (line in Coconut source)
                result.started_at = datetime.fromisoformat(item_data["started_at"])  #416 (line in Coconut source)
            if item_data.get("ended_at"):  #417 (line in Coconut source)
                result.ended_at = datetime.fromisoformat(item_data["ended_at"])  #418 (line in Coconut source)
# Items interrupted mid-run (RUNNING) are treated as PENDING for retry
            if result.status == BatchStatus.RUNNING:  #420 (line in Coconut source)
                result.status = BatchStatus.PENDING  #421 (line in Coconut source)

        return run  #423 (line in Coconut source)


# ---------------------------------------------------------------------------
# Deterministic node ID helpers (UUID v5 so IDs are stable across restarts)
# ---------------------------------------------------------------------------


@_coconut_tco  #430 (line in Coconut source)
def _run_node_id(run_id: str) -> str:  #430 (line in Coconut source)
    return _coconut_tail_call(str, uuid.uuid5(uuid.NAMESPACE_DNS, "batch_run:{_coconut_format_0}".format(_coconut_format_0=(run_id))))  #431 (line in Coconut source)



@_coconut_tco  #434 (line in Coconut source)
def _item_node_id(run_id: str, item_id: str) -> str:  #434 (line in Coconut source)
    return _coconut_tail_call(str, uuid.uuid5(uuid.NAMESPACE_DNS, "batch_item:{_coconut_format_0}:{_coconut_format_1}".format(_coconut_format_0=(run_id), _coconut_format_1=(item_id))))  #435 (line in Coconut source)
