"""Built-in echo tool."""

from __future__ import annotations

from typing import Any


async def echo(input: dict[str, Any]) -> str:
    """Simple echo tool for testing."""
    return f"Echo: {input}"
