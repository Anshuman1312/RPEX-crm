from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.lead_activity import LeadActivity


class LeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict[str, Any]) -> Lead:
        lead = Lead(**payload)
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def list_leads(self, skip: int, limit: int, status: str | None = None) -> list[Lead]:
        stmt = select(Lead).offset(skip).limit(limit).order_by(Lead.created_at.desc())
        if status:
            stmt = stmt.where(Lead.status == status)
        return list((await self.db.execute(stmt)).scalars().all())

    async def search_leads(self, filters: dict[str, Any]) -> tuple[list[Lead], int]:
        stmt = select(Lead)

        q = filters.get("q")
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(or_(Lead.name.ilike(pattern), Lead.email.ilike(pattern), Lead.phone.ilike(pattern)))

        statuses = filters.get("statuses") or []
        if statuses:
            stmt = stmt.where(Lead.status.in_(statuses))

        if filters.get("source"):
            stmt = stmt.where(Lead.source == filters["source"])

        if filters.get("medium"):
            stmt = stmt.where(Lead.medium == filters["medium"])

        if filters.get("campaign_id"):
            stmt = stmt.where(Lead.campaign_id == filters["campaign_id"])

        if filters.get("assigned_to"):
            stmt = stmt.where(Lead.assigned_to == filters["assigned_to"])

        if filters.get("created_from"):
            stmt = stmt.where(Lead.created_at >= filters["created_from"])

        if filters.get("created_to"):
            stmt = stmt.where(Lead.created_at <= filters["created_to"])

        extra_field_filters = filters.get("extra_field_filters") or {}
        for key, value in extra_field_filters.items():
            stmt = stmt.where(Lead.extra_data.contains({key: value}))

        sort_map = {
            "created_at": Lead.created_at,
            "status": Lead.status,
            "name": Lead.name,
            "email": Lead.email,
            "source": Lead.source,
        }
        sort_by = sort_map.get(filters.get("sort_by", "created_at"), Lead.created_at)
        sort_order = filters.get("sort_order", "desc").lower()
        stmt = stmt.order_by(asc(sort_by) if sort_order == "asc" else desc(sort_by))

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(total_stmt)).scalar_one()

        page = max(int(filters.get("page", 1)), 1)
        page_size = min(max(int(filters.get("page_size", 50)), 1), 500)
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def update_status(self, lead: Lead, status: str) -> Lead:
        lead.status = status
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def get_by_id(self, lead_id: str) -> Lead | None:
        return await self.db.get(Lead, lead_id)

    async def add_activity(self, lead_id: str, user_id: str, activity_type: str, description: str) -> LeadActivity:
        activity = LeadActivity(lead_id=lead_id, user_id=user_id, activity_type=activity_type, description=description)
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def dashboard_metrics(self) -> dict[str, int | float]:
        today = datetime.now(timezone.utc).date()
        total = (await self.db.execute(select(func.count()).select_from(Lead))).scalar_one()
        today_count = (
            await self.db.execute(select(func.count()).select_from(Lead).where(func.date(Lead.created_at) == today))
        ).scalar_one()
        converted = (
            await self.db.execute(select(func.count()).select_from(Lead).where(Lead.status == "CONVERTED"))
        ).scalar_one()
        pending = (
            await self.db.execute(select(func.count()).select_from(Lead).where(and_(Lead.status != "CONVERTED", Lead.status != "LOST")))
        ).scalar_one()
        conversion_rate = round((converted / total) * 100, 2) if total else 0.0
        return {
            "total_leads": total,
            "today_leads": today_count,
            "converted_leads": converted,
            "pending_leads": pending,
            "conversion_rate": conversion_rate,
        }
