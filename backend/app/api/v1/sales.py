from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException, status
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
    booking_data = payload.model_dump()
    booking_extra = {
        "payment_method": booking_data.pop("payment_method", None),
        "receipt": booking_data.pop("receipt", None),
        "plot_number": booking_data.pop("plot_number", None),
        "agreement_date": booking_data.pop("agreement_date", None),
        "emi_details": booking_data.pop("emi_details", None),
        "loan_required": booking_data.pop("loan_required", False),
        "kyc_documents": booking_data.pop("kyc_documents", []),
    }
    booking_data["extra_data"] = {
        **(booking_data.get("extra_data") or {}),
        **{key: value for key, value in booking_extra.items() if value not in (None, "")},
    }

    service = SalesService(SalesRepository(db), AuditRepository(db))
    row = await service.create_booking(booking_data, str(current_user.id))
    return {
        "id": str(row.id),
        "customer_id": str(row.customer_id),
        "project_name": row.project_name,
        "plot_number": (row.extra_data or {}).get("plot_number") or row.unit_code,
        "booking_value": row.booking_value,
        "payment_method": (row.extra_data or {}).get("payment_method"),
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
            "plot_number": (row.extra_data or {}).get("plot_number") or row.unit_code,
            "booking_value": row.booking_value,
            "booking_date": row.booking_date,
            "payment_method": (row.extra_data or {}).get("payment_method"),
            "receipt": (row.extra_data or {}).get("receipt"),
            "agreement_date": (row.extra_data or {}).get("agreement_date"),
            "emi_details": (row.extra_data or {}).get("emi_details"),
            "loan_required": (row.extra_data or {}).get("loan_required", False),
            "kyc_documents": (row.extra_data or {}).get("kyc_documents", []),
            "status": row.status,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
        }
        for row in rows
    ]


@router.get("/bookings/{booking_id}/documents", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES}))])
async def generate_booking_documents(booking_id: str, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    booking = await SalesRepository(db).get_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    extra = booking.extra_data or {}
    booking_receipt = {
        "title": "Booking Receipt",
        "booking_id": str(booking.id),
        "customer_id": str(booking.customer_id),
        "project": booking.project_name,
        "plot_number": extra.get("plot_number") or booking.unit_code,
        "booking_amount": str(booking.booking_value),
        "payment_method": extra.get("payment_method"),
        "receipt_ref": extra.get("receipt"),
        "booking_date": booking.booking_date,
    }
    booking_form = {
        "title": "Booking Form",
        "customer_id": str(booking.customer_id),
        "project": booking.project_name,
        "plot_number": extra.get("plot_number") or booking.unit_code,
        "agreement_date": extra.get("agreement_date"),
        "loan_required": extra.get("loan_required", False),
        "emi_details": extra.get("emi_details"),
        "kyc_documents": extra.get("kyc_documents", []),
    }
    agreement_checklist = {
        "title": "Agreement Checklist",
        "items": [
            {"name": "Booking Amount Captured", "done": bool(booking.booking_value)},
            {"name": "Payment Method Captured", "done": bool(extra.get("payment_method"))},
            {"name": "Receipt Uploaded/Referenced", "done": bool(extra.get("receipt"))},
            {"name": "Agreement Date Captured", "done": bool(extra.get("agreement_date"))},
            {"name": "KYC Documents Added", "done": bool(extra.get("kyc_documents"))},
            {"name": "Loan Requirement Captured", "done": extra.get("loan_required") is not None},
        ],
    }

    return {
        "booking_receipt": booking_receipt,
        "booking_form": booking_form,
        "agreement_checklist": agreement_checklist,
    }
