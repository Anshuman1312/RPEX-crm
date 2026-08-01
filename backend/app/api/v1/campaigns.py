from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate
from app.services.campaign_service import CampaignService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def create_campaign(payload: CampaignCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    campaign = await CampaignService(CampaignRepository(db)).create(payload.model_dump(), str(current_user.id))
    return {"id": str(campaign.id), "name": campaign.name, "platform": campaign.platform}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CAMPAIGNS}))])
async def list_campaigns(_: CurrentUser, db: AsyncSession = Depends(get_db)):
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
