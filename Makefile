# Always use the project venv's pinned tools (ruff is pinned in
# [project.optional-dependencies].dev) — global installs drift.
.PHONY: test typecheck lint check

test:
	.venv/bin/python -m pytest

typecheck:
	.venv/bin/python -m mypy

lint:
	.venv/bin/ruff check .

check: lint typecheck test
