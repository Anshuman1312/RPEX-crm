from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.invoice import FinanceLedgerEntryCreate, InvoiceCreate


class CustomerPaymentCreate(BaseModel):
    customer_id: str
    booking_id: str | None = None
    amount: Decimal = Field(gt=0)
    payment_date: date
    payment_mode: str = Field(min_length=1, max_length=32)
    reference_no: str | None = Field(default=None, max_length=128)
    status: str = Field(default="RECEIVED", max_length=32)
    notes: str | None = None
    partner_user_id: str | None = None


__all__ = ["CustomerPaymentCreate", "FinanceLedgerEntryCreate", "InvoiceCreate"]
