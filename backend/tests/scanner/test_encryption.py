"""Tests for Rule 4: Disabled Encryption."""

from app.scanner.models import ParsedResource
from app.scanner.rules.encryption import DisabledEncryptionRule

rule = DisabledEncryptionRule()


def test_detects_unencrypted_rds():
    r = ParsedResource(
        resource_type="aws_db_instance",
        name="main_db",
        attributes={"storage_encrypted": False},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1
    assert findings[0].rule_id == "ENCRYPTION_DISABLED"
    assert findings[0].severity == "high"


def test_passes_encrypted_rds():
    r = ParsedResource(
        resource_type="aws_db_instance",
        name="main_db",
        attributes={"storage_encrypted": True},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_detects_unencrypted_ebs():
    r = ParsedResource(
        resource_type="aws_ebs_volume",
        name="data_vol",
        attributes={"encrypted": False},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1


def test_passes_encrypted_ebs():
    r = ParsedResource(
        resource_type="aws_ebs_volume",
        name="data_vol",
        attributes={"encrypted": True},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_passes_no_encryption_attr():
    r = ParsedResource(
        resource_type="aws_db_instance",
        name="main_db",
        attributes={"engine": "postgres"},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_detects_unencrypted_rds_cluster():
    r = ParsedResource(
        resource_type="aws_rds_cluster",
        name="aurora",
        attributes={"storage_encrypted": False},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1
