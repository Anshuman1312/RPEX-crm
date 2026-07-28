from __future__ import annotations

from app.repositories.telecalling_repository import TelecallingRepository


class TelecallingService:
    def __init__(self, repo: TelecallingRepository):
        self.repo = repo

    async def create_call(self, payload: dict):
        return await self.repo.create_call(payload)
