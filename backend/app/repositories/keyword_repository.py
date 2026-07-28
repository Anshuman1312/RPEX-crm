from __future__ import annotations

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seo_keyword import SEOKeyword
from app.repositories.base import BaseRepository


class KeywordRepository(BaseRepository[SEOKeyword]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SEOKeyword)

    @staticmethod
    def _normalize(row: SEOKeyword) -> SEOKeyword:
        row.url = getattr(row, "url", None)
        row.target_position = getattr(row, "target_position", None)
        row.current_position = getattr(row, "current_position", None)
        row.traffic = getattr(row, "traffic", 0)
        row.clicks = getattr(row, "clicks", 0)
        row.impressions = getattr(row, "impressions", 0)
        return row

    async def create_keyword(self, payload: dict) -> SEOKeyword:
        row = await super().create(**payload)
        return self._normalize(row)

    async def list_all(self) -> list[SEOKeyword]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.created_at))
        result = await self.session.execute(query)
        return [self._normalize(row) for row in result.scalars().all()]
