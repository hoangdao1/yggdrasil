"""Preferred namespace for retrieval APIs."""

from __future__ import annotations

from typing import Any

from yggdrasil.retrieval.wrrf import RetrievalResult, semantic_search

__all__ = ["Embedder", "RetrievalResult", "semantic_search"]


def __getattr__(name: str) -> Any:
    if name == "Embedder":
        from yggdrasil.retrieval.embedder import Embedder

        return Embedder
    raise AttributeError(name)
