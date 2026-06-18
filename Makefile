# RAG against the machine - Makefile
.PHONY: install run debug clean lint lint-strict test

PYTHON := uv run python
MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	@echo "Installing project dependencies using UV..."
	uv pip install -e .

run:
	@echo "Running primary package command..."
	$(PYTHON) -m student --help

debug:
	@echo "Launching main command in debug mode with built-in pdb..."
	$(PYTHON) -m pdb -m student search "How to configure OpenAI server?" --k 5

clean:
	@echo "Removing temporary files and translation artifacts..."
	rm -rf .mypy_cache .pytest_cache .benchmarks htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

lint:
	@echo "Running standard flake8 style analysis..."
	uv run flake8 student/ tests/
	@echo "Evaluating strict type correctness with mypy..."
	uv run mypy student/ $(MYPY_FLAGS)

lint-strict:
	@echo "Running aggressive style checking..."
	uv run flake8 student/ tests/
	uv run mypy student/ --strict

test:
	@echo "Running edge-case test profiles..."
	uv run pytest tests/ -v