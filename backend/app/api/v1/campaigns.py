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
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "type": c.type,
            "platform": c.platform,
            "budget": str(c.budget),
            "start_date": c.start_date,
            "end_date": c.end_date,
            "channel": (c.extra_data or {}).get("channel") or c.type,
            "reach": int((c.extra_data or {}).get("reach") or 0),
            "leads": int((c.extra_data or {}).get("leads") or 0),
            "cpl": round(float(c.budget) / int((c.extra_data or {}).get("leads") or 0), 2)
            if int((c.extra_data or {}).get("leads") or 0)
            else 0,
            "roas": float((c.extra_data or {}).get("roas") or 0),
            "conversion": float((c.extra_data or {}).get("conversion") or 0),
        }
        for c in campaigns
    ]
