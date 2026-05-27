"""Rule 3: Detect publicly accessible database instances."""

from __future__ import annotations

from app.scanner.models import Finding, ParsedResource
from app.scanner.rules.base import BaseRule


class PublicDatabaseRule(BaseRule):
    rule_id = "DB_PUBLIC_ACCESS"
    name = "Public Database Exposure"
    description = "Database instance is publicly accessible from the internet."
    severity = "critical"
    resource_types = ["aws_db_instance", "aws_rds_cluster"]
    remediation = (
        "Set publicly_accessible = false and place the database "
        "inside a private subnet with appropriate security groups."
    )

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings: list[Finding] = []

        publicly_accessible = resource.attributes.get("publicly_accessible")
        if publicly_accessible is True:
            findings.append(
                self._make_finding(
                    resource,
                    file_path,
                    message=(
                        f"Database '{resource.full_name}' is publicly accessible. "
                        f"This exposes it directly to the internet."
                    ),
                )
            )

        return findings
