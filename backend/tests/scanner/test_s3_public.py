"""Tests for Rule 1: Public S3 Bucket Exposure."""

from app.scanner.models import ParsedResource
from app.scanner.rules.s3_public import PublicS3Rule

rule = PublicS3Rule()


def _make_s3(acl: str) -> ParsedResource:
    return ParsedResource(
        resource_type="aws_s3_bucket",
        name="test_bucket",
        attributes={"acl": acl, "bucket": "my-bucket"},
        line_start=1,
    )


def test_detects_public_read():
    findings = rule.evaluate(_make_s3("public-read"), "main.tf")
    assert len(findings) == 1
    assert findings[0].rule_id == "S3_PUBLIC_ACCESS"
    assert findings[0].severity == "critical"
    assert "public-read" in findings[0].message


def test_detects_public_read_write():
    findings = rule.evaluate(_make_s3("public-read-write"), "main.tf")
    assert len(findings) == 1


def test_detects_authenticated_read():
    findings = rule.evaluate(_make_s3("authenticated-read"), "main.tf")
    assert len(findings) == 1


def test_passes_private_acl():
    findings = rule.evaluate(_make_s3("private"), "main.tf")
    assert len(findings) == 0


def test_passes_no_acl():
    r = ParsedResource(
        resource_type="aws_s3_bucket",
        name="test_bucket",
        attributes={"bucket": "my-bucket"},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_finding_fields():
    findings = rule.evaluate(_make_s3("public-read"), "infra/main.tf")
    f = findings[0]
    assert f.resource_name == "aws_s3_bucket.test_bucket"
    assert f.file_path == "infra/main.tf"
    assert f.line_number == 1
    assert f.remediation != ""
