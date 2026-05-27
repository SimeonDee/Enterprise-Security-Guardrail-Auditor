# Security Rules Reference

This document describes the built-in security rules in the Enterprise Security Guardrail Auditor scanner engine.

---

## Architecture

The scanner engine uses a layered architecture:

```
Terraform Content
      │
      ▼
┌──────────────┐
│  TF Parser   │  Extracts resource blocks, attributes, nested blocks
└──────┬───────┘
       │  list[ParsedResource]
       ▼
┌──────────────┐
│ Rule Engine   │  Evaluates each resource against applicable rules
└──────┬───────┘
       │  list[Finding]
       ▼
┌──────────────┐
│ Risk Scorer   │  Calculates weighted 0–100 score
└──────┬───────┘
       │  ScanResult
       ▼
┌──────────────┐
│  Orchestrator │  ScanEngine ties all layers together
└──────────────┘
```

### Key Data Models

| Model | Purpose |
|---|---|
| `ParsedResource` | Represents a single Terraform resource with type, name, attributes, and nested blocks |
| `Finding` | A single security issue: rule_id, severity, resource, message, remediation, line number |
| `ScanResult` | Aggregated output: file name, resource count, findings list, risk score |

---

## Risk Scoring

The risk score is calculated as a **weighted percentage** on a 0–100 scale:

| Severity | Weight |
|----------|--------|
| Critical | 10.0   |
| High     | 7.0    |
| Medium   | 4.0    |
| Low      | 1.0    |
| Info     | 0.5    |

**Formula:**
```
score = (sum_of_weights / (num_findings × 10)) × 100
```

A score of **100** means all findings are critical. A score of **0** means no findings.

---

## Built-in Rules

### Rule 1: Public S3 Bucket Exposure

| Field | Value |
|---|---|
| **Rule ID** | `S3_PUBLIC_ACCESS` |
| **Severity** | Critical |
| **Resource Types** | `aws_s3_bucket` |
| **Detection** | Checks `acl` attribute for: `public-read`, `public-read-write`, `authenticated-read` |
| **Remediation** | Set the ACL to `private` and use bucket policies with least-privilege access controls. |

**Example (flagged):**
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-bucket"
  acl    = "public-read"  # ← FLAGGED
}
```

---

### Rule 2: Security Group Allows Open SSH

| Field | Value |
|---|---|
| **Rule ID** | `SG_OPEN_SSH` |
| **Severity** | Critical |
| **Resource Types** | `aws_security_group`, `aws_security_group_rule` |
| **Detection** | Checks ingress blocks for port 22 with CIDR `0.0.0.0/0` |
| **Remediation** | Restrict SSH access to specific trusted CIDR blocks or use a bastion host / SSM Session Manager. |

**Example (flagged):**
```hcl
resource "aws_security_group" "allow_ssh" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ← FLAGGED
  }
}
```

---

### Rule 3: Public Database Exposure

| Field | Value |
|---|---|
| **Rule ID** | `DB_PUBLIC_ACCESS` |
| **Severity** | Critical |
| **Resource Types** | `aws_db_instance`, `aws_rds_cluster` |
| **Detection** | Checks `publicly_accessible = true` |
| **Remediation** | Set `publicly_accessible = false` and place the database inside a private subnet with appropriate security groups. |

**Example (flagged):**
```hcl
resource "aws_db_instance" "main" {
  engine              = "postgres"
  publicly_accessible = true  # ← FLAGGED
}
```

---

### Rule 4: Disabled Encryption

| Field | Value |
|---|---|
| **Rule ID** | `ENCRYPTION_DISABLED` |
| **Severity** | High |
| **Resource Types** | `aws_db_instance`, `aws_rds_cluster`, `aws_ebs_volume`, `aws_s3_bucket` |
| **Detection** | Checks `storage_encrypted = false` (RDS) or `encrypted = false` (EBS) |
| **Remediation** | Enable encryption at rest by setting the appropriate encryption attribute to `true`. |

**Example (flagged):**
```hcl
resource "aws_db_instance" "main" {
  storage_encrypted = false  # ← FLAGGED
}
```

---

### Rule 5: Wildcard IAM Policy

| Field | Value |
|---|---|
| **Rule ID** | `IAM_WILDCARD` |
| **Severity** | Critical |
| **Resource Types** | `aws_iam_policy`, `aws_iam_role_policy`, `aws_iam_user_policy`, `aws_iam_group_policy` |
| **Detection** | Checks policy document for `"Action": "*"` or `"Resource": "*"` |
| **Remediation** | Replace wildcard (`*`) actions and resources with specific, least-privilege permissions. |

**Example (flagged):**
```hcl
resource "aws_iam_policy" "admin" {
  policy = <<EOF
{
  "Statement": [{
    "Action": "*",      # ← FLAGGED
    "Resource": "*"     # ← FLAGGED
  }]
}
EOF
}
```

---

## Adding Custom Rules

1. Create a new file in `app/scanner/rules/`
2. Subclass `BaseRule` and implement `evaluate()`
3. Register the rule in `registry.py` → `build_default_registry()`

```python
from app.scanner.rules.base import BaseRule
from app.scanner.models import Finding, ParsedResource

class MyCustomRule(BaseRule):
    rule_id = "CUSTOM_CHECK"
    name = "My Custom Check"
    description = "Checks for something specific."
    severity = "high"
    resource_types = ["aws_some_resource"]
    remediation = "Fix by doing X."

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings = []
        if resource.attributes.get("bad_thing") is True:
            findings.append(self._make_finding(
                resource, file_path,
                message="Bad thing detected!"
            ))
        return findings
```
