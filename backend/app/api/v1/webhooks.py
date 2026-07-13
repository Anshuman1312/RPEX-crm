from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.campaign import Campaign
from app.repositories.audit_repository import AuditRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.website_repository import WebsiteRepository
from app.schemas.lead import WebhookLeadIn
from app.services.lead_service import LeadService

router = APIRouter()


@router.post("/leads")
async def webhook_create_lead(
    payload: WebhookLeadIn,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    website = await WebsiteRepository(db).get_by_api_key(x_api_key)
    if not website:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    campaign_id = None
    if payload.campaign:
        stmt = select(Campaign).where(Campaign.name == payload.campaign)
        campaign = (await db.execute(stmt)).scalar_one_or_none()
        if campaign:
            campaign_id = campaign.id

    known = payload.model_dump(exclude_none=True)
    extra_data: dict[str, Any] = {}
    for key, value in known.items():
        if key not in {"name", "email", "phone", "source", "utm_medium"}:
            extra_data[key] = value

    lead_payload = {
        "website_id": website.id,
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone,
        "source": payload.source,
        "medium": payload.utm_medium,
        "campaign_id": campaign_id,
        "status": "NEW",
        "extra_data": extra_data,
    }

    service = LeadService(LeadRepository(db), AuditRepository(db))
    lead = await service.create_lead(lead_payload)
    return {"id": str(lead.id), "status": lead.status}
