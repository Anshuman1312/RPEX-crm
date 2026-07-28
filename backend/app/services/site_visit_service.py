from __future__ import annotations

from app.repositories.site_visit_repository import SiteVisitRepository


class SiteVisitService:
    def __init__(self, repo: SiteVisitRepository):
        self.repo = repo

    async def create(self, payload: dict, created_by: str):
        return await self.repo.create_visit(payload, created_by)
