import uuid

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DocumentAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_assets"
    __table_args__ = (
        Index("ix_document_assets_customer_id", "customer_id"),
        Index("ix_document_assets_booking_id", "booking_id"),
        Index("ix_document_assets_partner_user_id", "partner_user_id"),
        Index("ix_document_assets_category", "category"),
        Index("ix_document_assets_storage_key", "storage_key", unique=True),
    )

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    file_metadata: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    customer = relationship("Customer", back_populates="documents")
    booking = relationship("Booking", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents", foreign_keys=[uploaded_by])
    partner_user = relationship("User", back_populates="partner_documents", foreign_keys=[partner_user_id])
