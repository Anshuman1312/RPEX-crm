from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor


class VendorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> Vendor:
        row = Vendor(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_vendors(self, limit: int = 200) -> list[Vendor]:
        stmt = select(Vendor).order_by(Vendor.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())
