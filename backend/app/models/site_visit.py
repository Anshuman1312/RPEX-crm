from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class SiteVisit(Base, BaseModelMixin):
    __tablename__ = "site_visits"

    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    visit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    sales_executive: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pickup_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vehicle_assigned: Mapped[str | None] = mapped_column(String(100), nullable=True)
    driver: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attendance: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
