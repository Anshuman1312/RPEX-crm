from __future__ import annotations
from typing import Annotated, Sequence
from fastapi import Depends, HTTPException, status

# We import the plural version from core.deps
from app.core.deps import (
    get_current_user,
    get_current_permissions,
    require_permissions  # This must exist in core/deps.py
)

# 1. Provide the singular name that audit.py wants
def require_permission(permission: str):
    """Bridge for a single permission string."""
    return require_permissions({permission})

# 2. Provide a multi-permission helper
def require_any_permissions(permissions: Sequence[str]):
    """Bridge for multiple permission strings."""
    return require_permissions(set(permissions))

# 3. Export the user dependency
get_current_active_user = get_current_user


async def get_current_admin(
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Bridge for legacy admin-only routes."""
    role = getattr(current_user, "role", None)
    role_name = getattr(role, "name", None)
    if role_name not in {"ADMIN", "SUPER_ADMIN"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user