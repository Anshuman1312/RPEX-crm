from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_unit import InventoryUnit


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, row: InventoryUnit) -> InventoryUnit:
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_units(self, limit: int = 200, project_id: str | None = None) -> list[InventoryUnit]:
        stmt = select(InventoryUnit).order_by(InventoryUnit.created_at.desc()).limit(limit)
        if project_id:
            stmt = stmt.where(InventoryUnit.project_id == project_id)
        return list((await self.db.execute(stmt)).scalars().all())
