"""Importing the core package must not pull the heavy optional backends.

A tool call's child process imports `yggdrasil_lm.core.nodes` to build one node; the
Claude Agent SDK and MCP cost ~0.25 s of import time it never uses. The package's
public names resolve on first access instead (PEP 562)."""

from __future__ import annotations

import subprocess
import sys

import yggdrasil_lm


def _modules_after(code: str) -> set[str]:
    out = subprocess.run([sys.executable, "-c", code + "\nimport sys\nprint('\\n'.join(sys.modules))"],
                         capture_output=True, text=True, check=True)
    return set(out.stdout.split())


def test_core_import_does_not_load_the_sdk_or_mcp() -> None:
    mods = _modules_after("import yggdrasil_lm.core.nodes")
    assert "claude_agent_sdk" not in mods
    assert "mcp" not in mods
    assert "yggdrasil_lm.backends.claude_code" not in mods


def test_every_public_name_still_resolves() -> None:
    for name in yggdrasil_lm.__all__:
        assert getattr(yggdrasil_lm, name) is not None, name
    from yggdrasil_lm import ClaudeCodeExecutor, END_NODE, GraphExecutor  # noqa: F401


def test_an_unknown_name_is_an_attribute_error() -> None:
    try:
        yggdrasil_lm.no_such_name  # type: ignore[attr-defined]  # noqa: B018
    except AttributeError as exc:
        assert "no_such_name" in str(exc)
    else:
        raise AssertionError("expected AttributeError")
