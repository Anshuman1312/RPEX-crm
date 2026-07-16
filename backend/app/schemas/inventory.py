from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class InventoryUnitCreate(BaseModel):
    project_id: str
    plot_no: str = Field(min_length=1, max_length=64)
    size: str = Field(min_length=1, max_length=64)
    facing: str | None = Field(default=None, max_length=64)
    is_corner: bool = False
    price: Decimal = Field(gt=0)

    booking_status: str = Field(default="AVAILABLE", max_length=32)
    customer_name: str | None = Field(default=None, max_length=200)
    sales_executive: str | None = Field(default=None, max_length=200)
    booking_date: date | None = None
    agreement_status: str | None = Field(default=None, max_length=64)
    payment_status: str | None = Field(default=None, max_length=64)


class InventoryUnitOut(TimestampSchema):
    project_id: str
    plot_no: str
    size: str
    facing: str | None
    is_corner: bool
    price: Decimal

    booking_status: str
    customer_name: str | None
    sales_executive: str | None
    booking_date: date | None
    agreement_status: str | None
    payment_status: str | None
    color_code: str
