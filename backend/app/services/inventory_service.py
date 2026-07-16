from app.models.inventory_unit import InventoryUnit
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    async def create(self, payload: dict) -> InventoryUnit:
        row = InventoryUnit(**payload)
        return await self.repo.create(row)
