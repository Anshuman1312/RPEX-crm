"""
FastAPI routes for invoice and finance management.

Endpoints:
- Invoice CRUD: POST/GET/PATCH/DELETE
- Status management: POST /send, POST /cancel
- Payment tracking: POST /payments, GET /payment-summary
- Items: POST/GET items
- Payment mappings: POST/GET mappings
- Financial reports: GET /stats, /overdue, /due-soon
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceItemCreate,
    InvoiceItemResponse,
    InvoicePaymentReceived,
    InvoicePaymentMappingCreate,
    InvoicePaymentMappingResponse,
    FinanceLedgerEntryResponse,
    InvoiceSummary,
    CustomerInvoiceSummary,
)
from app.services.invoice_service import InvoiceService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


# ── Invoice CRUD ──────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_invoice(
    request: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new invoice. Requires invoices.create permission."""
    service = InvoiceService(session)

    invoice = await service.create_invoice(
        customer_id=request.customer_id,
        due_date=request.due_date,
        items=[item.model_dump() for item in request.items],
        booking_id=request.booking_id,
        project_id=request.project_id,
        notes=request.notes,
        created_by=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Invoice created | id={invoice.id} | number={invoice.invoice_number} | customer={request.customer_id}")

    return created(
        data=InvoiceResponse.model_validate(invoice).__dict__,
        message="Invoice created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_invoices(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    customer_id: str = Query(None),
    payment_statuses: str = Query(None, description="Comma-separated payment statuses"),
    invoice_statuses: str = Query(None, description="Comma-separated invoice statuses"),
    search: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List invoices with filtering and pagination."""
    service = InvoiceService(session)

    invoices, total = await service.list_invoices(
        customer_id=customer_id,
        payment_statuses=payment_statuses.split(",") if payment_statuses else None,
        invoice_statuses=invoice_statuses.split(",") if invoice_statuses else None,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    data = [InvoiceListResponse.model_validate(i).__dict__ for i in invoices]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{invoice_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get invoice with all details."""
    service = InvoiceService(session)
    invoice = await service.get_invoice(invoice_id)

    return ok(data=InvoiceResponse.model_validate(invoice).__dict__)


@router.patch("/{invoice_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_invoice(
    invoice_id: str,
    request: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update invoice (draft only)."""
    service = InvoiceService(session)

    invoice = await service.update_invoice(invoice_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Invoice updated | id={invoice_id} | updated_by={current_user.id}")

    return ok(data=InvoiceResponse.model_validate(invoice).__dict__)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.delete")),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Soft delete invoice (draft only)."""
    service = InvoiceService(session)
    await service.delete_invoice(invoice_id)

    await session.commit()

    logger.info(f"Invoice deleted | id={invoice_id} | deleted_by={current_user.id}")


# ── Invoice Status ────────────────────────────────────────────────────

@router.post("/{invoice_id}/send", status_code=status.HTTP_200_OK, response_model=dict)
async def send_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Send invoice to customer."""
    service = InvoiceService(session)

    invoice = await service.send_invoice(invoice_id)

    await session.commit()

    logger.info(f"Invoice sent | id={invoice_id} | sent_by={current_user.id}")

    return ok(data=InvoiceResponse.model_validate(invoice).__dict__)


@router.post("/{invoice_id}/cancel", status_code=status.HTTP_200_OK, response_model=dict)
async def cancel_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Cancel invoice."""
    service = InvoiceService(session)

    invoice = await service.cancel_invoice(invoice_id)

    await session.commit()

    logger.info(f"Invoice cancelled | id={invoice_id} | cancelled_by={current_user.id}")

    return ok(data=InvoiceResponse.model_validate(invoice).__dict__)


# ── Invoice Items ─────────────────────────────────────────────────────

@router.post("/{invoice_id}/items", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_invoice_item(
    invoice_id: str,
    request: InvoiceItemCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add item to invoice (draft only)."""
    service = InvoiceService(session)

    item = await service.add_item(
        invoice_id=invoice_id,
        description=request.description,
        quantity=request.quantity,
        unit_price=request.unit_price,
        gst_rate=request.gst_rate,
    )

    await session.commit()

    return created(
        data=InvoiceItemResponse.model_validate(item).__dict__,
        message="Item added successfully.",
    )


@router.get("/{invoice_id}/items", status_code=status.HTTP_200_OK, response_model=dict)
async def get_invoice_items(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get items for invoice."""
    service = InvoiceService(session)
    items = await service.get_invoice_items(invoice_id)

    data = [InvoiceItemResponse.model_validate(i).__dict__ for i in items]

    return ok(data=data)


# ── Payment Processing ────────────────────────────────────────────────

@router.post("/{invoice_id}/payments", status_code=status.HTTP_200_OK, response_model=dict)
async def record_payment(
    invoice_id: str,
    request: InvoicePaymentReceived,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Record payment received."""
    service = InvoiceService(session)

    invoice = await service.record_payment(
        invoice_id=invoice_id,
        amount=request.amount,
        payment_date=request.payment_date,
        payment_method=request.payment_method,
        transaction_ref=request.transaction_ref,
        notes=request.notes,
    )

    await session.commit()

    logger.info(f"Payment recorded | invoice={invoice_id} | amount={request.amount} | by={current_user.id}")

    return ok(
        data=InvoiceResponse.model_validate(invoice).__dict__,
        message="Payment recorded successfully.",
    )


# ── Payment Mapping ───────────────────────────────────────────────────

@router.post("/{invoice_id}/map-to-payment", status_code=status.HTTP_201_CREATED, response_model=dict)
async def map_to_payment_plan(
    invoice_id: str,
    request: InvoicePaymentMappingCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Map invoice to booking payment plan."""
    service = InvoiceService(session)

    mapping = await service.map_to_payment_plan(
        invoice_id=invoice_id,
        payment_plan_id=request.payment_plan_id,
        mapped_amount=request.mapped_amount,
    )

    await session.commit()

    return created(
        data=InvoicePaymentMappingResponse.model_validate(mapping).__dict__,
        message="Invoice mapped to payment plan successfully.",
    )


@router.get("/{invoice_id}/mappings", status_code=status.HTTP_200_OK, response_model=dict)
async def get_invoice_mappings(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get payment plan mappings for invoice."""
    service = InvoiceService(session)
    mappings = await service.get_invoice_mappings(invoice_id)

    data = [InvoicePaymentMappingResponse.model_validate(m).__dict__ for m in mappings]

    return ok(data=data)


# ── Financial Reports ─────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_invoice_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get invoice statistics."""
    service = InvoiceService(session)
    stats = await service.get_invoice_statistics()

    return ok(data=stats)


@router.get("/customer/{customer_id}/summary", status_code=status.HTTP_200_OK, response_model=dict)
async def get_customer_invoice_summary(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get customer's invoice summary."""
    service = InvoiceService(session)
    summary = await service.get_customer_invoice_summary(customer_id)

    return ok(data=summary)


@router.get("/ledger/balance", status_code=status.HTTP_200_OK, response_model=dict)
async def get_ledger_balance(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get financial ledger balance."""
    service = InvoiceService(session)
    balance = await service.get_ledger_balance()

    return ok(data=balance)


@router.get("/due/overdue", status_code=status.HTTP_200_OK, response_model=dict)
async def get_overdue_invoices(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get overdue invoices."""
    service = InvoiceService(session)
    invoices = await service.get_overdue_invoices()

    data = [InvoiceListResponse.model_validate(i).__dict__ for i in invoices]

    return ok(data=data)


@router.get("/due/upcoming", status_code=status.HTTP_200_OK, response_model=dict)
async def get_invoices_due_soon(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("invoices.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get invoices due within N days."""
    service = InvoiceService(session)
    invoices = await service.get_invoices_due_soon(days)

    data = [InvoiceListResponse.model_validate(i).__dict__ for i in invoices]

    return ok(data=data)
