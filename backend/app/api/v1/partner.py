from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cloudinary import signed_delivery_url
from app.core.config import get_settings
from app.core.deps import CurrentUser, get_current_permissions, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.finance_repository import FinanceRepository
from app.repositories.sales_repository import SalesRepository

router = APIRouter()
settings = get_settings()


@router.get("/dashboard", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_OWN_BOOKINGS_PAYMENTS}))])
async def partner_dashboard(
    current_user: CurrentUser,
    permissions: set[str] = Depends(get_current_permissions),
    db: AsyncSession = Depends(get_db),
):
    customer_repo = CustomerRepository(db)
    sales_repo = SalesRepository(db)
    finance_repo = FinanceRepository(db)
    document_repo = DocumentRepository(db)

    has_partner_scope = PERMISSIONS.ACCESS_PARTNER_PORTAL in permissions
    customers = await customer_repo.list_by_partner(str(current_user.id), limit=500) if has_partner_scope and hasattr(customer_repo, "list_by_partner") else []
    bookings = await sales_repo.list_bookings_by_partner(str(current_user.id), limit=500) if hasattr(sales_repo, "list_bookings_by_partner") else []
    payments = await finance_repo.list_payments_by_partner(str(current_user.id), limit=500) if hasattr(finance_repo, "list_payments_by_partner") else []
    documents = await document_repo.list_by_partner(str(current_user.id), limit=500) if has_partner_scope and hasattr(document_repo, "list_by_partner") else []

    total_booking_value = sum(float(getattr(row, "booking_value", 0)) for row in bookings)
    total_collections = sum(float(getattr(row, "amount", 0)) for row in payments)

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
    repo = CustomerRepository(db)
    rows = await repo.list_by_partner(str(current_user.id), limit=limit) if hasattr(repo, "list_by_partner") else []
    return [
        {
            "id": str(row.id),
            "full_name": getattr(row, "full_name", getattr(row, "name", "")),
            "email": row.email,
            "phone": row.phone,
            "city": getattr(row, "city", None),
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/bookings", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_OWN_BOOKINGS_PAYMENTS}))])
async def partner_bookings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    repo = SalesRepository(db)
    rows = await repo.list_bookings_by_partner(str(current_user.id), limit=limit) if hasattr(repo, "list_bookings_by_partner") else []
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "project_name": getattr(row, "project_name", None),
            "booking_value": getattr(row, "booking_value", 0),
            "booking_date": getattr(row, "booking_date", None),
            "status": getattr(row, "status", None),
        }
        for row in rows
    ]


@router.get("/payments", dependencies=[Depends(require_permissions({PERMISSIONS.VIEW_OWN_BOOKINGS_PAYMENTS}))])
async def partner_payments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    repo = FinanceRepository(db)
    rows = await repo.list_payments_by_partner(str(current_user.id), limit=limit) if hasattr(repo, "list_payments_by_partner") else []
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "amount": getattr(row, "amount", 0),
            "payment_date": getattr(row, "payment_date", None),
            "status": getattr(row, "status", None),
        }
        for row in rows
    ]


@router.get("/documents", dependencies=[Depends(require_permissions({PERMISSIONS.ACCESS_PARTNER_PORTAL}))])
async def partner_documents(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
):
    repo = DocumentRepository(db)
    rows = await repo.list_by_partner(str(current_user.id), limit=limit) if hasattr(repo, "list_by_partner") else []
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
            if getattr(settings, "cloudinary_cloud_name", None)
            else (row.file_metadata or {}).get("cloudinary_url"),
            "created_at": row.created_at,
        }
        for row in rows
    ]
