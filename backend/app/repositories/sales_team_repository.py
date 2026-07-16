from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales_team_report import SalesTeamReport


class SalesTeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> SalesTeamReport:
        row = SalesTeamReport(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_reports(self, limit: int = 100) -> list[SalesTeamReport]:
        stmt = select(SalesTeamReport).order_by(SalesTeamReport.report_date.desc(), SalesTeamReport.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())
