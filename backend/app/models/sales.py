from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class SalesBooking(Base, BaseModelMixin):
    __tablename__ = "sales_bookings"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    unit_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    booking_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NEW", index=True)
    partner_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
