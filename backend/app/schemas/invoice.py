"""
Pydantic schemas for invoice operations.

Includes:
- Invoice item schemas
- Invoice CRUD schemas
- Ledger entry schemas
- Payment mapping schemas
- Financial reports
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


# ── Invoice Item Schemas ──────────────────────────────────────────────

class InvoiceItemCreate(BaseModel):
    """Create invoice item."""

    description: str
    quantity: int = 1
    unit_price: Decimal
    gst_rate: Decimal = Field(default=0, ge=0, le=18)
    order_index: int = 0


class InvoiceItemUpdate(BaseModel):
    """Update invoice item."""

    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=18)
    order_index: Optional[int] = None


class InvoiceItemResponse(BaseModel):
    """Invoice item details."""

    id: str
    invoice_id: str
    description: str
    quantity: int
    unit_price: Decimal
    amount: Decimal
    gst_rate: Decimal
    gst_amount: Decimal
    item_total: Decimal
    order_index: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Invoice Schemas ───────────────────────────────────────────────────

class InvoiceCreate(BaseModel):
    """Create invoice."""

    booking_id: Optional[str] = None
    customer_id: str
    project_id: Optional[str] = None
    due_date: datetime
    items: List[InvoiceItemCreate]
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """Update invoice."""

    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceItemsUpdate(BaseModel):
    """Update invoice items."""

    items: List[InvoiceItemCreate]


class InvoiceStatusUpdate(BaseModel):
    """Update invoice status."""

    status: str = Field(pattern="^(DRAFT|SENT|ACCEPTED|REJECTED|CANCELLED)$")
    notes: Optional[str] = None


class InvoicePaymentReceived(BaseModel):
    """Record payment received against invoice."""

    amount: Decimal
    payment_date: datetime
    payment_method: str
    transaction_ref: str
    notes: Optional[str] = None


class InvoiceListResponse(BaseModel):
    """Invoice list item."""

    id: str
    invoice_number: str
    customer_id: str
    booking_id: Optional[str] = None
    invoice_date: datetime
    due_date: datetime
    subtotal: Decimal
    gst_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    payment_status: str
    invoice_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Full invoice details."""

    id: str
    invoice_number: str
    booking_id: Optional[str] = None
    customer_id: str
    project_id: Optional[str] = None
    invoice_date: datetime
    due_date: datetime
    subtotal: Decimal
    gst_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    payment_status: str
    invoice_status: str
    notes: Optional[str] = None
    invoice_url: Optional[str] = None
    sent_on: Optional[datetime] = None
    paid_on: Optional[datetime] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Ledger Entry Schemas ──────────────────────────────────────────────

class FinanceLedgerEntryCreate(BaseModel):
    """Create ledger entry."""

    invoice_id: Optional[str] = None
    entry_date: datetime
    entry_type: str
    description: str
    debit_amount: Decimal = 0
    credit_amount: Decimal = 0
    account_code: Optional[str] = None
    reference_number: Optional[str] = None
    remarks: Optional[str] = None


class FinanceLedgerEntryResponse(BaseModel):
    """Ledger entry details."""

    id: str
    invoice_id: Optional[str] = None
    entry_date: datetime
    entry_type: str
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    account_code: Optional[str] = None
    reference_number: Optional[str] = None
    remarks: Optional[str] = None
    posted_by_user_id: Optional[str] = None
    posted_on: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Payment Mapping Schemas ───────────────────────────────────────────

class InvoicePaymentMappingCreate(BaseModel):
    """Map invoice to payment plan."""

    payment_plan_id: str
    mapped_amount: Decimal


class InvoicePaymentMappingResponse(BaseModel):
    """Payment mapping details."""

    id: str
    invoice_id: str
    payment_plan_id: str
    mapped_amount: Decimal
    mapped_on: datetime

    class Config:
        from_attributes = True


# ── Financial Reports ────────────────────────────────────────────────

class InvoiceSummary(BaseModel):
    """Invoice financial summary."""

    total_invoices: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    average_payment_days: Optional[int] = None


class CustomerInvoiceSummary(BaseModel):
    """Customer invoice summary."""

    customer_id: str
    total_invoices: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal


class FinancialStatement(BaseModel):
    """Financial statement data."""

    total_revenue: Decimal
    total_gst: Decimal
    total_receivable: Decimal
    total_received: Decimal
    net_balance: Decimal
    period_start: datetime
    period_end: datetime
