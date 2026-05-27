.PHONY: help install dev lint test backend frontend docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────
install: ## Install all dependencies (backend + frontend)
	cd backend && python -m venv venv && . venv/bin/activate && pip install -e ".[dev]"
	cd frontend && npm ci

hooks: ## Install pre-commit hooks
	cd backend && . venv/bin/activate && pre-commit install --config ../.pre-commit-config.yaml

# ── Development ──────────────────────────────────────────────
backend: ## Start backend dev server
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend dev server
	cd frontend && npm run dev

# ── Quality ──────────────────────────────────────────────────
lint: ## Run all linters
	cd backend && . venv/bin/activate && \
		python -m ruff check app/ && \
		python -m black --check app/ && \
		python -m mypy app/ --ignore-missing-imports
	cd frontend && npx tsc --noEmit

test: ## Run all tests
	cd backend && . venv/bin/activate && python -m pytest tests/ -q
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && . venv/bin/activate && python -m pytest tests/ -q

test-frontend: ## Run frontend tests only
	cd frontend && npm test

# ── Docker ───────────────────────────────────────────────────
docker-up: ## Start all services via Docker Compose
	docker compose up --build -d

docker-down: ## Stop all services
	docker compose down

docker-logs: ## Tail logs from all services
	docker compose logs -f

# ── Cleanup ──────────────────────────────────────────────────
clean: ## Remove generated files
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.mypy_cache backend/.pytest_cache backend/.coverage
	rm -rf frontend/dist frontend/coverage
