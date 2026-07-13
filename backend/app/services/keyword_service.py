from app.models.seo_keyword import SEOKeyword
from app.repositories.keyword_repository import KeywordRepository


class KeywordService:
    def __init__(self, repo: KeywordRepository):
        self.repo = repo

    async def create(self, payload: dict) -> SEOKeyword:
        keyword = SEOKeyword(**payload)
        return await self.repo.create(keyword)
