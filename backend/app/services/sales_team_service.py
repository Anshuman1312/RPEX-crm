from __future__ import annotations

from app.repositories.sales_team_repository import SalesTeamRepository


class SalesTeamService:
    def __init__(self, repo: SalesTeamRepository):
        self.repo = repo

    async def create_report(self, payload: dict):
        return await self.repo.create_report(payload)
