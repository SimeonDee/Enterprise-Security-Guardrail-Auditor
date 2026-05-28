# API Reference

## Overview

| Property | Value |
|----------|-------|
| Base URL | `/api/v1` |
| Format | JSON |
| Auth | None (MVP) |
| OpenAPI | `GET /docs` (Swagger UI) |
| Redoc | `GET /redoc` |

All responses use JSON. Errors follow the format:

```json
{ "error": "ERROR_CODE", "detail": "Human-readable message" }
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No content (successful delete) |
| `404` | Resource not found |
| `409` | Conflict (duplicate) |
| `422` | Validation error |
| `500` | Internal server error |

### Pagination

List endpoints return paginated responses:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## Health

### `GET /health`

Returns service health status.

**Response** `200`

```json
{ "status": "healthy", "version": "0.1.0" }
```

---

## Scans

### `GET /scans`

List scans with pagination and optional filters.

**Query Parameters**

| Param       | Type   | Default | Description                              |
| ----------- | ------ | ------- | ---------------------------------------- |
| `page`      | int    | 1       | Page number (≥ 1)                        |
| `page_size` | int    | 20      | Items per page (1–100)                   |
| `status`    | string | —       | Filter: `pending`, `running`, `completed`, `failed` |
| `file_type` | string | —       | Filter: `terraform`, `cloudformation`    |

**Response** `200`

```json
{
  "items": [
    {
      "id": 1,
      "name": "My Scan",
      "status": "completed",
      "file_type": "terraform",
      "file_name": "main.tf",
      "total_violations": 3,
      "risk_score": 72.5,
      "created_at": "2025-01-01T00:00:00",
      "completed_at": "2025-01-01T00:00:01"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### `POST /scans`

Create a scan from a JSON payload.

**Request Body**

```json
{
  "name": "My Scan",
  "file_type": "terraform",
  "source_content": "resource \"aws_s3_bucket\" \"b\" { ... }",
  "file_name": "main.tf"
}
```

**Response** `201` — `ScanDetailResponse` (see GET /scans/{id})

### `POST /scans/upload`

Upload a `.tf` file and run a scan.

**Query Parameters**

| Param  | Type   | Required | Description |
| ------ | ------ | -------- | ----------- |
| `name` | string | yes      | Scan name   |

**Request Body** — `multipart/form-data`

| Field  | Type | Description               |
| ------ | ---- | ------------------------- |
| `file` | file | A `.tf` Terraform file    |

**Response** `201` — `ScanDetailResponse`

**Errors**

- `422` — File is not `.tf`, is empty, or name is missing.

### `GET /scans/{scan_id}`

Get scan details including violations.

**Response** `200`

```json
{
  "id": 1,
  "name": "My Scan",
  "status": "completed",
  "file_type": "terraform",
  "file_name": "main.tf",
  "total_violations": 2,
  "risk_score": 55.0,
  "created_at": "2025-01-01T00:00:00",
  "completed_at": "2025-01-01T00:00:01",
  "source_content": "resource ...",
  "violations": [
    {
      "id": 1,
      "scan_id": 1,
      "guardrail_id": null,
      "resource_name": "aws_s3_bucket.data",
      "file_path": "main.tf",
      "line_number": 2,
      "severity": "critical",
      "message": "S3 bucket has public ACL",
      "remediation": "Set ACL to private",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

**Errors**

- `404` — Scan not found.

### `DELETE /scans/{scan_id}`

Delete a scan and its violations.

**Response** `204` — No content.

**Errors**

- `404` — Scan not found.

---

## Guardrails

### `GET /guardrails`

List all guardrails. Supports `?enabled=true` filter.

**Response** `200` — Array of `GuardrailResponse`.

### `POST /guardrails`

Create a guardrail rule.

**Request Body**

```json
{
  "name": "Public S3 Bucket ACL",
  "description": "S3 bucket has a public ACL",
  "severity": "critical",
  "provider": "aws",
  "resource_type": "aws_s3_bucket",
  "pattern": "acl\\s*=\\s*\"(public-read|public-read-write)\"",
  "remediation": "Set ACL to private."
}
```

**Response** `201` — `GuardrailResponse`.

### `GET /guardrails/{guardrail_id}`

Get a single guardrail by ID.

**Errors** — `404` if not found.

### `PATCH /guardrails/{guardrail_id}`

Partially update a guardrail. All fields optional.

### `DELETE /guardrails/{guardrail_id}`

Delete a guardrail. **Response** `204`.

---

## Dashboard

### `GET /dashboard/summary`

Aggregated statistics for the dashboard.

**Response** `200`

```json
{
  "total_scans": 10,
  "total_violations": 25,
  "average_risk_score": 42.5,
  "critical_count": 8,
  "high_count": 10,
  "medium_count": 5,
  "low_count": 2,
  "recent_scans": [
    {
      "id": 1,
      "name": "Latest Scan",
      "risk_score": 72.5,
      "total_violations": 3,
      "status": "completed",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```
