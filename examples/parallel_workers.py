"""Runnable local example: supervisor / worker fan-out.

Run:
    python -m examples.parallel_workers
"""

from __future__ import annotations

import asyncio

from yggdrasil_lm import Edge, GraphExecutor, NetworkXGraphStore, create_agent

from examples._stub_backend import RuleBasedBackend, SmartReply


async def run_demo() -> None:
    store = NetworkXGraphStore()

    supervisor = create_agent("Supervisor", system_prompt="You coordinate the workers.")
    sentiment = create_agent("SentimentWorker", system_prompt="You analyze sentiment.")
    entities = create_agent("EntityWorker", system_prompt="You extract entities.")
    topics = create_agent("TopicWorker", system_prompt="You classify the topic.")

    for node in [supervisor, sentiment, entities, topics]:
        await store.upsert_node(node)

    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, sentiment.node_id))
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, entities.node_id))
    await store.upsert_edge(Edge.delegates_to(supervisor.node_id, topics.node_id))

    backend = RuleBasedBackend(
        [
            SmartReply("coordinate", "Supervisor ready. Delegating to workers."),
            SmartReply("sentiment", "Sentiment: the customer sounds frustrated but calm."),
            SmartReply("extract entities", "Entities: customer, invoice #4821, April renewal."),
            SmartReply("classify the topic", "Topic: billing dispute."),
        ]
    )
    executor = GraphExecutor(store, backend=backend)
    ctx = await executor.run(
        supervisor.node_id,
        "Analyze a support message about a billing dispute.",
        strategy="parallel",
    )

    print("\n--- Supervisor Output ---")
    print(ctx.outputs[supervisor.node_id]["node_result"]["text"])

    print("\n--- Worker Outputs ---")
    delegate_results = ctx.outputs[supervisor.node_id]["delegate_results"]
    for node_id, output in delegate_results.items():
        node = await store.get_node(node_id)
        print(f"{node.name}: {output['text']}")


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
