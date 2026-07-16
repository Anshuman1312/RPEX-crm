import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class HRRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hr_records"
    __table_args__ = (
        Index("ix_hr_records_employee_id", "employee_id"),
        Index("ix_hr_records_record_type", "record_type"),
        Index("ix_hr_records_record_date", "record_date"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False)
    record_type: Mapped[str] = mapped_column(String(32), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("HREmployee")
