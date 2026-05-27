# Final Project Summary

## Project Overview

The **Enterprise Security Guardrail Auditor** is an API-first web application that audits infrastructure-as-code files against a security baseline. It parses Terraform configuration files, evaluates them against 15 security rules, computes a weighted risk score, and presents findings through a visual dashboard.

## What Was Built

### Backend (Python/FastAPI)
- Async REST API with 4 resource groups (health, scans, guardrails, dashboard)
- Terraform parser extracting resource blocks, attributes, nested blocks, and heredocs
- Security scanner engine with 5 structured rules and 10 regex-based seed guardrails
- Risk scoring engine producing a weighted 0–100 score
- Paginated list endpoints with status/file_type filters
- File upload endpoint with size limit (10 MB) and UTF-8 validation
- App factory pattern with lifespan context manager
- Request logging middleware with X-Request-ID tracing
- Centralized error handling via APIError hierarchy
- Alembic migration setup for schema management

### Frontend (React/TypeScript)
- Dashboard with stats cards, severity bar chart (Recharts), recent scans table
- Scan management: paginated list, detail view with findings grouped by severity
- Dual-mode scan creation: file upload or content paste
- Guardrail configuration page
- Reusable components: RiskScoreBadge, SeverityBadge, StatusBadge, Pagination
- React Query for server state management with automatic caching

### DevOps
- Multi-stage Docker builds with non-root users and healthchecks
- docker-compose orchestration with SQLite volume persistence
- GitHub Actions CI pipeline (5 jobs: lint × 2, test × 2, docker build)
- Pre-commit hooks (ruff, black, mypy, secret detection, file size guard)
- Makefile with 12 developer shortcuts
- Environment variable management (.env.example, .env.docker)

## System Architecture

```
Frontend (React 19 + Vite + TypeScript + Tailwind)
        │
        │ HTTP/REST
        ▼
Backend (FastAPI + SQLAlchemy async)
        │
        ├── Scanner Engine
        │   ├── TerraformParser (regex-based HCL extraction)
        │   ├── RuleRegistry → 5 BaseRule subclasses
        │   ├── calculate_risk_score() (weighted 0–100)
        │   └── ScanEngine (orchestrator)
        │
        ├── ScannerService (business logic + dual scan paths)
        │
        └── SQLite via aiosqlite
```

## Risk Scoring Methodology

Findings are weighted by severity and normalized:

| Severity | Weight |
|----------|--------|
| Critical | 10.0 |
| High | 7.0 |
| Medium | 4.0 |
| Low | 1.0 |
| Info | 0.5 |

**Formula:** `score = (sum_of_weights / (num_findings × 10)) × 100`

The denominator uses the maximum possible weight (all-critical scenario), so the score represents how severe the findings are relative to the worst case.

## Scanner Design

The scanner uses a **layered pipeline** architecture:

1. **Parser** — Regex-based Terraform HCL parser. Extracts `resource` blocks with attributes, nested blocks, heredoc content, and line numbers. Pure Python with no binary dependencies.

2. **Rules** — Pluggable via `BaseRule` abstract class with `RuleRegistry` mapping resource types to applicable rules. Each rule receives a `ParsedResource` and returns `list[Finding]`.

3. **Scoring** — Weighted severity calculation normalized to 0–100. Deterministic, stateless, and pure functional.

4. **Engine** — `ScanEngine` ties parser → rules → scoring into a single `scan()` call returning an immutable `ScanResult`.

5. **Service** — `ScannerService` orchestrates the engine scan alongside legacy DB guardrail regex matching, deduplicates findings, persists violations, and updates scan status.

## Tradeoffs & MVP Limitations

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **SQLite** | Zero configuration, single-file database, fits MVP scope | No concurrent write scaling; migration to PostgreSQL needed for production |
| **Regex parser** | Pure Python, no binary dependencies, fast to implement | Limited HCL edge case coverage (e.g., nested quotes, complex expressions) |
| **Sync scanning** | Simpler request/response flow, adequate for single-file scans | Blocks the request thread; large files could cause timeouts |
| **No authentication** | Focus development time on scanner logic | Insecure for multi-tenant deployment; must add before production |
| **AWS rules only** | Most common cloud provider for Terraform users | No Azure/GCP coverage in current rule set |
| **No CloudFormation** | Terraform-first approach, HCL is more common | Limits utility for AWS-native teams using CFN |
| **Dual scan engine** | Backwards-compatible with DB guardrails, allows non-code rule additions | Deduplication complexity; two code paths to maintain |
| **React Query over Redux** | Built-in caching, simpler for server state | Less control over complex client-side state |

## Future Roadmap

### Near-term (Post-MVP)
- API key authentication middleware
- CloudFormation YAML/JSON parsing support
- Azure and GCP security rule packs
- Export scan results as PDF/CSV
- Error boundary in React frontend
- ESLint configuration for frontend
- Auto-seed guardrails on first startup

### Medium-term
- JWT/OAuth2 authentication with RBAC
- Async scan processing (background tasks)
- Secret redaction in stored source content
- Multi-file and zip upload scanning
- Scan history comparison and trend charts
- Custom guardrail creation via frontend UI

### Long-term
- PostgreSQL migration option
- Webhook notifications for critical findings
- Multi-tenant support
- CI/CD integration (GitHub Actions marketplace action)
- Policy-as-code enforcement (block deploys above risk threshold)

## AI-Assisted Development Workflow

This project was built using **AI-assisted development** with **GitHub Copilot powered by the Claude Opus 4.6 model**.

### Methodology

Each development phase followed a structured workflow:

1. **Prompt** — A detailed natural language specification describing the feature, constraints, and expected outputs
2. **Implementation** — AI generates all code, tests, and documentation
3. **Verification** — Automated test suites validate correctness (97 backend tests, 24 frontend tests)
4. **Audit** — Every prompt is recorded in `prompts.md` with exact text, summary, and action taken

### Development Timeline

| Turn | Phase | Deliverables |
|------|-------|-------------|
| 1 | Kickoff | Stack agreement, project scaffold |
| 2 | Scaffold | 40+ files, backend verified (24 tests) |
| 3 | Async Migration | SQLAlchemy async, 38 tests |
| 4 | Scanner Engine | 5 rules, parser, scoring (91 tests) |
| 5 | Scan API | Pagination, upload, thin controllers (97 tests) |
| 6 | Frontend MVP | React dashboard, all pages (24 frontend tests) |
| 7 | QA + Security | 26 findings, 10 fixed, all linters clean |
| 8 | DevOps | Docker, CI, pre-commit, env management |
| 9 | Documentation | Full documentation suite for submission |

### Key Observations

- **AI excels at scaffold-to-MVP**: Generating boilerplate, test files, configuration, and documentation is dramatically faster with AI assistance
- **Testing as guardrail**: Automated tests serve as the primary verification mechanism — every change is validated against the test suite
- **Linting as quality gate**: Four linters (ruff, black, mypy, tsc) catch issues that AI-generated code might introduce
- **Prompt engineering matters**: Detailed, structured prompts with clear constraints produce better results than vague requests
- **Human oversight remains essential**: Architecture decisions, security review, and tradeoff analysis require human judgment

## Quality Metrics

| Metric | Value |
|--------|-------|
| Backend tests | 97 |
| Backend coverage | 94.65% |
| Frontend tests | 24 |
| Total files | 40+ |
| Lint violations | 0 |
| Security findings | 26 cataloged, 10 fixed |
| Git commits | 9 |
| Documentation files | 13 |

## Repository

**GitHub:** [github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor](https://github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor)

## License

MIT
