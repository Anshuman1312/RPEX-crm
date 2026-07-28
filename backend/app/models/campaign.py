from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class Campaign(Base, BaseModelMixin):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    budget: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    leads = relationship("Lead", back_populates="campaign", lazy="dynamic")
    keywords = relationship("SEOKeyword", back_populates="campaign", lazy="dynamic")
