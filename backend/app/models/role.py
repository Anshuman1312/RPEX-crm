from __future__ import annotations

from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role_permission import RolePermission


class Role(BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    User Role entity. Defines a collection of permissions.
    
    Attributes:
        name: Display name (e.g., "Finance Manager")
        code: Unique slug used in code (e.g., "finance_manager")
        description: Description of role responsibilities
        is_system: If True, this role cannot be deleted
        status: ACTIVE/INACTIVE
        relationships:
            users: List of users assigned to this role
            role_permissions: List of permissions linked to this role
    """

    __tablename__ = "roles"

    # ── Identifiers ────────────────────────────────────────────────────────
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # ── Configuration ──────────────────────────────────────────────────────
    is_system = Column(Boolean, default=False)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)

    # ── Relationships ──────────────────────────────────────────────────────
    users = relationship(
        "User",
        back_populates="role",
        lazy="select"
    )
    
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Role {self.code}>"