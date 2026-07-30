"""
Booking models for property reservations and purchase tracking.

Models:
- Booking: Core booking entity with state machine (PENDING → BLOCKED → CONFIRMED → POSSESSION_INITIATED → COMPLETED)
- BookingPaymentPlan: Payment schedule with milestones and due dates
- BookingApproval: Approval workflow tracking (requires CEO, Finance Manager, Sales Manager)
- BookingCancellation: Cancellation audit trail with refund tracking
- Possession: Possession tracking after booking confirmation
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.base import Base
from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin
from app.utils.enums import BookingStatus, BookingApprovalStatus, PaymentStatus


class Booking(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Booking/Reservation entity.

    Attributes:
        booking_number: BOOK-000001 (auto-generated, UNIQUE indexed)
        unit_id: FK to Unit (UNIQUE indexed - one booking per unit, but can be cancelled)
        customer_id: FK to Customer (indexed)
        booking_date: When booking created
        booking_amount: Amount paid at booking (Numeric with precision)
        total_unit_price: Total unit price at time of booking
        status: State machine (PENDING→BLOCKED→CONFIRMED→POSSESSION_INITIATED→COMPLETED, indexed)
        booking_expiry_date: Booking expires if not confirmed by this date
        booking_notes: Customer notes/special requests
        assignment_to_user_id: FK to User (sales agent, indexed)
        approval_status: Booking approval status (indexed)
        approval_completed_at: When final approval completed
        related_lead_id: FK to Lead (if converted from lead)
        confirmed_by_user_id: FK to User (who confirmed booking)
        confirmed_at: When booking confirmed
        cancellation_initiated_at: When cancellation started
        cancellation_reason: Reason for cancellation
    """

    __tablename__ = "bookings"
    __table_args__ = (
        Index("idx_bookings_booking_number", "booking_number"),
        Index("idx_bookings_unit_id", "unit_id"),
        Index("idx_bookings_customer_id", "customer_id"),
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_approval_status", "approval_status"),
        Index("idx_bookings_assignment_user_id", "assignment_to_user_id"),
        UniqueConstraint("unit_id", "is_deleted", name="uq_unit_active_booking"),
    )

    booking_number = Column(String(50), nullable=False, unique=True, index=True)
    unit_id = Column(PG_UUID(as_uuid=True), ForeignKey("units.id"), nullable=False, index=True)
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    booking_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    booking_amount = Column(Numeric(15, 2), nullable=False)
    total_unit_price = Column(Numeric(15, 2), nullable=False)
    status = Column(String(50), nullable=False, default=BookingStatus.INITIATED.value, index=True)
    booking_expiry_date = Column(DateTime, nullable=True)
    booking_notes = Column(Text, nullable=True)
    assignment_to_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    approval_status = Column(String(50), nullable=False, default=BookingApprovalStatus.PENDING.value, index=True)
    approval_completed_at = Column(DateTime, nullable=True)
    related_lead_id = Column(PG_UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    confirmed_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    cancellation_initiated_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    unit = relationship("Unit", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    assigned_to_user = relationship(
        "User",
        foreign_keys=[assignment_to_user_id],
        back_populates="assigned_bookings",
    )
    payment_plans = relationship(
        "BookingPaymentPlan",
        back_populates="booking",
        cascade="all, delete-orphan",
        lazy="select",
    )
    approvals = relationship(
        "BookingApproval",
        back_populates="booking",
        cascade="all, delete-orphan",
        lazy="select",
    )
    cancellation = relationship(
        "BookingCancellation",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )
    possession = relationship(
        "Possession",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Booking {self.booking_number}: Unit {self.unit_id} | {self.status}>"


class BookingPaymentPlan(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Payment plan/milestone for booking.

    Attributes:
        booking_id: FK to Booking (indexed)
        milestone_name: Registration, Agreement, Construction Phase 1-3, Possession, etc.
        percentage: % of total unit price due at this milestone (max 100)
        due_date: When payment due
        amount: Amount due (Numeric)
        payment_status: PENDING/PAID/OVERDUE/WAIVED (indexed)
        payment_date: When payment received
        payment_method: CASH/CHECK/TRANSFER/CARD
        transaction_ref: External transaction reference
        notes: Additional notes
        grace_period_days: Days of grace after due date
    """

    __tablename__ = "booking_payment_plans"
    __table_args__ = (
        Index("idx_booking_payment_plans_booking_id", "booking_id"),
        Index("idx_booking_payment_plans_payment_status", "payment_status"),
    )

    booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, index=True)
    milestone_name = Column(String(100), nullable=False)
    percentage = Column(Integer, nullable=False)  # 0-100
    due_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_status = Column(String(50), nullable=False, default=PaymentStatus.PENDING.value, index=True)
    payment_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    transaction_ref = Column(String(100), nullable=True, unique=True)
    notes = Column(Text, nullable=True)
    grace_period_days = Column(Integer, default=0)

    # Relationships
    booking = relationship("Booking", back_populates="payment_plans")

    def __repr__(self) -> str:
        return f"<BookingPaymentPlan {self.milestone_name}: {self.percentage}% ({self.payment_status})>"


class BookingApproval(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Multi-level approval workflow for bookings.

    Attributes:
        booking_id: FK to Booking (indexed)
        approval_level: 1=Sales Manager, 2=Finance Manager, 3=CEO
        approver_user_id: FK to User (indexed)
        status: PENDING/APPROVED/REJECTED (indexed)
        notes: Approval notes/rejection reason
        approval_date: When approved/rejected
        approval_order: Sequence (1, 2, 3)
    """

    __tablename__ = "booking_approvals"
    __table_args__ = (
        Index("idx_booking_approvals_booking_id", "booking_id"),
        Index("idx_booking_approvals_approver_user_id", "approver_user_id"),
        Index("idx_booking_approvals_status", "status"),
    )

    booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, index=True)
    approval_level = Column(Integer, nullable=False)  # 1, 2, 3
    approver_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default=BookingApprovalStatus.PENDING.value, index=True)
    notes = Column(Text, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_order = Column(Integer, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_user_id])

    def __repr__(self) -> str:
        return f"<BookingApproval Level {self.approval_level}: {self.status}>"


class BookingCancellation(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Booking cancellation record.

    Attributes:
        booking_id: FK to Booking (UNIQUE, indexed)
        cancellation_date: When cancelled
        reason: Cancellation reason
        cancelled_by_user_id: FK to User (indexed)
        refund_amount: Amount to be refunded (Numeric)
        refund_status: PENDING/PROCESSED/FAILED (indexed)
        refund_date: When refund processed
        refund_transaction_ref: Refund transaction reference
        notes: Additional notes
    """

    __tablename__ = "booking_cancellations"
    __table_args__ = (
        Index("idx_booking_cancellations_booking_id", "booking_id"),
        Index("idx_booking_cancellations_cancelled_by_user_id", "cancelled_by_user_id"),
        Index("idx_booking_cancellations_refund_status", "refund_status"),
    )

    booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True, index=True)
    cancellation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    reason = Column(Text, nullable=False)
    cancelled_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    refund_amount = Column(Numeric(15, 2), nullable=True)
    refund_status = Column(String(50), nullable=True, index=True)
    refund_date = Column(DateTime, nullable=True)
    refund_transaction_ref = Column(String(100), nullable=True, unique=True)
    notes = Column(Text, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="cancellation")
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by_user_id])

    def __repr__(self) -> str:
        return f"<BookingCancellation Booking {self.booking_id}: {self.refund_status}>"


class Possession(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Possession tracking after booking confirmation.

    Attributes:
        booking_id: FK to Booking (UNIQUE, indexed)
        possession_date: Scheduled possession date
        possession_handed_date: When actually handed over
        possession_notes: Possession notes
        keys_handed_by_user_id: FK to User (indexed)
        keys_handed_to_customer: Whether keys handed to customer
        documents_handed: Whether all documents handed
        final_inspection_done: Whether final inspection done
        inspected_by_user_id: FK to User (indexed)
        inspection_notes: Final inspection notes
        possession_status: SCHEDULED/HANDED_OVER/COMPLETED (indexed)
    """

    __tablename__ = "possessions"
    __table_args__ = (
        Index("idx_possessions_booking_id", "booking_id"),
        Index("idx_possessions_keys_handed_by_user_id", "keys_handed_by_user_id"),
        Index("idx_possessions_inspected_by_user_id", "inspected_by_user_id"),
        Index("idx_possessions_status", "possession_status"),
    )

    booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True, index=True)
    possession_date = Column(DateTime, nullable=False)
    possession_handed_date = Column(DateTime, nullable=True)
    possession_notes = Column(Text, nullable=True)
    keys_handed_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    keys_handed_to_customer = Column(Boolean, default=False)
    documents_handed = Column(Boolean, default=False)
    final_inspection_done = Column(Boolean, default=False)
    inspected_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    inspection_notes = Column(Text, nullable=True)
    possession_status = Column(String(50), nullable=False, default="SCHEDULED", index=True)

    # Relationships
    booking = relationship("Booking", back_populates="possession")
    keys_handed_by_user = relationship("User", foreign_keys=[keys_handed_by_user_id])
    inspected_by_user = relationship("User", foreign_keys=[inspected_by_user_id])

    def __repr__(self) -> str:
        return f"<Possession Booking {self.booking_id}: {self.possession_status}>"
