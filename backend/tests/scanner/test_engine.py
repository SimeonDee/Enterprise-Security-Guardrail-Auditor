"""Tests for the scan engine orchestrator."""

from app.scanner.engine import ScanEngine
from app.scanner.rules.registry import RuleRegistry, build_default_registry

INSECURE_TF = """
resource "aws_s3_bucket" "data" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}

resource "aws_security_group" "allow_ssh" {
  name = "allow_ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "main" {
  engine              = "postgres"
  publicly_accessible = true
  storage_encrypted   = false
}

resource "aws_iam_policy" "admin" {
  name   = "admin-policy"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
  }]
}
EOF
}
"""

SECURE_TF = """
resource "aws_s3_bucket" "data" {
  bucket = "my-private-bucket"
  acl    = "private"
}

resource "aws_security_group" "restricted" {
  name = "restricted-sg"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}

resource "aws_db_instance" "main" {
  engine              = "postgres"
  publicly_accessible = false
  storage_encrypted   = true
}
"""


def test_engine_detects_insecure_resources():
    engine = ScanEngine()
    result = engine.scan(INSECURE_TF, "main.tf")

    assert result.total_resources == 4
    assert result.total_findings >= 4  # S3 + SSH + public DB + encryption + IAM
    assert result.risk_score > 0
    assert result.file_name == "main.tf"

    rule_ids = {f.rule_id for f in result.findings}
    assert "S3_PUBLIC_ACCESS" in rule_ids
    assert "SG_OPEN_SSH" in rule_ids
    assert "DB_PUBLIC_ACCESS" in rule_ids
    assert "ENCRYPTION_DISABLED" in rule_ids
    assert "IAM_WILDCARD" in rule_ids


def test_engine_passes_secure_resources():
    engine = ScanEngine()
    result = engine.scan(SECURE_TF, "main.tf")

    assert result.total_resources == 3
    assert result.total_findings == 0
    assert result.risk_score == 0.0


def test_engine_empty_content():
    engine = ScanEngine()
    result = engine.scan("", "empty.tf")
    assert result.total_resources == 0
    assert result.total_findings == 0
    assert result.risk_score == 0.0


def test_engine_severity_breakdown():
    engine = ScanEngine()
    result = engine.scan(INSECURE_TF, "main.tf")
    breakdown = result.severity_breakdown
    assert "critical" in breakdown
    assert breakdown["critical"] >= 3  # S3, SSH, DB, IAM


def test_engine_custom_registry():
    registry = RuleRegistry()
    engine = ScanEngine(registry=registry)
    result = engine.scan(INSECURE_TF, "main.tf")
    # No rules registered → no findings
    assert result.total_findings == 0


def test_default_registry_has_all_rules():
    registry = build_default_registry()
    assert len(registry.rules) == 5


def test_registry_get_rules_for_type():
    registry = build_default_registry()
    s3_rules = registry.get_rules_for("aws_s3_bucket")
    assert len(s3_rules) >= 1
    assert any(r.rule_id == "S3_PUBLIC_ACCESS" for r in s3_rules)


def test_registry_no_rules_for_unknown_type():
    registry = build_default_registry()
    rules = registry.get_rules_for("aws_unknown_resource")
    assert len(rules) == 0
