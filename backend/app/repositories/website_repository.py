from __future__ import annotations

import secrets

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.website import Website
from app.repositories.base import BaseRepository


class WebsiteRepository(BaseRepository[Website]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Website)

    async def create(self, name: str, domain: str, status: bool = True) -> Website:
        return await super().create(
            name=name,
            domain=domain,
            status=status,
            api_key=secrets.token_urlsafe(24),
        )

    async def get_by_api_key(self, api_key: str) -> Website | None:
        query = select(self.model).where(and_(self.model.api_key == api_key, self.model.is_deleted == False))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_all(self) -> list[Website]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.created_at))
        result = await self.session.execute(query)
        return result.scalars().all()
