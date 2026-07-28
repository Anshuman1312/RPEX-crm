from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class InventoryUnitCreate(BaseModel):
	project_id: str
	plot_no: str = Field(min_length=1, max_length=64)
	size: Decimal | None = Field(default=None, ge=0)
	facing: str | None = Field(default=None, max_length=32)
	is_corner: bool = False
	price: Decimal | None = Field(default=None, ge=0)
	booking_status: str = Field(default="AVAILABLE", max_length=32)
	customer_name: str | None = Field(default=None, max_length=200)
	sales_executive: str | None = Field(default=None, max_length=200)
	booking_date: date | None = None
	agreement_status: str | None = Field(default=None, max_length=32)
	payment_status: str | None = Field(default=None, max_length=32)

