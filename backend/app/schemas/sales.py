from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    customer_id: str
    project_name: str = Field(min_length=1, max_length=200)
    unit_code: str | None = Field(default=None, max_length=100)
    plot_number: str | None = Field(default=None, max_length=100)
    booking_value: Decimal = Field(gt=0)
    booking_date: datetime | None = None
    status: str = Field(default="NEW", max_length=50)
    partner_user_id: str | None = None
    payment_method: str | None = None
    receipt: str | None = None
    agreement_date: datetime | None = None
    emi_details: dict[str, Any] | None = None
    loan_required: bool = False
    kyc_documents: list[dict[str, Any]] = []
    extra_data: dict[str, Any] = {}
