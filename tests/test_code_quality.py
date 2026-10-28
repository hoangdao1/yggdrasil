"""AST-based code-quality gates: no monster functions, no index-loop anti-patterns.

Ruff (see ``[tool.ruff.lint]`` in pyproject.toml) enforces statements/branches/
complexity caps per function, but it cannot cap LINE COUNT, and it has no stable
rule against ``for i in range(len(seq))``. Both gaps are closed here so that
``make check`` (and therefore CI) fails on them.

Budgets are intentionally generous; tighten over time, never raise without
discussion:

- ``MAX_FUNCTION_LINES = 80``  (docstring excluded, body lines counted)
"""

from __future__ import annotations

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN_DIRS = ("yggdrasil_lm", "tests", "examples", "benchmarks")

MAX_FUNCTION_LINES = 80

Func = ast.FunctionDef | ast.AsyncFunctionDef


def _python_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for dirname in SCAN_DIRS:
        root = REPO_ROOT / dirname
        if root.is_dir():
            files.extend(sorted(root.rglob("*.py")))
    return files


def _is_docstring(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def _body_line_count(func: Func) -> int:
    """Body length in source lines: end of last statement minus first body line.

    The docstring is excluded so a well-documented small function is not punished.
    """
    body = func.body
    first = body[1] if len(body) > 1 and _is_docstring(body[0]) else body[0]
    last = max(stmt.end_lineno or stmt.lineno for stmt in body)
    return last - first.lineno + 1


def _walk_functions(tree: ast.Module) -> list[Func]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _is_single_arg_range_len(node: ast.AST) -> bool:
    """True for `range(len(X))` with exactly one argument — the index-loop smell."""
    if not isinstance(node, (ast.For, ast.AsyncFor)):
        return False
    call = node.iter
    return (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "range"
        and len(call.args) == 1
        and isinstance(call.args[0], ast.Call)
        and isinstance(call.args[0].func, ast.Name)
        and call.args[0].func.id == "len"
    )


def _describe(path: pathlib.Path, node: ast.AST) -> str:
    where = getattr(node, "parent", None)
    prefix = f"{where.name}." if isinstance(where, (ast.FunctionDef, ast.AsyncFunctionDef)) else ""
    return f"{path.relative_to(REPO_ROOT)}:{node.lineno}  {prefix}{getattr(node, 'name', '?')}"


def test_no_monster_functions() -> None:
    """Every function/method body stays within MAX_FUNCTION_LINES."""
    monsters: list[tuple[int, str]] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for func in _walk_functions(tree):
            lines = _body_line_count(func)
            if lines > MAX_FUNCTION_LINES:
                monsters.append((lines, _describe(path, func)))

    assert not monsters, (
        f"{len(monsters)} function(s) exceed the {MAX_FUNCTION_LINES}-line budget "
        "(extract focused helpers — see CONTRIBUTING.md, 'Declarative by Default'):\n"
        + "\n".join(f"  {lines:4d} lines  {where}" for lines, where in sorted(monsters, reverse=True))
    )


def test_no_index_loops() -> None:
    """`for i in range(len(seq))` is banned — iterate directly or use enumerate()."""
    offenders = [
        f"  {path.relative_to(REPO_ROOT)}:{node.lineno}  "
        f"{type(node).__name__} over range(len(...)) — use the iterable "
        "directly, or enumerate() when the index is needed"
        for path in _python_files()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if _is_single_arg_range_len(node)
    ]

    assert not offenders, (
        f"{len(offenders)} index-loop anti-pattern(s) found:\n" + "\n".join(offenders)
    )