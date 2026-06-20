.PHONY: compile watch test clean

compile:
	python -m coconut yggdrasil_lm/ --target sys --quiet

watch:
	python -m coconut yggdrasil_lm/ --target sys --watch

test: compile
	pytest

clean:
	find yggdrasil_lm -name "*.py" -not -name "__coconut__.py" -delete
	find yggdrasil_lm -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
