.PHONY: build up down restart logs test clean lint

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
	python3 -m pytest tests/

test-e2e:
	python3 -m pytest tests/test_e2e.py -v

lint:
	python3 -m black app/ tests/
	python3 -m isort app/ tests/
	python3 -m flake8 app/ tests/
	python3 -m mypy app/

load-test:
	python3 -m locust -f load_test.py --host=http://localhost:8080

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f test.db

migration:
	docker-compose exec app alembic revision --autogenerate -m "$(message)"

migrate:
	docker-compose exec app alembic upgrade head

shell:
	docker-compose exec app python

psql:
	docker-compose exec postgres psql -U pr_reviewer -d pr_reviewer_db

