from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.guardrail import Provider, Severity


class GuardrailBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    severity: Severity
    provider: Provider
    resource_type: str = Field(..., min_length=1, max_length=100)
    pattern: str = Field(..., min_length=1)
    remediation: str = Field(..., min_length=1)
    enabled: bool = True


class GuardrailCreate(GuardrailBase):
    pass


class GuardrailUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    severity: Severity | None = None
    provider: Provider | None = None
    resource_type: str | None = Field(None, min_length=1, max_length=100)
    pattern: str | None = Field(None, min_length=1)
    remediation: str | None = Field(None, min_length=1)
    enabled: bool | None = None


class GuardrailResponse(GuardrailBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
