.PHONY: test typecheck lint check

test:
	pytest

typecheck:
	mypy

lint:
	ruff check .

check: lint typecheck test
