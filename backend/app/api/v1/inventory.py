from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryUnitCreate
from app.services.inventory_service import InventoryService

router = APIRouter()

STATUS_COLOR_MAP = {
    "AVAILABLE": "GREEN",
    "HOLD": "YELLOW",
    "BOOKED": "BLUE",
    "SOLD": "RED",
}


def _normalize_status(status: str) -> str:
    normalized = (status or "").strip().upper()
    return normalized if normalized in STATUS_COLOR_MAP else "AVAILABLE"


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_INVENTORY}))])
async def create_inventory_unit(payload: InventoryUnitCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    data["booking_status"] = _normalize_status(data.get("booking_status", "AVAILABLE"))
    row = await InventoryService(InventoryRepository(db)).create(data)
    return {
        "id": str(row.id),
        "plot_no": row.plot_no,
        "booking_status": row.booking_status,
        "color_code": STATUS_COLOR_MAP[row.booking_status],
    }


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_INVENTORY}))])
async def list_inventory_units(
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=200, ge=1, le=1000),
    project_id: str | None = Query(default=None),
):
    rows = await InventoryRepository(db).list_units(limit=limit, project_id=project_id)
    return [
        {
            "id": str(row.id),
            "project_id": str(row.project_id),
            "plot_no": row.plot_no,
            "size": row.size,
            "facing": row.facing,
            "is_corner": row.is_corner,
            "corner_or_normal": "CORNER" if row.is_corner else "NORMAL",
            "price": row.price,
            "booking_status": row.booking_status,
            "customer_name": row.customer_name,
            "sales_executive": row.sales_executive,
            "booking_date": row.booking_date,
            "agreement_status": row.agreement_status,
            "payment_status": row.payment_status,
            "color_code": STATUS_COLOR_MAP.get(row.booking_status, "GREEN"),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]
