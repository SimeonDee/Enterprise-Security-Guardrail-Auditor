# Enterprise Security Guardrail Auditor

<p align="center">
  <strong>Audit infrastructure-as-code files against security baselines. Flag high-risk patterns. Visualize risk.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/react-19-61dafb?logo=react&logoColor=white" alt="React 19">
  <img src="https://img.shields.io/badge/fastapi-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/coverage-95%25-brightgreen" alt="Coverage 95%">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
</p>

---

## What It Does

Upload a Terraform (`.tf`) file and instantly receive:

- **Security findings** — public S3 buckets, open SSH ports, wildcard IAM policies, unencrypted databases, and more
- **Risk score** — weighted 0–100 score based on finding severity
- **Visual dashboard** — severity breakdown charts, trend data, recent scan history
- **Remediation guidance** — actionable fix recommendations for every finding

## Architecture

```
┌────────────────────────┐          ┌──────────────────────────────┐
│   React Frontend       │   HTTP   │      FastAPI Backend         │
│   TypeScript + Vite    │ ──────▶  │                              │
│   Tailwind + Recharts  │          │  Routes → Services → Models  │
└────────────────────────┘          │                              │
                                    │  ┌────────────────────────┐  │
                                    │  │   Scanner Engine        │  │
                                    │  │   Parser → Rules →      │  │
                                    │  │   Scoring → Results     │  │
                                    │  └────────────────────────┘  │
                                    │                              │
                                    │  SQLAlchemy + SQLite         │
                                    └──────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 6, TypeScript, Tailwind CSS 3, Recharts, React Query |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.x (async), Pydantic v2 |
| Database | SQLite via aiosqlite |
| Testing | pytest (97 tests, 95% coverage) / Vitest + RTL (24 tests) |
| DevOps | Docker, GitHub Actions CI, pre-commit hooks |
| Linting | ruff, black, mypy, tsc |

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor.git
cd Enterprise-Security-Guardrail-Auditor

cp .env.example .env
cp backend/.env.example backend/.env.docker

docker compose up --build -d
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs

### Local Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm ci
npm run dev
```

## Security Rules

Five built-in rules detect critical AWS misconfigurations:

| Rule | Severity | Detects |
|------|----------|---------|
| S3 Public Access | Critical | Public ACL on S3 buckets |
| Open SSH | Critical | Port 22 open to 0.0.0.0/0 |
| Public Database | Critical | RDS publicly accessible |
| Disabled Encryption | High | Encryption explicitly disabled |
| Wildcard IAM | Critical | `"Action": "*"` in IAM policies |

Rules are extensible — add new ones by subclassing `BaseRule`. See [docs/security-rules.md](docs/security-rules.md).

## Risk Scoring

Findings are weighted by severity and normalized to a 0–100 scale:

| Severity | Weight | Example |
|----------|--------|---------|
| Critical | 10 | 3 critical findings → score 100 |
| High | 7 | 3 high findings → score 70 |
| Medium | 4 | 3 medium findings → score 40 |
| Low | 1 | 3 low findings → score 10 |

## API

RESTful JSON API at `/api/v1/`. Full reference: [docs/api-reference.md](docs/api-reference.md)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scans` | GET | List scans (paginated, filterable) |
| `/scans` | POST | Create scan from JSON |
| `/scans/upload` | POST | Upload `.tf` file |
| `/scans/{id}` | GET | Scan detail + violations |
| `/scans/{id}` | DELETE | Delete scan |
| `/guardrails` | GET/POST | List / create rules |
| `/guardrails/{id}` | GET/PATCH/DELETE | Read / update / delete rule |
| `/dashboard/summary` | GET | Aggregated stats |

## Testing

```bash
# Backend — 97 tests, 94.65% coverage
cd backend && source venv/bin/activate
pytest

# Frontend — 24 tests
cd frontend && npm test
```

## Project Structure

```
├── .github/workflows/ci.yml    # GitHub Actions CI (5 jobs)
├── .pre-commit-config.yaml      # Pre-commit hooks
├── Makefile                     # Developer shortcuts
├── docker-compose.yml           # Docker orchestration
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   ├── core/                # Middleware, logging, errors
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── scanner/             # Security engine
│   │   │   ├── parser.py        # Terraform HCL parser
│   │   │   ├── rules/           # Pluggable rule system
│   │   │   ├── scoring.py       # Risk score calculator
│   │   │   └── engine.py        # Orchestrator
│   │   ├── schemas/             # Pydantic request/response
│   │   └── services/            # Business logic
│   └── tests/                   # 97 pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Route pages
│   │   ├── services/api.ts      # Axios API client
│   │   └── types/api.ts         # TypeScript interfaces
│   └── src/test/                # Vitest tests
└── docs/                        # Project documentation
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, data flow, design decisions |
| [API Reference](docs/api-reference.md) | Complete endpoint documentation |
| [Security Rules](docs/security-rules.md) | Rule details + custom rule guide |
| [Deployment](docs/deployment.md) | Docker setup, env vars, data persistence |
| [Dev Workflow](docs/dev-workflow.md) | Setup, testing, CI, pre-commit |
| [Frontend](docs/frontend.md) | React architecture, components, testing |
| [Security Audit](docs/security-audit.md) | 26-finding security review |
| [QA Report](docs/qa-report.md) | Quality assessment report |
| [Presentation](docs/presentation.md) | Project overview slides |
| [Final Summary](docs/final-summary.md) | Project retrospective |

## Sample Test Files

The `samples/` directory contains intentionally vulnerable Terraform configurations for testing:

| File | Vulnerabilities | Purpose |
|------|----------------|---------|
| [vulnerable-infra.tf](samples/vulnerable-infra.tf) | 11 findings | Core rule coverage (S3, SSH, DB, encryption, IAM) |
| [multi-service-vulnerable.tf](samples/multi-service-vulnerable.tf) | 9 findings | Edge cases (wide port ranges, group policies, authenticated-read) |

Upload these via the dashboard or API to validate the scanner end-to-end.

## Contributing

Contributions are welcome. Please follow the workflow below to keep the codebase clean and consistent.

### Branch Naming Convention

```
<type>/<short-description>
```

| Type | Use case | Example |
|------|----------|---------|
| `feat/` | New feature | `feat/cloudformation-parser` |
| `fix/` | Bug fix | `fix/scoring-division-error` |
| `docs/` | Documentation only | `docs/update-api-reference` |
| `refactor/` | Code restructure (no behavior change) | `refactor/scanner-pipeline` |
| `test/` | Adding or updating tests | `test/iam-wildcard-edge-cases` |
| `chore/` | Config, CI, dependencies | `chore/upgrade-fastapi` |

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary>

<optional body>
```

**Examples:**
```
feat: add CloudFormation YAML parser
fix: handle empty ingress blocks in SSH rule
docs: update API reference with upload endpoint
test: add edge case tests for risk scoring
chore: bump SQLAlchemy to 2.1
```

### Pull Request Workflow

1. **Fork** the repository (or create a branch from `main`)
2. **Create a feature branch** following the naming convention above
3. **Make changes** — keep PRs focused on a single concern
4. **Run quality checks locally** before pushing:
   ```bash
   # Backend
   cd backend && source venv/bin/activate
   make lint        # ruff + black + mypy
   make test-backend  # pytest with coverage

   # Frontend
   cd frontend
   npx tsc --noEmit  # Type check
   npm test           # Vitest
   npm run build      # Production build
   ```
5. **Push** and open a PR against `main`
6. **CI must pass** — all 5 GitHub Actions jobs (backend-lint, backend-test, frontend-lint, frontend-test, docker-build)
7. **Code review** — at least one approval required

### Code Quality Requirements

All PRs must meet these gates before merge:

| Check | Requirement |
|-------|-------------|
| Backend tests | All passing, ≥85% coverage |
| Frontend tests | All passing |
| ruff | 0 lint errors |
| black | 0 formatting changes |
| mypy | 0 type errors |
| tsc | 0 TypeScript errors |
| Build | `npm run build` succeeds |
| Pre-commit | All hooks pass (`make hooks` to install) |

### Local Development Workflow

```bash
# 1. Clone and set up
git clone https://github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor.git
cd Enterprise-Security-Guardrail-Auditor

# 2. Install pre-commit hooks
make hooks

# 3. Backend setup
cd backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# 4. Frontend setup
cd ../frontend
npm ci

# 5. Start development servers
make backend    # Terminal 1: uvicorn on port 8000
make frontend   # Terminal 2: Vite on port 5173

# 6. Run checks before committing
make lint       # All linters
make test       # All tests
```

See [docs/dev-workflow.md](docs/dev-workflow.md) for the full developer guide.

## AI-Assisted Development

This project was built using **AI-assisted development** with **GitHub Copilot (Claude Opus 4.6)**. Every prompt and action is recorded in [prompts.md](prompts.md). The full development — from scaffold to production-ready MVP — was completed in 12 turns of structured interaction.

## Author

**Simeon Adedokun**

- GitHub: [@SimeonDee](https://github.com/SimeonDee)

## License

MIT
