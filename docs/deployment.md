# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- (For local dev) Python 3.11+, Node.js 20+

---

## Quick Start — Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor.git
cd Enterprise-Security-Guardrail-Auditor

# 2. Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env.docker

# 3. Build and start
docker compose up --build -d

# 4. Verify
curl http://localhost:8000/api/v1/health/
# → {"status": "healthy", "version": "0.1.0"}

open http://localhost:3000
```

The backend runs on port **8000**, the frontend on port **3000**.

---

## Architecture

```
┌──────────────┐       ┌──────────────────┐
│   Frontend   │──:80──│  nginx (static)  │
│  (React/TS)  │       │  + API proxy     │
└──────────────┘       └───────┬──────────┘
                               │ /api/* → :8000
                       ┌───────▼──────────┐
                       │    Backend        │
                       │  (FastAPI/Py)     │
                       │  + uvicorn        │
                       └───────┬──────────┘
                               │
                       ┌───────▼──────────┐
                       │   SQLite file     │
                       │  (Docker volume)  │
                       └──────────────────┘
```

---

## Docker Images

### Backend (`backend/Dockerfile`)

- **Base:** `python:3.11-slim`
- **Multi-stage:** Builder installs deps, runtime copies only needed packages
- **Non-root user:** Runs as `appuser`
- **Healthcheck:** Polls `/api/v1/health/` every 30s
- **Data volume:** SQLite DB persisted at `/app/data/`

### Frontend (`frontend/Dockerfile`)

- **Base:** `node:20-slim` (build) → `nginx:1.27-alpine` (runtime)
- **Build arg:** `VITE_API_BASE_URL` injected at build time
- **Healthcheck:** Polls `/` every 30s
- **Nginx:** SPA routing + API reverse proxy to backend

---

## Environment Variables

### Root `.env` (docker-compose)

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | `8000` | Host port for backend |
| `FRONTEND_PORT` | `3000` | Host port for frontend |

### Backend `.env.docker`

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max upload file size |
| `DATABASE_URL` | (set in compose) | SQLite connection string |

See `backend/.env.example` for the full list.

---

## Data Persistence

SQLite data is stored in a Docker named volume `sqlite-data`, mounted at `/app/data/` inside the backend container.

```bash
# Inspect volume
docker volume inspect enterprise-security-guardrail-auditor_sqlite-data

# Back up the database
docker cp guardrail-backend:/app/data/guardrail_auditor.db ./backup.db

# Restore
docker cp ./backup.db guardrail-backend:/app/data/guardrail_auditor.db
```

To reset the database:

```bash
docker compose down -v   # removes volumes
docker compose up --build -d
```

---

## Operations

```bash
# View logs
docker compose logs -f
docker compose logs -f backend

# Restart a single service
docker compose restart backend

# Rebuild after code changes
docker compose up --build -d

# Stop everything
docker compose down

# Stop + remove data
docker compose down -v
```

---

## Port Conflicts

If ports 8000 or 3000 are in use, override via `.env`:

```env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

---

## Health Checks

Both services include Docker healthchecks:

```bash
docker inspect --format='{{.State.Health.Status}}' guardrail-backend
docker inspect --format='{{.State.Health.Status}}' guardrail-frontend
```

The frontend `depends_on` the backend with `condition: service_healthy`, ensuring the API is available before the frontend starts.
