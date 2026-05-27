# QA Report

**Project:** Enterprise Security Guardrail Auditor  
**Date:** 2025-07-25  
**Scope:** Full-stack quality assessment — backend, frontend, infrastructure  

---

## 1. Test Coverage

### Backend (Python / pytest)

| Metric | Value |
|--------|-------|
| Total Tests | 97 |
| Passed | 97 |
| Failed | 0 |
| Coverage | 94.65% |
| Threshold | 85% |

**Coverage by module:**

| Module | Coverage |
|--------|----------|
| `app/api/v1/endpoints/` | 95-100% |
| `app/core/` | 94-100% |
| `app/models/` | 95-97% |
| `app/scanner/` | 76-100% |
| `app/schemas/` | 100% |
| `app/services/scanner.py` | 90% |

**Uncovered areas:**
- `app/database.py` (57%) — `init_db()` / `close_db()` lifecycle hooks
- `app/scanner/rules/open_ssh.py` (76%) — IPv6 cidr_blocks branch
- `app/services/scanner.py` (90%) — failure-path exception handler, `_extract_resource_name` edge cases

### Frontend (TypeScript / Vitest)

| Metric | Value |
|--------|-------|
| Total Tests | 24 |
| Passed | 24 |
| Failed | 0 |
| TypeScript Errors | 0 |

---

## 2. Linting Compliance

| Tool | Backend Result | Frontend Result |
|------|---------------|-----------------|
| ruff | ✅ All checks passed | N/A |
| black | ✅ All files formatted | N/A |
| mypy | ✅ 0 errors (41 files) | N/A |
| tsc | N/A | ✅ 0 errors |
| ESLint | N/A | ⚠️ Not configured (ESLint 9 config missing) |

**Action item:** Add `eslint.config.js` for frontend in a future pass.

---

## 3. Security Assessment

See [docs/security-audit.md](security-audit.md) for the full 26-finding report.

**Summary:** 10 fixed, 16 deferred. No SQL injection, XSS, or RCE vectors found. Primary concern is the absence of authentication (I01, deferred to Phase 2).

---

## 4. API Correctness & REST Compliance

### Endpoints Reviewed

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/v1/health/` | GET | ✅ | Returns version + status |
| `/api/v1/scans/` | GET | ✅ | Paginated, filterable by status/file_type |
| `/api/v1/scans/` | POST | ✅ | Creates + runs scan in one step |
| `/api/v1/scans/upload` | POST | ✅ | Multipart .tf upload with size/type validation |
| `/api/v1/scans/{id}` | GET | ✅ | Eager-loads violations |
| `/api/v1/scans/{id}` | DELETE | ✅ | Cascades to violations, returns 204 |
| `/api/v1/guardrails/` | GET | ✅ | Paginated with enabled filter |
| `/api/v1/guardrails/` | POST | ✅ | Unique name check, returns 201 |
| `/api/v1/guardrails/{id}` | GET | ✅ | Standard 404 on missing |
| `/api/v1/guardrails/{id}` | PATCH | ✅ | Partial update |
| `/api/v1/guardrails/{id}` | DELETE | ✅ | Returns 204 |
| `/api/v1/dashboard/summary` | GET | ✅ | Aggregated stats + recent scans |

**REST Compliance:** All endpoints follow standard HTTP semantics (201 on create, 204 on delete, proper 404/409/422 error codes).

---

## 5. Database Schema Consistency

| Check | Status |
|-------|--------|
| FK constraints (violations → scans, violations → guardrails) | ✅ |
| Cascade delete (scan → violations) | ✅ |
| Nullable FK (guardrail_id on violations) | ✅ |
| Enum columns (ScanStatus, FileType, Severity, Provider) | ✅ |
| Timezone-aware timestamps | ✅ |
| Auto-generated created_at / updated_at | ✅ |
| Alembic migration exists | ✅ |

---

## 6. Async/Await Correctness

| Check | Status |
|-------|--------|
| All DB operations use `await` | ✅ |
| `async_sessionmaker` used throughout | ✅ |
| `selectinload` for eager loading (N+1 prevention) | ✅ |
| Lifespan context manager for startup/shutdown | ✅ |
| No sync I/O in async handlers | ⚠️ (I07: `ScanEngine.scan()` is sync) |

---

## 7. Scanner Logic Correctness

### Parser (`app/scanner/parser.py`)

| Check | Status |
|-------|--------|
| Extracts resource type + name | ✅ |
| Tracks line numbers | ✅ |
| Handles nested blocks | ✅ |
| Handles heredoc strings | ✅ |
| Handles braces in strings | ⚠️ (I08: not tracked) |
| Handles indented resources | ⚠️ (I15: `^resource` requires line-start) |

### Rules (5 implemented)

| Rule | Correctness | Notes |
|------|-------------|-------|
| S3 Public ACL | ✅ | Checks `acl` attribute for public values |
| Open SSH | ✅ | Checks port 22 + open CIDR. ⚠️ Missing IPv6 |
| Public DB | ✅ | Checks `publicly_accessible = true` |
| Encryption | ⚠️ | Only flags `encrypted = false`, not missing key |
| IAM Wildcard | ✅ | Checks both Action and Resource wildcards |

### Scoring (`app/scanner/scoring.py`)

| Check | Status |
|-------|--------|
| Weighted by severity | ✅ |
| 0-100 range | ✅ |
| Handles empty findings | ✅ |
| Float precision handled | ✅ |

---

## 8. Architecture Consistency

| Check | Status |
|-------|--------|
| App factory pattern | ✅ |
| Layered architecture (routes → services → models) | ✅ |
| Thin controllers | ✅ |
| Dependency injection via FastAPI `Depends` | ✅ |
| Pydantic schemas separate from ORM models | ✅ |
| Config via pydantic-settings | ✅ |
| Centralized error handling (APIError hierarchy) | ✅ |
| Request logging middleware | ✅ |
| Frontend component/page separation | ✅ |
| React Query for server state | ✅ |

---

## 9. Issues Fixed in This QA Pass

| # | Description | Severity | File |
|---|-------------|----------|------|
| 1 | Added try/except failure handling in `run_scan` | HIGH | `services/scanner.py` |
| 2 | Added upload file size limit (10 MB) | HIGH | `endpoints/scans.py` |
| 3 | Added UnicodeDecodeError handling | MEDIUM | `endpoints/scans.py` |
| 4 | Constrained guardrails `limit` param | MEDIUM | `endpoints/guardrails.py` |
| 5 | Guarded duplicate log handlers | LOW | `core/logging.py` |
| 6 | Removed 4 unused imports | LOW | Multiple files |
| 7 | Removed unused variable | LOW | `scanner/parser.py` |
| 8 | Converted `str+Enum` → `StrEnum` | LOW | 3 model files |
| 9 | Fixed mypy forward-ref errors | LOW | 3 model files |
| 10 | Fixed all ruff/black/mypy violations | LOW | Multiple files |

---

## 10. Recommendations for Next Phase

1. **Authentication** — Add JWT/OAuth2 middleware (CRITICAL)
2. **Background scanning** — Move `ScanEngine.scan()` to async worker (HIGH)
3. **Secret redaction** — Strip sensitive values from `source_content` before storage (HIGH)
4. **ESLint config** — Add `eslint.config.js` for frontend linting (MEDIUM)
5. **Integration tests** — End-to-end scan upload → result verification (MEDIUM)
6. **Dependency lockfile** — Add `pip-compile` or `uv.lock` for reproducible builds (LOW)
