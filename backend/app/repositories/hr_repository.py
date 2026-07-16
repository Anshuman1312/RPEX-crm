from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr_employee import HREmployee
from app.models.hr_record import HRRecord


class HRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_employee(self, payload: dict) -> HREmployee:
        row = HREmployee(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_employees(self, limit: int = 100) -> list[HREmployee]:
        stmt = select(HREmployee).order_by(HREmployee.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def create_record(self, payload: dict) -> HRRecord:
        row = HRRecord(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_records(self, limit: int = 200) -> list[HRRecord]:
        stmt = select(HRRecord).order_by(HRRecord.record_date.desc(), HRRecord.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())
