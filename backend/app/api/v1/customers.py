from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate
from app.services.customer_service import CustomerService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CUSTOMERS}))])
async def create_customer(payload: CustomerCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = CustomerService(CustomerRepository(db), AuditRepository(db))
    row = await service.create_customer(
        {
            **payload.model_dump(),
            "created_by": current_user.id,
        },
        str(current_user.id),
    )
    return {
        "id": str(row.id),
        "full_name": row.full_name,
        "email": row.email,
        "phone": row.phone,
        "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
    }


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_CUSTOMERS}))])
async def list_customers(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await CustomerRepository(db).list_customers(limit=limit)
    return [
        {
            "id": str(row.id),
            "full_name": row.full_name,
            "email": row.email,
            "phone": row.phone,
            "city": row.city,
            "created_at": row.created_at,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
        }
        for row in rows
    ]
