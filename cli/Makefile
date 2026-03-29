.PHONY: help setup test test-fast clean install

help:
	@echo "arclith-cli — Makefile"
	@echo ""
	@echo "  setup      Install dependencies (uv sync --group dev)"
	@echo "  test       Run E2E tests (scaffold + validation)"
	@echo "  test-fast  Run tests excluding slow markers"
	@echo "  install    Install CLI globally (uv tool install .)"
	@echo "  clean      Remove test artifacts"

setup:
	uv sync --group dev

test:
	uv run pytest tests/ -v

test-fast:
	uv run pytest tests/ -v -m "not slow"

install:
	uv tool install .

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

