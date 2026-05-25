"""Shared pytest configuration for the yggdrasil test suite.

Registers a ``live_llm`` marker for tests that hit a real LLM backend. Such
tests are skipped by default; set ``YGG_LIVE_LLM=1`` to run them.

Usage:

    @pytest.mark.live_llm
    async def test_critic_flags_hype():
        app = GraphApp()  # real backend
        ...

Run live tests with:

    YGG_LIVE_LLM=1 pytest -m live_llm
"""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "live_llm: test hits a real LLM backend; gated by YGG_LIVE_LLM=1",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if os.environ.get("YGG_LIVE_LLM"):
        return
    skip = pytest.mark.skip(reason="live LLM test; set YGG_LIVE_LLM=1 to run")
    for item in items:
        if "live_llm" in item.keywords:
            item.add_marker(skip)
