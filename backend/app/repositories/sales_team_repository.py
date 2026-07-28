from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales_team import SalesTeamReport
from app.repositories.base import BaseRepository


class SalesTeamRepository(BaseRepository[SalesTeamReport]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SalesTeamReport)

    async def create_report(self, payload: dict) -> SalesTeamReport:
        return await super().create(**payload)

    async def list_reports(self, limit: int = 100) -> list[SalesTeamReport]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.report_date), desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
