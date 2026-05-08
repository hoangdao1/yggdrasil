"""Runnable local example: split → parallel workers → join → summarizer.

Demonstrates TransformNode for fan-out splitting and fan-in joining without
any LLM calls in the transform steps.

Run:
    python -m examples.fan_in_workers
"""

from __future__ import annotations

import asyncio
from typing import Any

from yggdrasil_lm import (
    Edge,
    GraphExecutor,
    NetworkXGraphStore,
    TransformNode,
    create_agent,
    create_transform,
)

from examples._stub_backend import RuleBasedBackend, SmartReply


def split_items(data: dict[str, Any]) -> dict[str, Any]:
    """Split a list of items into per-worker buckets written to state."""
    items: list[str] = data.get("items", ["item_a", "item_b", "item_c"])
    return {f"bucket_{i}": item for i, item in enumerate(items)}


def join_results(data: dict[str, Any]) -> dict[str, Any]:
    """Merge outputs from all worker node_ids into a single summary dict."""
    combined = []
    for key in sorted(data):
        val = data[key]
        text = val.get("text", str(val)) if isinstance(val, dict) else str(val)
        combined.append(f"[{key}] {text}")
    return {"merged": "\n".join(combined)}


async def run_demo() -> None:
    store = NetworkXGraphStore()

    splitter = create_transform(
        "Splitter",
        callable_ref="examples.fan_in_workers.split_items",
        description="Splits input items into per-worker buckets",
        output_key="buckets",
        is_async=False,
    )
    worker_a = create_agent("WorkerA", system_prompt="Process bucket_0.")
    worker_b = create_agent("WorkerB", system_prompt="Process bucket_1.")
    worker_c = create_agent("WorkerC", system_prompt="Process bucket_2.")
    joiner = create_transform(
        "Joiner",
        callable_ref="examples.fan_in_workers.join_results",
        description="Merges all worker outputs into one payload",
        input_keys=[worker_a.node_id, worker_b.node_id, worker_c.node_id],
        output_key="joined",
        is_async=False,
    )
    summarizer = create_agent("Summarizer", system_prompt="Summarize the joined results.")

    for node in [splitter, worker_a, worker_b, worker_c, joiner, summarizer]:
        await store.upsert_node(node)

    # splitter → workers (fan-out)
    for worker in [worker_a, worker_b, worker_c]:
        await store.upsert_edge(Edge.delegates_to(splitter.node_id, worker.node_id))

    # workers → joiner (fan-in — also declared via input_keys)
    for worker in [worker_a, worker_b, worker_c]:
        await store.upsert_edge(Edge.delegates_to(worker.node_id, joiner.node_id))

    # joiner → summarizer
    await store.upsert_edge(Edge.delegates_to(joiner.node_id, summarizer.node_id))

    backend = RuleBasedBackend([
        SmartReply("bucket_0", "WorkerA result: processed item_a"),
        SmartReply("bucket_1", "WorkerB result: processed item_b"),
        SmartReply("bucket_2", "WorkerC result: processed item_c"),
        SmartReply("summarize", "Summary: all three items processed successfully."),
    ])
    executor = GraphExecutor(store, backend=backend)
    executor.register_tool("examples.fan_in_workers.split_items", split_items)
    executor.register_tool("examples.fan_in_workers.join_results", join_results)

    ctx = await executor.run(
        splitter.node_id,
        "Process items: item_a, item_b, item_c",
        strategy="topological",
        state={"items": ["item_a", "item_b", "item_c"]},
    )

    print("\n--- Splitter buckets (state) ---")
    print(ctx.state.data.get("buckets"))

    print("\n--- Worker outputs ---")
    for worker in [worker_a, worker_b, worker_c]:
        out = ctx.outputs.get(worker.node_id, {})
        print(f"  {worker.name}: {out.get('text', out)}")

    print("\n--- Joined result (state) ---")
    print(ctx.state.data.get("joined"))

    print("\n--- Summarizer ---")
    print(ctx.outputs.get(summarizer.node_id, {}).get("text"))


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
