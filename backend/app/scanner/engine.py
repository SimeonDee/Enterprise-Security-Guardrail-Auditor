"""Scan engine — orchestrates parser → rule evaluation → scoring."""

from __future__ import annotations

from app.scanner.models import Finding, ParsedResource, ScanResult
from app.scanner.parser import TerraformParser
from app.scanner.rules.registry import RuleRegistry, build_default_registry
from app.scanner.scoring import calculate_risk_score


class ScanEngine:
    """Top-level orchestrator for security scans."""

    def __init__(self, registry: RuleRegistry | None = None) -> None:
        self._parser = TerraformParser()
        self._registry = registry or build_default_registry()

    def scan(self, content: str, file_name: str = "main.tf") -> ScanResult:
        """Run a full scan on Terraform content."""
        resources = self._parser.parse(content)
        findings = self._evaluate_rules(resources, file_name)
        risk_score = calculate_risk_score(findings)

        return ScanResult(
            file_name=file_name,
            total_resources=len(resources),
            findings=findings,
            risk_score=risk_score,
        )

    def _evaluate_rules(
        self, resources: list[ParsedResource], file_path: str
    ) -> list[Finding]:
        all_findings: list[Finding] = []
        for resource in resources:
            rules = self._registry.get_rules_for(resource.resource_type)
            for rule in rules:
                findings = rule.evaluate(resource, file_path)
                all_findings.extend(findings)
        return all_findings
