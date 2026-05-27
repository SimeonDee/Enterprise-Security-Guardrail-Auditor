"""Rule 4: Detect disabled encryption on storage and database resources."""

from __future__ import annotations

from app.scanner.models import Finding, ParsedResource
from app.scanner.rules.base import BaseRule

_ENCRYPTION_CHECKS: dict[str, list[tuple[str, str]]] = {
    "aws_db_instance": [
        ("storage_encrypted", "RDS instance storage encryption is disabled."),
    ],
    "aws_rds_cluster": [
        ("storage_encrypted", "RDS cluster storage encryption is disabled."),
    ],
    "aws_ebs_volume": [
        ("encrypted", "EBS volume encryption is disabled."),
    ],
    "aws_s3_bucket": [
        # Some legacy configs set server_side_encryption directly
    ],
}


class DisabledEncryptionRule(BaseRule):
    rule_id = "ENCRYPTION_DISABLED"
    name = "Disabled Encryption"
    description = "Storage or database resource does not have encryption enabled."
    severity = "high"
    resource_types = list(_ENCRYPTION_CHECKS.keys())
    remediation = (
        "Enable encryption at rest by setting the appropriate encryption "
        "attribute to true (e.g. storage_encrypted = true, encrypted = true)."
    )

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings: list[Finding] = []

        checks = _ENCRYPTION_CHECKS.get(resource.resource_type, [])
        for attr_name, message in checks:
            value = resource.attributes.get(attr_name)
            # Flag when explicitly set to false
            if value is False:
                findings.append(
                    self._make_finding(
                        resource,
                        file_path,
                        message=f"{resource.full_name}: {message}",
                    )
                )

        return findings
