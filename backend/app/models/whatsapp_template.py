from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class WhatsAppTemplate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "whatsapp_templates"
    __table_args__ = (
        Index("ix_whatsapp_templates_name", "name"),
        Index("ix_whatsapp_templates_type", "template_type"),
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    template_type: Mapped[str] = mapped_column(String(32), nullable=False, default="AUTO_REPLY")
    body: Mapped[str] = mapped_column(Text, nullable=False)
