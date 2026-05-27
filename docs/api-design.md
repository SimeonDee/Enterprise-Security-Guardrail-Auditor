# API Design — v1

Base URL: `/api/v1`

## Health

| Method | Endpoint      | Description       |
|--------|---------------|-------------------|
| GET    | `/health/`    | Health check      |

**Response:**
```json
{ "status": "healthy", "version": "0.1.0" }
```

---

## Guardrails

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| GET    | `/guardrails/`        | List all guardrails       |
| POST   | `/guardrails/`        | Create a guardrail        |
| GET    | `/guardrails/{id}`    | Get a specific guardrail  |
| PATCH  | `/guardrails/{id}`    | Update a guardrail        |
| DELETE | `/guardrails/{id}`    | Delete a guardrail        |

**Query Params (GET list):** `skip`, `limit`, `enabled`

**Create Payload:**
```json
{
  "name": "Public S3 Bucket ACL",
  "description": "S3 bucket has a public ACL",
  "severity": "critical",
  "provider": "aws",
  "resource_type": "aws_s3_bucket",
  "pattern": "acl\\s*=\\s*\"(public-read|public-read-write)\"",
  "remediation": "Set ACL to private",
  "enabled": true
}
```

**Severity Enum:** `critical | high | medium | low | info`  
**Provider Enum:** `aws | azure | gcp | generic`

---

## Scans

| Method | Endpoint         | Description             |
|--------|------------------|-------------------------|
| GET    | `/scans/`        | List all scans          |
| POST   | `/scans/`        | Create & run a scan     |
| GET    | `/scans/{id}`    | Get scan with violations|
| DELETE | `/scans/{id}`    | Delete a scan           |

**Create Payload:**
```json
{
  "name": "Production audit",
  "file_type": "terraform",
  "source_content": "resource \"aws_s3_bucket\" ...",
  "file_name": "main.tf"
}
```

**file_type Enum:** `terraform | cloudformation`

**Detail Response** includes `violations[]` array and `source_content`.

---

## Dashboard

| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| GET    | `/dashboard/summary`  | Aggregated statistics |

**Response:**
```json
{
  "total_scans": 10,
  "total_violations": 42,
  "average_risk_score": 65.3,
  "critical_count": 8,
  "high_count": 12,
  "medium_count": 15,
  "low_count": 7,
  "recent_scans": [...]
}
```

---

## Error Responses

All errors follow a structured format:
```json
{
  "error": "NOT_FOUND",
  "detail": "Guardrail with id 42 not found"
}
```

| Code | Error Code         | Meaning                |
|------|--------------------|------------------------|
| 404  | `NOT_FOUND`        | Resource not found     |
| 409  | `CONFLICT`         | Duplicate resource     |
| 422  | `VALIDATION_ERROR` | Validation error       |
| 500  | `INTERNAL_ERROR`   | Unexpected server error|

All responses include an `X-Request-ID` header for request tracing.

---

## Infrastructure Notes

- **Async**: All endpoints use async SQLAlchemy with aiosqlite
- **Migrations**: Alembic configured for async (aiosqlite)
- **Caching**: Redis cache abstraction available (NullCache default)
- **Logging**: Structured request/response logging with timing
