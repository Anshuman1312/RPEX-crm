"""
Pydantic schemas for booking operations.

Includes:
- Payment plan schemas
- Approval schemas
- Cancellation schemas
- Possession schemas
- Booking CRUD schemas (Create, Update, Read responses, Status updates)
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.utils.enums import BookingStatus, BookingApprovalStatus, PaymentStatus


# ── Payment Plan Schemas ──────────────────────────────────────────────

class BookingPaymentPlanCreate(BaseModel):
    """Create payment plan milestone."""

    milestone_name: str
    percentage: int = Field(ge=0, le=100)
    due_date: datetime
    amount: Decimal
    payment_method: Optional[str] = None
    grace_period_days: int = 0
    notes: Optional[str] = None


class BookingPaymentPlanUpdate(BaseModel):
    """Update payment plan."""

    milestone_name: Optional[str] = None
    percentage: Optional[int] = Field(None, ge=0, le=100)
    due_date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    grace_period_days: Optional[int] = None
    notes: Optional[str] = None


class BookingPaymentPlanResponse(BaseModel):
    """Payment plan details."""

    id: str
    booking_id: str
    milestone_name: str
    percentage: int
    due_date: datetime
    amount: Decimal
    payment_status: str
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_ref: Optional[str] = None
    notes: Optional[str] = None
    grace_period_days: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentMarkAsPaidRequest(BaseModel):
    """Mark payment as paid."""

    payment_date: datetime
    transaction_ref: str
    payment_method: str
    notes: Optional[str] = None


# ── Approval Schemas ──────────────────────────────────────────────────

class BookingApprovalResponse(BaseModel):
    """Booking approval details."""

    id: str
    booking_id: str
    approval_level: int
    approver_user_id: str
    status: str
    notes: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class BookingApprovalActionRequest(BaseModel):
    """Approve or reject booking."""

    status: str = Field(pattern="^(APPROVED|REJECTED)$")
    notes: Optional[str] = None


# ── Cancellation Schemas ──────────────────────────────────────────────

class BookingCancellationResponse(BaseModel):
    """Cancellation details."""

    id: str
    booking_id: str
    cancellation_date: datetime
    reason: str
    cancelled_by_user_id: str
    refund_amount: Optional[Decimal] = None
    refund_status: Optional[str] = None
    refund_date: Optional[datetime] = None
    refund_transaction_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCancellationRequest(BaseModel):
    """Cancel a booking."""

    reason: str
    notes: Optional[str] = None


# ── Possession Schemas ────────────────────────────────────────────────

class PossessionCreate(BaseModel):
    """Create possession record."""

    possession_date: datetime
    possession_notes: Optional[str] = None


class PossessionHandoverRequest(BaseModel):
    """Handover possession to customer."""

    keys_handed_to_customer: bool = True
    documents_handed: bool = True
    final_inspection_done: bool = False
    inspection_notes: Optional[str] = None


class PossessionResponse(BaseModel):
    """Possession details."""

    id: str
    booking_id: str
    possession_date: datetime
    possession_handed_date: Optional[datetime] = None
    possession_notes: Optional[str] = None
    keys_handed_by_user_id: Optional[str] = None
    keys_handed_to_customer: bool
    documents_handed: bool
    final_inspection_done: bool
    inspected_by_user_id: Optional[str] = None
    inspection_notes: Optional[str] = None
    possession_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Booking CRUD Schemas ──────────────────────────────────────────────

class BookingCreate(BaseModel):
    """Create booking."""

    unit_id: str
    customer_id: str
    booking_amount: Decimal
    booking_expiry_date: Optional[datetime] = None
    booking_notes: Optional[str] = None
    assignment_to_user_id: Optional[str] = None
    related_lead_id: Optional[str] = None


class BookingUpdate(BaseModel):
    """Update booking details."""

    booking_expiry_date: Optional[datetime] = None
    booking_notes: Optional[str] = None
    assignment_to_user_id: Optional[str] = None


class BookingStatusUpdate(BaseModel):
    """Update booking status."""

    status: str = Field(pattern="^(initiated|confirmed|approved|agreement_signed|possession|cancelled|defaulted)$")
    notes: Optional[str] = None


class BookingConfirmRequest(BaseModel):
    """Confirm a booking."""

    notes: Optional[str] = None


class BookingListResponse(BaseModel):
    """Booking list item."""

    id: str
    booking_number: str
    unit_id: str
    customer_id: str
    booking_date: datetime
    booking_amount: Decimal
    total_unit_price: Decimal
    status: str
    approval_status: str
    assignment_to_user_id: Optional[str] = None
    booking_expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Full booking details."""

    id: str
    booking_number: str
    unit_id: str
    customer_id: str
    booking_date: datetime
    booking_amount: Decimal
    total_unit_price: Decimal
    status: str
    approval_status: str
    booking_expiry_date: Optional[datetime] = None
    booking_notes: Optional[str] = None
    assignment_to_user_id: Optional[str] = None
    related_lead_id: Optional[str] = None
    confirmed_by_user_id: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    cancellation_initiated_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    payment_plans: List[BookingPaymentPlanResponse] = []
    approvals: List[BookingApprovalResponse] = []
    cancellation: Optional[BookingCancellationResponse] = None
    possession: Optional[PossessionResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
