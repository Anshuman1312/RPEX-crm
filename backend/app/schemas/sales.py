from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class BookingCreate(BaseModel):
    customer_id: str
    project_name: str = Field(min_length=2, max_length=128)
    unit_code: str | None = Field(default=None, max_length=64)
    booking_value: Decimal = Field(gt=0)
    booking_date: date
    status: str = Field(default="BOOKED", max_length=32)
    sales_executive_id: str | None = None
    partner_user_id: str | None = None
    extra_data: dict[str, Any] = Field(default_factory=dict)


class BookingOut(TimestampSchema):
    customer_id: str
    project_name: str
    unit_code: str | None
    booking_value: Decimal
    booking_date: date
    status: str
    sales_executive_id: str | None
    partner_user_id: str | None
    extra_data: dict[str, Any]
