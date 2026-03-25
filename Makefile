.PHONY: lint typecheck security complexity test coverage quality precommit setup

SRC := arclith
UV  := uv run --frozen

setup:
	uv sync --group dev --extra all
	git config core.hooksPath .githooks

lint:
	$(UV) ruff check $(SRC)

typecheck:
	$(UV) mypy $(SRC)

security:
	$(UV) bandit -r $(SRC) -ll

complexity:
	@output=$$($(UV) radon cc $(SRC) --min C -s); \
	if [ -n "$$output" ]; then echo "$$output"; exit 1; fi

test:
	$(UV) pytest -v

coverage:
	uv run --frozen --extra all pytest --cov --cov-report=term-missing --cov-report=html

quality: lint security complexity typecheck coverage

precommit: lint typecheck security

