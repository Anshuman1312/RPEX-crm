from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository
from app.schemas.finance import CustomerPaymentCreate, InvoiceCreate
from app.services.finance_service import FinanceService

router = APIRouter()


@router.post("/payments", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def create_payment(payload: CustomerPaymentCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = FinanceService(FinanceRepository(db), AuditRepository(db))
    row = await service.create_payment(
        {
            **payload.model_dump(),
            "recorded_by": current_user.id,
        },
        str(current_user.id),
    )
    return {
        "id": str(row.id),
        "customer_id": str(row.customer_id),
        "amount": row.amount,
        "status": row.status,
    }


@router.get("/payments", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def list_payments(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await FinanceRepository(db).list_payments(limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "booking_id": str(row.booking_id) if row.booking_id else None,
            "amount": row.amount,
            "payment_date": row.payment_date,
            "payment_mode": row.payment_mode,
            "status": row.status,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
        }
        for row in rows
    ]


@router.post("/invoices", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def create_invoice(payload: InvoiceCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = FinanceService(FinanceRepository(db), AuditRepository(db))
    row = await service.create_invoice(
        {
            **payload.model_dump(),
            "created_by": current_user.id,
        },
        str(current_user.id),
    )
    return {
        "id": str(row.id),
        "invoice_number": row.invoice_number,
        "amount": row.amount,
        "status": row.status,
    }


@router.get("/invoices", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def list_invoices(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await FinanceRepository(db).list_invoices(limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id),
            "booking_id": str(row.booking_id) if row.booking_id else None,
            "invoice_number": row.invoice_number,
            "invoice_date": row.invoice_date,
            "amount": row.amount,
            "gst_amount": row.gst_amount,
            "status": row.status,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
        }
        for row in rows
    ]
