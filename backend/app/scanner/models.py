"""Data models for the scanner engine — fully decoupled from the ORM layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParsedResource:
    """A single Terraform resource block extracted by the parser."""

    resource_type: str
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    blocks: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    line_start: int = 0
    line_end: int = 0
    raw_block: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.resource_type}.{self.name}"


@dataclass(frozen=True)
class Finding:
    """A single security finding produced by a rule."""

    rule_id: str
    severity: str
    resource_type: str
    resource_name: str
    message: str
    remediation: str
    file_path: str
    line_number: int
    context: str = ""


@dataclass
class ScanResult:
    """Aggregated result of a full scan."""

    file_name: str
    total_resources: int
    findings: list[Finding] = field(default_factory=list)
    risk_score: float = 0.0

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def severity_breakdown(self) -> dict[str, int]:
        breakdown: dict[str, int] = {}
        for f in self.findings:
            breakdown[f.severity] = breakdown.get(f.severity, 0) + 1
        return breakdown
