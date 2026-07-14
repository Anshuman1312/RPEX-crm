import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Lead(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_email", "email"),
        Index("ix_leads_status", "status"),
        Index("ix_leads_created_at", "created_at"),
        Index("ix_leads_status_created_at", "status", "created_at"),
        Index("ix_leads_campaign_created_at", "campaign_id", "created_at"),
        Index("ix_leads_assigned_status", "assigned_to", "status"),
        Index("ix_leads_campaign_id", "campaign_id"),
        Index("ix_leads_assigned_to", "assigned_to"),
        Index("ix_leads_extra_data_gin", "extra_data", postgresql_using="gin"),
    )

    website_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("websites.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    medium: Mapped[str | None] = mapped_column(String(64), nullable=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="NEW")
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    website = relationship("Website", back_populates="leads")
    campaign = relationship("Campaign", back_populates="leads")
    assignee = relationship("User", back_populates="assigned_leads", foreign_keys=[assigned_to])
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")
