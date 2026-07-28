from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class SalesTeamReport(Base, BaseModelMixin):
    __tablename__ = "sales_team_reports"

    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sales_executive_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sales_executive_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    achieved_sales_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    bookings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    commission_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    site_visits_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attendance_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PRESENT")
    daily_report: Mapped[str | None] = mapped_column(Text, nullable=True)
