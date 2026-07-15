from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.sales_repository import SalesRepository
from app.schemas.sales import BookingCreate
from app.services.sales_service import SalesService

router = APIRouter()


@router.post("/bookings", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES}))])
async def create_booking(payload: BookingCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SalesService(SalesRepository(db), AuditRepository(db))
    row = await service.create_booking(payload.model_dump(), str(current_user.id))
    return {
        "id": str(row.id),
        "customer_id": str(row.customer_id),
        "project_name": row.project_name,
        "booking_value": row.booking_value,
        "status": row.status,
    }


@router.get("/bookings", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES}))])
async def list_bookings(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await SalesRepository(db).list_bookings(limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "project_name": row.project_name,
            "booking_value": row.booking_value,
            "booking_date": row.booking_date,
            "status": row.status,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
        }
        for row in rows
    ]
