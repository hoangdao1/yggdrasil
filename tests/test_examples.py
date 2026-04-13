from __future__ import annotations

import pytest

from examples.approval_workflow import run_demo as run_approval_workflow
from examples.builder_echo import run_demo as run_builder_echo
from examples.deterministic_routing import run_demo as run_deterministic_routing
from examples.parallel_workers import run_demo as run_parallel_workers
from examples.research_pipeline import run_pipeline
from examples._stub_backend import SequenceBackend, end_turn


@pytest.mark.asyncio
async def test_builder_echo_example_runs():
    await run_builder_echo()


@pytest.mark.asyncio
async def test_deterministic_routing_example_runs():
    await run_deterministic_routing()


@pytest.mark.asyncio
async def test_approval_workflow_example_runs():
    await run_approval_workflow()


@pytest.mark.asyncio
async def test_parallel_workers_example_runs():
    await run_parallel_workers()


@pytest.mark.asyncio
async def test_research_pipeline_example_runs():
    """Smoke-test the research pipeline with a stub backend (no API key required)."""
    backend = SequenceBackend([
        end_turn("Research complete. SYNTHESIS NEEDED"),
        end_turn("Synthesis report complete."),
    ])
    await run_pipeline("test query", backend=backend)


