import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SEOKeyword(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "seo_keywords"

    keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    target_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    traffic: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    campaign = relationship("Campaign", back_populates="keywords")
