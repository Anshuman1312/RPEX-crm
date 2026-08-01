from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class SiteVisit(Base, BaseModelMixin):
    __tablename__ = "site_visits"

    # ── Scheduling ────────────────────────────────────────────────────────────
    
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    """Date of site visit"""
    
    visit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    """Time of site visit"""
    
    site_visit_scheduled: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    """When the site visit was scheduled"""
    
    site_visit_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """Whether site visit was completed"""

    # ── Customer & Personnel ───────────────────────────────────────────────────
    
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    """Name of visitor/customer"""
    
    sales_executive: Mapped[str | None] = mapped_column(String(200), nullable=True)
    """Sales executive handling the visit"""

    # ── Logistics ──────────────────────────────────────────────────────────────
    
    pickup_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """Whether pickup is required"""
    
    vehicle_assigned: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """Vehicle assigned for pickup"""
    
    driver: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """Driver name"""
    
    number_of_visitors: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    """Number of visitors attending site visit"""

    # ── Attendance & Feedback ──────────────────────────────────────────────────
    
    attendance: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    """Attendance status: PENDING, ATTENDED, CANCELLED, NO_SHOW"""
    
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    """Site visit feedback from customer"""
    
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """Outcome of visit: interested, not_interested, follow_up_required, etc."""

    # ── Audit ──────────────────────────────────────────────────────────────────
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    """User who created the site visit record"""
