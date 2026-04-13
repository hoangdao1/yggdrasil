"""Benchmark task definitions.

Each BenchmarkTask encodes:
- query: the user prompt given to every system under test
- agent_roles: per-agent instructions for multi-agent baselines
  (graph-agent builds this from the graph; baselines use them directly)
- eval_fn: lightweight quality check on the final output string
- tags: labels for filtering/grouping
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AgentRole:
    """One agent's identity in a multi-agent pipeline."""
    name: str
    system_prompt: str
    # tools this agent should have access to (names match allowed_tools on CLI)
    tools: list[str] = field(default_factory=list)


@dataclass
class BenchmarkTask:
    id: str
    name: str
    query: str
    # Ordered pipeline of agents — graph-agent builds this from graph edges;
    # the multi-agent baseline chains these as sequential headless calls.
    agent_roles: list[AgentRole]
    # Full system prompt for the single-agent baseline (no graph composition).
    single_agent_system: str
    eval_fn: Callable[[str], bool]
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Task 1 — Research & synthesis (2-agent pipeline)
# ---------------------------------------------------------------------------

RESEARCH_TASK = BenchmarkTask(
    id="research_synthesis",
    name="Research + Synthesis (2-agent)",
    query=(
        "What are the main differences between Python asyncio and JavaScript Promises? "
        "Focus on error propagation and cancellation semantics."
    ),
    agent_roles=[
        AgentRole(
            name="Researcher",
            system_prompt=(
                "You are a technical researcher. Find accurate, detailed information "
                "about the topic using WebSearch. Summarise your findings with citations. "
                "When done, end with 'SYNTHESIS NEEDED'."
            ),
            tools=["WebSearch"],
        ),
        AgentRole(
            name="Synthesizer",
            system_prompt=(
                "You are a technical writer. Given research findings, produce a "
                "well-structured report with: an executive summary, key differences "
                "table, and actionable recommendations. Use markdown."
            ),
            tools=[],
        ),
    ],
    single_agent_system=(
        "You are a technical expert on async programming. "
        "Research and synthesise a detailed comparison of Python asyncio vs JavaScript Promises, "
        "focusing on error propagation and cancellation semantics. "
        "Use WebSearch if needed. Format as a structured markdown report."
    ),
    eval_fn=lambda out: (
        any(kw in out.lower() for kw in ["asyncio", "promise", "async"])
        and any(kw in out.lower() for kw in ["cancel", "error", "exception", "reject"])
        and len(out) > 200
    ),
    tags=["multi-agent", "research", "web-search"],
)


# ---------------------------------------------------------------------------
# Task 2 — Code analysis (2-agent: analyser → reviewer)
# ---------------------------------------------------------------------------

CODEBASE_ANALYSIS_TASK = BenchmarkTask(
    id="code_analysis",
    name="Codebase Analysis + Review (2-agent)",
    query=(
        "Analyse the yggdrasil/core/executor.py file. "
        "Identify the top 3 algorithmic bottlenecks and suggest concrete improvements."
    ),
    agent_roles=[
        AgentRole(
            name="Analyser",
            system_prompt=(
                "You are a senior software engineer. Read and analyse the provided file "
                "using Read/Grep/Glob tools. Identify algorithmic complexity, hot paths, "
                "and potential bottlenecks. Write a structured analysis. "
                "End with 'REVIEW NEEDED'."
            ),
            tools=["Read", "Grep", "Glob"],
        ),
        AgentRole(
            name="Reviewer",
            system_prompt=(
                "You are a performance engineering expert. Given a code analysis, "
                "produce concrete improvement recommendations with pseudocode where helpful. "
                "Rank suggestions by expected impact."
            ),
            tools=[],
        ),
    ],
    single_agent_system=(
        "You are a senior software engineer and performance expert. "
        "Read yggdrasil/core/executor.py using available tools, analyse it for "
        "algorithmic bottlenecks, and produce concrete ranked improvement recommendations."
    ),
    eval_fn=lambda out: (
        any(kw in out.lower() for kw in ["bottleneck", "complex", "o(n", "performance", "optimis"])
        and any(kw in out.lower() for kw in ["suggest", "recommend", "improve", "could", "should"])
        and len(out) > 200
    ),
    tags=["multi-agent", "code-analysis", "file-tools"],
)


# ---------------------------------------------------------------------------
# Task 3 — Simple Q&A (1-agent, no tools) — sanity-check / overhead baseline
# ---------------------------------------------------------------------------

SIMPLE_QA_TASK = BenchmarkTask(
    id="simple_qa",
    name="Simple Q&A (1-agent, no tools)",
    query=(
        "Explain the difference between BFS and DFS graph traversal "
        "and give one real-world use case for each."
    ),
    agent_roles=[
        AgentRole(
            name="Expert",
            system_prompt="You are a computer science expert. Answer concisely and accurately.",
            tools=[],
        ),
    ],
    single_agent_system=(
        "You are a computer science expert. Answer questions concisely and accurately."
    ),
    eval_fn=lambda out: (
        "bfs" in out.lower() and "dfs" in out.lower()
        and any(kw in out.lower() for kw in ["breadth", "depth"])
        and len(out) > 100
    ),
    tags=["single-agent", "no-tools", "overhead"],
)


ALL_TASKS: list[BenchmarkTask] = [
    RESEARCH_TASK,
    CODEBASE_ANALYSIS_TASK,
    SIMPLE_QA_TASK,
]

TASK_MAP: dict[str, BenchmarkTask] = {t.id: t for t in ALL_TASKS}
