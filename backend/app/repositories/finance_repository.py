from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer_payment import CustomerPayment
from app.models.invoice import FinanceLedgerEntry, Invoice
from app.repositories.base import BaseRepository


class FinanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = BaseRepository(session, CustomerPayment)
        self.invoice_repo = BaseRepository(session, Invoice)
        self.ledger_repo = BaseRepository(session, FinanceLedgerEntry)

    @staticmethod
    def _coerce_uuid(value: str | None) -> UUID | None:
        return UUID(str(value)) if value else None

    @staticmethod
    def _normalize_payment(row: CustomerPayment) -> CustomerPayment:
        row.partner_user_id = getattr(row, "partner_user_id", None) or getattr(row, "created_by", None)
        return row

    @staticmethod
    def _normalize_invoice(row: Invoice) -> Invoice:
        row.amount = getattr(row, "amount", None) or row.total_amount
        row.status = getattr(row, "status", None) or row.payment_status
        row.partner_user_id = getattr(row, "partner_user_id", None) or getattr(row, "created_by", None)
        return row

    @staticmethod
    def _normalize_ledger(row: FinanceLedgerEntry) -> FinanceLedgerEntry:
        row.amount = getattr(row, "amount", None)
        if row.amount is None:
            debit = Decimal(str(row.debit_amount or 0))
            credit = Decimal(str(row.credit_amount or 0))
            row.amount = debit if debit else credit
        row.reference_no = getattr(row, "reference_no", None) or row.reference_number
        row.notes = getattr(row, "notes", None) or row.remarks
        row.status = getattr(row, "status", None) or "POSTED"
        row.extra_data = getattr(row, "extra_data", None) or {}
        return row

    async def create_payment(self, payload: dict[str, Any]) -> CustomerPayment:
        row = await self.payment_repo.create(
            customer_id=self._coerce_uuid(payload.get("customer_id")),
            booking_id=self._coerce_uuid(payload.get("booking_id")),
            amount=payload["amount"],
            payment_date=payload["payment_date"],
            payment_mode=payload["payment_mode"],
            reference_no=payload.get("reference_no"),
            status=payload.get("status", "RECEIVED"),
            notes=payload.get("notes"),
            created_by=self._coerce_uuid(payload.get("recorded_by") or payload.get("created_by")),
        )
        return self._normalize_payment(row)

    async def list_payments(self, limit: int = 100) -> list[CustomerPayment]:
        query = (
            select(CustomerPayment)
            .where(CustomerPayment.is_deleted == False)
            .order_by(desc(CustomerPayment.payment_date), desc(CustomerPayment.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self._normalize_payment(row) for row in result.scalars().all()]

    async def list_payments_by_partner(self, partner_user_id: str, limit: int = 100) -> list[CustomerPayment]:
        partner_uuid = self._coerce_uuid(partner_user_id)
        query = (
            select(CustomerPayment)
            .where(
                and_(
                    CustomerPayment.created_by == partner_uuid,
                    CustomerPayment.is_deleted == False,
                )
            )
            .order_by(desc(CustomerPayment.payment_date), desc(CustomerPayment.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self._normalize_payment(row) for row in result.scalars().all()]

    async def create_invoice(self, payload: dict[str, Any]) -> Invoice:
        row = await self.invoice_repo.create(
            invoice_number=payload["invoice_number"],
            booking_id=payload.get("booking_id"),
            customer_id=payload["customer_id"],
            project_id=payload.get("project_id"),
            invoice_date=payload["invoice_date"],
            due_date=payload["due_date"],
            subtotal=payload["subtotal"],
            gst_amount=payload["gst_amount"],
            total_amount=payload["total_amount"],
            paid_amount=payload.get("paid_amount", 0),
            payment_status=payload.get("payment_status", "PENDING"),
            invoice_status=payload.get("invoice_status", "DRAFT"),
            notes=payload.get("notes"),
            created_by=self._coerce_uuid(payload.get("created_by")),
        )
        return self._normalize_invoice(row)

    async def list_invoices(self, limit: int = 100) -> list[Invoice]:
        query = (
            select(Invoice)
            .where(Invoice.is_deleted == False)
            .order_by(desc(Invoice.invoice_date), desc(Invoice.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self._normalize_invoice(row) for row in result.scalars().all()]

    async def create_ledger_entry(self, payload: dict[str, Any]) -> FinanceLedgerEntry:
        row = await self.ledger_repo.create(
            invoice_id=payload.get("invoice_id"),
            entry_date=payload["entry_date"],
            entry_type=payload["entry_type"],
            description=payload["description"],
            debit_amount=payload.get("debit_amount", 0),
            credit_amount=payload.get("credit_amount", 0),
            account_code=payload.get("account_code"),
            reference_number=payload.get("reference_number") or payload.get("reference_no"),
            remarks=payload.get("remarks") or payload.get("notes"),
            posted_by_user_id=payload.get("created_by"),
            posted_on=payload.get("entry_date"),
            created_by=self._coerce_uuid(payload.get("created_by")),
        )
        return self._normalize_ledger(row)

    async def list_ledger_entries(self, entry_type: str | None = None, limit: int = 200) -> list[FinanceLedgerEntry]:
        filters = [FinanceLedgerEntry.is_deleted == False]
        if entry_type:
            filters.append(FinanceLedgerEntry.entry_type == entry_type)
        query = (
            select(FinanceLedgerEntry)
            .where(and_(*filters))
            .order_by(desc(FinanceLedgerEntry.entry_date), desc(FinanceLedgerEntry.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self._normalize_ledger(row) for row in result.scalars().all()]

    async def finance_snapshot(self) -> dict[str, Any]:
        payments_total = await self.session.scalar(
            select(func.coalesce(func.sum(CustomerPayment.amount), 0)).where(CustomerPayment.is_deleted == False)
        )
        invoices_total = await self.session.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(Invoice.is_deleted == False)
        )
        ledger_debit = await self.session.scalar(
            select(func.coalesce(func.sum(FinanceLedgerEntry.debit_amount), 0)).where(FinanceLedgerEntry.is_deleted == False)
        )
        ledger_credit = await self.session.scalar(
            select(func.coalesce(func.sum(FinanceLedgerEntry.credit_amount), 0)).where(FinanceLedgerEntry.is_deleted == False)
        )
        return {
            "payments_total": float(payments_total or 0),
            "invoices_total": float(invoices_total or 0),
            "ledger_debit_total": float(ledger_debit or 0),
            "ledger_credit_total": float(ledger_credit or 0),
            "profit_estimate": float((ledger_credit or 0) - (ledger_debit or 0)),
        }
