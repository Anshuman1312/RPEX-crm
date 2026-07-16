from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.booking import Booking
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.user import User
from app.schemas.ai import AIAskRequest

router = APIRouter()


@router.post("/ask", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_ANALYTICS}))])
async def ask_ai(payload: AIAskRequest, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    q = payload.question.lower().strip()

    if "hot leads" in q:
        rows = (
            await db.execute(
                select(Lead.id, Lead.name, Lead.status, Lead.created_at)
                .where(Lead.status.in_(["INTERESTED", "SITE_VISIT", "NEGOTIATION"]))
                .order_by(Lead.created_at.desc())
                .limit(10)
            )
        ).all()
        return {
            "answer": "Top hot leads based on active pipeline stages.",
            "data": [{"id": str(r.id), "name": r.name, "status": r.status, "created_at": r.created_at} for r in rows],
        }

    if "closed the most deals" in q:
        rows = (
            await db.execute(
                select(User.name, func.count(Booking.id).label("bookings"))
                .join(Booking, Booking.sales_executive_id == User.id)
                .group_by(User.name)
                .order_by(func.count(Booking.id).desc())
                .limit(1)
            )
        ).first()
        return {"answer": "Top deal closer.", "data": rows._asdict() if rows else {}}

    if "conversion rate from facebook" in q:
        total = (
            await db.execute(select(func.count()).select_from(Lead).where(func.lower(Lead.source) == "facebook"))
        ).scalar_one()
        converted = (
            await db.execute(
                select(func.count()).select_from(Lead).where(func.lower(Lead.source) == "facebook", Lead.status == "BOOKING")
            )
        ).scalar_one()
        rate = round((converted / total) * 100, 2) if total else 0
        return {"answer": "Facebook conversion rate computed.", "data": {"total": total, "converted": converted, "conversion_rate": rate}}

    if "campaign generated the most bookings" in q:
        rows = (
            await db.execute(
                select(Campaign.name, func.count(Lead.id).label("bookings"))
                .join(Lead, Lead.campaign_id == Campaign.id)
                .where(Lead.status == "BOOKING")
                .group_by(Campaign.name)
                .order_by(func.count(Lead.id).desc())
                .limit(1)
            )
        ).first()
        return {"answer": "Top campaign by bookings.", "data": rows._asdict() if rows else {}}

    if "predict sales" in q:
        month_start = datetime.now(timezone.utc).date().replace(day=1)
        sales = (
            await db.execute(select(func.coalesce(func.sum(Booking.booking_value), 0)).where(Booking.booking_date >= month_start))
        ).scalar_one()
        prediction = round(float(sales) * 1.15, 2)
        return {"answer": "Simple trend-based sales prediction for this month.", "data": {"current_sales": float(sales), "predicted_sales": prediction}}

    if "follow-up priority" in q:
        rows = (
            await db.execute(
                select(Lead.id, Lead.name, Lead.status, Lead.created_at)
                .where(Lead.status.in_(["NEGOTIATION", "SITE_VISIT", "INTERESTED"]))
                .order_by(Lead.created_at.asc())
                .limit(10)
            )
        ).all()
        return {
            "answer": "Suggested follow-up priority list.",
            "data": [{"id": str(r.id), "name": r.name, "status": r.status, "created_at": r.created_at} for r in rows],
        }

    return {"answer": "Try asking about hot leads, top closer, Facebook conversion, top campaign, sales prediction, or follow-up priority.", "data": {}}
