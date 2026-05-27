from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scan import Scan
from app.models.violation import Violation
from app.schemas.dashboard import DashboardSummary, ScanBrief

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    total_scans = (await db.execute(select(func.count(Scan.id)))).scalar() or 0
    total_violations = (
        await db.execute(select(func.count(Violation.id)))
    ).scalar() or 0
    avg_score = (await db.execute(select(func.avg(Scan.risk_score)))).scalar() or 0.0

    critical = (
        await db.execute(
            select(func.count(Violation.id)).where(Violation.severity == "critical")
        )
    ).scalar() or 0
    high = (
        await db.execute(
            select(func.count(Violation.id)).where(Violation.severity == "high")
        )
    ).scalar() or 0
    medium = (
        await db.execute(
            select(func.count(Violation.id)).where(Violation.severity == "medium")
        )
    ).scalar() or 0
    low = (
        await db.execute(
            select(func.count(Violation.id)).where(Violation.severity == "low")
        )
    ).scalar() or 0

    result = await db.execute(select(Scan).order_by(Scan.created_at.desc()).limit(10))
    recent = result.scalars().all()

    recent_briefs = [
        ScanBrief(
            id=s.id,
            name=s.name,
            risk_score=s.risk_score,
            total_violations=s.total_violations,
            status=s.status.value,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in recent
    ]

    return DashboardSummary(
        total_scans=total_scans,
        total_violations=total_violations,
        average_risk_score=round(float(avg_score), 2),
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        low_count=low,
        recent_scans=recent_briefs,
    )
