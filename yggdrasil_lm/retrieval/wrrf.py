"""Weighted Reciprocal Rank Fusion (wRRF) for two-stage tool→agent retrieval.

Algorithm (from arXiv:2511.18194), extended with score-weighted fusion:
1. Embed query → q_vec
2. vector_search(TOOL nodes) → tool_hits ranked by cosine score
3. vector_search(AGENT nodes) → agent_hits ranked by cosine score
4. Walk HAS_TOOL edges upstream from tool hits → find parent AgentNodes,
   capturing each edge's weight as a tool-affinity prior.
5. Score fusion per candidate agent:
     tool_score  = w_tool  * cosine_score * edge_weight / (rank + k)
     agent_score = w_agent * cosine_score / (rank + k)
     tag_bonus   = len(tool.tags ∩ query_tags) * tag_weight   [optional]
     final_score = tool_score + agent_score + tag_bonus
6. Return top_k agents by final_score.

Improvements over pure rank-based RRF:
- Cosine score magnitude is preserved: a tool at rank 1 with cosine 0.95
  scores much higher than one at rank 1 with cosine 0.51.
- HAS_TOOL edge weight acts as a structural affinity prior: tools that are
  semantically central to their agent (set via attach_tool()) are boosted
  independently of query-time similarity.
- Optional query_tags enable concept-overlap bonuses for tools tagged with
  matching concepts, providing a structured signal on top of embeddings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yggdrasil_lm.core.edges import EdgeType
from yggdrasil_lm.core.nodes import AgentNode, NodeType, ToolNode
from yggdrasil_lm.core.store import GraphStore


@dataclass
class RetrievalResult:
    """A ranked agent retrieval result."""

    agent:       AgentNode
    score:       float
    via_tools:   list[ToolNode] = field(default_factory=list)   # tools that surfaced this agent
    tool_scores: list[float]    = field(default_factory=list)   # cosine scores of those tools


async def _agents_from_tool_hits(
    store: GraphStore,
    tool_hits: list[tuple[Any, float]],
) -> dict[str, list[tuple[AgentNode, ToolNode, float, float]]]:
    """Walk HAS_TOOL edges upstream from tool hits to their parent AgentNodes.

    Returns agent_id → list of (AgentNode, ToolNode, cosine_score, edge_weight);
    edge.weight is the tool-affinity prior set at attach time.
    """
    tool_to_agents: dict[str, list[tuple[AgentNode, ToolNode, float, float]]] = {}
    for tool_node, tool_score in tool_hits:
        match tool_node:
            case ToolNode():
                parent_edges = await store.get_edges(
                    tool_node.node_id, edge_type=EdgeType.HAS_TOOL, direction="in"
                )
                for edge in parent_edges:
                    parent = await store.get_node(edge.src_id)
                    match parent:
                        case AgentNode() if parent.is_valid:
                            tool_to_agents.setdefault(parent.node_id, []).append(
                                (parent, tool_node, tool_score, edge.weight)
                            )
    return tool_to_agents


@dataclass(frozen=True)
class _FusionWeights:
    """Score-fusion knobs for weighted RRF (see semantic_search)."""

    w_tool:       float
    w_agent:      float
    k:            int
    top_k_tools:  int
    top_k_agents: int
    query_tags:   tuple[str, ...] | None
    tag_weight:   float


def _seed_agent_candidates(
    agent_hits: list[tuple[Any, float]],
    agent_rank_score: dict[str, tuple[int, float]],
    weights: _FusionWeights,
) -> dict[str, dict[str, Any]]:
    """Seed candidates from direct agent hits — score = w_agent * cosine / (rank + k)."""
    return {
        node.node_id: {
            "agent":       node,
            "agent_score": weights.w_agent * cosine / (rank + weights.k),
            "tool_score":  0.0,
            "via_tools":   [],
            "tool_scores": [],
        }
        for rank, (node, cosine) in enumerate(agent_hits)
        if isinstance(node, AgentNode)
    }


def _apply_tool_scores(
    candidates: dict[str, dict[str, Any]],
    tool_to_agents: dict[str, list[tuple[AgentNode, ToolNode, float, float]]],
    tool_rank_score: dict[str, tuple[int, float]],
    agent_rank_score: dict[str, tuple[int, float]],
    weights: _FusionWeights,
) -> None:
    """Fold tool-driven scores into the candidate agents (in place).

    score = w_tool * cosine * edge_weight / (rank + k), plus a tag-overlap bonus.
    """
    for agent_id, entries in tool_to_agents.items():
        # Pick the entry whose tool has the best (lowest) rank
        best_entry = min(
            entries,
            key=lambda e: tool_rank_score.get(e[1].node_id, (weights.top_k_tools, 0.0))[0],
        )
        best_rank, best_cosine = tool_rank_score.get(
            best_entry[1].node_id, (weights.top_k_tools, 0.0)
        )
        tool_score = weights.w_tool * best_cosine * best_entry[3] / (best_rank + weights.k)

        # Tag overlap bonus: score boost per concept tag shared between the
        # best-ranked tool and the caller-supplied query_tags.
        if weights.query_tags:
            overlap = len(set(best_entry[1].tags) & set(weights.query_tags))
            tool_score += overlap * weights.tag_weight

        a_rank, a_cosine = agent_rank_score.get(agent_id, (weights.top_k_agents, 0.0))
        agent_score = weights.w_agent * a_cosine / (a_rank + weights.k)

        fused = candidates.get(agent_id)
        if fused is None:
            candidates[agent_id] = {
                "agent":       best_entry[0],
                "agent_score": agent_score,
                "tool_score":  tool_score,
                "via_tools":   [e[1] for e in entries],
                "tool_scores": [e[2] for e in entries],
            }
        else:
            fused["tool_score"]  += tool_score
            fused["via_tools"]   += [e[1] for e in entries]
            fused["tool_scores"] += [e[2] for e in entries]


async def semantic_search(  # noqa: PLR0913, PLR0917 — public retrieval API; every parameter documented
    store: GraphStore,
    query_embedding: list[float],
    top_k: int = 5,
    top_k_tools: int = 20,
    top_k_agents: int = 10,
    w_tool: float = 0.7,
    w_agent: float = 0.3,
    k: int = 60,                        # RRF smoothing constant
    query_tags: list[str] | None = None,  # concept tags extracted from the query
    tag_weight: float = 0.1,              # score bonus per matching tag
) -> list[RetrievalResult]:
    """Find the best AgentNodes for a query via score-weighted wRRF.

    Args:
        store:           The graph store to search.
        query_embedding: Dense vector of the user query.
        top_k:           Number of final agent results to return.
        top_k_tools:     How many tool nodes to retrieve before walking upstream.
        top_k_agents:    How many agent nodes to retrieve directly.
        w_tool:          Weight for tool-driven score (higher = tools drive the result).
        w_agent:         Weight for direct agent score.
        k:               RRF smoothing constant (60 is the standard default).
        query_tags:      Optional concept tags (e.g. ["code_execution", "python"]).
                         Tools whose tags overlap with these receive a bonus per match.
        tag_weight:      Bonus added per matching tag.
    """
    import asyncio

    # Step 1: Search ToolNodes and AgentNodes in parallel
    tool_coro  = store.vector_search(query_embedding, node_types=[NodeType.TOOL],  top_k=top_k_tools)
    agent_coro = store.vector_search(query_embedding, node_types=[NodeType.AGENT], top_k=top_k_agents)
    tool_hits, agent_hits = await asyncio.gather(tool_coro, agent_coro)

    # Build fast lookup: tool_node_id → (rank, cosine_score)
    tool_rank_score: dict[str, tuple[int, float]] = {
        node.node_id: (rank, score)
        for rank, (node, score) in enumerate(tool_hits)
        if isinstance(node, ToolNode)
    }

    # Step 2: Walk HAS_TOOL edges upstream from tool hits → find parent AgentNodes.
    tool_to_agents = await _agents_from_tool_hits(store, tool_hits)

    # Step 3: Build rank lookup for direct agent hits
    agent_rank_score: dict[str, tuple[int, float]] = {
        node.node_id: (rank, score)
        for rank, (node, score) in enumerate(agent_hits)
        if isinstance(node, AgentNode)
    }

    weights = _FusionWeights(
        w_tool=w_tool, w_agent=w_agent, k=k,
        top_k_tools=top_k_tools, top_k_agents=top_k_agents,
        query_tags=tuple(query_tags) if query_tags else None,
        tag_weight=tag_weight,
    )

    # Step 4: Build fused score for every candidate agent
    candidates = _seed_agent_candidates(agent_hits, agent_rank_score, weights)
    _apply_tool_scores(candidates, tool_to_agents, tool_rank_score, agent_rank_score, weights)

    # Step 5: Rank by fused score
    ranked = sorted(
        candidates.values(),
        key=lambda c: c["agent_score"] + c["tool_score"],
        reverse=True,
    )

    return [
        RetrievalResult(
            agent=c["agent"],
            score=c["agent_score"] + c["tool_score"],
            via_tools=c["via_tools"],
            tool_scores=c["tool_scores"],
        )
        for c in ranked[:top_k]
    ]
