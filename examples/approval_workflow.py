"""Runnable local example: explicit approval step with resume.

Run:
    python -m examples.approval_workflow
"""

from __future__ import annotations

import asyncio

from yggdrasil import ApprovalNode, GraphExecutor, NetworkXGraphStore, create_agent

from examples._stub_backend import SequenceBackend, end_turn


async def run_demo() -> None:
    store = NetworkXGraphStore()

    approved = create_agent(
        "ApprovedPath",
        system_prompt="You confirm that the request can proceed.",
    )
    rejected = create_agent(
        "RejectedPath",
        system_prompt="You explain why the request was rejected.",
    )
    approval = ApprovalNode(
        name="ManagerApproval",
        instructions="Manager must approve the purchase.",
        assignees=["mgr-1"],
        approved_target_id=approved.node_id,
        rejected_target_id=rejected.node_id,
    )

    for node in [approval, approved, rejected]:
        await store.upsert_node(node)

    executor = GraphExecutor(store, backend=SequenceBackend([end_turn("Approved and ready.")]))
    ctx = await executor.run(approval.node_id, "Request approval for a laptop purchase.")

    print("\n--- Pending Inbox ---")
    for task in ctx.state.inbox.values():
        print(
            {
                "task_id": task.task_id,
                "assigned_to": task.assigned_to,
                "waiting_for": task.waiting_for,
            }
        )

    ctx.state.data["approval"] = {"approved": True, "assigned_to": "mgr-1"}
    resumed = await executor.resume(approval.node_id, ctx, query="Continue after approval.")

    print("\n--- Resumed Outputs ---")
    for node_id, output in resumed.outputs.items():
        node = await store.get_node(node_id)
        if isinstance(output, dict) and "text" in output:
            print(f"{node.name}: {output['text']}")


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
