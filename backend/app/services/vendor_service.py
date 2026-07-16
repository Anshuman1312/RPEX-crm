from app.repositories.vendor_repository import VendorRepository


class VendorService:
    def __init__(self, repo: VendorRepository):
        self.repo = repo

    async def create(self, payload: dict):
        return await self.repo.create(payload)
