.PHONY: install test lint run db-up db-down

install:
	python -m pip install -e ".[dev]"

test:
	pytest --cov=caferank --cov-report=term-missing

lint:
	ruff check src tests

run:
	caferank run

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

