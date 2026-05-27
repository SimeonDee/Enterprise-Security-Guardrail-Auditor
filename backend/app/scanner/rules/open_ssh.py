"""Rule 2: Detect security groups that allow SSH from 0.0.0.0/0."""

from __future__ import annotations

from app.scanner.models import Finding, ParsedResource
from app.scanner.rules.base import BaseRule


class OpenSSHRule(BaseRule):
    rule_id = "SG_OPEN_SSH"
    name = "Security Group Allows Open SSH"
    description = "Security group allows SSH (port 22) from any IP address (0.0.0.0/0)."
    severity = "critical"
    resource_types = ["aws_security_group", "aws_security_group_rule"]
    remediation = (
        "Restrict SSH access to specific trusted CIDR blocks "
        "or use a bastion host / SSM Session Manager."
    )

    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        findings: list[Finding] = []

        # Check ingress blocks in aws_security_group
        for ingress in resource.blocks.get("ingress", []):
            if self._is_open_ssh(ingress):
                findings.append(
                    self._make_finding(
                        resource,
                        file_path,
                        message=(
                            f"Security group '{resource.full_name}' allows "
                            f"SSH (port 22) from 0.0.0.0/0."
                        ),
                    )
                )

        # Check top-level attrs for aws_security_group_rule
        if resource.resource_type == "aws_security_group_rule":
            if self._is_open_ssh(resource.attributes):
                findings.append(
                    self._make_finding(
                        resource,
                        file_path,
                        message=(
                            f"Security group rule '{resource.full_name}' allows "
                            f"SSH (port 22) from 0.0.0.0/0."
                        ),
                    )
                )

        return findings

    def _is_open_ssh(self, attrs: dict) -> bool:
        from_port = attrs.get("from_port")
        to_port = attrs.get("to_port")
        cidr = attrs.get("cidr_blocks")

        port_match = False
        if from_port is not None and to_port is not None:
            try:
                port_match = int(from_port) <= 22 <= int(to_port)
            except (TypeError, ValueError):
                pass
        elif from_port is not None:
            try:
                port_match = int(from_port) == 22
            except (TypeError, ValueError):
                pass

        if not port_match:
            return False

        if isinstance(cidr, list):
            return "0.0.0.0/0" in cidr
        if isinstance(cidr, str):
            return cidr == "0.0.0.0/0"

        return False
