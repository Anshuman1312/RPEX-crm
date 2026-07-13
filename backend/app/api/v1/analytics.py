from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.seo_keyword import SEOKeyword
from app.repositories.lead_repository import LeadRepository

router = APIRouter()


@router.get("/dashboard", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_ANALYTICS}))])
async def dashboard_metrics(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    lead_metrics = await LeadRepository(db).dashboard_metrics()

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

    return {
        **lead_metrics,
        "top_campaign": top_campaign_row[0] if top_campaign_row else None,
        "top_keyword": top_keyword_row[0] if top_keyword_row else None,
        "sales_performance": {
            "placeholder": True,
            "note": "Aggregate by assignee and conversions in later iteration",
        },
    }
