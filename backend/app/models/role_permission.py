from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.permission import Permission


class RolePermission(BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Many-to-Many junction table for Roles and Permissions.
    
    Attributes:
        role_id: FK to roles table
        permission_id: FK to permissions table
        relationships:
            role: The linked Role object
            permission: The linked Permission object
    """

    __tablename__ = "role_permissions"

    # ── Foreign Keys ───────────────────────────────────────────────────────
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── Relationships ──────────────────────────────────────────────────────
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    def __repr__(self) -> str:
        return f"<RolePermission R:{self.role_id} P:{self.permission_id}>"