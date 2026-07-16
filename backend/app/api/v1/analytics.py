from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.booking import Booking
from app.models.campaign import Campaign
from app.models.customer_payment import CustomerPayment
from app.models.followup import FollowUp
from app.models.lead import Lead
from app.models.seo_keyword import SEOKeyword
from app.models.user import User
from app.repositories.lead_repository import LeadRepository

router = APIRouter()


@router.get("/dashboard", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_ANALYTICS}))])
async def dashboard_metrics(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    lead_metrics = await LeadRepository(db).dashboard_metrics()

    bookings_count = (
        await db.execute(select(func.count()).select_from(Booking))
    ).scalar_one()
    sales_value = (
        await db.execute(select(func.coalesce(func.sum(Booking.booking_value), 0)).select_from(Booking))
    ).scalar_one()
    revenue = (
        await db.execute(select(func.coalesce(func.sum(CustomerPayment.amount), 0)).select_from(CustomerPayment))
    ).scalar_one()
    marketing_spend = (
        await db.execute(select(func.coalesce(func.sum(Campaign.budget), 0)).select_from(Campaign))
    ).scalar_one()
    pending_followups = (
        await db.execute(
            select(func.count())
            .select_from(FollowUp)
            .where(FollowUp.status.in_(["PENDING", "SCHEDULED"]))
        )
    ).scalar_one()

    # Site visits are approximated by today's lead captures until a dedicated visits table is added.
    site_visits_today = lead_metrics["today_leads"]

    total_leads = int(lead_metrics["total_leads"])
    cpl = float(marketing_spend) / total_leads if total_leads else 0.0

    top_campaign_row = (
        await db.execute(
            select(Campaign.name, func.count(Lead.id).label("lead_count"))
            .join(Lead, Lead.campaign_id == Campaign.id)
            .group_by(Campaign.name)
            .order_by(func.count(Lead.id).desc())
            .limit(1)
        )
    ).first()

    top_keyword_row = (
        await db.execute(
            select(SEOKeyword.keyword, SEOKeyword.traffic)
            .order_by(SEOKeyword.traffic.desc())
            .limit(1)
        )
    ).first()

    lead_perf_rows = (
        await db.execute(
            select(
                Lead.assigned_to.label("user_id"),
                func.count(Lead.id).label("assigned_leads"),
                func.sum(func.case((Lead.status == "BOOKING", 1), else_=0)).label("converted_leads"),
            )
            .where(Lead.assigned_to.is_not(None))
            .group_by(Lead.assigned_to)
        )
    ).all()

    booking_perf_rows = (
        await db.execute(
            select(
                Booking.sales_executive_id.label("user_id"),
                func.count(Booking.id).label("bookings"),
                func.coalesce(func.sum(Booking.booking_value), 0).label("sales_value"),
            )
            .where(Booking.sales_executive_id.is_not(None))
            .group_by(Booking.sales_executive_id)
        )
    ).all()

    team_stats: dict[str, dict] = {}
    user_ids: set[str] = set()

    for row in lead_perf_rows:
        if not row.user_id:
            continue
        user_id = str(row.user_id)
        user_ids.add(user_id)
        team_stats[user_id] = {
            "user_id": user_id,
            "name": "Unknown",
            "assigned_leads": int(row.assigned_leads or 0),
            "converted_leads": int(row.converted_leads or 0),
            "bookings": 0,
            "sales_value": 0.0,
        }

    for row in booking_perf_rows:
        if not row.user_id:
            continue
        user_id = str(row.user_id)
        user_ids.add(user_id)
        existing = team_stats.get(
            user_id,
            {
                "user_id": user_id,
                "name": "Unknown",
                "assigned_leads": 0,
                "converted_leads": 0,
                "bookings": 0,
                "sales_value": 0.0,
            },
        )
        existing["bookings"] = int(row.bookings or 0)
        existing["sales_value"] = float(row.sales_value or 0)
        team_stats[user_id] = existing

    if user_ids:
        users = (
            await db.execute(select(User.id, User.name).where(User.id.in_(list(user_ids))))
        ).all()
        for user in users:
            key = str(user.id)
            if key in team_stats:
                team_stats[key]["name"] = user.name

    sales_team_performance = []
    for stat in team_stats.values():
        assigned_leads = stat["assigned_leads"]
        converted_leads = stat["converted_leads"]
        conversion_rate = round((converted_leads / assigned_leads) * 100, 2) if assigned_leads else 0.0
        sales_team_performance.append(
            {
                **stat,
                "conversion_rate": conversion_rate,
            }
        )

    sales_team_performance.sort(key=lambda row: (row["sales_value"], row["converted_leads"]), reverse=True)

    return {
        **lead_metrics,
        "new_leads_today": lead_metrics["today_leads"],
        "site_visits_today": site_visits_today,
        "bookings": int(bookings_count),
        "sales_value": round(float(sales_value), 2),
        "revenue": round(float(revenue), 2),
        "marketing_spend": round(float(marketing_spend), 2),
        "cpl": round(cpl, 2),
        "pending_followups": int(pending_followups),
        "top_campaign": top_campaign_row[0] if top_campaign_row else None,
        "top_keyword": top_keyword_row[0] if top_keyword_row else None,
        "sales_team_performance": sales_team_performance,
    }
