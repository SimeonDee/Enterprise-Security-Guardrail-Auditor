# Project To-Do

## ✅ Completed
- [x] Project scaffold (backend + frontend + docs)
- [x] FastAPI backend with SQLAlchemy + SQLite
- [x] Data models: Guardrail, Scan, Violation
- [x] REST API: CRUD guardrails, scans, dashboard summary
- [x] Scanner service with regex-based rule engine
- [x] 10 built-in AWS security guardrail rules (seed data)
- [x] Risk score calculation engine
- [x] React frontend: Dashboard, Scans, ScanDetail, NewScan, Guardrails
- [x] Recharts-based severity bar chart on dashboard
- [x] Component tests (RiskScoreBadge, SeverityBadge, App)
- [x] Backend tests (health, guardrails CRUD, scans, dashboard, scanner)
- [x] pyproject.toml with black/ruff/mypy config
- [x] Vitest + RTL test setup with 85% coverage threshold
- [x] Docker-ready (Dockerfile for both + docker-compose)
- [x] Documentation (architecture.md, setup.md, api-design.md)
- [x] Async SQLAlchemy migration (aiosqlite driver)
- [x] App factory pattern with lifespan context manager
- [x] Centralized error handling (APIError hierarchy)
- [x] Request logging middleware with X-Request-ID
- [x] Redis cache abstraction layer (Protocol + NullCache)
- [x] Structured logging setup
- [x] Alembic migration setup (async env.py + initial migration)
- [x] All tests converted to async (38 tests, 95% coverage)

## 🔲 Next Up (MVP Completion)
- [ ] Seed guardrails on first startup (auto-seed endpoint or startup event)
- [ ] File upload endpoint (multipart form) as alternative to paste
- [ ] CloudFormation YAML/JSON parsing support in scanner
- [ ] Add more guardrail rules (Azure, GCP)
- [ ] Error boundary in React frontend
- [ ] Loading states / skeleton loaders
- [ ] Pagination on scan list
- [ ] API key authentication middleware
- [ ] Export scan results as PDF/CSV
- [ ] CI/CD pipeline (GitHub Actions)

## 🔮 Post-MVP
- [ ] Async scan processing (background tasks)
- [ ] Scan history comparison / trend charts
- [ ] Custom guardrail creation via frontend UI
- [ ] Multi-file / zip upload scanning
- [ ] Webhook notifications for critical findings
- [ ] RBAC / multi-tenant support
- [ ] PostgreSQL migration option
