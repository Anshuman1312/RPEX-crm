from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerStatusUpdate,
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerKYCCreate,
    CustomerKYCResponse,
    CustomerKYCVerify,
    CustomerPreferenceCreate,
    CustomerPreferenceUpdate,
    CustomerPreferenceResponse,
)
from app.services.customer_service import CustomerService
from app.utils.filters import SortDirection
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


# ── Customer CRUD ──────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_customer(
    request: CustomerCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new customer. Requires customers.create permission."""
    service = CustomerService(session)

    customer = await service.create_customer(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        customer_type=request.customer_type,
        company_name=request.company_name,
        alternate_phone=request.alternate_phone,
        referred_by_user_id=request.referred_by_user_id,
        lead_converted_from_id=request.lead_converted_from_id,
        preferred_contact_method=request.preferred_contact_method,
        preferred_language=request.preferred_language,
        gstin=request.gstin,
        pan=request.pan,
        notes=request.notes,
        created_by=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Customer created | id={customer.id} | number={customer.customer_number}")

    return created(
        data=CustomerResponse.model_validate(customer).__dict__,
        message="Customer created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_customers(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: str = Query(None),
    statuses: str = Query(None, description="Comma-separated statuses"),
    customer_types: str = Query(None, description="Comma-separated types"),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List customers with filtering and pagination."""
    service = CustomerService(session)

    customers, total = await service.list_customers(
        search=search,
        statuses=statuses.split(",") if statuses else None,
        customer_types=customer_types.split(",") if customer_types else None,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=SortDirection(sort_direction),
    )

    data = [CustomerListResponse.model_validate(c).__dict__ for c in customers]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{customer_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get customer with all details."""
    service = CustomerService(session)
    customer = await service.get_customer(customer_id)

    return ok(data=CustomerResponse.model_validate(customer).__dict__)


@router.patch("/{customer_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_customer(
    customer_id: str,
    request: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update customer details."""
    service = CustomerService(session)

    customer = await service.update_customer(customer_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Customer updated | id={customer_id} | updated_by={current_user.id}")

    return ok(data=CustomerResponse.model_validate(customer).__dict__)


@router.post("/{customer_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def change_customer_status(
    customer_id: str,
    request: CustomerStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Change customer status."""
    service = CustomerService(session)

    customer = await service.change_status(customer_id, request.status, request.reason)

    await session.commit()

    logger.info(f"Customer status changed | id={customer_id} | status={request.status}")

    return ok(data=CustomerResponse.model_validate(customer).__dict__)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.delete")),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Soft delete a customer."""
    service = CustomerService(session)
    await service.delete_customer(customer_id)

    await session.commit()

    logger.info(f"Customer deleted | id={customer_id} | deleted_by={current_user.id}")


# ── Address Management ────────────────────────────────────────────────────

@router.post("/{customer_id}/addresses", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_customer_address(
    customer_id: str,
    request: CustomerAddressCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add address to customer."""
    service = CustomerService(session)

    address = await service.add_address(
        customer_id=customer_id,
        address_type=request.address_type,
        full_address=request.full_address,
        street=request.street,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        country=request.country,
        is_primary=request.is_primary,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=CustomerAddressResponse.model_validate(address).__dict__,
        message="Address added successfully.",
    )


@router.get("/{customer_id}/addresses", status_code=status.HTTP_200_OK, response_model=dict)
async def get_customer_addresses(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get all addresses for customer."""
    service = CustomerService(session)
    addresses = await service.get_addresses(customer_id)

    data = [CustomerAddressResponse.model_validate(a).__dict__ for a in addresses]

    return ok(data=data)


@router.patch("/{customer_id}/addresses/{address_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_customer_address(
    customer_id: str,
    address_id: str,
    request: CustomerAddressCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update customer address."""
    service = CustomerService(session)

    address = await service.update_address(address_id, **request.model_dump())

    await session.commit()

    return ok(data=CustomerAddressResponse.model_validate(address).__dict__)


@router.delete("/{customer_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_customer_address(
    customer_id: str,
    address_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete customer address."""
    service = CustomerService(session)
    await service.delete_address(address_id)

    await session.commit()


# ── KYC Management ────────────────────────────────────────────────────

@router.post("/{customer_id}/kyc", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_kyc_document(
    customer_id: str,
    request: CustomerKYCCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add KYC document for customer."""
    service = CustomerService(session)

    kyc = await service.add_kyc_document(
        customer_id=customer_id,
        document_type=request.document_type,
        document_number=request.document_number,
        issued_by=request.issued_by,
        issued_date=request.issued_date,
        expiry_date=request.expiry_date,
        document_url=request.document_url,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=CustomerKYCResponse.model_validate(kyc).__dict__,
        message="KYC document added successfully.",
    )


@router.get("/{customer_id}/kyc", status_code=status.HTTP_200_OK, response_model=dict)
async def get_kyc_documents(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get KYC documents for customer."""
    service = CustomerService(session)
    documents = await service.get_kyc_documents(customer_id)

    data = [CustomerKYCResponse.model_validate(d).__dict__ for d in documents]

    return ok(data=data)


@router.post("/{customer_id}/kyc/{kyc_id}/verify", status_code=status.HTTP_200_OK, response_model=dict)
async def verify_kyc_document(
    customer_id: str,
    kyc_id: str,
    request: CustomerKYCVerify,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.verify")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Verify or reject KYC document."""
    service = CustomerService(session)

    kyc = await service.verify_kyc_document(
        kyc_id=kyc_id,
        verification_status=request.verification_status,
        verified_by_user_id=str(current_user.id),
        rejection_reason=request.rejection_reason,
    )

    await session.commit()

    logger.info(f"KYC verified | kyc_id={kyc_id} | status={request.verification_status}")

    return ok(data=CustomerKYCResponse.model_validate(kyc).__dict__)


# ── Preferences Management ────────────────────────────────────────────────

@router.post("/{customer_id}/preferences", status_code=status.HTTP_200_OK, response_model=dict)
async def update_customer_preferences(
    customer_id: str,
    request: CustomerPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update customer preferences."""
    service = CustomerService(session)

    prefs = await service.update_preferences(customer_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    return ok(data=CustomerPreferenceResponse.model_validate(prefs).__dict__)


@router.get("/{customer_id}/preferences", status_code=status.HTTP_200_OK, response_model=dict)
async def get_customer_preferences(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get customer preferences."""
    service = CustomerService(session)
    prefs = await service.get_preferences(customer_id)

    return ok(data=CustomerPreferenceResponse.model_validate(prefs).__dict__)


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_customer_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("customers.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get customer statistics."""
    service = CustomerService(session)
    stats = await service.get_customer_statistics()

    return ok(data=stats)
