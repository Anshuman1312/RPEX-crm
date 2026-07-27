from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.utils.enums import CustomerStatus, DocumentType


# ── Address Schemas ────────────────────────────────────────────────────────

class CustomerAddressCreate(BaseModel):
    """Create customer address."""
    address_type: str  # BILLING/SHIPPING/COMMUNICATION
    full_address: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "IN"
    is_primary: bool = False


class CustomerAddressUpdate(BaseModel):
    """Update customer address."""
    address_type: Optional[str] = None
    full_address: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_primary: Optional[bool] = None


class CustomerAddressResponse(BaseModel):
    """Customer address response."""
    id: str
    address_type: str
    full_address: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── KYC Document Schemas ────────────────────────────────────────────────────

class CustomerKYCCreate(BaseModel):
    """Create KYC document."""
    document_type: str
    document_number: str
    issued_by: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_url: Optional[str] = None


class CustomerKYCUpdate(BaseModel):
    """Update KYC document."""
    document_number: Optional[str] = None
    issued_by: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_url: Optional[str] = None


class CustomerKYCResponse(BaseModel):
    """Customer KYC response."""
    id: str
    document_type: str
    document_number: str
    issued_by: Optional[str]
    issued_date: Optional[datetime]
    expiry_date: Optional[datetime]
    document_url: Optional[str]
    verification_status: str
    verified_by_user_id: Optional[str]
    verified_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerKYCVerify(BaseModel):
    """Verify KYC document."""
    verification_status: str  # VERIFIED/REJECTED
    rejection_reason: Optional[str] = None


# ── Preference Schemas ────────────────────────────────────────────────────────

class CustomerPreferenceCreate(BaseModel):
    """Create customer preferences."""
    interested_project_ids: Optional[str] = None
    preferred_unit_type: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    investment_timeline: Optional[str] = None
    purpose: Optional[str] = None
    preferred_furnished: Optional[str] = None
    amenities_interested: Optional[str] = None


class CustomerPreferenceUpdate(BaseModel):
    """Update customer preferences."""
    interested_project_ids: Optional[str] = None
    preferred_unit_type: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    investment_timeline: Optional[str] = None
    purpose: Optional[str] = None
    preferred_furnished: Optional[str] = None
    amenities_interested: Optional[str] = None


class CustomerPreferenceResponse(BaseModel):
    """Customer preferences response."""
    id: str
    customer_id: str
    interested_project_ids: Optional[str]
    preferred_unit_type: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    preferred_location: Optional[str]
    investment_timeline: Optional[str]
    purpose: Optional[str]
    preferred_furnished: Optional[str]
    amenities_interested: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Customer Schemas ────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    """Create customer."""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    alternate_phone: Optional[str] = None
    company_name: Optional[str] = None
    customer_type: str = "INDIVIDUAL"
    referred_by_user_id: Optional[str] = None
    lead_converted_from_id: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    preferred_language: str = "en"
    gstin: Optional[str] = None
    pan: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Update customer."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    company_name: Optional[str] = None
    customer_type: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    preferred_language: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    notes: Optional[str] = None


class CustomerStatusUpdate(BaseModel):
    """Update customer status."""
    status: str  # ACTIVE/INACTIVE/BLACKLISTED/SUSPENDED
    reason: Optional[str] = None


class CustomerListResponse(BaseModel):
    """Customer list response (subset of fields for list view)."""
    id: str
    customer_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    company_name: Optional[str]
    customer_type: str
    status: str
    referred_by_user_id: Optional[str]
    lead_converted_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerResponse(BaseModel):
    """Full customer response with all details."""
    id: str
    customer_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    alternate_phone: Optional[str]
    company_name: Optional[str]
    customer_type: str
    status: str
    referred_by_user_id: Optional[str]
    referred_by_date: Optional[datetime]
    lead_converted_from_id: Optional[str]
    lead_converted_date: Optional[datetime]
    preferred_contact_method: Optional[str]
    preferred_language: str
    gstin: Optional[str]
    pan: Optional[str]
    notes: Optional[str]
    
    # ── Related data ───────────────────────────────────────────────────────
    addresses: List[CustomerAddressResponse] = []
    kyc_documents: List[CustomerKYCResponse] = []
    
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
