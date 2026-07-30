from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

import uuid


# ── Request/Response DTOs ──────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Login with email and password."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)


class RegisterRequest(BaseModel):
    name: str = Field(default="User", min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str = Field(min_length=10, max_length=20)
    role_name: str = Field(default="SALES")


class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = 1800
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Request to refresh the access token."""

    refresh_token: str



class PermissionDetail(BaseModel):
    """Permission detail."""

    id: uuid.UUID
    code: str
    module: str
    action: str


class RoleDetail(BaseModel):
    """Role detail with permissions."""

    id: uuid.UUID
    name: str
    code: str
    permissions: list[PermissionDetail] = []


class UserResponse(BaseModel):
    """Full user response (for logged-in user info)."""

    id: uuid.UUID
    email: str
    phone: str
    full_name: str
    employee_code: str
    status: str
    is_verified: bool
    last_login_at: Optional[datetime] = None
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    role: Optional[RoleDetail] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Create user request (admin endpoint)."""

    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8, max_length=255)
    employee_code: str = Field(..., min_length=1, max_length=50)
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    role_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    """Update user request."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    role_id: Optional[uuid.UUID] = None


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    old_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)
    confirm_password: str = Field(..., min_length=8, max_length=255)

    def validate_passwords_match(self) -> bool:
        return self.new_password == self.confirm_password


class UserListResponse(BaseModel):
    """User list item (less info than full response)."""

    id: uuid.UUID
    email: str
    full_name: str
    employee_code: str
    status: str
    is_verified: bool
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
