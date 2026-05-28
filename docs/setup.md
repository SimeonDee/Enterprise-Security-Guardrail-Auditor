# Local Development Setup

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+

## Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Linting & formatting
black app/ tests/
ruff check app/ tests/
mypy app/
```

The API will be available at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

The frontend will be available at http://localhost:5173  
API requests are proxied to the backend via Vite config.

## Docker (Full Stack)

```bash
# From project root
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Sample Test Files

The `samples/` directory contains intentionally vulnerable Terraform files for testing:

- `samples/vulnerable-infra.tf` — 11 vulnerabilities across all rule types
- `samples/multi-service-vulnerable.tf` — 9 vulnerabilities with edge cases

Upload these via the dashboard or API to validate the scanner.

## Seed Data

Built-in guardrails are seeded automatically when the application starts via the lifespan handler. You can also seed them manually through the guardrails API:

```bash
# Create a guardrail via the API
curl -X POST http://localhost:8000/api/v1/guardrails \
  -H "Content-Type: application/json" \
  -d '{"name": "my-rule", "description": "...", "severity": "high", "pattern": "...", "provider": "aws"}'
```
