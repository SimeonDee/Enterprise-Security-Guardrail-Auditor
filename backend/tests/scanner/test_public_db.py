"""Tests for Rule 3: Public Database Exposure."""

from app.scanner.models import ParsedResource
from app.scanner.rules.public_db import PublicDatabaseRule

rule = PublicDatabaseRule()


def _make_rds(publicly_accessible: bool) -> ParsedResource:
    return ParsedResource(
        resource_type="aws_db_instance",
        name="main_db",
        attributes={
            "engine": "postgres",
            "publicly_accessible": publicly_accessible,
        },
        line_start=1,
    )


def test_detects_public_rds():
    findings = rule.evaluate(_make_rds(True), "main.tf")
    assert len(findings) == 1
    assert findings[0].rule_id == "DB_PUBLIC_ACCESS"
    assert findings[0].severity == "critical"


def test_passes_private_rds():
    findings = rule.evaluate(_make_rds(False), "main.tf")
    assert len(findings) == 0


def test_passes_no_attribute():
    r = ParsedResource(
        resource_type="aws_db_instance",
        name="main_db",
        attributes={"engine": "mysql"},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_detects_public_rds_cluster():
    r = ParsedResource(
        resource_type="aws_rds_cluster",
        name="aurora",
        attributes={"publicly_accessible": True},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1
