import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FinanceLedgerEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "finance_ledger_entries"
    __table_args__ = (
        Index("ix_finance_ledger_entries_entry_type", "entry_type"),
        Index("ix_finance_ledger_entries_entry_date", "entry_date"),
    )

    entry_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reference_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="POSTED")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    creator = relationship("User")
    
class ExpenseLedger(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "expense_ledger"
    
    category: Mapped[str] = mapped_column(String(50)) # Marketing-Indoor, Salary, Legal, etc.
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    reference_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True) # ID of Vendor or Employee
    description: Mapped[str] = mapped_column(Text)
    payment_mode: Mapped[str] = mapped_column(String(20)) # Cash, Bank
