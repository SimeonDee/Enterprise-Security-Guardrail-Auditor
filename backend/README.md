# Backend — Enterprise Security Guardrail Auditor

Python/FastAPI backend providing the REST API, security scanner engine, and data persistence layer.

## Tech Stack

- **Python 3.11+** with async/await throughout
- **FastAPI** — API framework with automatic OpenAPI docs
- **SQLAlchemy 2.x** (async) — ORM with aiosqlite driver
- **Pydantic v2** — request/response validation
- **SQLite** — zero-config database

## Setup

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Test

```bash
pytest                    # 97 tests, 94.65% coverage
pytest -x -q              # Quick mode, stop on first failure
pytest tests/scanner/     # Scanner tests only
```

## Lint

```bash
python -m ruff check app/       # Linting
python -m black --check app/    # Formatting
python -m mypy app/ --ignore-missing-imports  # Type checking
```

## Architecture

```
app/
├── api/v1/
│   ├── endpoints/          # Thin route handlers
│   │   ├── scans.py        # CRUD + upload + pagination
│   │   ├── guardrails.py   # CRUD with filters
│   │   ├── dashboard.py    # Aggregated stats
│   │   └── health.py       # Health check
│   └── router.py           # Router aggregation
├── core/
│   ├── exceptions.py       # APIError hierarchy (404, 409, 422, 500)
│   ├── logging.py          # Structured logging
│   ├── middleware.py        # Request logging + X-Request-ID
│   └── cache.py            # Cache protocol + NullCache
├── models/
│   ├── guardrail.py        # Guardrail ORM (severity, provider, pattern)
│   ├── scan.py             # Scan ORM (status, risk_score, violations)
│   └── violation.py        # Violation ORM (finding details)
├── scanner/
│   ├── parser.py           # Terraform HCL parser (regex-based)
│   ├── engine.py           # Scan orchestrator
│   ├── scoring.py          # Risk score calculator (0–100)
│   ├── models.py           # ParsedResource, Finding, ScanResult
│   └── rules/
│       ├── base.py         # BaseRule ABC
│       ├── registry.py     # RuleRegistry + default rules
│       ├── s3_public.py    # S3 public ACL detection
│       ├── open_ssh.py     # Open SSH port detection
│       ├── public_db.py    # Public database detection
│       ├── encryption.py   # Disabled encryption detection
│       └── iam_wildcard.py # Wildcard IAM policy detection
├── schemas/                # Pydantic v2 request/response models
├── services/
│   ├── scanner.py          # ScannerService (business logic)
│   └── seed.py             # Built-in guardrail definitions
├── config.py               # pydantic-settings configuration
├── database.py             # Async engine + session factory
└── main.py                 # App factory + lifespan + middleware
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Async SQLAlchemy + aiosqlite | Non-blocking I/O for FastAPI |
| App factory pattern | Testable, configurable app creation |
| Thin controllers | Routes delegate to ScannerService |
| Dual scan engine | New rule engine + legacy DB guardrail regex compatibility |
| Frozen dataclasses for scanner models | Immutable, hashable, decoupled from ORM |

## Environment Variables

See `.env.example` for all options. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./guardrail_auditor.db` | Database connection |
| `DEBUG` | `false` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_UPLOAD_SIZE_MB` | `10` | Upload file size limit |
| `CORS_ORIGINS` | `["http://localhost:5173","http://localhost:3000"]` | Allowed origins |
