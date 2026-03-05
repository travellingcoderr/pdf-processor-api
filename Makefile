.PHONY: up down restart logs-api logs-worker logs-frontend env

up:
	docker compose up --build

down:
	docker compose down

restart: down up

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

logs-frontend:
	docker compose logs -f frontend

env:
	@if [ -f .env ]; then \
		echo ".env already exists; not overwriting."; \
	else \
		cp .env.example .env; \
		echo "Created .env from .env.example. Please edit it with your secrets."; \
	fi
