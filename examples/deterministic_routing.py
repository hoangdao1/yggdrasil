"""Runnable local example: deterministic routing from workflow state.

Run:
    python -m examples.deterministic_routing
"""

from __future__ import annotations

import asyncio

from yggdrasil import GraphExecutor, NetworkXGraphStore, RouteRule, create_agent

from examples._stub_backend import SequenceBackend, end_turn


async def run_demo() -> None:
    store = NetworkXGraphStore()

    manager = create_agent(
        "ManagerReview",
        system_prompt="You are the manager escalation reviewer.",
    )
    intake = create_agent(
        "SupportIntake",
        system_prompt="You triage support tickets.",
        route_rules=[
            RouteRule(
                name="escalate_billing",
                source="state",
                path="ticket.escalated",
                operator="equals",
                value=True,
                target_node_id=manager.node_id,
                priority=10,
            )
        ],
    )

    await store.upsert_node(intake)
    await store.upsert_node(manager)

    backend = SequenceBackend(
        [
            end_turn("Ticket classified and ready for routing."),
            end_turn("Manager review complete: refund approved."),
        ]
    )
    executor = GraphExecutor(store, backend=backend)
    ctx = await executor.run(
        intake.node_id,
        "Customer reports duplicate billing on the same order.",
        state={"ticket": {"escalated": True}},
    )

    print("\n--- Outputs ---")
    for node_id, output in ctx.outputs.items():
        node = await store.get_node(node_id)
        print(f"{node.name}: {output['text']}")

    print("\n--- Routing Events ---")
    for event in ctx.trace:
        if event.event_type == "routing":
            print(event.payload)


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
