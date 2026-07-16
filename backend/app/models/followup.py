import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FollowUp(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "followups"

    lead_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    assigned_to: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    followup_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_followup_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    remark: Mapped[str] = mapped_column(Text, nullable=False)
    call_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meeting_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice_recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sms_log: Mapped[list[dict]] = mapped_column(JSONType, default=list, nullable=False)
    followup_history: Mapped[list[dict]] = mapped_column(JSONType, default=list, nullable=False)
    auto_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")

    lead = relationship("Lead", back_populates="followups")
