"""Example: Research → Synthesis pipeline.

Demonstrates the full yggdrasil architecture:

Graph topology:
    ResearcherAgent  ──HAS_TOOL──► WebSearchTool
    ResearcherAgent  ──HAS_CONTEXT──► PythonDocsContext
    ResearcherAgent  ──HAS_PROMPT──► ResearcherPrompt
    ResearcherAgent  ──DELEGATES_TO──► SynthesizerAgent
    SynthesizerAgent ──HAS_PROMPT──► SynthesizerPrompt

Execution (sequential):
    1. ResearcherAgent composes itself via graph traversal
       → system = ResearcherPrompt.render() + PythonDocsContext.content
       → tools  = [WebSearchTool schema]
    2. LLM decides to call web_search("...")
    3. web_search result is materialised as a new ContextNode + PRODUCES edge
    4. LLM returns its research summary
    5. routing_table["default"] → SynthesizerAgent
    6. SynthesizerAgent composes itself, writes the final report

Run:
    ANTHROPIC_API_KEY=<key> python -m examples.research_pipeline
"""

from __future__ import annotations

import asyncio
import os

from yggdrasil_lm import AgentNode, ContextNode, Edge, GraphExecutor, NetworkXGraphStore, ToolNode
from yggdrasil_lm.core.executor import AgentComposer
from yggdrasil_lm.core.nodes import PromptNode
from yggdrasil_lm.tools.registry import default_registry


async def build_graph(store: NetworkXGraphStore) -> str:
    """Construct the research pipeline graph. Returns the entry agent node_id."""

    # ── 1. Prompt nodes ───────────────────────────────────────────────────
    researcher_prompt = PromptNode(
        name="ResearcherSystemPrompt",
        description="System prompt for the Researcher agent",
        template=(
            "You are a technical researcher. Your job is to find accurate, "
            "up-to-date information on the given topic using the web_search tool. "
            "Search for relevant details, cite sources, and summarise your findings "
            "clearly. When you are done researching, end your response with "
            "'SYNTHESIS NEEDED' so the synthesis step is triggered."
        ),
    )

    synthesizer_prompt = PromptNode(
        name="SynthesizerSystemPrompt",
        description="System prompt for the Synthesizer agent",
        template=(
            "You are a technical writer. Given research findings, produce a "
            "well-structured, concise report with: an executive summary, key findings, "
            "and actionable next steps. Use markdown formatting."
        ),
    )

    # ── 2. Context node (static knowledge) ───────────────────────────────
    python_docs_ctx = ContextNode(
        name="Python Ecosystem Overview",
        description="Background context about the Python ecosystem",
        content=(
            "Python is a high-level, dynamically typed programming language widely "
            "used for data science, web development, automation, and AI/ML. "
            "Key libraries include NumPy, Pandas, FastAPI, LangChain, and PyTorch. "
            "Python 3.11+ introduced significant performance improvements (up to 60% "
            "faster than 3.10). The async/await paradigm is standard for I/O-bound tasks."
        ),
        source="static-knowledge",
        token_count=100,
    )

    # ── 3. Tool node ──────────────────────────────────────────────────────
    web_search_tool = ToolNode(
        name="web_search",
        description=(
            "Search the web for current information on any topic. "
            "Returns titles and snippets from the top results."
        ),
        callable_ref="tools.web_search.search",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5).",
                },
            },
            "required": ["query"],
        },
        output_schema={"type": "string"},
        is_async=True,
    )

    # ── 4. Agent nodes ────────────────────────────────────────────────────
    synthesizer = AgentNode(
        name="SynthesizerAgent",
        description="Synthesises research findings into a structured report",
        model=os.getenv("AGENT_MODEL", "claude-sonnet-4-6"),
        routing_table={"default": "__END__"},
    )

    researcher = AgentNode(
        name="ResearcherAgent",
        description="Researches technical topics using web search and background context",
        model=os.getenv("AGENT_MODEL", "claude-sonnet-4-6"),
        routing_table={
            "synthesis needed": synthesizer.node_id,
            "default":          synthesizer.node_id,  # always hand off to synthesizer
        },
    )

    # ── 5. Store all nodes ────────────────────────────────────────────────
    for node in [
        researcher_prompt, synthesizer_prompt,
        python_docs_ctx,
        web_search_tool,
        researcher, synthesizer,
    ]:
        await store.upsert_node(node)

    # ── 6. Wire composition via edges ──────────────────────────────────
    edges = [
        # Researcher composition
        Edge.has_tool(researcher.node_id, web_search_tool.node_id),
        Edge.has_context(researcher.node_id, python_docs_ctx.node_id, weight=0.8),
        Edge.has_prompt(researcher.node_id, researcher_prompt.node_id),

        # Delegation
        Edge.delegates_to(researcher.node_id, synthesizer.node_id),

        # Synthesizer composition
        Edge.has_prompt(synthesizer.node_id, synthesizer_prompt.node_id),
    ]
    for edge in edges:
        await store.upsert_edge(edge)

    return researcher.node_id


async def run_pipeline(query: str, backend=None) -> None:
    store    = NetworkXGraphStore()
    entry_id = await build_graph(store)

    composer = AgentComposer(store)
    executor = GraphExecutor(store, composer, backend=backend)
    default_registry.attach(executor)

    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    ctx = await executor.run(
        entry_node_id=entry_id,
        query=query,
        strategy="sequential",
    )

    # Print trace (hop events only)
    print("\n--- Execution Trace ---")
    for step in ctx.trace:
        if step.event_type == "hop":
            hop_num = step.payload.get("hop", "?")
            summary = step.payload.get("summary", "")[:120]
            print(f"  [hop {hop_num}] {step.node_name}")
            print(f"       {summary}")

    # Print final output
    print("\n--- Final Output ---")
    for node_id, output in ctx.outputs.items():
        node = await store.get_node(node_id)
        if node:
            label = f"{node.name} ({node.node_type})"
        else:
            label = node_id
        if isinstance(output, dict) and "text" in output:
            print(f"\n[{label}]\n{output['text']}\n")

    print(f"\nTotal hops: {ctx.hop_count}")


def main() -> None:
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "What are the most important Python async improvements in recent versions, "
        "and how do they compare to JavaScript's async model?"
    )
    asyncio.run(run_pipeline(query))


if __name__ == "__main__":
    main()
