from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking


class SalesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(self, payload: dict[str, Any]) -> Booking:
        row = Booking(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_bookings(self, limit: int = 100) -> list[Booking]:
        stmt = select(Booking).order_by(Booking.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_bookings_by_partner(self, partner_user_id: str, limit: int = 100) -> list[Booking]:
        stmt = (
            select(Booking)
            .where(Booking.partner_user_id == partner_user_id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_id(self, booking_id: str) -> Booking | None:
        return await self.db.get(Booking, booking_id)
