# Project To-Do

## ✅ Completed

### Project Foundation
- [x] Project scaffold (backend + frontend + docs)
- [x] FastAPI backend with app factory pattern + lifespan context manager
- [x] SQLAlchemy 2.x async (aiosqlite driver) + Alembic migrations
- [x] Pydantic v2 data models: Guardrail, Scan, Violation
- [x] Centralized error handling (APIError hierarchy)
- [x] Request logging middleware with X-Request-ID
- [x] Structured logging setup
- [x] Redis cache abstraction layer (Protocol + NullCache)
- [x] Environment variable management (.env.example, .env.docker)

### Scanner Engine
- [x] Terraform parser with HCL block extraction + heredoc support
- [x] BaseRule ABC + RuleRegistry for extensible rule system
- [x] 5 engine rules: S3 public, Open SSH, Public DB, Disabled Encryption, Wildcard IAM
- [x] 10 built-in AWS seed guardrails (regex-based)
- [x] Risk scoring engine (0–100 weighted by severity)
- [x] ScanEngine orchestrator with dual-path scanning + dedup
- [x] Sample Terraform files for testing (11 + 9 vulnerabilities)

### REST API
- [x] CRUD guardrails with limit/enabled filters
- [x] Paginated scan list with status/file_type filters
- [x] File upload endpoint (POST /scans/upload) for .tf files
- [x] Dashboard summary endpoint
- [x] Health check endpoint
- [x] PaginatedResponse generic schema
- [x] Upload file size limit (10 MB) + UTF-8 validation

### Frontend
- [x] React 19 + TypeScript + Tailwind CSS 3 + Recharts + React Query
- [x] Dashboard: stats cards, severity bar chart, recent scans
- [x] Scan List: paginated table with status/type filters
- [x] New Scan: dual-mode (upload file / paste content)
- [x] Scan Detail: findings grouped by severity, risk score badge
- [x] Guardrails: security rule management interface
- [x] Reusable components: LoadingSpinner, ErrorMessage, Pagination, StatusBadge

### Testing & Quality
- [x] Backend: 97 tests, 94.65% coverage (pytest + pytest-asyncio)
- [x] Frontend: 24 tests (Vitest + React Testing Library)
- [x] Linting: ruff, black, mypy, tsc — all clean (0 errors)
- [x] QA + Security audit: 26 findings cataloged, 10 fixed
- [x] Pre-commit hooks (ruff, black, mypy, secret detection)

### DevOps & Deployment
- [x] Backend Dockerfile: multi-stage, non-root, healthcheck
- [x] Frontend Dockerfile: multi-stage, nginx, build args, healthcheck
- [x] docker-compose.yml: SQLite persistence, healthchecks, env_file
- [x] GitHub Actions CI: 5-job pipeline (lint × 2 + test × 2 + docker build)
- [x] Makefile: 12 developer shortcut commands
- [x] CI pipeline fix (setuptools flat-layout package discovery)

### Documentation
- [x] Root README.md: professional GitHub-ready with badges + contributor workflow
- [x] backend/README.md + frontend/README.md
- [x] docs/architecture.md, api-reference.md, security-rules.md
- [x] docs/deployment.md, dev-workflow.md, frontend.md
- [x] docs/security-audit.md, qa-report.md
- [x] docs/presentation.md (13-slide Markdown) + presentation.pptx (15-slide PowerPoint)
- [x] docs/final-summary.md — project retrospective
- [x] prompts.md — complete audit log
- [x] to-do.md — structured task tracking

---

## 🔲 Post-MVP Enhancements

### Authentication & Authorization
- [ ] API key authentication middleware
- [ ] JWT/OAuth2 with RBAC
- [ ] Multi-tenant support

### Scanner Improvements
- [ ] CloudFormation YAML/JSON parsing
- [ ] Azure and GCP rule packs
- [ ] HCL2 library parser (replace regex)
- [ ] Handle braces inside quoted strings
- [ ] Support indented resource declarations
- [ ] Open SSH rule: check ipv6_cidr_blocks
- [ ] Encryption rule: flag missing keys (not just explicit false)

### Frontend Enhancements
- [ ] Error boundary in React frontend
- [ ] ESLint config (eslint.config.js)
- [ ] Custom guardrail creation via UI
- [ ] Scan trend comparison / history charts

### API & Processing
- [ ] Async scan processing (background tasks)
- [ ] Multi-file / zip upload scanning
- [ ] Export scan results as PDF/CSV
- [ ] Webhook notifications for critical findings
- [ ] Secret redaction in source_content before storage

### Infrastructure & Operations
- [ ] PostgreSQL migration option
- [ ] Disable OpenAPI docs in production
- [ ] Dependency lockfile for reproducible builds
- [ ] Seed guardrails on first startup (auto-seed event)
