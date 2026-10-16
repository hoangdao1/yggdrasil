.PHONY: test typecheck lint check

test:
	pytest

typecheck:
	mypy

lint:
	ruff check yggdrasil_lm

check: lint typecheck test
