"""Tests for the scoring engine."""

from app.scanner.models import Finding
from app.scanner.scoring import SEVERITY_WEIGHTS, calculate_risk_score


def _finding(severity: str) -> Finding:
    return Finding(
        rule_id="TEST",
        severity=severity,
        resource_type="aws_test",
        resource_name="aws_test.item",
        message="test",
        remediation="fix it",
        file_path="main.tf",
        line_number=1,
    )


def test_empty_findings():
    assert calculate_risk_score([]) == 0.0


def test_all_critical():
    findings = [_finding("critical") for _ in range(3)]
    assert calculate_risk_score(findings) == 100.0


def test_all_low():
    findings = [_finding("low") for _ in range(3)]
    score = calculate_risk_score(findings)
    expected = (1.0 / 10.0) * 100
    assert score == expected


def test_mixed_severity():
    findings = [_finding("critical"), _finding("low")]
    score = calculate_risk_score(findings)
    expected = round(((10.0 + 1.0) / (2 * 10.0)) * 100, 2)
    assert score == expected


def test_capped_at_100():
    # Even with extreme inputs, should not exceed 100
    findings = [_finding("critical") for _ in range(100)]
    assert calculate_risk_score(findings) == 100.0


def test_severity_weights_correct():
    assert SEVERITY_WEIGHTS["critical"] == 10.0
    assert SEVERITY_WEIGHTS["high"] == 7.0
    assert SEVERITY_WEIGHTS["medium"] == 4.0
    assert SEVERITY_WEIGHTS["low"] == 1.0
    assert SEVERITY_WEIGHTS["info"] == 0.5
