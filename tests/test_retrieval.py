"""Tests for semantic retrieval — wRRF tool→agent search."""

import pytest

from yggdrasil_lm.core.edges import Edge
from yggdrasil_lm.core.nodes import AgentNode, ToolNode
from yggdrasil_lm.core.store import NetworkXGraphStore
from yggdrasil_lm.retrieval.wrrf import semantic_search


def _vec(seed: float, dim: int = 8) -> list[float]:
    """Generate a simple unit vector for testing."""
    import math
    raw = [seed + i * 0.01 for i in range(dim)]
    norm = math.sqrt(sum(x * x for x in raw))
    return [x / norm for x in raw]


@pytest.fixture
def store():
    return NetworkXGraphStore()


async def _build_retrieval_graph(store: NetworkXGraphStore):
    """Two agents, each with a distinct tool, all with embeddings."""
    agent_a = AgentNode(
        name="CodeAgent",
        description="An agent for code-related tasks",
        embedding=_vec(1.0),
    )
    agent_b = AgentNode(
        name="ResearchAgent",
        description="An agent for research and information gathering",
        embedding=_vec(2.0),
    )
    tool_a = ToolNode(
        name="run_python",
        description="Execute Python code snippets",
        callable_ref="tools.code_exec.run_python",
        embedding=_vec(1.1),   # close to agent_a
        input_schema={"type": "object", "properties": {"code": {"type": "string"}}},
    )
    tool_b = ToolNode(
        name="web_search",
        description="Search the web for current information",
        callable_ref="tools.web_search.search",
        embedding=_vec(2.1),   # close to agent_b
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
    )

    for n in [agent_a, agent_b, tool_a, tool_b]:
        await store.upsert_node(n)

    # Wire: agent_a owns tool_a, agent_b owns tool_b
    await store.upsert_edge(Edge.has_tool(agent_a.node_id, tool_a.node_id))
    await store.upsert_edge(Edge.has_tool(agent_b.node_id, tool_b.node_id))

    return agent_a, agent_b, tool_a, tool_b


@pytest.mark.asyncio
async def test_semantic_search_returns_agents(store):
    agent_a, agent_b, tool_a, tool_b = await _build_retrieval_graph(store)

    # Query close to code/python domain
    query_vec = _vec(1.05)
    results = await semantic_search(store, query_vec, top_k=2)

    assert len(results) > 0
    agent_ids = [r.agent.node_id for r in results]
    # CodeAgent should rank higher for a code-like query
    assert agent_a.node_id in agent_ids


@pytest.mark.asyncio
async def test_semantic_search_infers_agent_via_tool(store):
    """Agent is found via tool embedding match, not direct agent match."""
    agent_a, agent_b, tool_a, tool_b = await _build_retrieval_graph(store)

    # Query extremely close to tool_b (research domain)
    query_vec = _vec(2.09)
    results = await semantic_search(store, query_vec, top_k=5)

    # agent_b should be discovered via tool_b's embedding
    agent_ids = [r.agent.node_id for r in results]
    assert agent_b.node_id in agent_ids

    # The winning result for research query should mention tool_b as the via_tool
    research_result = next(r for r in results if r.agent.node_id == agent_b.node_id)
    tool_names = [t.name for t in research_result.via_tools]
    assert "web_search" in tool_names


@pytest.mark.asyncio
async def test_semantic_search_empty_graph(store):
    """Empty graph returns empty results without error."""
    results = await semantic_search(store, _vec(1.0), top_k=5)
    assert results == []


@pytest.mark.asyncio
async def test_semantic_search_no_embeddings(store):
    """Nodes without embeddings are skipped gracefully."""
    agent = AgentNode(name="NoEmbed", description="no embedding", embedding=None)
    await store.upsert_node(agent)

    results = await semantic_search(store, _vec(1.0), top_k=5)
    assert results == []


@pytest.mark.asyncio
async def test_semantic_search_top_k_respected(store):
    """top_k limits the number of results."""
    agent_a, agent_b, *_ = await _build_retrieval_graph(store)
    results = await semantic_search(store, _vec(1.5), top_k=1)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_semantic_search_scores_in_descending_order(store):
    """Results should be sorted by score descending."""
    await _build_retrieval_graph(store)
    results = await semantic_search(store, _vec(1.5), top_k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# New tests: score-weighted fusion, attach_tool auto-weight, tag overlap
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_high_cosine_beats_low_cosine_at_same_rank(store):
    """Score-weighted fusion: agent with higher cosine tool should outscore lower cosine."""
    import math

    def unit(v: list[float]) -> list[float]:
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    # query points along [1, 0, 0]
    query_vec = unit([1.0, 0.0, 0.0])

    # tool_hi: cosine ≈ 1.0 with query
    # tool_lo: cosine ≈ 0.0 with query
    tool_hi = ToolNode(name="tool_hi", description="hi", embedding=unit([1.0, 0.0, 0.0]),
                       callable_ref="x", input_schema={})
    tool_lo = ToolNode(name="tool_lo", description="lo", embedding=unit([0.0, 1.0, 0.0]),
                       callable_ref="x", input_schema={})
    agent_hi = AgentNode(name="AgentHi", embedding=unit([1.0, 0.0, 0.0]))
    agent_lo = AgentNode(name="AgentLo", embedding=unit([0.0, 1.0, 0.0]))

    for n in [tool_hi, tool_lo, agent_hi, agent_lo]:
        await store.upsert_node(n)
    await store.upsert_edge(Edge.has_tool(agent_hi.node_id, tool_hi.node_id))
    await store.upsert_edge(Edge.has_tool(agent_lo.node_id, tool_lo.node_id))

    results = await semantic_search(store, query_vec, top_k=2)
    assert results[0].agent.name == "AgentHi"
    assert results[1].agent.name == "AgentLo"


@pytest.mark.asyncio
async def test_attach_tool_auto_weight():
    """attach_tool() computes weight = cosine(agent.emb, tool.emb)."""
    store = NetworkXGraphStore()
    agent = AgentNode(name="A", embedding=[1.0, 0.0])
    tool  = ToolNode(name="T", callable_ref="x", input_schema={}, embedding=[1.0, 0.0])
    await store.upsert_node(agent)
    await store.upsert_node(tool)

    edge = await store.attach_tool(agent.node_id, tool.node_id)
    assert abs(edge.weight - 1.0) < 1e-6


@pytest.mark.asyncio
async def test_attach_tool_orthogonal_vectors():
    """Orthogonal agent/tool embeddings produce weight ≈ 0."""
    store = NetworkXGraphStore()
    agent = AgentNode(name="A", embedding=[1.0, 0.0])
    tool  = ToolNode(name="T", callable_ref="x", input_schema={}, embedding=[0.0, 1.0])
    await store.upsert_node(agent)
    await store.upsert_node(tool)

    edge = await store.attach_tool(agent.node_id, tool.node_id)
    assert abs(edge.weight) < 1e-6


@pytest.mark.asyncio
async def test_attach_tool_fallback_without_embeddings():
    """attach_tool() uses weight=1.0 when nodes have no embeddings."""
    store = NetworkXGraphStore()
    agent = AgentNode(name="A")
    tool  = ToolNode(name="T", callable_ref="x", input_schema={})
    await store.upsert_node(agent)
    await store.upsert_node(tool)

    edge = await store.attach_tool(agent.node_id, tool.node_id)
    assert edge.weight == 1.0


@pytest.mark.asyncio
async def test_attach_tool_explicit_weight_overrides_auto():
    """Explicit weight overrides cosine auto-computation."""
    store = NetworkXGraphStore()
    agent = AgentNode(name="A", embedding=[1.0, 0.0])
    tool  = ToolNode(name="T", callable_ref="x", input_schema={}, embedding=[1.0, 0.0])
    await store.upsert_node(agent)
    await store.upsert_node(tool)

    edge = await store.attach_tool(agent.node_id, tool.node_id, weight=0.55)
    assert edge.weight == 0.55


@pytest.mark.asyncio
async def test_tag_overlap_bonus_boosts_matching_tool(store):
    """An agent whose tool has matching tags should rank above one that does not."""
    import math

    def unit(v: list[float]) -> list[float]:
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    query_vec = unit([1.0, 0.0, 0.0])

    # Both tools have similar cosine scores; only tool_tagged has matching tags.
    tool_tagged   = ToolNode(name="tagged",   description="t", tags=["python", "code"],
                             embedding=unit([1.0, 0.01, 0.0]), callable_ref="x", input_schema={})
    tool_untagged = ToolNode(name="untagged", description="u", tags=[],
                             embedding=unit([1.0, 0.0,  0.0]), callable_ref="x", input_schema={})
    agent_tagged   = AgentNode(name="TaggedAgent",   embedding=unit([1.0, 0.01, 0.0]))
    agent_untagged = AgentNode(name="UntaggedAgent", embedding=unit([1.0, 0.0,  0.0]))

    for n in [tool_tagged, tool_untagged, agent_tagged, agent_untagged]:
        await store.upsert_node(n)
    await store.upsert_edge(Edge.has_tool(agent_tagged.node_id,   tool_tagged.node_id))
    await store.upsert_edge(Edge.has_tool(agent_untagged.node_id, tool_untagged.node_id))

    results = await semantic_search(
        store, query_vec, top_k=2,
        query_tags=["python", "code"],
        tag_weight=1.0,   # large bonus to ensure tag effect is visible
    )

    assert results[0].agent.name == "TaggedAgent"


@pytest.mark.asyncio
async def test_tool_node_tags_field():
    """ToolNode stores tags without error."""
    tool = ToolNode(
        name="run_python",
        callable_ref="tools.code_exec.run_python",
        input_schema={},
        tags=["code_execution", "python"],
    )
    assert tool.tags == ["code_execution", "python"]
