# RAG against the machine - Makefile
install:
	uv sync

run:
	uv run python -m student

debug:
	uv run python -m pdb -m student

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	uv run flake8 . --exclude=.venv,__pycache__,.mypy_cache,data
	uv run mypy . --exclude=data \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict