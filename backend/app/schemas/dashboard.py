from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_scans: int
    total_violations: int
    average_risk_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    recent_scans: list["ScanBrief"]


class ScanBrief(BaseModel):
    id: int
    name: str
    risk_score: float
    total_violations: int
    status: str
    created_at: str


class SeverityBreakdown(BaseModel):
    severity: str
    count: int


class HealthResponse(BaseModel):
    status: str
    version: str
