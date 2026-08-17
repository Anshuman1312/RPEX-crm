from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.base import Base
from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin
from app.utils.enums import CustomerStatus, DocumentType


class Customer(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Customer entity representing real estate buyers/investors.
    
    Attributes:
        customer_number: Unique sequential ID (CUST-000001)
        first_name: Customer first name
        last_name: Customer last name
        email: Email address (UNIQUE)
        phone: Primary phone number (UNIQUE normalized)
        alternate_phone: Alternative contact number
        company_name: Optional company/organization name
        customer_type: Individual/Corporate
        status: ACTIVE/INACTIVE/BLACKLISTED/SUSPENDED
        referred_by_user_id: FK to User who referred
        referred_by_date: When customer was referred
        lead_converted_from_id: FK to Lead (if converted from lead)
        lead_converted_date: When lead was converted to customer
        preferred_contact_method: Phone/Email/WhatsApp
        preferred_language: Language preference
        gstin: Optional GST registration number
        pan: Optional PAN for Indian customers
        notes: Internal notes
        relationships:
            addresses: CustomerAddress[] - Billing, shipping, etc.
            kyc_documents: CustomerKYC[] - ID proofs, address proof, etc.
            bookings: Booking[] - Property bookings
            payments: CustomerPayment[] - Payment history
            referred_by_user: User - Sales person who referred
            converted_from_lead: Lead - Original lead if applicable
    """

    __tablename__ = "customers"

    # ── Identifiers ────────────────────────────────────────────────────────
    customer_number = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # ── Contact ────────────────────────────────────────────────────────────
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    alternate_phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    
    # ── Classification ────────────────────────────────────────────────────────
    customer_type = Column(String(50), nullable=False, default="INDIVIDUAL")  # INDIVIDUAL/CORPORATE
    status = Column(String(50), nullable=False, default=CustomerStatus.ACTIVE.value, index=True)
    
    # ── Referral & Conversion ────────────────────────────────────────────────
    referred_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referred_by_date = Column(DateTime, nullable=True)
    lead_converted_from_id = Column(PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    lead_converted_date = Column(DateTime, nullable=True)
    
    # ── Preferences ────────────────────────────────────────────────────────
    preferred_contact_method = Column(String(50), nullable=True)  # PHONE/EMAIL/WHATSAPP
    preferred_language = Column(String(20), default="en")
    
    # ── Compliance ────────────────────────────────────────────────────────────
    gstin = Column(String(15), nullable=True, unique=True, index=True)  # GST registration
    pan = Column(String(10), nullable=True, unique=True, index=True)    # PAN (India)
    
    # ── Notes ────────────────────────────────────────────────────────────
    notes = Column(Text, nullable=True)
    
    # ── Relationships ──────────────────────────────────────────────────────
    addresses = relationship(
        "CustomerAddress",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )
    kyc_documents = relationship(
        "CustomerKYC",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )
    bookings = relationship(
        "Booking",
        back_populates="customer",
        foreign_keys="Booking.customer_id",
        lazy="select"
    )
    invoices = relationship(
        "Invoice",
        back_populates="customer",
        foreign_keys="Invoice.customer_id",
        lazy="select",
    )
    payments = relationship(
        "CustomerPayment",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )
    followups = relationship(
        "FollowUp",
        back_populates="customer",
        foreign_keys="FollowUp.customer_id",
        lazy="select"
    )
    referred_by_user = relationship(
        "User",
        back_populates="referred_customers",
        foreign_keys=[referred_by_user_id],
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Customer {self.customer_number}: {self.first_name} {self.last_name}>"


class CustomerAddress(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Customer addresses (billing, shipping, communication).
    
    Attributes:
        customer_id: FK to Customer
        address_type: BILLING/SHIPPING/COMMUNICATION
        full_address: Complete address
        street: Street address
        city: City
        state: State/Province
        postal_code: Zip/Postal code
        country: Country code (default: IN)
        is_primary: Is this the primary address
        relationships:
            customer: Customer - Parent customer
    """

    __tablename__ = "customer_addresses"

    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type = Column(String(50), nullable=False, default="BILLING")  # BILLING/SHIPPING/COMMUNICATION
    
    full_address = Column(Text, nullable=False)
    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(2), nullable=False, default="IN")
    
    is_primary = Column(Boolean, default=False, index=True)
    
    # ── Relationships ──────────────────────────────────────────────────────
    customer = relationship("Customer", back_populates="addresses")
    
    def __repr__(self) -> str:
        return f"<CustomerAddress {self.address_type}: {self.city}>"


class CustomerKYC(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Customer KYC (Know Your Customer) documents.
    
    Attributes:
        customer_id: FK to Customer
        document_type: ID_PROOF/ADDRESS_PROOF/INCOME_PROOF/PAN/AADHAAR
        document_number: ID/PAN/Aadhaar number
        issued_by: Issuing authority
        issued_date: When issued
        expiry_date: When expires (if applicable)
        document_url: URL/path to document file
        verified_by_user_id: FK to User who verified
        verified_at: When verification happened
        verification_status: PENDING/VERIFIED/REJECTED/EXPIRED
        rejection_reason: Why rejected (if applicable)
        relationships:
            customer: Customer - Parent customer
            verified_by_user: User - User who verified
    """

    __tablename__ = "customer_kycs"

    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    document_type = Column(String(50), nullable=False)  # ID_PROOF/ADDRESS_PROOF/INCOME_PROOF/PAN/AADHAAR
    document_number = Column(String(100), nullable=False, index=True)
    issued_by = Column(String(255), nullable=True)
    issued_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    document_url = Column(String(500), nullable=True)
    
    # ── Verification ──────────────────────────────────────────────────────
    verified_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_status = Column(String(50), nullable=False, default="PENDING")  # PENDING/VERIFIED/REJECTED/EXPIRED
    rejection_reason = Column(Text, nullable=True)
    
    # ── Relationships ──────────────────────────────────────────────────────
    customer = relationship("Customer", back_populates="kyc_documents")
    verified_by_user = relationship(
        "User",
        back_populates="verified_kyc",
        foreign_keys=[verified_by_user_id],
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<CustomerKYC {self.document_type}: {self.verification_status}>"


class CustomerPreference(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Customer preferences and interests.
    
    Attributes:
        customer_id: FK to Customer
        interested_project_ids: JSON array of interested project IDs
        preferred_unit_type: FLAT/VILLA/PLOT/COMMERCIAL
        budget_min: Minimum budget in base currency
        budget_max: Maximum budget
        preferred_location: Preferred area/locality
        investment_timeline: IMMEDIATE/3_MONTHS/6_MONTHS/1_YEAR
        purpose: SELF_USE/INVESTMENT/RENTAL
        preferred_furnished: UNFURNISHED/SEMI_FURNISHED/FULLY_FURNISHED
        amenities_interested: JSON array of amenities
        relationships:
            customer: Customer - Parent customer
    """

    __tablename__ = "customer_preferences"

    customer_id = Column(PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    interested_project_ids = Column(String(1000), nullable=True)  # JSON array as string
    preferred_unit_type = Column(String(50), nullable=True)
    
    budget_min = Column(Numeric(15, 2), nullable=True)
    budget_max = Column(Numeric(15, 2), nullable=True)
    
    preferred_location = Column(String(255), nullable=True)
    investment_timeline = Column(String(50), nullable=True)
    purpose = Column(String(50), nullable=True)
    preferred_furnished = Column(String(50), nullable=True)
    amenities_interested = Column(String(1000), nullable=True)  # JSON array as string
    
    # ── Relationships ──────────────────────────────────────────────────────
    customer = relationship("Customer", lazy="select")
    
    def __repr__(self) -> str:
        return f"<CustomerPreference {self.customer_id}: {self.preferred_unit_type}>"
