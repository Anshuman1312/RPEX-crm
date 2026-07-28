from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class HREmployeeCreate(BaseModel):
    user_id: str | None = None
    full_name: str = Field(min_length=2, max_length=200)
    department: str | None = Field(default=None, max_length=100)
    designation: str | None = Field(default=None, max_length=100)
    salary: Decimal | None = Field(default=None, ge=0)
    incentives: Decimal | None = Field(default=None, ge=0)
    performance_score: Decimal | None = Field(default=None, ge=0, le=100)


class HRRecordCreate(BaseModel):
    employee_id: str
    record_type: str = Field(min_length=1, max_length=64)
    record_date: date
    status: str = Field(default="ACTIVE", max_length=32)
    details: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
