from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class InventoryUnit(Base, BaseModelMixin):
	__tablename__ = "inventory_units"

	project_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("projects.id", ondelete="CASCADE"),
		nullable=False,
		index=True,
	)
	plot_no: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
	size: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
	facing: Mapped[str | None] = mapped_column(String(32), nullable=True)
	is_corner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
	booking_status: Mapped[str] = mapped_column(String(32), default="AVAILABLE", nullable=False, index=True)
	customer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
	sales_executive: Mapped[str | None] = mapped_column(String(200), nullable=True)
	booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
	agreement_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
	payment_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

