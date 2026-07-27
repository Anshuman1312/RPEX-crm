from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer, CustomerAddress, CustomerKYC, CustomerPreference
from app.repositories.base import BaseRepository
from app.utils.filters import SortDirection


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer entity with advanced filtering."""

    async def get_by_customer_number(self, customer_number: str) -> Optional[Customer]:
        """Get customer by customer number."""
        stmt = select(Customer).where(Customer.customer_number == customer_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        stmt = select(Customer).where(Customer.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number."""
        stmt = select(Customer).where(Customer.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_pan(self, pan: str) -> Optional[Customer]:
        """Get customer by PAN."""
        stmt = select(Customer).where(Customer.pan == pan)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_gstin(self, gstin: str) -> Optional[Customer]:
        """Get customer by GSTIN."""
        stmt = select(Customer).where(Customer.gstin == gstin)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_addresses_and_kyc(self, customer_id: str) -> Optional[Customer]:
        """Get customer with addresses and KYC documents (eager loading)."""
        stmt = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(
                selectinload(Customer.addresses),
                selectinload(Customer.kyc_documents),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_with_filter(
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
        """
        List customers with advanced filtering.
        
        Args:
            search: Search by name, email, phone
            statuses: Filter by status (ACTIVE, INACTIVE, etc.)
            customer_types: Filter by type (INDIVIDUAL, CORPORATE)
            referred_by_user_id: Filter by referrer
            skip: Pagination offset
            limit: Pagination limit
            sort_by: Sort column
            sort_direction: ASC or DESC
            
        Returns:
            Tuple of (customers, total_count)
        """
        filters = []

        # Text search
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Customer.first_name.ilike(search_pattern),
                    Customer.last_name.ilike(search_pattern),
                    Customer.email.ilike(search_pattern),
                    Customer.phone.ilike(search_pattern),
                    Customer.customer_number.ilike(search_pattern),
                )
            )

        # Status filter
        if statuses:
            filters.append(Customer.status.in_(statuses))

        # Type filter
        if customer_types:
            filters.append(Customer.customer_type.in_(customer_types))

        # Referrer filter
        if referred_by_user_id:
            filters.append(Customer.referred_by_user_id == referred_by_user_id)

        # Soft delete
        filters.append(Customer.is_deleted == False)

        # Count total
        count_stmt = select(func.count()).select_from(Customer)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch paginated results
        stmt = select(Customer).where(and_(*filters) if filters else True)

        # Sort
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_direction == SortDirection.ASC:
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        customers = result.scalars().all()

        return customers, total or 0

    async def get_by_status(self, status: str) -> List[Customer]:
        """Get all customers with a specific status."""
        stmt = (
            select(Customer)
            .where(and_(Customer.status == status, Customer.is_deleted == False))
            .order_by(Customer.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self) -> dict:
        """Get count of customers by status."""
        stmt = (
            select(Customer.status, func.count(Customer.id).label("count"))
            .where(Customer.is_deleted == False)
            .group_by(Customer.status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {status: count for status, count in rows}

    async def count_by_type(self) -> dict:
        """Get count of customers by type."""
        stmt = (
            select(Customer.customer_type, func.count(Customer.id).label("count"))
            .where(Customer.is_deleted == False)
            .group_by(Customer.customer_type)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {ctype: count for ctype, count in rows}

    async def get_referred_by_user(self, user_id: str) -> List[Customer]:
        """Get customers referred by a specific user."""
        stmt = (
            select(Customer)
            .where(
                and_(
                    Customer.referred_by_user_id == user_id,
                    Customer.is_deleted == False,
                )
            )
            .order_by(Customer.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_converted_from_leads(self, skip: int = 0, limit: int = 50) -> Tuple[List[Customer], int]:
        """Get customers converted from leads."""
        filters = [
            Customer.lead_converted_from_id.isnot(None),
            Customer.is_deleted == False,
        ]

        # Count total
        count_stmt = select(func.count()).select_from(Customer).where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch results
        stmt = (
            select(Customer)
            .where(and_(*filters))
            .order_by(Customer.lead_converted_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        customers = result.scalars().all()

        return customers, total or 0


class CustomerAddressRepository(BaseRepository[CustomerAddress]):
    """Repository for Customer addresses."""

    async def get_customer_addresses(self, customer_id: str) -> List[CustomerAddress]:
        """Get all addresses for a customer."""
        stmt = (
            select(CustomerAddress)
            .where(CustomerAddress.customer_id == customer_id)
            .order_by(CustomerAddress.is_primary.desc(), CustomerAddress.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_primary_address(self, customer_id: str) -> Optional[CustomerAddress]:
        """Get primary address for a customer."""
        stmt = select(CustomerAddress).where(
            and_(
                CustomerAddress.customer_id == customer_id,
                CustomerAddress.is_primary == True,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_type(self, customer_id: str, address_type: str) -> Optional[CustomerAddress]:
        """Get address by type (BILLING, SHIPPING, etc.)."""
        stmt = select(CustomerAddress).where(
            and_(
                CustomerAddress.customer_id == customer_id,
                CustomerAddress.address_type == address_type,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()


class CustomerKYCRepository(BaseRepository[CustomerKYC]):
    """Repository for Customer KYC documents."""

    async def get_customer_documents(self, customer_id: str) -> List[CustomerKYC]:
        """Get all KYC documents for a customer."""
        stmt = (
            select(CustomerKYC)
            .where(CustomerKYC.customer_id == customer_id)
            .order_by(CustomerKYC.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_document_type(self, customer_id: str, document_type: str) -> Optional[CustomerKYC]:
        """Get KYC document by type."""
        stmt = select(CustomerKYC).where(
            and_(
                CustomerKYC.customer_id == customer_id,
                CustomerKYC.document_type == document_type,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_document_number(self, document_number: str) -> Optional[CustomerKYC]:
        """Get KYC document by document number (for duplicate checking)."""
        stmt = select(CustomerKYC).where(CustomerKYC.document_number == document_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_verified_documents(self, customer_id: str) -> List[CustomerKYC]:
        """Get all verified documents for a customer."""
        stmt = (
            select(CustomerKYC)
            .where(
                and_(
                    CustomerKYC.customer_id == customer_id,
                    CustomerKYC.verification_status == "VERIFIED",
                )
            )
            .order_by(CustomerKYC.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_verification(self) -> List[CustomerKYC]:
        """Get all documents pending verification."""
        stmt = (
            select(CustomerKYC)
            .where(CustomerKYC.verification_status == "PENDING")
            .order_by(CustomerKYC.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class CustomerPreferenceRepository(BaseRepository[CustomerPreference]):
    """Repository for Customer preferences."""

    async def get_by_customer(self, customer_id: str) -> Optional[CustomerPreference]:
        """Get preferences for a customer."""
        stmt = select(CustomerPreference).where(CustomerPreference.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_budget_range(
        self,
        min_budget: float,
        max_budget: float,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[CustomerPreference], int]:
        """Get customers interested in a budget range."""
        filters = [
            CustomerPreference.budget_min <= max_budget,
            CustomerPreference.budget_max >= min_budget,
        ]

        # Count total
        count_stmt = select(func.count()).select_from(CustomerPreference).where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch results
        stmt = (
            select(CustomerPreference)
            .where(and_(*filters))
            .order_by(CustomerPreference.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        preferences = result.scalars().all()

        return preferences, total or 0

    async def get_by_unit_type(
        self,
        unit_type: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[CustomerPreference], int]:
        """Get customers interested in a specific unit type."""
        filters = [CustomerPreference.preferred_unit_type == unit_type]

        # Count total
        count_stmt = select(func.count()).select_from(CustomerPreference).where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch results
        stmt = (
            select(CustomerPreference)
            .where(and_(*filters))
            .order_by(CustomerPreference.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        preferences = result.scalars().all()

        return preferences, total or 0

    async def get_by_location(
        self,
        location: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[CustomerPreference], int]:
        """Get customers interested in a specific location."""
        filters = [CustomerPreference.preferred_location.ilike(f"%{location}%")]

        # Count total
        count_stmt = select(func.count()).select_from(CustomerPreference).where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch results
        stmt = (
            select(CustomerPreference)
            .where(and_(*filters))
            .order_by(CustomerPreference.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        preferences = result.scalars().all()

        return preferences, total or 0
