.PHONY: lint typecheck security complexity test coverage quality precommit setup

SRC := arclith
UV  := uv run --frozen

setup:
	uv sync --group dev --extra all

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
	$(UV) pytest \
		--cov=$(SRC) \
		--cov-report=term-missing --cov-report=html --cov-branch \
		--cov-fail-under=90

quality: lint security complexity typecheck coverage

precommit: lint typecheck security

