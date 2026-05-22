"""End-to-end demo of GraphNode: a reusable sub-graph driven by a real LLM.

Backend selection is generic — point this script at any provider supported
by ``GraphApp``:

    # Anthropic (default if ANTHROPIC_API_KEY is set)
    export ANTHROPIC_API_KEY=...
    python examples/subgraph_reuse.py

    # Any OpenAI-compatible endpoint (Ollama, vLLM, mlx-lm, OpenAI itself, …)
    export YGG_PROVIDER=compatible
    export YGG_BASE_URL=http://localhost:1234/v1
    export YGG_API_KEY=dummy
    export YGG_MODEL=your-model-id
    python examples/subgraph_reuse.py

What this exercises:
  1. A reusable sub-graph (extractor → critic chain) wrapped as a single
     GraphNode and run TWICE from different parent contexts.
  2. ``input_map`` threading parent-state values into each sub-run.
  3. ``exit_node_id`` so the sub-graph surfaces ONLY the critic's verdict,
     not the extractor's intermediate output.
  4. ``scope_outputs=True`` (default) so the two reuses do not collide in
     the parent's ``ctx.outputs``.
"""

from __future__ import annotations

import asyncio
import os

from yggdrasil_lm.app import GraphApp


def build_app() -> tuple[GraphApp, str]:
    """Pick a backend from environment variables and return (app, model_id)."""
    provider = os.environ.get("YGG_PROVIDER", "anthropic")
    model    = os.environ.get("YGG_MODEL", "claude-sonnet-4-6")
    if provider == "anthropic":
        return GraphApp(), model
    return (
        GraphApp(
            provider=provider,
            base_url=os.environ.get("YGG_BASE_URL"),
            api_key=os.environ.get("YGG_API_KEY", "local"),
        ),
        model,
    )


async def main() -> None:
    app, model = build_app()

    # --- Build the reusable sub-graph ----------------------------------
    extractor = await app.add_agent(
        "Extractor",
        model=model,
        system_prompt=(
            "You read a short product description from `state.data.product_text` "
            "(also restated in the user message) and emit a single line: "
            "'CLAIM: <the single strongest marketing claim>'. No commentary."
        ),
        routing_table={"default": ""},  # filled in below
    )
    critic = await app.add_agent(
        "Critic",
        model=model,
        system_prompt=(
            "Given a CLAIM line in the conversation, respond with exactly one "
            "of: 'VERDICT: SUPPORTABLE' or 'VERDICT: HYPE'. Add a one-sentence "
            "rationale on the next line."
        ),
        routing_table={"default": "__END__"},
    )
    extractor.routing_table["default"] = critic.node_id
    await app.store.upsert_node(extractor)

    review_pipeline = await app.add_subgraph(
        "ReviewPipeline",
        entry=extractor,
        exit=critic,                          # surface critic's verdict only
        input_map={"product_text": "current_product"},
    )

    # --- Parent graph: run the same sub-graph twice --------------------
    products = [
        "QuantumBoost X9 — increases your laptop's battery life by 400% via "
        "AI-driven quantum dynamics in the firmware.",
        "FieldNotes notebook — 48 pages of dot-grid paper, cloth cover, "
        "sewn binding, A5 size.",
    ]

    for i, text in enumerate(products, start=1):
        print(f"\n=== Product {i} ===\n{text}")
        ctx = await app.run(
            review_pipeline,
            query=f"Review this product:\n{text}",
            state={"current_product": text},
        )
        result = ctx.outputs.get(review_pipeline.node_id)
        verdict_text = result.get("text") if isinstance(result, dict) else result
        print(f"\nSub-graph result (from exit node = Critic):\n{verdict_text}")

        leaked = [
            nid for nid in (extractor.node_id, critic.node_id)
            if nid in ctx.outputs
        ]
        assert not leaked, f"Inner nodes leaked to parent outputs: {leaked}"
        assert ctx.state.data.get("product_text") == text

        sub_events = [
            e for e in ctx.trace
            if e.event_type in ("subgraph_enter", "subgraph_exit")
        ]
        for ev in sub_events:
            print(f"  trace: {ev.event_type}  payload={ev.payload}")


if __name__ == "__main__":
    asyncio.run(main())
