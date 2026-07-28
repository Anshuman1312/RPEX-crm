from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class SEOKeyword(Base, BaseModelMixin):
    __tablename__ = "seo_keywords"

    keyword: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    match_type: Mapped[str] = mapped_column(String(32), nullable=False, default="BROAD")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    bid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    campaign = relationship("Campaign", back_populates="keywords")
