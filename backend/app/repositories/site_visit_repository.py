from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_visit import SiteVisit
from app.repositories.base import BaseRepository


class SiteVisitRepository(BaseRepository[SiteVisit]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SiteVisit)

    async def create_visit(self, payload: dict, created_by: str | None = None) -> SiteVisit:
        return await super().create(
            **payload,
            created_by=UUID(str(created_by)) if created_by else payload.get("created_by"),
        )

    async def list_all(self, limit: int = 300) -> list[SiteVisit]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.visit_date), desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
