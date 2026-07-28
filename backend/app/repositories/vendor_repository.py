from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.repositories.base import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Vendor)

    async def create_vendor(self, payload: dict) -> Vendor:
        return await super().create(**payload)

    async def list_vendors(self, limit: int = 200) -> list[Vendor]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
