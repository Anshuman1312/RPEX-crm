from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.security import decode_access_token
from app.database.postgres import get_db_session
from app.models.user import User
from app.permissions.checker import PermissionChecker
from app.services.auth_service import UserService


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """
    FastAPI dependency to extract and validate the current user from JWT token.

    Token format: Authorization: Bearer <access_token>

    Raises:
        AuthenticationException: if token is missing or invalid
    """
    if not authorization:
        raise AuthenticationException("Missing authorization header.")

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationException("Invalid authorization header format.")

    token = parts[1]

    # Decode and validate token
    try:
        payload = decode_access_token(token)
    except Exception:
        raise AuthenticationException("Invalid or expired token.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid token payload.")

    # Fetch user
    user_service = UserService(session)
    user = await user_service.get_user(user_id)

    if not user or user.status != "active":
        raise AuthenticationException("User not found or inactive.")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """
    FastAPI dependency to require admin user (admin role).

    Raises:
        AuthorizationException: if user doesn't have admin role
    """
    checker = PermissionChecker(session)

    # Check for admin permission (or specific admin role code)
    has_admin = await checker.user_has_permission(str(current_user.id), "admin.access")

    if not has_admin:
        raise AuthorizationException("Admin access required.")

    return current_user


def require_permission(*permission_codes: str):
    """
    Factory for a permission-checking dependency.

    Usage:
        @router.get("/endpoint")
        async def endpoint(
            current_user: User = Depends(get_current_user),
            _ = Depends(require_permission("leads.view", "leads.create"))
        ):
            ...

    Checks if user has AT LEAST ONE of the specified permissions.
    """

    async def _check_permission(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> User:
        checker = PermissionChecker(session)
        has_any = await checker.user_has_any_permission(str(current_user.id), list(permission_codes))

        if not has_any:
            raise AuthorizationException(
                f"You do not have permission to access this resource. Required: {', '.join(permission_codes)}"
            )

        return current_user

    return _check_permission


def require_all_permissions(*permission_codes: str):
    """
    Factory for a stricter permission-checking dependency (ALL permissions required).

    Usage:
        @router.delete("/endpoint/{id}")
        async def endpoint(
            current_user: User = Depends(get_current_user),
            _ = Depends(require_all_permissions("leads.delete", "audit.log"))
        ):
            ...
    """

    async def _check_permission(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> User:
        checker = PermissionChecker(session)
        has_all = await checker.user_has_all_permissions(str(current_user.id), list(permission_codes))

        if not has_all:
            raise AuthorizationException(
                f"You do not have all required permissions. Required: {', '.join(permission_codes)}"
            )

        return current_user

    return _check_permission
