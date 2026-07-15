from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict[str, Any]) -> Customer:
        row = Customer(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_customers(self, limit: int = 100) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_by_partner(self, partner_user_id: str, limit: int = 100) -> list[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.partner_user_id == partner_user_id)
            .order_by(Customer.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())
