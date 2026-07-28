from __future__ import annotations

from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
	def __init__(self, repo: InventoryRepository):
		self.repo = repo

	async def create(self, payload: dict):
		return await self.repo.create_unit(payload)

