from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class SiteVisitCreate(BaseModel):
    visit_date: date
    visit_time: datetime | None = None
    customer_name: str = Field(min_length=1, max_length=200)
    sales_executive: str | None = Field(default=None, max_length=200)
    pickup_required: bool = False
    vehicle_assigned: str | None = Field(default=None, max_length=100)
    driver: str | None = Field(default=None, max_length=100)
    attendance: str = Field(default="PENDING", max_length=32)
    feedback: str | None = None
    outcome: str | None = Field(default=None, max_length=100)
