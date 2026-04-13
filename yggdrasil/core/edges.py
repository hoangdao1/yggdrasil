"""Edge types for the yggdrasil system.

Edges are typed, weighted, and temporally valid.
Multiple edge types can exist between the same two nodes (multi-relational graph).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Edge type enum
# ---------------------------------------------------------------------------

class EdgeType(StrEnum):
    # Composition edges — define what an agent IS made of
    HAS_TOOL     = "HAS_TOOL"      # agent → tool
    HAS_CONTEXT  = "HAS_CONTEXT"   # agent → context
    HAS_PROMPT   = "HAS_PROMPT"    # agent → prompt

    # Control-flow edges
    DELEGATES_TO = "DELEGATES_TO"  # agent → agent (routing / delegation)

    # Provenance edges — track execution history in the graph
    PRODUCES     = "PRODUCES"      # agent/tool → context (output materialised as node)

    # Knowledge edges — document/entity relationships
    MENTIONS     = "MENTIONS"      # context → entity
    NEXT         = "NEXT"          # context → context (sequence within a doc)

    # Knowledge edges — concept taxonomy
    COVERS       = "COVERS"        # context → concept tag (for structured filtering)

    # Retrieval edges — populated by the embedder / indexer
    SIMILAR_TO   = "SIMILAR_TO"    # any → any (semantic similarity)

    # Validation edges
    VALIDATES    = "VALIDATES"     # schema → tool/context

    # Meta-graph edges
    CONTAINS     = "CONTAINS"      # graph-node → node (sub-graph membership)


# ---------------------------------------------------------------------------
# Edge model
# ---------------------------------------------------------------------------

class Edge(BaseModel):
    """A typed, weighted, temporally-valid directed edge between two nodes.

    Temporal validity:
    - valid_at / invalid_at control when this relationship is active.
    - Setting invalid_at=now() retires an edge without deleting it,
      preserving history for point-in-time queries.
    """

    edge_id:    str      = Field(default_factory=_uuid)
    edge_type:  EdgeType = EdgeType.HAS_CONTEXT
    src_id:     str      = ""
    dst_id:     str      = ""

    # Relationship strength — used to rank context nodes when composing agents.
    # Higher weight = more relevant context injected first.
    weight:     float    = 1.0

    # Optional LLM-generated or human-written relationship summary.
    description: str     = ""

    # Extensible metadata
    attributes:  dict[str, Any] = Field(default_factory=dict)

    # Temporal validity
    valid_at:    datetime       = Field(default_factory=_now)
    invalid_at:  datetime | None = None

    # Partition key (same as nodes)
    group_id:   str = "default"

    # Workflow / graph versioning
    version: int = 1
    graph_version: str = "v1"
    graph_revision_id: str = ""

    # Minimal role-based access control for traversals that rely on edges
    required_roles: list[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if this edge is currently active."""
        now = _now()
        return self.valid_at <= now and (
            self.invalid_at is None or self.invalid_at > now
        )

    def expire(self) -> "Edge":
        """Return a copy of this edge marked as expired right now."""
        return self.model_copy(update={"invalid_at": _now()})

    @classmethod
    def has_tool(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.HAS_TOOL, src_id=src_id, dst_id=dst_id, **kw)

    @classmethod
    def has_context(cls, src_id: str, dst_id: str, weight: float = 1.0, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.HAS_CONTEXT, src_id=src_id, dst_id=dst_id, weight=weight, **kw)

    @classmethod
    def has_prompt(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.HAS_PROMPT, src_id=src_id, dst_id=dst_id, **kw)

    @classmethod
    def delegates_to(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.DELEGATES_TO, src_id=src_id, dst_id=dst_id, **kw)

    @classmethod
    def produces(cls, src_id: str, dst_id: str, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.PRODUCES, src_id=src_id, dst_id=dst_id, **kw)

    @classmethod
    def similar_to(cls, src_id: str, dst_id: str, weight: float = 1.0, **kw: Any) -> "Edge":
        return cls(edge_type=EdgeType.SIMILAR_TO, src_id=src_id, dst_id=dst_id, weight=weight, **kw)
