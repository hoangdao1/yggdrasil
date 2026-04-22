"""Node embedder — generates dense vectors for nodes using sentence-transformers.

Usage:
    embedder = Embedder()
    await embedder.embed_node(store, node)           # embed one node in-place
    await embedder.embed_all(store, node_types=[...])  # batch embed
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError as _e:
    raise ImportError(
        "sentence-transformers is required for Embedder. "
        "Install it with: pip install 'yggdrasil[embeddings]'"
    ) from _e

from yggdrasil_lm.core.nodes import AnyNode, NodeType
from yggdrasil_lm.core.store import GraphStore


EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


class Embedder:
    """Generates and stores embeddings for graph nodes.

    The embedding source text is: f"{node.name}: {node.description}"
    For ContextNodes, the content is appended (up to 2000 chars).
    """

    def __init__(self, model: str = EMBED_MODEL) -> None:
        self.model = model
        self._client: Any = None

    def _get_client(self) -> SentenceTransformer:
        if self._client is None:
            self._client = SentenceTransformer(self.model)
        return self._client

    def _node_text(self, node: AnyNode) -> str:
        """Produce the text to embed for a given node."""
        from yggdrasil_lm.core.nodes import ContextNode, ToolNode
        parts = []
        if node.name:
            parts.append(node.name)
        if node.description:
            parts.append(node.description)
        if isinstance(node, ContextNode) and node.content:
            parts.append(node.content[:2000])
        if isinstance(node, ToolNode) and node.input_schema:
            parts.append(json.dumps(node.input_schema)[:500])
        return ": ".join(parts) or node.node_id

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string and return the vector."""
        client = self._get_client()
        vec = await asyncio.to_thread(client.encode, text, normalize_embeddings=True)
        return vec.tolist()

    async def embed_node(self, store: GraphStore, node: AnyNode) -> AnyNode:
        """Compute and store an embedding for a single node."""
        text = self._node_text(node)
        vec = await self.embed_text(text)
        updated = node.model_copy(update={"embedding": vec})
        await store.upsert_node(updated)
        return updated

    async def embed_all(
        self,
        store: GraphStore,
        node_types: list[NodeType] | None = None,
        skip_existing: bool = True,
    ) -> int:
        """Embed all nodes matching node_types. Returns count of nodes embedded."""
        nodes = await store.list_nodes(only_valid=False)
        count = 0
        for node in nodes:
            if node_types and node.node_type not in node_types:
                continue
            if skip_existing and node.embedding:
                continue
            await self.embed_node(store, node)
            count += 1
        return count
