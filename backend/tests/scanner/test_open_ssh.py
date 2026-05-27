"""Tests for Rule 2: Open SSH."""

from app.scanner.models import ParsedResource
from app.scanner.rules.open_ssh import OpenSSHRule

rule = OpenSSHRule()


def _make_sg_with_ingress(
    from_port: int = 22,
    to_port: int = 22,
    cidr: list[str] | str = "0.0.0.0/0",
) -> ParsedResource:
    cidr_val = cidr if isinstance(cidr, list) else [cidr]
    return ParsedResource(
        resource_type="aws_security_group",
        name="allow_ssh",
        blocks={
            "ingress": [
                {
                    "from_port": from_port,
                    "to_port": to_port,
                    "protocol": "tcp",
                    "cidr_blocks": cidr_val,
                }
            ]
        },
        line_start=1,
    )


def test_detects_open_ssh():
    findings = rule.evaluate(_make_sg_with_ingress(), "main.tf")
    assert len(findings) == 1
    assert findings[0].rule_id == "SG_OPEN_SSH"
    assert findings[0].severity == "critical"


def test_detects_ssh_in_port_range():
    findings = rule.evaluate(
        _make_sg_with_ingress(from_port=0, to_port=65535), "main.tf"
    )
    assert len(findings) == 1


def test_passes_restricted_cidr():
    findings = rule.evaluate(_make_sg_with_ingress(cidr=["10.0.0.0/8"]), "main.tf")
    assert len(findings) == 0


def test_passes_non_ssh_port():
    findings = rule.evaluate(
        _make_sg_with_ingress(from_port=443, to_port=443), "main.tf"
    )
    assert len(findings) == 0


def test_passes_no_ingress():
    r = ParsedResource(
        resource_type="aws_security_group",
        name="empty_sg",
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_detects_sg_rule_resource():
    r = ParsedResource(
        resource_type="aws_security_group_rule",
        name="ssh_rule",
        attributes={
            "type": "ingress",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1


def test_passes_sg_rule_restricted():
    r = ParsedResource(
        resource_type="aws_security_group_rule",
        name="ssh_rule",
        attributes={
            "type": "ingress",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["10.0.0.0/8"],
        },
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0
