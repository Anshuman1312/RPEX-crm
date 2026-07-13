from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead_saved_view import LeadSavedView


class LeadSavedViewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> LeadSavedView:
        row = LeadSavedView(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_for_user(self, user_id: str) -> list[LeadSavedView]:
        stmt = (
            select(LeadSavedView)
            .where(or_(LeadSavedView.user_id == user_id, LeadSavedView.is_public.is_(True)))
            .order_by(LeadSavedView.updated_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def delete_for_user(self, view_id: str, user_id: str) -> bool:
        row = await self.db.get(LeadSavedView, view_id)
        if not row or str(row.user_id) != user_id:
            return False
        await self.db.delete(row)
        await self.db.commit()
        return True
