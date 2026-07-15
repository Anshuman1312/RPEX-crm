import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CustomerPayment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customer_payments"
    __table_args__ = (
        Index("ix_customer_payments_customer_id", "customer_id"),
        Index("ix_customer_payments_booking_id", "booking_id"),
        Index("ix_customer_payments_partner_user_id", "partner_user_id"),
        Index("ix_customer_payments_reference_no", "reference_no"),
        Index("ix_customer_payments_payment_date", "payment_date"),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="RECEIVED")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    customer = relationship("Customer", back_populates="payments")
    booking = relationship("Booking", back_populates="payments")
    recorder = relationship("User", back_populates="recorded_payments", foreign_keys=[recorded_by])
    partner_user = relationship("User", back_populates="partner_payments", foreign_keys=[partner_user_id])
