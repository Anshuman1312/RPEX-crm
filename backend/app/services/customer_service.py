from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerAddress, CustomerKYC, CustomerPreference
from app.repositories.customer_repository import (
    CustomerRepository,
    CustomerAddressRepository,
    CustomerKYCRepository,
    CustomerPreferenceRepository,
)
from app.utils.filters import SortDirection
from app.utils.numbering import NumberingService
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from loguru import logger


class CustomerService:
    """Service for customer management business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.customer_repo = CustomerRepository(session)
        self.address_repo = CustomerAddressRepository(session)
        self.kyc_repo = CustomerKYCRepository(session)
        self.preference_repo = CustomerPreferenceRepository(session)
        self.numbering_service = NumberingService(session)

    # ── Customer CRUD ──────────────────────────────────────────────────────

    async def create_customer(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        customer_type: str = "INDIVIDUAL",
        company_name: Optional[str] = None,
        alternate_phone: Optional[str] = None,
        referred_by_user_id: Optional[str] = None,
        lead_converted_from_id: Optional[str] = None,
        preferred_contact_method: Optional[str] = None,
        preferred_language: str = "en",
        gstin: Optional[str] = None,
        pan: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: str = "system",
    ) -> Customer:
        """
        Create a new customer.
        
        Args:
            first_name: First name (required)
            last_name: Last name (required)
            email: Email address (must be unique)
            phone: Phone number (must be unique)
            customer_type: INDIVIDUAL or CORPORATE
            company_name: Company name (required for CORPORATE)
            alternate_phone: Alternative phone number
            referred_by_user_id: ID of user who referred
            lead_converted_from_id: If converted from a lead
            preferred_contact_method: PHONE/EMAIL/WHATSAPP
            preferred_language: Language preference
            gstin: GST registration number
            pan: PAN number
            notes: Internal notes
            created_by: User ID creating this
            
        Returns:
            Created Customer instance
            
        Raises:
            ConflictException: If email or phone already exists
            ValidationException: If validation fails
        """
        # Check for duplicate email
        existing_by_email = await self.customer_repo.get_by_email(email)
        if existing_by_email:
            raise ConflictException(f"Customer with email {email} already exists")

        # Check for duplicate phone
        existing_by_phone = await self.customer_repo.get_by_phone(phone)
        if existing_by_phone:
            raise ConflictException(f"Customer with phone {phone} already exists")

        # Check for duplicate PAN
        if pan:
            existing_by_pan = await self.customer_repo.get_by_pan(pan)
            if existing_by_pan:
                raise ConflictException(f"Customer with PAN {pan} already exists")

        # Check for duplicate GSTIN
        if gstin:
            existing_by_gstin = await self.customer_repo.get_by_gstin(gstin)
            if existing_by_gstin:
                raise ConflictException(f"Customer with GSTIN {gstin} already exists")

        # Generate customer number
        customer_number = await self.numbering_service.get_next_number("CUST")

        # Create customer
        customer = Customer(
            customer_number=customer_number,
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            phone=phone,
            alternate_phone=alternate_phone,
            company_name=company_name,
            customer_type=customer_type,
            referred_by_user_id=referred_by_user_id,
            referred_by_date=datetime.utcnow() if referred_by_user_id else None,
            lead_converted_from_id=lead_converted_from_id,
            lead_converted_date=datetime.utcnow() if lead_converted_from_id else None,
            preferred_contact_method=preferred_contact_method,
            preferred_language=preferred_language,
            gstin=gstin,
            pan=pan,
            notes=notes,
            created_by=created_by,
        )

        self.session.add(customer)
        await self.session.flush()

        # Auto-create preferences record
        preference = CustomerPreference(
            customer_id=str(customer.id),
            created_by=created_by,
        )
        self.session.add(preference)

        logger.info(f"Customer created | id={customer.id} | number={customer_number} | email={email}")

        return customer

    async def get_customer(self, customer_id: str) -> Customer:
        """Get customer by ID with related data."""
        customer = await self.customer_repo.get_with_addresses_and_kyc(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")
        return customer

    async def list_customers(
        self,
        search: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        customer_types: Optional[List[str]] = None,
        referred_by_user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: SortDirection = SortDirection.DESC,
    ) -> Tuple[List[Customer], int]:
        """List customers with filtering."""
        return await self.customer_repo.list_with_filter(
            search=search,
            statuses=statuses,
            customer_types=customer_types,
            referred_by_user_id=referred_by_user_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def update_customer(self, customer_id: str, **kwargs) -> Customer:
        """Update customer fields."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        # Check for email uniqueness if email is being updated
        if "email" in kwargs and kwargs["email"]:
            existing = await self.customer_repo.get_by_email(kwargs["email"])
            if existing and str(existing.id) != customer_id:
                raise ConflictException(f"Email {kwargs['email']} already in use")
            kwargs["email"] = kwargs["email"].lower()

        # Check for phone uniqueness
        if "phone" in kwargs and kwargs["phone"]:
            existing = await self.customer_repo.get_by_phone(kwargs["phone"])
            if existing and str(existing.id) != customer_id:
                raise ConflictException(f"Phone {kwargs['phone']} already in use")

        # Update allowed fields
        allowed_fields = {
            "first_name", "last_name", "email", "phone", "alternate_phone",
            "company_name", "preferred_contact_method", "preferred_language",
            "gstin", "pan", "notes"
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(customer, field, value)

        customer.updated_at = datetime.utcnow()

        logger.info(f"Customer updated | id={customer_id}")

        return customer

    async def change_status(
        self,
        customer_id: str,
        status: str,
        reason: Optional[str] = None,
    ) -> Customer:
        """Change customer status."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        old_status = customer.status
        customer.status = status
        customer.updated_at = datetime.utcnow()

        logger.info(f"Customer status changed | id={customer_id} | {old_status} → {status}")

        return customer

    async def delete_customer(self, customer_id: str) -> None:
        """Soft delete a customer."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException(f"Customer {customer_id} not found")

        await self.customer_repo.soft_delete(customer_id)

        logger.info(f"Customer deleted | id={customer_id}")

    # ── Address Management ────────────────────────────────────────────────

    async def add_address(
        self,
        customer_id: str,
        address_type: str,
        full_address: str,
        street: str,
        city: str,
        state: str,
        postal_code: str,
        country: str = "IN",
        is_primary: bool = False,
        created_by: str = "system",
    ) -> CustomerAddress:
        """Add address for customer."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        # If marking as primary, unmark others
        if is_primary:
            stmt_update = "UPDATE customer_addresses SET is_primary = FALSE WHERE customer_id = :cid AND is_primary = TRUE"
            await self.session.execute(stmt_update, {"cid": customer_id})

        address = CustomerAddress(
            customer_id=customer_id,
            address_type=address_type,
            full_address=full_address,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_primary=is_primary,
            created_by=created_by,
        )

        self.session.add(address)

        logger.info(f"Address added | customer_id={customer_id} | type={address_type}")

        return address

    async def update_address(self, address_id: str, **kwargs) -> CustomerAddress:
        """Update customer address."""
        address = await self.address_repo.get_by_id(address_id)
        if not address:
            raise NotFoundException(f"Address {address_id} not found")

        # If marking as primary, unmark others
        if kwargs.get("is_primary") == True:
            stmt_update = "UPDATE customer_addresses SET is_primary = FALSE WHERE customer_id = :cid AND id != :aid"
            await self.session.execute(stmt_update, {"cid": address.customer_id, "aid": address_id})

        for field, value in kwargs.items():
            if value is not None and hasattr(address, field):
                setattr(address, field, value)

        address.updated_at = datetime.utcnow()

        return address

    async def delete_address(self, address_id: str) -> None:
        """Delete customer address."""
        address = await self.address_repo.get_by_id(address_id)
        if not address:
            raise NotFoundException(f"Address {address_id} not found")

        await self.address_repo.delete(address_id)

        logger.info(f"Address deleted | id={address_id}")

    async def get_addresses(self, customer_id: str) -> List[CustomerAddress]:
        """Get all addresses for customer."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        return await self.address_repo.get_customer_addresses(customer_id)

    # ── KYC Management ────────────────────────────────────────────────────

    async def add_kyc_document(
        self,
        customer_id: str,
        document_type: str,
        document_number: str,
        issued_by: Optional[str] = None,
        issued_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None,
        document_url: Optional[str] = None,
        created_by: str = "system",
    ) -> CustomerKYC:
        """Add KYC document for customer."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        # Check for duplicate document number
        existing = await self.kyc_repo.get_by_document_number(document_number)
        if existing and str(existing.customer_id) != customer_id:
            raise ConflictException(f"Document number {document_number} already exists")

        kyc = CustomerKYC(
            customer_id=customer_id,
            document_type=document_type,
            document_number=document_number,
            issued_by=issued_by,
            issued_date=issued_date,
            expiry_date=expiry_date,
            document_url=document_url,
            verification_status="PENDING",
            created_by=created_by,
        )

        self.session.add(kyc)

        logger.info(f"KYC document added | customer_id={customer_id} | type={document_type}")

        return kyc

    async def verify_kyc_document(
        self,
        kyc_id: str,
        verification_status: str,
        verified_by_user_id: str,
        rejection_reason: Optional[str] = None,
    ) -> CustomerKYC:
        """Verify or reject KYC document."""
        kyc = await self.kyc_repo.get_by_id(kyc_id)
        if not kyc:
            raise NotFoundException(f"KYC document {kyc_id} not found")

        kyc.verification_status = verification_status
        kyc.verified_by_user_id = verified_by_user_id
        kyc.verified_at = datetime.utcnow()
        kyc.rejection_reason = rejection_reason

        logger.info(f"KYC verified | id={kyc_id} | status={verification_status}")

        return kyc

    async def get_kyc_documents(self, customer_id: str) -> List[CustomerKYC]:
        """Get all KYC documents for customer."""
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer or customer.is_deleted:
            raise NotFoundException(f"Customer {customer_id} not found")

        return await self.kyc_repo.get_customer_documents(customer_id)

    # ── Preferences Management ────────────────────────────────────────────

    async def update_preferences(
        self,
        customer_id: str,
        **kwargs
    ) -> CustomerPreference:
        """Update customer preferences."""
        pref = await self.preference_repo.get_by_customer(customer_id)
        if not pref:
            raise NotFoundException(f"Preferences for customer {customer_id} not found")

        for field, value in kwargs.items():
            if value is not None and hasattr(pref, field):
                setattr(pref, field, value)

        pref.updated_at = datetime.utcnow()

        logger.info(f"Customer preferences updated | customer_id={customer_id}")

        return pref

    async def get_preferences(self, customer_id: str) -> CustomerPreference:
        """Get customer preferences."""
        pref = await self.preference_repo.get_by_customer(customer_id)
        if not pref:
            raise NotFoundException(f"Preferences for customer {customer_id} not found")

        return pref

    # ── Statistics ────────────────────────────────────────────────────────

    async def get_customer_statistics(self) -> dict:
        """Get customer statistics."""
        by_status = await self.customer_repo.count_by_status()
        by_type = await self.customer_repo.count_by_type()

        return {
            "by_status": by_status,
            "by_type": by_type,
            "total": sum(by_status.values()),
        }
