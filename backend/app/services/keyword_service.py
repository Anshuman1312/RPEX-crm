from __future__ import annotations

from app.repositories.keyword_repository import KeywordRepository


class KeywordService:
    def __init__(self, repo: KeywordRepository):
        self.repo = repo

    async def create(self, payload: dict):
        return await self.repo.create_keyword(payload)
