from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Campaign)

    async def list_all(self) -> list[Campaign]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.created_at))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, payload: dict[str, Any], created_by_user_id: str | None = None) -> Campaign:
        instance = self.model(**payload)
        if created_by_user_id:
            instance.created_by = UUID(str(created_by_user_id))
        self.session.add(instance)
        await self.session.flush()
        return instance
