import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Booking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_customer_id", "customer_id"),
        Index("ix_bookings_sales_executive_id", "sales_executive_id"),
        Index("ix_bookings_partner_user_id", "partner_user_id"),
        Index("ix_bookings_status", "status"),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    project_name: Mapped[str] = mapped_column(String(128), nullable=False)
    unit_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    booking_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="BOOKED")
    sales_executive_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    customer = relationship("Customer", back_populates="bookings")
    sales_executive = relationship("User", back_populates="sales_bookings", foreign_keys=[sales_executive_id])
    partner_user = relationship("User", back_populates="partner_bookings", foreign_keys=[partner_user_id])
    payments = relationship("CustomerPayment", back_populates="booking")
    documents = relationship("DocumentAsset", back_populates="booking")
    invoices = relationship("Invoice", back_populates="booking")
