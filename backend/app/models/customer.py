import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_phone", "phone"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_partner_user_id", "partner_user_id"),
    )

    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    alternate_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    anniversary_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    creator = relationship("User", back_populates="created_customers", foreign_keys=[created_by])
    partner_user = relationship("User", back_populates="partner_customers", foreign_keys=[partner_user_id])
    bookings = relationship("Booking", back_populates="customer")
    payments = relationship("CustomerPayment", back_populates="customer")
    documents = relationship("DocumentAsset", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
