from typing import Any

from pydantic import BaseModel, Field


class ApprovalRequestCreate(BaseModel):
    module: str = Field(min_length=2, max_length=64)
    entity_type: str = Field(min_length=2, max_length=64)
    entity_id: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=2, max_length=64)
    approver_id: str | None = None
    reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecision(BaseModel):
    status: str = Field(pattern="^(APPROVED|REJECTED)$")
    notes: str | None = None
