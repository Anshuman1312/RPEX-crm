from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_visit import SiteVisit


class SiteVisitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, row: SiteVisit) -> SiteVisit:
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_all(self, limit: int = 300) -> list[SiteVisit]:
        stmt = select(SiteVisit).order_by(SiteVisit.visit_date.desc(), SiteVisit.visit_time.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())
