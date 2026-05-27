# Developer Workflow Guide

## Initial Setup

```bash
# Clone
git clone https://github.com/SimeonDee/Enterprise-Security-Guardrail-Auditor.git
cd Enterprise-Security-Guardrail-Auditor

# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
cd ..

# Frontend
cd frontend
npm ci
cd ..

# Pre-commit hooks
cd backend && source venv/bin/activate
pre-commit install --config ../.pre-commit-config.yaml
cd ..
```

Or use the Makefile shortcut:

```bash
make install
```

---

## Daily Development

### Start Services

```bash
# Terminal 1 — Backend (auto-reload)
make backend
# → http://localhost:8000/docs

# Terminal 2 — Frontend (HMR)
make frontend
# → http://localhost:5173
```

### Run Tests

```bash
make test            # Both backend + frontend
make test-backend    # Backend only (97 tests, 94%+ coverage)
make test-frontend   # Frontend only (24 tests)
```

### Run Linters

```bash
make lint
```

This runs: `ruff check` → `black --check` → `mypy` → `tsc --noEmit`

---

## Pre-Commit Hooks

Hooks run automatically on `git commit` and check:

| Hook | Scope | What it does |
|------|-------|-------------|
| `ruff` | Backend | Lint + auto-fix Python |
| `ruff-format` | Backend | Format Python (ruff) |
| `black` | Backend | Format Python (black) |
| `mypy` | Backend | Type check Python |
| `trailing-whitespace` | All | Remove trailing spaces |
| `end-of-file-fixer` | All | Ensure files end with newline |
| `check-yaml` | All | Validate YAML syntax |
| `check-json` | All | Validate JSON syntax |
| `check-added-large-files` | All | Block files > 500 KB |
| `check-merge-conflict` | All | Detect conflict markers |
| `detect-private-key` | All | Block private keys |

### Manual Run

```bash
# Run all hooks on staged files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files
```

---

## CI Pipeline

GitHub Actions CI runs on every push to `main` and every pull request.

### Pipeline Structure

```
ci.yml
├── backend-lint     (ruff, black, mypy)
├── backend-test     (pytest, coverage ≥ 85%)
├── frontend-lint    (tsc --noEmit)
├── frontend-test    (vitest)
└── docker-build     (builds both images — runs after tests pass)
```

### Workflow

1. **Create branch:** `git checkout -b feat/my-feature`
2. **Make changes** and commit (pre-commit hooks run)
3. **Push:** `git push -u origin feat/my-feature`
4. **Open PR** against `main` — CI runs automatically
5. **Review** — all 4 CI jobs must pass
6. **Merge** to `main` — CI runs again on the merge commit

---

## Docker Workflow

```bash
# Build + start
make docker-up

# View logs
make docker-logs

# Stop
make docker-down

# Full rebuild
docker compose down -v && docker compose up --build -d
```

---

## Project Structure

```
Enterprise-Security-Guardrail-Auditor/
├── .github/workflows/ci.yml   # GitHub Actions CI
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .env.example               # Root env template
├── docker-compose.yml         # Multi-service orchestration
├── Makefile                   # Developer shortcuts
├── backend/
│   ├── .dockerignore
│   ├── .env.example           # Backend env template
│   ├── .env.docker            # Docker-specific env
│   ├── Dockerfile             # Multi-stage Python image
│   ├── pyproject.toml         # Dependencies + tool config
│   ├── app/                   # Application code
│   └── tests/                 # Pytest test suite
├── frontend/
│   ├── .dockerignore
│   ├── Dockerfile             # Multi-stage Node → nginx
│   ├── nginx.conf             # SPA routing + API proxy
│   ├── package.json           # Dependencies
│   └── src/                   # React source
└── docs/                      # Project documentation
```

---

## Makefile Commands

```bash
make help           # Show all available commands
make install        # Install all dependencies
make hooks          # Install pre-commit hooks
make backend        # Start backend dev server
make frontend       # Start frontend dev server
make lint           # Run all linters
make test           # Run all tests
make test-backend   # Backend tests only
make test-frontend  # Frontend tests only
make docker-up      # Docker Compose up
make docker-down    # Docker Compose down
make docker-logs    # Tail Docker logs
make clean          # Remove generated files
```

---

## Environment Variables

### Local Development

Copy the example files and edit as needed:

```bash
cp backend/.env.example backend/.env
```

The backend reads from `backend/.env` automatically via pydantic-settings. For the frontend, Vite reads `VITE_*` variables from the environment.

### Docker

Docker Compose reads:
- Root `.env` — port mappings
- `backend/.env.docker` — backend config overrides
- `DATABASE_URL` is set directly in `docker-compose.yml`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | Change `BACKEND_PORT` in `.env` |
| Port 3000 in use | Change `FRONTEND_PORT` in `.env` |
| Python import errors | Ensure venv is activated: `source backend/venv/bin/activate` |
| `npm ci` fails | Delete `node_modules` and retry |
| Pre-commit not running | Run `pre-commit install --config .pre-commit-config.yaml` |
| Coverage below 85% | Check `pytest --cov-report=html` for uncovered lines |
| Docker build fails | Check `.dockerignore` isn't excluding needed files |
