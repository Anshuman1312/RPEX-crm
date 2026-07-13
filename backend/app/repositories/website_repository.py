import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.website import Website


class WebsiteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, domain: str, status: bool) -> Website:
        website = Website(name=name, domain=domain, status=status, api_key=secrets.token_urlsafe(32))
        self.db.add(website)
        await self.db.commit()
        await self.db.refresh(website)
        return website

    async def list_all(self) -> list[Website]:
        return list((await self.db.execute(select(Website))).scalars().all())

    async def get_by_api_key(self, api_key: str) -> Website | None:
        stmt = select(Website).where(Website.api_key == api_key, Website.status.is_(True))
        return (await self.db.execute(stmt)).scalar_one_or_none()
