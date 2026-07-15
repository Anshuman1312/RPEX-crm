from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class CustomerPaymentCreate(BaseModel):
    customer_id: str
    booking_id: str | None = None
    amount: Decimal = Field(gt=0)
    payment_date: date
    payment_mode: str = Field(min_length=2, max_length=32)
    reference_no: str | None = Field(default=None, max_length=128)
    status: str = Field(default="RECEIVED", max_length=32)
    notes: str | None = None
    partner_user_id: str | None = None


class CustomerPaymentOut(TimestampSchema):
    customer_id: str
    booking_id: str | None
    amount: Decimal
    payment_date: date
    payment_mode: str
    reference_no: str | None
    status: str
    notes: str | None
    recorded_by: str
    partner_user_id: str | None


class InvoiceCreate(BaseModel):
    customer_id: str
    booking_id: str | None = None
    invoice_number: str = Field(min_length=2, max_length=64)
    invoice_date: date
    due_date: date | None = None
    amount: Decimal = Field(gt=0)
    gst_amount: Decimal = Field(default=0, ge=0)
    status: str = Field(default="DRAFT", max_length=32)
    notes: str | None = None
    partner_user_id: str | None = None


class InvoiceOut(TimestampSchema):
    customer_id: str
    booking_id: str | None
    invoice_number: str
    invoice_date: date
    due_date: date | None
    amount: Decimal
    gst_amount: Decimal
    status: str
    notes: str | None
    created_by: str
    partner_user_id: str | None
