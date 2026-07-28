from __future__ import annotations
from typing import Annotated, Sequence
from fastapi import Depends

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