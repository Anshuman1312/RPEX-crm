from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance_ledger_entry import FinanceLedgerEntry
from app.models.customer_payment import CustomerPayment
from app.models.invoice import Invoice


class FinanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payload: dict[str, Any]) -> CustomerPayment:
        row = CustomerPayment(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_payments(self, limit: int = 100) -> list[CustomerPayment]:
        stmt = select(CustomerPayment).order_by(CustomerPayment.payment_date.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_payments_by_partner(self, partner_user_id: str, limit: int = 100) -> list[CustomerPayment]:
        stmt = (
            select(CustomerPayment)
            .where(CustomerPayment.partner_user_id == partner_user_id)
            .order_by(CustomerPayment.payment_date.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def create_invoice(self, payload: dict[str, Any]) -> Invoice:
        row = Invoice(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_invoices(self, limit: int = 100) -> list[Invoice]:
        stmt = select(Invoice).order_by(Invoice.invoice_date.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_invoices_by_partner(self, partner_user_id: str, limit: int = 100) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.partner_user_id == partner_user_id)
            .order_by(Invoice.invoice_date.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def create_ledger_entry(self, payload: dict[str, Any]) -> FinanceLedgerEntry:
        row = FinanceLedgerEntry(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_ledger_entries(self, entry_type: str | None = None, limit: int = 200) -> list[FinanceLedgerEntry]:
        stmt = select(FinanceLedgerEntry)
        if entry_type:
            stmt = stmt.where(FinanceLedgerEntry.entry_type == entry_type)
        stmt = stmt.order_by(FinanceLedgerEntry.entry_date.desc(), FinanceLedgerEntry.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def finance_snapshot(self) -> dict:
        customer_payments = (
            await self.db.execute(select(func.coalesce(func.sum(CustomerPayment.amount), 0)).select_from(CustomerPayment))
        ).scalar_one()
        invoice_value = (
            await self.db.execute(select(func.coalesce(func.sum(Invoice.amount), 0)).select_from(Invoice))
        ).scalar_one()

        def sum_by(entry_type: str):
            return self.db.execute(
                select(func.coalesce(func.sum(FinanceLedgerEntry.amount), 0)).where(FinanceLedgerEntry.entry_type == entry_type)
            )

        developer_payments = (await sum_by("DEVELOPER_PAYMENT")).scalar_one()
        marketing_expenses = (await sum_by("MARKETING_EXPENSE")).scalar_one()
        commissions = (await sum_by("COMMISSION")).scalar_one()
        vendor_payments = (await sum_by("VENDOR_PAYMENT")).scalar_one()
        receipts = (await sum_by("RECEIPT")).scalar_one()
        gst = (await sum_by("GST")).scalar_one()

        total_income = float(customer_payments) + float(receipts)
        total_expense = float(developer_payments) + float(marketing_expenses) + float(commissions) + float(vendor_payments) + float(gst)
        profit = total_income - total_expense

        return {
            "customer_payments": round(float(customer_payments), 2),
            "invoice_value": round(float(invoice_value), 2),
            "developer_payments": round(float(developer_payments), 2),
            "marketing_expenses": round(float(marketing_expenses), 2),
            "commissions": round(float(commissions), 2),
            "vendor_payments": round(float(vendor_payments), 2),
            "receipts": round(float(receipts), 2),
            "gst": round(float(gst), 2),
            "profit": round(float(profit), 2),
        }
