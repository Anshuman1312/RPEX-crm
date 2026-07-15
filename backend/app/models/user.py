import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role = relationship("Role", back_populates="users")
    assigned_leads = relationship("Lead", back_populates="assignee", foreign_keys="Lead.assigned_to")
    created_customers = relationship("Customer", back_populates="creator", foreign_keys="Customer.created_by")
    partner_customers = relationship("Customer", back_populates="partner_user", foreign_keys="Customer.partner_user_id")
    sales_bookings = relationship("Booking", back_populates="sales_executive", foreign_keys="Booking.sales_executive_id")
    partner_bookings = relationship("Booking", back_populates="partner_user", foreign_keys="Booking.partner_user_id")
    recorded_payments = relationship("CustomerPayment", back_populates="recorder", foreign_keys="CustomerPayment.recorded_by")
    partner_payments = relationship("CustomerPayment", back_populates="partner_user", foreign_keys="CustomerPayment.partner_user_id")
    created_invoices = relationship("Invoice", back_populates="creator", foreign_keys="Invoice.created_by")
    partner_invoices = relationship("Invoice", back_populates="partner_user", foreign_keys="Invoice.partner_user_id")
    uploaded_documents = relationship("DocumentAsset", back_populates="uploader", foreign_keys="DocumentAsset.uploaded_by")
    partner_documents = relationship("DocumentAsset", back_populates="partner_user", foreign_keys="DocumentAsset.partner_user_id")
