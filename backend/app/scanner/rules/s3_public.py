"""Rule 1: Detect publicly exposed S3 buckets."""

from __future__ import annotations

from app.scanner.models import Finding, ParsedResource
from app.scanner.rules.base import BaseRule

_PUBLIC_ACLS = {"public-read", "public-read-write", "authenticated-read"}


class PublicS3Rule(BaseRule):
    rule_id = "S3_PUBLIC_ACCESS"
    name = "Public S3 Bucket Exposure"
    description = (
        "S3 bucket is configured with a public ACL, "
        "potentially exposing sensitive data to the internet."
    )
    severity = "critical"
    resource_types = ["aws_s3_bucket"]
    remediation = (
        "Set the ACL to 'private' and use bucket policies "
        "with least-privilege access controls."
    )

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings: list[Finding] = []

        acl = resource.attributes.get("acl")
        if isinstance(acl, str) and acl in _PUBLIC_ACLS:
            findings.append(
                self._make_finding(
                    resource,
                    file_path,
                    message=(
                        f"S3 bucket '{resource.full_name}' has public ACL "
                        f"'{acl}'. Data may be exposed to the internet."
                    ),
                )
            )

        return findings
