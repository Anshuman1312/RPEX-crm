from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class HREmployeeCreate(BaseModel):
    user_id: str | None = None
    full_name: str = Field(min_length=2, max_length=200)
    department: str | None = Field(default=None, max_length=64)
    designation: str | None = Field(default=None, max_length=64)
    salary: Decimal = Field(default=0, ge=0)
    incentives: Decimal = Field(default=0, ge=0)
    performance_score: float = Field(default=0, ge=0)


class HRRecordCreate(BaseModel):
    employee_id: str
    record_type: str = Field(max_length=32)
    record_date: date
    status: str = Field(max_length=32)
    details: str | None = None
