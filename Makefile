.PHONY: up down restart logs-api logs-worker freeze env

up:
	docker compose up --build

down:
	docker compose down

restart: down up

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

freeze:
	./scripts/freeze.sh

env:
	@if [ -f .env ]; then \
		echo ".env already exists; not overwriting."; \
	else \
		cp .env.example .env; \
		echo "Created .env from .env.example. Please edit it with your secrets."; \
	fi
