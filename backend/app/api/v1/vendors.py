from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import VendorCreate
from app.services.vendor_service import VendorService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_VENDORS}))])
async def create_vendor(payload: VendorCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await VendorService(VendorRepository(db)).create(payload.model_dump())
    return {"id": str(row.id), "name": row.name, "category": row.category}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_VENDORS}))])
async def list_vendors(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=200, ge=1, le=500)):
    rows = await VendorRepository(db).list_vendors(limit=limit)
    return [
        {
            "id": str(row.id),
            "name": row.name,
            "category": row.category,
            "phone": row.phone,
            "email": row.email,
            "notes": row.notes,
        }
        for row in rows
    ]
