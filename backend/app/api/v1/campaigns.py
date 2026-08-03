from fastapi import APIRouter, Depends, Body
from datetime import date
from fastapi import Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate
from app.services.campaign_service import CampaignService

router = APIRouter()


@router.get("/stats/kpis", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def get_campaign_kpis(
    _: CurrentUser,
    statuses: str = Query(None, description="Comma-separated campaign statuses: active, upcoming, ended"),
    priorities: str = Query(None, description="Comma-separated priorities (not applicable for campaigns)"),
    sources: str = Query(None, description="Comma-separated campaign platforms"),
    db: AsyncSession = Depends(get_db),
):
    """Get campaign KPIs with optional status/source filters."""
    today = date.today()
    status_values = [s.strip().lower() for s in statuses.split(",") if s.strip()] if statuses else None
    source_values = [s.strip().lower() for s in sources.split(",") if s.strip()] if sources else None
    priority_values = [p.strip().lower() for p in priorities.split(",") if p.strip()] if priorities else None

    active_condition = and_(Campaign.start_date.is_not(None), Campaign.start_date <= today, or_(Campaign.end_date.is_(None), Campaign.end_date >= today))
    upcoming_condition = and_(Campaign.start_date.is_not(None), Campaign.start_date > today)
    ended_condition = and_(Campaign.end_date.is_not(None), Campaign.end_date < today)

    filters = [Campaign.is_deleted == False]

    if source_values:
        filters.append(func.lower(Campaign.platform).in_(source_values))

    if status_values:
        status_conditions = []
        if "active" in status_values:
            status_conditions.append(active_condition)
        if "upcoming" in status_values:
            status_conditions.append(upcoming_condition)
        if "ended" in status_values:
            status_conditions.append(ended_condition)
        if status_conditions:
            filters.append(or_(*status_conditions))

    query = select(
        func.count(Campaign.id).label("total_campaigns"),
        func.count(Campaign.id).filter(active_condition).label("active_campaigns"),
        func.count(Campaign.id).filter(upcoming_condition).label("upcoming_campaigns"),
        func.count(Campaign.id).filter(ended_condition).label("ended_campaigns"),
    ).where(and_(*filters))

    row = (await db.execute(query)).one()

    return {
        "total_campaigns": row.total_campaigns or 0,
        "active_campaigns": row.active_campaigns or 0,
        "upcoming_campaigns": row.upcoming_campaigns or 0,
        "ended_campaigns": row.ended_campaigns or 0,
        "filters_applied": {
            "statuses": status_values,
            "priorities": priority_values,
            "sources": source_values,
            "ignored_filters": ["priorities"] if priority_values else [],
        },
    }


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def create_campaign(payload: CampaignCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    """Create a new campaign."""
    campaign = await CampaignService(db).create(payload.model_dump(), str(current_user.id))
    return {"id": str(campaign.id), "name": campaign.name, "platform": campaign.platform}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def list_campaigns(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    """List all campaigns with metrics."""
    campaigns = await CampaignRepository(db).list_all()
    result = []
    for c in campaigns:
        extra_data = c.extra_data or {}
        
        # Safe type conversions with error handling
        try:
            leads = int(extra_data.get("leads") or 0)
            reach = int(extra_data.get("reach") or 0)
            roas = float(extra_data.get("roas") or 0)
            conversion = float(extra_data.get("conversion") or 0)
            budget = float(c.budget) if c.budget else 0
        except (ValueError, TypeError):
            # Default safe values if conversion fails
            leads = reach = 0
            roas = conversion = 0.0
            budget = 0.0
        
        # Calculate CPL safely - avoid division by zero
        cpl = round(budget / leads, 2) if leads > 0 else 0
        
        result.append({
            "id": str(c.id),
            "name": c.name or "",
            "type": c.type or "",
            "platform": c.platform or "",
            "budget": str(c.budget),
            "start_date": c.start_date,
            "end_date": c.end_date,
            "channel": extra_data.get("channel") or c.type,
            "reach": reach,
            "leads": leads,
            "cpl": cpl,
            "roas": roas,
            "conversion": conversion,
        })
    return result


@router.post("/{campaign_id}/execute", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def execute_campaign(
    campaign_id: str,
    current_user: CurrentUser,
    target_filters: dict = Body(None, description="Optional filters for targeting leads/customers"),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a campaign on its configured platform.
    
    The campaign will be sent to all relevant leads and customers based on the platform:
    - WhatsApp: Uses phone numbers and templates
    - Email: Uses email addresses and HTML/text content
    - SMS: Uses phone numbers for text messages
    - Notification: Sends in-app notifications
    
    Args:
        campaign_id: Campaign ID to execute
        target_filters: Optional filters for targeting (e.g., {"status": "active"})
    
    Returns:
        Execution result with metrics (sent count, failed count, reach, etc.)
    """
    campaign_service = CampaignService(db)
    result = await campaign_service.execute_campaign(campaign_id, str(current_user.id), target_filters)
    return result


@router.get("/{campaign_id}/performance", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def get_campaign_performance(
    campaign_id: str,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed campaign performance metrics.
    
    Returns:
        Performance data including reach, sent count, leads, budget, ROI, etc.
    """
    campaign_service = CampaignService(db)
    performance = await campaign_service.get_campaign_performance(campaign_id)
    return performance
