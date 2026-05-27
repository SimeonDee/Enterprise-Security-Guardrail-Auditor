"""Rule 5: Detect wildcard IAM policies (* permissions)."""

from __future__ import annotations

import re

from app.scanner.models import Finding, ParsedResource
from app.scanner.rules.base import BaseRule

_WILDCARD_ACTION_RE = re.compile(r'"Action"\s*:\s*"\*"', re.IGNORECASE)
_WILDCARD_RESOURCE_RE = re.compile(r'"Resource"\s*:\s*"\*"', re.IGNORECASE)


class WildcardIAMRule(BaseRule):
    rule_id = "IAM_WILDCARD"
    name = "Wildcard IAM Policy"
    description = (
        "IAM policy grants wildcard (*) actions or applies to all resources, "
        "violating the principle of least privilege."
    )
    severity = "critical"
    resource_types = [
        "aws_iam_policy",
        "aws_iam_role_policy",
        "aws_iam_user_policy",
        "aws_iam_group_policy",
    ]
    remediation = (
        "Replace wildcard (*) actions and resources with specific, "
        "least-privilege permissions scoped to the required services."
    )

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings: list[Finding] = []

        policy_doc = resource.attributes.get("policy")
        if not isinstance(policy_doc, str):
            return findings

        # Check raw string for wildcard patterns
        if _WILDCARD_ACTION_RE.search(policy_doc):
            findings.append(
                self._make_finding(
                    resource,
                    file_path,
                    message=(
                        f"IAM policy '{resource.full_name}' grants wildcard (*) "
                        f"actions, providing overly permissive access."
                    ),
                )
            )

        if _WILDCARD_RESOURCE_RE.search(policy_doc):
            findings.append(
                self._make_finding(
                    resource,
                    file_path,
                    message=(
                        f"IAM policy '{resource.full_name}' applies to all "
                        f"resources (*), violating least-privilege."
                    ),
                )
            )

        return findings
