import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class HREmployee(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hr_employees"
    __table_args__ = (
        Index("ix_hr_employees_user_id", "user_id"),
        Index("ix_hr_employees_department", "department"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(64), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    incentives: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    performance_score: Mapped[float] = mapped_column(nullable=False, default=0)
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    user = relationship("User")
