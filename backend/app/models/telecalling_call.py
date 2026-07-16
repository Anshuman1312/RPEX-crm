import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class TelecallingCall(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telecalling_calls"
    __table_args__ = (
        Index("ix_telecalling_calls_call_date", "call_date"),
        Index("ix_telecalling_calls_status", "status"),
        Index("ix_telecalling_calls_telecaller_id", "telecaller_id"),
    )

    call_date: Mapped[date] = mapped_column(Date, nullable=False)
    telecaller_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    lead_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="NOT_CONNECTED")
    call_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    call_recording_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    daily_target: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    telecaller = relationship("User")
    lead = relationship("Lead")
