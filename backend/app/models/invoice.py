"""
Invoice and finance ledger models for billing and accounting.

Models:
- Invoice: Billing documents for bookings/projects
- InvoiceItem: Line items in invoice (with GST calculations)
- FinanceLedgerEntry: Accounting entries (debit/credit tracking)
- InvoicePaymentMapping: Link between invoices and booking payment plans
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.base import Base
from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin
from app.utils.enums import PaymentStatus, LedgerEntryType


class Invoice(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Invoice entity for billing.

    Attributes:
        invoice_number: INV-000001 (auto-generated, UNIQUE indexed)
        booking_id: FK to Booking (indexed)
        customer_id: FK to Customer (indexed)
        project_id: FK to Project (indexed)
        invoice_date: When invoice generated
        due_date: When payment due (indexed)
        subtotal: Sum of all line item amounts (Numeric)
        gst_amount: Total GST (Numeric)
        total_amount: Final amount due (Numeric)
        paid_amount: Amount received so far (Numeric)
        payment_status: PENDING/PARTIALLY_PAID/PAID/OVERDUE/CANCELLED (indexed)
        invoice_status: DRAFT/SENT/ACCEPTED/REJECTED/CANCELLED (indexed)
        notes: Notes/terms
        invoice_url: PDF URL
        sent_on: When sent to customer
        paid_on: When marked paid
    """

    __tablename__ = "invoices"
    __table_args__ = (
        Index("idx_invoices_invoice_number", "invoice_number"),
        Index("idx_invoices_booking_id", "booking_id"),
        Index("idx_invoices_customer_id", "customer_id"),
        Index("idx_invoices_project_id", "project_id"),
        Index("idx_invoices_due_date", "due_date"),
        Index("idx_invoices_payment_status", "payment_status"),
        Index("idx_invoices_status", "invoice_status"),
    )

    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True, index=True)
    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), nullable=False)
    gst_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0)
    payment_status = Column(String(50), nullable=False, default=PaymentStatus.PENDING.value, index=True)
    invoice_status = Column(String(50), nullable=False, default="DRAFT", index=True)
    notes = Column(Text, nullable=True)
    invoice_url = Column(String(255), nullable=True)
    sent_on = Column(DateTime, nullable=True)
    paid_on = Column(DateTime, nullable=True)

    # Relationships
    booking = relationship("Booking", foreign_keys=[booking_id])
    customer = relationship("Customer", back_populates="invoices")
    project = relationship("Project", foreign_keys=[project_id])
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="select",
    )
    ledger_entries = relationship(
        "FinanceLedgerEntry",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number}: {self.total_amount} ({self.payment_status})>"


class InvoiceItem(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Line item in invoice.

    Attributes:
        invoice_id: FK to Invoice (indexed)
        description: Item description
        quantity: Qty (default 1)
        unit_price: Price per unit (Numeric)
        amount: Total before tax (Numeric)
        gst_rate: GST % (0-18)
        gst_amount: Calculated GST (Numeric)
        item_total: Amount + GST (Numeric)
        order_index: Line item order
    """

    __tablename__ = "invoice_items"
    __table_args__ = (Index("idx_invoice_items_invoice_id", "invoice_id"),)

    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=0)  # 0-18%
    gst_amount = Column(Numeric(15, 2), nullable=False, default=0)
    item_total = Column(Numeric(15, 2), nullable=False)
    order_index = Column(Integer, default=0)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self) -> str:
        return f"<InvoiceItem {self.description}: {self.item_total}>"


class FinanceLedgerEntry(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Accounting ledger entry (debit/credit).

    Attributes:
        invoice_id: FK to Invoice (indexed)
        entry_date: When entry recorded
        entry_type: INVOICE/PAYMENT/ADJUSTMENT/REFUND/GST (indexed)
        description: Entry description
        debit_amount: Debit side (Numeric)
        credit_amount: Credit side (Numeric)
        account_code: GL account code
        reference_number: External reference (e.g., check #, transaction ID)
        remarks: Additional notes
        posted_by_user_id: FK to User (indexed)
        posted_on: When posted
    """

    __tablename__ = "finance_ledger_entries"
    __table_args__ = (
        Index("idx_finance_ledger_entries_invoice_id", "invoice_id"),
        Index("idx_finance_ledger_entries_entry_type", "entry_type"),
        Index("idx_finance_ledger_entries_posted_by_user_id", "posted_by_user_id"),
    )

    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True, index=True)
    entry_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    entry_type = Column(String(50), nullable=False, index=True)  # INVOICE/PAYMENT/ADJUSTMENT/REFUND/GST
    description = Column(String(255), nullable=False)
    debit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    account_code = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True, unique=True)
    remarks = Column(Text, nullable=True)
    posted_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    posted_on = Column(DateTime, nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="ledger_entries")
    posted_by_user = relationship("User", foreign_keys=[posted_by_user_id])

    def __repr__(self) -> str:
        return f"<LedgerEntry {self.entry_type}: D={self.debit_amount} C={self.credit_amount}>"


class InvoicePaymentMapping(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Mapping between invoice items and booking payment plan milestones.

    Attributes:
        invoice_id: FK to Invoice (indexed)
        payment_plan_id: FK to BookingPaymentPlan (indexed)
        mapped_amount: Amount mapped (Numeric)
        mapped_on: When mapped
    """

    __tablename__ = "invoice_payment_mappings"
    __table_args__ = (
        Index("idx_invoice_payment_mappings_invoice_id", "invoice_id"),
        Index("idx_invoice_payment_mappings_payment_plan_id", "payment_plan_id"),
    )

    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    payment_plan_id = Column(PG_UUID(as_uuid=True), ForeignKey("booking_payment_plans.id"), nullable=False, index=True)
    mapped_amount = Column(Numeric(15, 2), nullable=False)
    mapped_on = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<InvoicePaymentMapping {self.mapped_amount}>"
