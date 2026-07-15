from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cloudinary import signed_delivery_url
from app.core.config import get_settings
from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.finance_repository import FinanceRepository
from app.repositories.sales_repository import SalesRepository

router = APIRouter()
settings = get_settings()


@router.get("/dashboard", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_dashboard(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    customer_repo = CustomerRepository(db)
    sales_repo = SalesRepository(db)
    finance_repo = FinanceRepository(db)
    document_repo = DocumentRepository(db)

    customers = await customer_repo.list_by_partner(str(current_user.id), limit=500)
    bookings = await sales_repo.list_bookings_by_partner(str(current_user.id), limit=500)
    payments = await finance_repo.list_payments_by_partner(str(current_user.id), limit=500)
    documents = await document_repo.list_by_partner(str(current_user.id), limit=500)

    total_booking_value = sum(float(row.booking_value) for row in bookings)
    total_collections = sum(float(row.amount) for row in payments)

    return {
        "customers": len(customers),
        "bookings": len(bookings),
        "payments": len(payments),
        "documents": len(documents),
        "total_booking_value": round(total_booking_value, 2),
        "total_collections": round(total_collections, 2),
    }


@router.get("/customers", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_customers(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await CustomerRepository(db).list_by_partner(str(current_user.id), limit=limit)
    return [
        {
            "id": str(row.id),
            "full_name": row.full_name,
            "email": row.email,
            "phone": row.phone,
            "city": row.city,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/bookings", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_bookings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await SalesRepository(db).list_bookings_by_partner(str(current_user.id), limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "project_name": row.project_name,
            "booking_value": row.booking_value,
            "booking_date": row.booking_date,
            "status": row.status,
        }
        for row in rows
    ]


@router.get("/payments", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_payments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await FinanceRepository(db).list_payments_by_partner(str(current_user.id), limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "amount": row.amount,
            "payment_date": row.payment_date,
            "status": row.status,
        }
        for row in rows
    ]


@router.get("/documents", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_documents(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await DocumentRepository(db).list_by_partner(str(current_user.id), limit=limit)
    return [
        {
            "id": str(row.id),
            "category": row.category,
            "file_name": row.file_name,
            "storage_key": row.storage_key,
            "signed_url": signed_delivery_url(
                row.storage_key,
                (row.file_metadata or {}).get("resource_type", "image"),
            )
            if settings.cloudinary_cloud_name
            else (row.file_metadata or {}).get("cloudinary_url"),
            "created_at": row.created_at,
        }
        for row in rows
    ]
