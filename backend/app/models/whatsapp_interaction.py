from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.database.types import JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class WhatsAppInteraction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "whatsapp_interactions"
    __table_args__ = (
        Index("ix_whatsapp_interactions_type", "interaction_type"),
        Index("ix_whatsapp_interactions_phone", "phone"),
    )

    interaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False, default="OUTBOUND")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
