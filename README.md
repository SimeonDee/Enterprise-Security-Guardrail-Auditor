# Enterprise Security Guardrail Auditor

A scanner that audits infrastructure configuration files (Terraform/CloudFormation) against a security baseline. Flags high-risk patterns—such as public S3 buckets or open SSH ports—and presents a visual **Risk Score** dashboard.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker compose up --build
```

## Docs

- [Architecture](docs/architecture.md)
- [Setup](docs/setup.md)
- [API Design](docs/api-design.md)

## API

Swagger UI: http://localhost:8000/docs

## Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```
