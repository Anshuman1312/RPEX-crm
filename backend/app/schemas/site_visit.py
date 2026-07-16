from datetime import date, time

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class SiteVisitCreate(BaseModel):
    visit_date: date
    visit_time: time
    customer_name: str = Field(min_length=2, max_length=200)
    sales_executive: str = Field(min_length=2, max_length=200)
    pickup_required: bool = False
    vehicle_assigned: str | None = Field(default=None, max_length=128)
    driver: str | None = Field(default=None, max_length=128)
    attendance: str = Field(default="PENDING", max_length=32)
    feedback: str | None = None
    outcome: str | None = Field(default=None, max_length=64)


class SiteVisitOut(TimestampSchema):
    visit_date: date
    visit_time: time
    customer_name: str
    sales_executive: str
    pickup_required: bool
    vehicle_assigned: str | None
    driver: str | None
    attendance: str
    feedback: str | None
    outcome: str | None
    created_by: str
