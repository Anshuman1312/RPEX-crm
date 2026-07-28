from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class HREmployee(Base, BaseModelMixin):
    __tablename__ = "hr_employees"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    salary: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    incentives: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    performance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)


class HRRecord(Base, BaseModelMixin):
    __tablename__ = "hr_records"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hr_employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    record_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE", index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
