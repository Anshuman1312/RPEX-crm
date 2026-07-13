from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign


class CampaignRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, campaign: Campaign) -> Campaign:
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def list_all(self) -> list[Campaign]:
        return list((await self.db.execute(select(Campaign).order_by(Campaign.created_at.desc()))).scalars().all())
