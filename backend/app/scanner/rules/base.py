"""Abstract base class for all security rules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.scanner.models import Finding, ParsedResource


class BaseRule(ABC):
    """Every security rule must subclass BaseRule and implement evaluate()."""

    rule_id: str
    name: str
    description: str
    severity: str  # critical | high | medium | low | info
    resource_types: list[str]  # e.g. ["aws_s3_bucket"]
    remediation: str

    @abstractmethod
    def evaluate(self, resource: ParsedResource, file_path: str) -> list[Finding]:
        """Evaluate a parsed resource and return any findings."""
        ...

    def _make_finding(
        self,
        resource: ParsedResource,
        file_path: str,
        message: str,
        line_number: int | None = None,
        context: str = "",
    ) -> Finding:
        """Helper to build a Finding with common fields pre-filled."""
        return Finding(
            rule_id=self.rule_id,
            severity=self.severity,
            resource_type=resource.resource_type,
            resource_name=resource.full_name,
            message=message,
            remediation=self.remediation,
            file_path=file_path,
            line_number=line_number or resource.line_start,
            context=context,
        )
