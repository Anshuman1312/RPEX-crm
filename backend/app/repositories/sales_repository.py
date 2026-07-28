from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import SalesBooking
from app.repositories.base import BaseRepository


class SalesRepository(BaseRepository[SalesBooking]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SalesBooking)

    @staticmethod
    def _coerce_uuid(value: str | None) -> UUID | None:
        return UUID(str(value)) if value else None

    async def create_booking(self, payload: dict) -> SalesBooking:
        return await super().create(
            customer_id=self._coerce_uuid(payload.get("customer_id")),
            project_name=payload.get("project_name") or "",
            unit_code=payload.get("unit_code") or payload.get("plot_number") or "",
            booking_value=payload.get("booking_value") or 0,
            booking_date=payload.get("booking_date"),
            status=payload.get("status") or "NEW",
            partner_user_id=self._coerce_uuid(payload.get("partner_user_id")),
            extra_data=payload.get("extra_data") or {},
        )

    async def list_bookings(self, limit: int = 100) -> list[SalesBooking]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_bookings_by_partner(self, partner_user_id: str, limit: int = 100) -> list[SalesBooking]:
        query = (
            select(self.model)
            .where(and_(self.model.partner_user_id == self._coerce_uuid(partner_user_id), self.model.is_deleted == False))
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
