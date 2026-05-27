"""Risk scoring engine — converts findings into a 0-100 weighted score."""

from __future__ import annotations

from app.scanner.models import Finding

SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 10.0,
    "high": 7.0,
    "medium": 4.0,
    "low": 1.0,
    "info": 0.5,
}


def calculate_risk_score(findings: list[Finding]) -> float:
    """Calculate a risk score from 0 to 100.

    The score is the weighted sum of findings divided by the
    theoretical maximum (all critical), capped at 100.
    """
    if not findings:
        return 0.0

    total_weight = sum(SEVERITY_WEIGHTS.get(f.severity, 0) for f in findings)
    max_possible = len(findings) * SEVERITY_WEIGHTS["critical"]
    score = (total_weight / max_possible) * 100 if max_possible > 0 else 0.0
    return round(min(score, 100.0), 2)
