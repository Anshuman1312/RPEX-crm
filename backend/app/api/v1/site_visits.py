from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.site_visit_repository import SiteVisitRepository
from app.schemas.site_visit import SiteVisitCreate
from app.services.site_visit_service import SiteVisitService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES}))])
async def create_site_visit(payload: SiteVisitCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await SiteVisitService(SiteVisitRepository(db)).create(payload.model_dump(), str(current_user.id))
    return {"id": str(row.id), "customer_name": row.customer_name, "attendance": row.attendance}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES}))])
async def list_site_visits(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=300, ge=1, le=1000)):
    rows = await SiteVisitRepository(db).list_all(limit=limit)
    return [
        {
            "id": str(row.id),
            "visit_date": row.visit_date,
            "visit_time": row.visit_time,
            "customer_name": row.customer_name,
            "sales_executive": row.sales_executive,
            "pickup_required": row.pickup_required,
            "vehicle_assigned": row.vehicle_assigned,
            "driver": row.driver,
            "attendance": row.attendance,
            "feedback": row.feedback,
            "outcome": row.outcome,
            "created_by": str(row.created_by),
            "created_at": row.created_at,
        }
        for row in rows
    ]
