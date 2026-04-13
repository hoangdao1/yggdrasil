"""Opt-in code execution tool."""

from __future__ import annotations

from typing import Any


async def run_python(input: dict[str, Any]) -> str:
    """Execute a Python code snippet in a subprocess."""
    import asyncio

    code = input.get("code", "")
    timeout = input.get("timeout", 10)

    if not code:
        return "No code provided."

    try:
        proc = await asyncio.create_subprocess_exec(
            "python3",
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        result = stdout.decode() + stderr.decode()
        return result.strip() or "(no output)"
    except asyncio.TimeoutError:
        return f"Execution timed out after {timeout}s."
    except Exception as exc:
        return f"Execution error: {exc}"
