.PHONY: build up down restart logs test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f app

logs-postgres:
	docker-compose logs -f postgres

test:
	docker-compose exec app pytest

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

migration:
	docker-compose exec app alembic revision --autogenerate -m "$(message)"

migrate:
	docker-compose exec app alembic upgrade head

shell:
	docker-compose exec app python

psql:
	docker-compose exec postgres psql -U pr_reviewer -d pr_reviewer_db

