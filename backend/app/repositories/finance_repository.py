from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
