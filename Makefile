.PHONY: up down logs shell-backend shell-db reset

up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build -d
	@echo "\n✅ App running:"
	@echo "  Frontend : http://localhost:3000"
	@echo "  API docs : http://localhost:8000/docs"
	@echo "  MinIO UI : http://localhost:9001"

down:
	docker compose down

logs:
	docker compose logs -f

shell-backend:
	docker exec -it siie_backend bash

shell-db:
	docker exec -it siie_postgres psql -U $$(grep POSTGRES_USER .env | cut -d= -f2) -d $$(grep POSTGRES_DB .env | cut -d= -f2)

reset:
	docker compose down -v
	docker compose up --build -d
