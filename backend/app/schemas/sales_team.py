from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class SalesTeamReportCreate(BaseModel):
    report_date: date
    sales_executive_id: str
    sales_executive_name: str = Field(min_length=2, max_length=200)
    target_value: Decimal = Field(default=0, ge=0)
    achieved_sales_value: Decimal = Field(default=0, ge=0)
    bookings_count: int = Field(default=0, ge=0)
    commission_value: Decimal = Field(default=0, ge=0)
    site_visits_count: int = Field(default=0, ge=0)
    attendance_status: str = Field(default="PRESENT", max_length=32)
    daily_report: str | None = None
