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

from yggdrasil.core.edges import EdgeType
from yggdrasil.core.nodes import AgentNode, AnyNode, NodeType, ToolNode
from yggdrasil.core.store import GraphStore


@dataclass
class RetrievalResult:
    """A ranked agent retrieval result."""

    agent:       AgentNode
    score:       float
    via_tools:   list[ToolNode] = field(default_factory=list)   # tools that surfaced this agent
    tool_scores: list[float]    = field(default_factory=list)   # cosine scores of those tools


async def semantic_search(
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
    # Also capture edge.weight as the tool-affinity prior set at attach time.
    # tool_to_agents: agent_id → list of (AgentNode, ToolNode, cosine_score, edge_weight)
    tool_to_agents: dict[str, list[tuple[AgentNode, ToolNode, float, float]]] = {}
    for tool_node, tool_score in tool_hits:
        if not isinstance(tool_node, ToolNode):
            continue
        parent_edges = await store.get_edges(
            tool_node.node_id, edge_type=EdgeType.HAS_TOOL, direction="in"
        )
        for edge in parent_edges:
            parent = await store.get_node(edge.src_id)
            if parent and isinstance(parent, AgentNode) and parent.is_valid:
                agent_id = parent.node_id
                if agent_id not in tool_to_agents:
                    tool_to_agents[agent_id] = []
                tool_to_agents[agent_id].append(
                    (parent, tool_node, tool_score, edge.weight)
                )

    # Step 3: Build rank lookup for direct agent hits
    agent_rank_score: dict[str, tuple[int, float]] = {
        node.node_id: (rank, score)
        for rank, (node, score) in enumerate(agent_hits)
        if isinstance(node, AgentNode)
    }

    # Step 4: Build fused score for every candidate agent
    candidates: dict[str, dict[str, Any]] = {}

    # From direct agent hits — score = w_agent * cosine / (rank + k)
    for rank, (node, cosine) in enumerate(agent_hits):
        if not isinstance(node, AgentNode):
            continue
        candidates[node.node_id] = {
            "agent":       node,
            "agent_score": w_agent * cosine / (rank + k),
            "tool_score":  0.0,
            "via_tools":   [],
            "tool_scores": [],
        }

    # From tool-inferred agents — score = w_tool * cosine * edge_weight / (rank + k)
    for agent_id, entries in tool_to_agents.items():
        # Pick the entry whose tool has the best (lowest) rank
        best_entry = min(
            entries,
            key=lambda e: tool_rank_score.get(e[1].node_id, (top_k_tools, 0.0))[0],
        )
        best_rank, best_cosine = tool_rank_score.get(
            best_entry[1].node_id, (top_k_tools, 0.0)
        )
        best_edge_weight = best_entry[3]
        tool_score = w_tool * best_cosine * best_edge_weight / (best_rank + k)

        # Tag overlap bonus: score boost per concept tag shared between the
        # best-ranked tool and the caller-supplied query_tags.
        if query_tags:
            best_tool = best_entry[1]
            overlap = len(set(best_tool.tags) & set(query_tags))
            tool_score += overlap * tag_weight

        a_rank, a_cosine = agent_rank_score.get(agent_id, (top_k_agents, 0.0))
        agent_score = w_agent * a_cosine / (a_rank + k)

        if agent_id not in candidates:
            candidates[agent_id] = {
                "agent":       best_entry[0],
                "agent_score": agent_score,
                "tool_score":  tool_score,
                "via_tools":   [e[1] for e in entries],
                "tool_scores": [e[2] for e in entries],
            }
        else:
            candidates[agent_id]["tool_score"]  += tool_score
            candidates[agent_id]["via_tools"]   += [e[1] for e in entries]
            candidates[agent_id]["tool_scores"] += [e[2] for e in entries]

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
