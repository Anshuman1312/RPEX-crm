from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seo_keyword import SEOKeyword


class KeywordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, keyword: SEOKeyword) -> SEOKeyword:
        self.db.add(keyword)
        await self.db.commit()
        await self.db.refresh(keyword)
        return keyword

    async def list_all(self) -> list[SEOKeyword]:
        return list((await self.db.execute(select(SEOKeyword).order_by(SEOKeyword.created_at.desc()))).scalars().all())
