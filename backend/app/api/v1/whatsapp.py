from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.whatsapp_repository import WhatsAppRepository
from app.schemas.whatsapp import WhatsAppInteractionCreate, WhatsAppTemplateCreate
from app.services.whatsapp_service import WhatsAppService

router = APIRouter()


@router.post("/templates", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WHATSAPP}))])
async def create_template(payload: WhatsAppTemplateCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await WhatsAppService(WhatsAppRepository(db)).create_template(payload.model_dump())
    return {"id": str(row.id), "name": row.name, "template_type": row.template_type}


@router.get("/templates", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WHATSAPP}))])
async def list_templates(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=200, ge=1, le=500)):
    rows = await WhatsAppRepository(db).list_templates(limit=limit)
    return [
        {"id": str(row.id), "name": row.name, "template_type": row.template_type, "body": row.body}
        for row in rows
    ]


@router.post("/interactions", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WHATSAPP}))])
async def create_interaction(payload: WhatsAppInteractionCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await WhatsAppService(WhatsAppRepository(db)).create_interaction(payload.model_dump())
    return {"id": str(row.id), "interaction_type": row.interaction_type, "phone": row.phone}


@router.get("/interactions", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WHATSAPP}))])
async def list_interactions(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=300, ge=1, le=500)):
    rows = await WhatsAppRepository(db).list_interactions(limit=limit)
    return [
        {
            "id": str(row.id),
            "interaction_type": row.interaction_type,
            "phone": row.phone,
            "message": row.message,
            "campaign_name": row.campaign_name,
            "direction": row.direction,
            "sent_at": row.sent_at,
        }
        for row in rows
    ]
