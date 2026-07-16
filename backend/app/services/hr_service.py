from app.repositories.hr_repository import HRRepository


class HRService:
    def __init__(self, repo: HRRepository):
        self.repo = repo

    async def create_employee(self, payload: dict):
        return await self.repo.create_employee(payload)

    async def create_record(self, payload: dict):
        return await self.repo.create_record(payload)
