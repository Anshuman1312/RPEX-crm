import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SalesTeamReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sales_team_reports"
    __table_args__ = (
        Index("ix_sales_team_reports_report_date", "report_date"),
        Index("ix_sales_team_reports_sales_executive_id", "sales_executive_id"),
    )

    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    sales_executive_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sales_executive_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    achieved_sales_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    bookings_count: Mapped[int] = mapped_column(nullable=False, default=0)
    commission_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    site_visits_count: Mapped[int] = mapped_column(nullable=False, default=0)
    attendance_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PRESENT")
    daily_report: Mapped[str | None] = mapped_column(Text, nullable=True)

    sales_executive = relationship("User")
