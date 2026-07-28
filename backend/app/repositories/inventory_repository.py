from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryUnit
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryUnit]):
	def __init__(self, session: AsyncSession):
		super().__init__(session, InventoryUnit)

	@staticmethod
	def _coerce_uuid(value: str | None) -> UUID | None:
		return UUID(str(value)) if value else None

	async def create_unit(self, payload: dict) -> InventoryUnit:
		return await super().create(
			project_id=self._coerce_uuid(payload.get("project_id")),
			plot_no=payload["plot_no"],
			size=payload.get("size"),
			facing=payload.get("facing"),
			is_corner=payload.get("is_corner", False),
			price=payload.get("price"),
			booking_status=payload.get("booking_status", "AVAILABLE"),
			customer_name=payload.get("customer_name"),
			sales_executive=payload.get("sales_executive"),
			booking_date=payload.get("booking_date"),
			agreement_status=payload.get("agreement_status"),
			payment_status=payload.get("payment_status"),
		)

	async def list_units(self, limit: int = 200, project_id: str | None = None) -> list[InventoryUnit]:
		filters = [self.model.is_deleted == False]
		project_uuid = self._coerce_uuid(project_id)
		if project_uuid:
			filters.append(self.model.project_id == project_uuid)

		query = (
			select(self.model)
			.where(and_(*filters))
			.order_by(desc(self.model.created_at))
			.limit(limit)
		)
		result = await self.session.execute(query)
		return result.scalars().all()

