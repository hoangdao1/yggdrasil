"""Image query and visual RAG example.

Demonstrates two patterns:
1. Inline image query — pass an image alongside the question at call time.
2. Visual RAG — attach a persistent image ContextNode to an agent so it is
   included automatically on every call.

Run (requires ANTHROPIC_API_KEY):
    python examples/image_query_and_visual_rag.py

Both patterns follow the Anthropic / OpenAI content-block schema under the
hood.  The OpenAI-compatible backend converts them automatically.
"""

import asyncio

from yggdrasil_lm.app import GraphApp
from yggdrasil_lm.media import build_query, image_from_url


SAMPLE_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/"
    "PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
)


async def pattern_1_inline_image_query() -> None:
    """Send an image together with the question in a single run() call."""
    print("=== Pattern 1: inline image query ===")
    app = GraphApp()
    agent = await app.add_agent("Vision", system_prompt="You are a helpful vision assistant.")

    query = build_query("What do you see in this image?", image_from_url(SAMPLE_IMAGE_URL))
    ctx = await app.run(agent, query)
    print(ctx.outputs[agent.node_id]["text"])


async def pattern_2_visual_rag() -> None:
    """Attach an image ContextNode — the agent sees it on every call."""
    print("\n=== Pattern 2: visual RAG (persistent image context) ===")
    app = GraphApp()
    agent = await app.add_agent(
        "Analyst",
        system_prompt="You are a visual analyst. Use the provided image context to answer questions.",
    )

    # Attach a URL-based image as a persistent context node
    logo = await app.add_image_context(
        "Sample image",
        url=SAMPLE_IMAGE_URL,
        description="A demo PNG with transparency.",
    )
    await app.connect_context(agent, logo)

    # The image is injected automatically — no need to include it in the query
    ctx = await app.run(agent, "Describe the colours in the image.")
    print(ctx.outputs[agent.node_id]["text"])


async def main() -> None:
    await pattern_1_inline_image_query()
    await pattern_2_visual_rag()


if __name__ == "__main__":
    asyncio.run(main())
