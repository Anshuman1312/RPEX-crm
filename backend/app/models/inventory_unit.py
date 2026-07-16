import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class InventoryUnit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inventory_units"
    __table_args__ = (
        Index("ix_inventory_units_project_id", "project_id"),
        Index("ix_inventory_units_plot_no", "plot_no"),
        Index("ix_inventory_units_booking_status", "booking_status"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    plot_no: Mapped[str] = mapped_column(String(64), nullable=False)
    size: Mapped[str] = mapped_column(String(64), nullable=False)
    facing: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_corner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    booking_status: Mapped[str] = mapped_column(String(32), nullable=False, default="AVAILABLE")
    customer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sales_executive: Mapped[str | None] = mapped_column(String(200), nullable=True)
    booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    agreement_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
