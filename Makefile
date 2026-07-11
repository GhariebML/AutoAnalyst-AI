# Makefile 

.PHONY: install test lint format validate

install:
	python -m pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check .

format:
	black .

validate:
	# simple validation trigger – in real use you’d add schema validation logic
	python scripts/validate_schemas.py
