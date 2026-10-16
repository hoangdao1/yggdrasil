.PHONY: test lint check

test:
	pytest

lint:
	ruff check yggdrasil_lm

check: lint test
