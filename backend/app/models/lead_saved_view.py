import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LeadSavedView(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "lead_saved_views"
    __table_args__ = (Index("ix_lead_saved_views_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    filters: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
