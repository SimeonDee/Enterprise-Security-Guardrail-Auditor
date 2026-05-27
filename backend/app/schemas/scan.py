from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.scan import FileType, ScanStatus


class ScanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    source_content: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1, max_length=255)


class ScanResponse(BaseModel):
    id: int
    name: str
    status: ScanStatus
    file_type: FileType
    file_name: str
    total_violations: int
    risk_score: float
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ScanDetailResponse(ScanResponse):
    source_content: str
    violations: list["ViolationResponse"] = []


class ViolationResponse(BaseModel):
    id: int
    scan_id: int
    guardrail_id: int
    resource_name: str
    file_path: str
    line_number: int | None = None
    severity: str
    message: str
    remediation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
