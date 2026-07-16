import uuid
from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Index, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SiteVisit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "site_visits"
    __table_args__ = (
        Index("ix_site_visits_visit_date", "visit_date"),
        Index("ix_site_visits_customer_name", "customer_name"),
        Index("ix_site_visits_sales_executive", "sales_executive"),
    )

    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    visit_time: Mapped[time] = mapped_column(Time, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sales_executive: Mapped[str] = mapped_column(String(200), nullable=False)

    pickup_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    vehicle_assigned: Mapped[str | None] = mapped_column(String(128), nullable=True)
    driver: Mapped[str | None] = mapped_column(String(128), nullable=True)
    attendance: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
