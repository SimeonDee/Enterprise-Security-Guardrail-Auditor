import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.guardrail import Guardrail
from app.models.scan import FileType, Scan, ScanStatus
from app.models.violation import Violation
from app.schemas.scan import ScanCreate

# Severity weights for risk score calculation
SEVERITY_WEIGHTS = {
    "critical": 10.0,
    "high": 7.0,
    "medium": 4.0,
    "low": 1.0,
    "info": 0.5,
}


class ScannerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run_scan(self, payload: ScanCreate) -> Scan:
        scan = Scan(
            name=payload.name,
            file_type=payload.file_type,
            source_content=payload.source_content,
            file_name=payload.file_name,
            status=ScanStatus.RUNNING,
        )
        self.db.add(scan)
        await self.db.flush()

        stmt = select(Guardrail).where(Guardrail.enabled == True)  # noqa: E712
        result = await self.db.execute(stmt)
        guardrails = result.scalars().all()

        violations: list[Violation] = []
        for guardrail in guardrails:
            found = self._check_pattern(
                content=payload.source_content,
                pattern=guardrail.pattern,
                guardrail=guardrail,
                scan=scan,
                file_name=payload.file_name,
            )
            violations.extend(found)

        self.db.add_all(violations)

        scan.total_violations = len(violations)
        scan.risk_score = self._calculate_risk_score(violations)
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.now(timezone.utc)

        await self.db.commit()

        # Re-fetch with violations eagerly loaded
        stmt = (
            select(Scan)
            .where(Scan.id == scan.id)
            .options(selectinload(Scan.violations))
        )
        result = await self.db.execute(stmt)
        return result.scalars().one()

    def _check_pattern(
        self,
        content: str,
        pattern: str,
        guardrail: Guardrail,
        scan: Scan,
        file_name: str,
    ) -> list[Violation]:
        violations = []
        lines = content.splitlines()

        try:
            compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error:
            return violations

        for line_num, line in enumerate(lines, start=1):
            if compiled.search(line):
                resource_name = self._extract_resource_name(lines, line_num)
                violation = Violation(
                    scan_id=scan.id,
                    guardrail_id=guardrail.id,
                    resource_name=resource_name,
                    file_path=file_name,
                    line_number=line_num,
                    severity=guardrail.severity.value,
                    message=f"{guardrail.name}: {guardrail.description}",
                    remediation=guardrail.remediation,
                )
                violations.append(violation)

        return violations

    def _extract_resource_name(self, lines: list[str], current_line: int) -> str:
        for i in range(current_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("resource ") or line.startswith("Resource"):
                parts = line.split('"')
                if len(parts) >= 4:
                    return f"{parts[1]}.{parts[3]}"
                return line
        return f"line-{current_line}"

    def _calculate_risk_score(self, violations: list[Violation]) -> float:
        if not violations:
            return 0.0
        total_weight = sum(SEVERITY_WEIGHTS.get(v.severity, 0) for v in violations)
        max_possible = len(violations) * SEVERITY_WEIGHTS["critical"]
        score = (total_weight / max_possible) * 100 if max_possible > 0 else 0.0
        return round(min(score, 100.0), 2)
