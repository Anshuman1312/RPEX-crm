from app.models.site_visit import SiteVisit
from app.repositories.site_visit_repository import SiteVisitRepository


class SiteVisitService:
    def __init__(self, repo: SiteVisitRepository):
        self.repo = repo

    async def create(self, payload: dict, user_id: str) -> SiteVisit:
        row = SiteVisit(**payload, created_by=user_id)
        return await self.repo.create(row)
