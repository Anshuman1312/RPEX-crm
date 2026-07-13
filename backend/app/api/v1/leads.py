import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.lead_saved_view_repository import LeadSavedViewRepository
from app.schemas.lead import LeadQueryFilters, LeadSavedViewCreate, LeadUpdateStatus
from app.services.lead_service import LeadService

router = APIRouter()


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_LEADS}))])
async def list_leads(
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
    q: str | None = Query(default=None),
    statuses: str | None = Query(default=None, description="Comma separated statuses"),
    source: str | None = Query(default=None),
    medium: str | None = Query(default=None),
    campaign_id: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    created_from: str | None = Query(default=None),
    created_to: str | None = Query(default=None),
    extra_filters: str | None = Query(default=None, description='JSON object, example: {"city":"Delhi"}'),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
):
    parsed_extra_filters = {}
    if extra_filters:
        try:
            parsed_extra_filters = json.loads(extra_filters)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON in extra_filters") from exc

    filters = LeadQueryFilters(
        q=q,
        statuses=[s.strip() for s in statuses.split(",")] if statuses else [],
        source=source,
        medium=medium,
        campaign_id=campaign_id,
        assigned_to=assigned_to,
        created_from=created_from,
        created_to=created_to,
        extra_field_filters=parsed_extra_filters,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    repo = LeadRepository(db)
    leads, total = await repo.search_leads(filters.model_dump())
    return {
        "items": [
            {
                "id": str(lead.id),
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "status": lead.status,
                "source": lead.source,
                "medium": lead.medium,
                "campaign_id": str(lead.campaign_id) if lead.campaign_id else None,
                "assigned_to": str(lead.assigned_to) if lead.assigned_to else None,
                "extra_data": lead.extra_data,
                "created_at": lead.created_at,
            }
            for lead in leads
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch("/{lead_id}/status", dependencies=[Depends(require_permissions({PERMISSIONS.EDIT_LEADS}))])
async def update_lead_status(
    lead_id: str,
    payload: LeadUpdateStatus,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(LeadRepository(db), AuditRepository(db))
    lead = await service.update_status(lead_id, str(current_user.id), payload.status, payload.description)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return {"id": str(lead.id), "status": lead.status}


@router.post("/views", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_LEADS}))])
async def create_saved_view(payload: LeadSavedViewCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await LeadSavedViewRepository(db).create(
        {
            "user_id": current_user.id,
            "name": payload.name,
            "filters": payload.filters,
            "is_public": payload.is_public,
        }
    )
    return {"id": str(row.id), "name": row.name, "is_public": row.is_public}


@router.get("/views", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_LEADS}))])
async def list_saved_views(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    rows = await LeadSavedViewRepository(db).list_for_user(str(current_user.id))
    return [
        {
            "id": str(row.id),
            "user_id": str(row.user_id),
            "name": row.name,
            "filters": row.filters,
            "is_public": row.is_public,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


@router.delete("/views/{view_id}", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_LEADS}))])
async def delete_saved_view(view_id: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    deleted = await LeadSavedViewRepository(db).delete_for_user(view_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved view not found")
    return {"deleted": True}
