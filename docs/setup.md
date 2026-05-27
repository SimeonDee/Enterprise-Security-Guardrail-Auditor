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

## Seed Data

To seed built-in guardrails, use the API:

```bash
# The seed script provides default rules — call via the API or run:
python -c "
from app.database import SessionLocal, engine, Base
from app.models.guardrail import Guardrail
from app.services.seed import BUILTIN_RULES

Base.metadata.create_all(bind=engine)
db = SessionLocal()
for rule in BUILTIN_RULES:
    if not db.query(Guardrail).filter(Guardrail.name == rule['name']).first():
        db.add(Guardrail(**rule))
db.commit()
print(f'Seeded {len(BUILTIN_RULES)} guardrails')
"
```
