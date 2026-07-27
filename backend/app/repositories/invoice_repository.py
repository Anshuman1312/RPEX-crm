"""
Repository layer for invoice and finance data access.

Classes:
- InvoiceRepository: Invoice CRUD + advanced filtering
- InvoiceItemRepository: Invoice line items
- FinanceLedgerRepository: Accounting entries
- InvoicePaymentMappingRepository: Payment mappings
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.invoice import (
    Invoice,
    InvoiceItem,
    FinanceLedgerEntry,
    InvoicePaymentMapping,
)
from app.repositories.base import BaseRepository
from app.utils.enums import PaymentStatus


class InvoiceRepository(BaseRepository[Invoice]):
    """Invoice data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Invoice)

    async def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number."""
        stmt = select(self.model).where(
            and_(
                self.model.invoice_number == invoice_number,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_items(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice with items."""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.items))
            .where(
                and_(
                    self.model.id == invoice_id,
                    self.model.is_deleted == False,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_customer_invoices(self, customer_id: str) -> List[Invoice]:
        """Get all invoices for customer."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.customer_id == customer_id,
                    self.model.is_deleted == False,
                )
            )
            .order_by(desc(self.model.invoice_date))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_booking_invoices(self, booking_id: str) -> List[Invoice]:
        """Get invoices for booking."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.booking_id == booking_id,
                    self.model.is_deleted == False,
                )
            )
            .order_by(desc(self.model.invoice_date))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_with_filter(
        self,
        customer_id: Optional[str] = None,
        payment_statuses: Optional[List[str]] = None,
        invoice_statuses: Optional[List[str]] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> Tuple[List[Invoice], int]:
        """Filter invoices with advanced options."""
        filters = [self.model.is_deleted == False]

        if customer_id:
            filters.append(self.model.customer_id == customer_id)
        if payment_statuses:
            filters.append(self.model.payment_status.in_(payment_statuses))
        if invoice_statuses:
            filters.append(self.model.invoice_status.in_(invoice_statuses))
        if date_from:
            filters.append(self.model.invoice_date >= date_from)
        if date_to:
            filters.append(self.model.invoice_date <= date_to)
        if search:
            filters.append(
                or_(
                    self.model.invoice_number.ilike(f"%{search}%"),
                    self.model.notes.ilike(f"%{search}%"),
                )
            )

        # Count query
        count_stmt = select(func.count()).select_from(self.model).where(and_(*filters))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # List query
        sort_column = getattr(self.model, sort_by, self.model.created_at)
        if sort_direction == "desc":
            sort_column = desc(sort_column)

        stmt = (
            select(self.model)
            .where(and_(*filters))
            .order_by(sort_column)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        invoices = result.scalars().all()

        return invoices, total

    async def get_overdue_invoices(self) -> List[Invoice]:
        """Get overdue invoices (past due date, not paid)."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.due_date < func.now(),
                    self.model.payment_status.in_(
                        [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]
                    ),
                    self.model.is_deleted == False,
                )
            )
            .order_by(self.model.due_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_invoices_due_soon(self, days: int = 7) -> List[Invoice]:
        """Get invoices due within N days."""
        future_date = func.now() + func.make_interval(days=days)
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.due_date <= future_date,
                    self.model.due_date >= func.now(),
                    self.model.payment_status.in_(
                        [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]
                    ),
                    self.model.is_deleted == False,
                )
            )
            .order_by(self.model.due_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_payment_status(self) -> dict:
        """Get invoice count by payment status."""
        stmt = (
            select(self.model.payment_status, func.count(self.model.id))
            .where(self.model.is_deleted == False)
            .group_by(self.model.payment_status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {status: count for status, count in rows}

    async def get_total_receivable(self) -> float:
        """Get total outstanding receivable."""
        stmt = select(func.sum(self.model.total_amount - self.model.paid_amount)).where(
            and_(
                self.model.payment_status.in_(
                    [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]
                ),
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)

    async def get_total_revenue(self, date_from: Optional[datetime] = None) -> float:
        """Get total revenue from invoices."""
        filters = [self.model.is_deleted == False]
        if date_from:
            filters.append(self.model.invoice_date >= date_from)

        stmt = select(func.sum(self.model.total_amount)).where(and_(*filters))
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)


class InvoiceItemRepository(BaseRepository[InvoiceItem]):
    """Invoice item data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InvoiceItem)

    async def get_invoice_items(self, invoice_id: str) -> List[InvoiceItem]:
        """Get all items for invoice."""
        stmt = (
            select(self.model)
            .where(self.model.invoice_id == invoice_id)
            .order_by(self.model.order_index)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_items_total_gst(self, invoice_id: str) -> float:
        """Get total GST for invoice items."""
        stmt = select(func.sum(self.model.gst_amount)).where(
            self.model.invoice_id == invoice_id
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)


class FinanceLedgerRepository(BaseRepository[FinanceLedgerEntry]):
    """Financial ledger data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, FinanceLedgerEntry)

    async def get_invoice_entries(self, invoice_id: str) -> List[FinanceLedgerEntry]:
        """Get all ledger entries for invoice."""
        stmt = (
            select(self.model)
            .where(self.model.invoice_id == invoice_id)
            .order_by(desc(self.model.entry_date))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_entries_by_type(
        self, entry_type: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None
    ) -> List[FinanceLedgerEntry]:
        """Get ledger entries by type within date range."""
        filters = [self.model.entry_type == entry_type]
        if date_from:
            filters.append(self.model.entry_date >= date_from)
        if date_to:
            filters.append(self.model.entry_date <= date_to)

        stmt = (
            select(self.model)
            .where(and_(*filters))
            .order_by(desc(self.model.entry_date))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_debit(self, date_from: Optional[datetime] = None) -> float:
        """Get total debit amount."""
        filters = []
        if date_from:
            filters.append(self.model.entry_date >= date_from)

        stmt = select(func.sum(self.model.debit_amount))
        if filters:
            stmt = stmt.where(and_(*filters))
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)

    async def get_total_credit(self, date_from: Optional[datetime] = None) -> float:
        """Get total credit amount."""
        filters = []
        if date_from:
            filters.append(self.model.entry_date >= date_from)

        stmt = select(func.sum(self.model.credit_amount))
        if filters:
            stmt = stmt.where(and_(*filters))
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)

    async def get_balance(self, date_from: Optional[datetime] = None) -> float:
        """Get ledger balance (debit - credit)."""
        total_debit = await self.get_total_debit(date_from)
        total_credit = await self.get_total_credit(date_from)
        return total_debit - total_credit


class InvoicePaymentMappingRepository(BaseRepository[InvoicePaymentMapping]):
    """Invoice payment mapping data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InvoicePaymentMapping)

    async def get_invoice_mappings(self, invoice_id: str) -> List[InvoicePaymentMapping]:
        """Get all payment mappings for invoice."""
        stmt = (
            select(self.model)
            .where(self.model.invoice_id == invoice_id)
            .order_by(self.model.mapped_on)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_payment_plan_mappings(self, payment_plan_id: str) -> List[InvoicePaymentMapping]:
        """Get all invoices mapped to payment plan."""
        stmt = (
            select(self.model)
            .where(self.model.payment_plan_id == payment_plan_id)
            .order_by(self.model.mapped_on)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_mapping_total(self, invoice_id: str) -> float:
        """Get total amount mapped for invoice."""
        stmt = select(func.sum(self.model.mapped_amount)).where(
            self.model.invoice_id == invoice_id
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)
