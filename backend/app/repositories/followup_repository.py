from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.followup import FollowUp


class FollowUpRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> FollowUp:
        row = FollowUp(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_by_assignee(self, user_id: str | None = None) -> list[FollowUp]:
        stmt = select(FollowUp).order_by(FollowUp.followup_date.asc())
        if user_id:
            stmt = stmt.where(FollowUp.assigned_to == user_id)
        return list((await self.db.execute(stmt)).scalars().all())
