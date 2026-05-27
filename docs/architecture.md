# Architecture Overview

## System Design

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│  Vite + TypeScript + Tailwind CSS + Recharts                 │
│                                                              │
│  Pages: Dashboard | Scans | ScanDetail | NewScan | Guardrails│
│  Services: API client (axios)                                │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP (REST JSON)
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                           │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────────┐ │
│  │ Health  │  │Guardrails│  │   Scans   │  │  Dashboard  │ │
│  │  API    │  │   CRUD   │  │  + Scan   │  │  Summary    │ │
│  └─────────┘  └──────────┘  └─────┬─────┘  └─────────────┘ │
│                                   │                          │
│                          ┌────────▼────────┐                 │
│                          │ Scanner Service │                 │
│                          │ (Rule Engine)   │                 │
│                          └────────┬────────┘                 │
│                                   │                          │
│                          ┌────────▼────────┐                 │
│                          │  SQLAlchemy ORM │                 │
│                          └────────┬────────┘                 │
└───────────────────────────────────┼──────────────────────────┘
                                    │
                           ┌────────▼────────┐
                           │  SQLite Database │
                           │ guardrail_auditor│
                           │     .db          │
                           └─────────────────┘
```

## Data Model

### Guardrail
Security rules that define what to look for. Each guardrail has:
- Regex pattern to match against IaC files
- Severity level (critical/high/medium/low/info)
- Provider scope (AWS/Azure/GCP/generic)
- Remediation guidance

### Scan
An audit run against an uploaded IaC file. Produces:
- List of violations matched by guardrails
- Computed risk score (0-100%)

### Violation
A single finding linking a scan to a guardrail, with:
- Resource name, file path, line number
- Severity and remediation from the matched guardrail

## Risk Score Calculation

```
severity_weights = {critical: 10, high: 7, medium: 4, low: 1, info: 0.5}
weighted_sum = sum(weight for each violation)
max_possible = num_violations * 10
risk_score = (weighted_sum / max_possible) * 100
```

## API-First Design

All functionality is exposed through versioned REST endpoints (`/api/v1/`).
The frontend is a pure consumer of the API — no server-side rendering.
OpenAPI docs auto-generated at `/docs`.

## Tech Stack

| Layer     | Technology           |
|-----------|---------------------|
| Frontend  | React 19 + Vite + TS + Tailwind |
| Backend   | Python 3.11 + FastAPI |
| ORM       | SQLAlchemy 2.x       |
| Database  | SQLite               |
| Charts    | Recharts             |
| Testing   | pytest / Vitest + RTL|
| Container | Docker + docker-compose |
