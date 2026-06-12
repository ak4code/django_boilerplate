.PHONY: env install run migrate makemigrations superuser test lint format up down logs

env:
	@if [ -f .env ]; then \
		echo ".env уже существует, пропускаю."; \
	else \
		cp .env.example .env && echo "Создано .env из .env.example."; \
	fi

install:
	uv sync --group dev

run:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

superuser:
	uv run python manage.py createsuperuser

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run bandit -c pyproject.toml -r .

format:
	uv run ruff check --fix .
	uv run ruff format .

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f django
