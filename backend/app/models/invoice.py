import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Invoice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        Index("ix_invoices_customer_id", "customer_id"),
        Index("ix_invoices_booking_id", "booking_id"),
        Index("ix_invoices_partner_user_id", "partner_user_id"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_invoice_number", "invoice_number", unique=True),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True
    )
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    gst_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    customer = relationship("Customer", back_populates="invoices")
    booking = relationship("Booking", back_populates="invoices")
    creator = relationship("User", back_populates="created_invoices", foreign_keys=[created_by])
    partner_user = relationship("User", back_populates="partner_invoices", foreign_keys=[partner_user_id])
