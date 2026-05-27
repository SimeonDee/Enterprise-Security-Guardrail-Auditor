# Architecture Overview

## System Design

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (React 19)                    │
│  Vite 6 + TypeScript + Tailwind CSS 3 + Recharts             │
│                                                              │
│  Pages: Dashboard | Scans | ScanDetail | NewScan | Guardrails│
│  State: React Query (@tanstack/react-query)                  │
│  Routing: React Router DOM 7                                 │
│  HTTP: Axios                                                 │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP (REST JSON)
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                           │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────────┐ │
│  │ Health  │  │Guardrails│  │   Scans   │  │  Dashboard  │ │
│  │  API    │  │   CRUD   │  │  + Upload │  │  Summary    │ │
│  └─────────┘  └──────────┘  └─────┬─────┘  └─────────────┘ │
│                                   │                          │
│                 ┌─────────────────▼──────────────────┐       │
│                 │        Scanner Service              │       │
│                 │  ┌─────────┐  ┌────────┐  ┌──────┐│       │
│                 │  │ Parser  │→ │ Rules  │→ │Score ││       │
│                 │  └─────────┘  └────────┘  └──────┘│       │
│                 └─────────────────┬──────────────────┘       │
│                                   │                          │
│                 ┌─────────────────▼──────────────────┐       │
│                 │   SQLAlchemy 2.x (async)            │       │
│                 │   Models: Guardrail | Scan | Violation │    │
│                 └─────────────────┬──────────────────┘       │
│                                   │                          │
│  Middleware: RequestLogging, CORS │                          │
│  Errors: APIError hierarchy       │                          │
│  Config: pydantic-settings        │                          │
└───────────────────────────────────┼──────────────────────────┘
                                    │ aiosqlite (async)
                           ┌────────▼────────┐
                           │  SQLite Database │
                           │ guardrail_auditor│
                           │     .db          │
                           └─────────────────┘
```

## Scanner Engine Pipeline

The scanner engine is the core of the system. It processes Terraform files through a four-stage pipeline:

```
                        Terraform Content (string)
                                │
                    ┌───────────▼────────────┐
              1.   │   TerraformParser       │  Regex-based HCL extraction
                   │   .parse(content)       │  Handles nested blocks, heredocs
                   └───────────┬─────────────┘
                               │  list[ParsedResource]
                    ┌──────────▼─────────────┐
              2.   │   RuleRegistry          │  Routes resources to applicable rules
                   │   .get_rules_for(type)  │  Each rule is a BaseRule subclass
                   └──────────┬──────────────┘
                              │  list[Finding]
                    ┌─────────▼──────────────┐
              3.   │   calculate_risk_score  │  Weighted severity scoring
                   │   0–100 normalized      │  critical=10, high=7, med=4, low=1
                   └─────────┬───────────────┘
                             │  float (0.0–100.0)
                    ┌────────▼───────────────┐
              4.   │   ScanResult            │  Aggregated immutable output
                   │   findings + score      │  Returned to ScannerService
                   └─────────────────────────┘
```

### Parser

`TerraformParser.parse(content)` extracts `resource` blocks from Terraform HCL using regex. It handles:

- Nested brace matching for block boundaries
- Attribute extraction (`key = "value"` and `key = true/false`)
- Nested block extraction (`ingress { ... }`)
- Heredoc content (`<<EOF ... EOF`) for inline policies
- Line number tracking for precise finding locations

### Rule System

Rules are pluggable via the `BaseRule` abstract class:

```python
class BaseRule(ABC):
    rule_id: str           # e.g. "S3_PUBLIC_ACCESS"
    severity: str          # critical | high | medium | low | info
    resource_types: list   # e.g. ["aws_s3_bucket"]

    @abstractmethod
    def evaluate(self, resource, file_path) -> list[Finding]: ...
```

`RuleRegistry` maps resource types to applicable rules. Adding a new rule requires:
1. Subclass `BaseRule`
2. Implement `evaluate()`
3. Register in `build_default_registry()`

### Dual Scan Paths

`ScannerService.run_scan()` executes two scan paths and deduplicates:
1. **Engine scan** — `ScanEngine` with structured rules (5 rules)
2. **Legacy scan** — DB guardrail regex patterns (10 seed rules)

Findings are deduplicated by `(resource_name, message)` before storage.

## Data Model

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Guardrail     │     │     Scan         │     │   Violation     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │     │ id              │
│ name            │     │ name            │     │ scan_id (FK)    │
│ description     │     │ status (enum)   │     │ guardrail_id(FK)│
│ severity (enum) │     │ file_type (enum)│     │ resource_name   │
│ provider (enum) │     │ file_name       │     │ file_path       │
│ resource_type   │     │ source_content  │     │ line_number     │
│ pattern (regex) │     │ risk_score      │     │ severity        │
│ remediation     │     │ total_violations│     │ message         │
│ enabled         │     │ created_at      │     │ remediation     │
│ created_at      │     │ completed_at    │     │ created_at      │
│ updated_at      │     └────────┬────────┘     └─────────────────┘
└─────────────────┘              │ 1:N cascade          ▲
                                 └──────────────────────┘
```

### Enums

| Enum | Values |
|------|--------|
| `Severity` | `critical`, `high`, `medium`, `low`, `info` |
| `Provider` | `aws`, `azure`, `gcp`, `generic` |
| `ScanStatus` | `pending`, `running`, `completed`, `failed` |
| `FileType` | `terraform`, `cloudformation` |

## Risk Score Calculation

The risk score is a **weighted percentage** on a 0–100 scale:

| Severity | Weight |
|----------|--------|
| Critical | 10.0 |
| High | 7.0 |
| Medium | 4.0 |
| Low | 1.0 |
| Info | 0.5 |

**Formula:**
```
weighted_sum = sum(SEVERITY_WEIGHTS[finding.severity] for each finding)
max_possible = num_findings × 10.0  (all-critical scenario)
risk_score   = (weighted_sum / max_possible) × 100, capped at 100
```

**Examples:**
- 3 critical findings → `(30 / 30) × 100 = 100`
- 2 critical + 1 low → `(21 / 30) × 100 = 70`
- 5 medium findings → `(20 / 50) × 100 = 40`

## API Design

All functionality is exposed through versioned REST endpoints (`/api/v1/`).

**Design principles:**
- Thin controllers — routes delegate to `ScannerService`
- Paginated list endpoints with `PaginatedResponse[T]`
- Consistent error format via `APIError` hierarchy
- File upload with size limit (10 MB) and UTF-8 validation
- OpenAPI docs auto-generated at `/docs`
- CORS configured for frontend origins

## Request Lifecycle

```
HTTP Request
    │
    ▼
RequestLoggingMiddleware (assigns X-Request-ID, logs timing)
    │
    ▼
CORSMiddleware (validates origin)
    │
    ▼
FastAPI Router → Endpoint Handler
    │
    ▼
Dependency Injection (get_db → AsyncSession)
    │
    ▼
ScannerService (business logic)
    │
    ▼
SQLAlchemy Async Session → SQLite
    │
    ▼
Pydantic Schema Serialization → JSON Response
```

## Deployment Architecture

```
┌──────────────────────────────────────────┐
│          Docker Compose                   │
│                                          │
│  ┌────────────────┐  ┌────────────────┐  │
│  │   Frontend     │  │    Backend     │  │
│  │  nginx:1.27    │  │  Python 3.11   │  │
│  │  Port 3000     │──│  Port 8000     │  │
│  │  SPA routing   │  │  Non-root user │  │
│  │  + API proxy   │  │  Healthcheck   │  │
│  └────────────────┘  └───────┬────────┘  │
│                              │           │
│                    ┌─────────▼────────┐  │
│                    │  SQLite Volume   │  │
│                    │  /app/data/      │  │
│                    └──────────────────┘  │
└──────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + Vite + TypeScript + Tailwind CSS | 19 / 6 / 5.x / 3 |
| Charts | Recharts | 2.x |
| Server State | @tanstack/react-query | 5.x |
| Backend | Python + FastAPI + Pydantic | 3.11 / 0.115 / 2.x |
| ORM | SQLAlchemy (async) | 2.x |
| Database | SQLite via aiosqlite | — |
| Testing | pytest + pytest-asyncio / Vitest + RTL | — |
| Linting | ruff, black, mypy / tsc | — |
| Container | Docker + docker-compose | — |
| CI | GitHub Actions | — |
| Hooks | pre-commit (ruff, black, mypy) | — |

## Design Decisions & Tradeoffs

| Decision | Rationale | Tradeoff |
|----------|-----------|----------|
| SQLite over PostgreSQL | Zero-config, single-file, fits MVP scope | No concurrent write scaling |
| Regex parser over HCL library | Pure Python, no binary deps | Limited edge case coverage |
| Sync scanning | Simpler request flow, adequate for single-file scans | Blocks request thread for large files |
| Dual scan engine | Backwards-compatible with DB guardrails | Dedup complexity |
| Frozen dataclasses | Immutable scan results, hashable | Slightly verbose |
| App factory pattern | Testable, configurable | Minor boilerplate |
| React Query over Redux | Built-in caching, optimistic updates, simpler | Less control over global state |
