"""Tests for Rule 5: Wildcard IAM Policies."""

from app.scanner.models import ParsedResource
from app.scanner.rules.iam_wildcard import WildcardIAMRule

rule = WildcardIAMRule()


def _make_iam_policy(policy: str) -> ParsedResource:
    return ParsedResource(
        resource_type="aws_iam_policy",
        name="admin",
        attributes={"policy": policy},
        line_start=1,
    )


WILDCARD_ACTION_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}"""

WILDCARD_RESOURCE_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "*"
  }]
}"""

WILDCARD_BOTH_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
  }]
}"""

SAFE_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}"""


def test_detects_wildcard_action():
    findings = rule.evaluate(_make_iam_policy(WILDCARD_ACTION_POLICY), "main.tf")
    assert len(findings) == 1
    assert findings[0].rule_id == "IAM_WILDCARD"
    assert "wildcard" in findings[0].message.lower()


def test_detects_wildcard_resource():
    findings = rule.evaluate(_make_iam_policy(WILDCARD_RESOURCE_POLICY), "main.tf")
    assert len(findings) == 1
    assert "resource" in findings[0].message.lower()


def test_detects_both_wildcards():
    findings = rule.evaluate(_make_iam_policy(WILDCARD_BOTH_POLICY), "main.tf")
    assert len(findings) == 2


def test_passes_safe_policy():
    findings = rule.evaluate(_make_iam_policy(SAFE_POLICY), "main.tf")
    assert len(findings) == 0


def test_passes_no_policy_attr():
    r = ParsedResource(
        resource_type="aws_iam_policy",
        name="empty",
        attributes={},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_passes_non_string_policy():
    r = ParsedResource(
        resource_type="aws_iam_policy",
        name="empty",
        attributes={"policy": 42},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 0


def test_applies_to_role_policy():
    r = ParsedResource(
        resource_type="aws_iam_role_policy",
        name="admin_role",
        attributes={"policy": WILDCARD_ACTION_POLICY},
        line_start=1,
    )
    findings = rule.evaluate(r, "main.tf")
    assert len(findings) == 1
