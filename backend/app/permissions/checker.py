from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Permission, UserPermission
from app.repositories.user_repository import UserRepository


class PermissionChecker:
    """
    Runtime permission checker.

    Combines role permissions and user-specific permission overrides.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def user_has_permission(self, user_id: str | uuid.UUID, permission_code: str) -> bool:
        """
        Check if user has a specific permission.

        Logic:
          1. If user has explicit deny (UserPermission.is_granted=false), return False
          2. If user has explicit grant (UserPermission.is_granted=true), return True
          3. If user's role has the permission, return True
          4. Otherwise, return False
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        user = await self.user_repo.get_with_role_and_permissions(str(user_id))
        if not user:
            return False

        # ── Check user-specific permission override ────────────────────────
        from sqlalchemy import select, and_

        override_query = (
            select(UserPermission)
            .join(Permission)
            .where(
                and_(
                    UserPermission.user_id == user_id,
                    Permission.code == permission_code,
                )
            )
        )
        override_result = await self.session.execute(override_query)
        override = override_result.scalars().first()

        if override:
            return override.is_granted

        # ── Check role permissions ─────────────────────────────────────────
        if user.role:
            for permission in user.role.permissions:
                if permission.code == permission_code:
                    return True

        return False

    async def user_has_any_permission(
        self, user_id: str | uuid.UUID, permission_codes: list[str]
    ) -> bool:
        """Check if user has any of the given permissions."""
        for code in permission_codes:
            if await self.user_has_permission(user_id, code):
                return True
        return False

    async def user_has_all_permissions(
        self, user_id: str | uuid.UUID, permission_codes: list[str]
    ) -> bool:
        """Check if user has all of the given permissions."""
        for code in permission_codes:
            if not await self.user_has_permission(user_id, code):
                return False
        return True

    async def get_user_permissions(self, user_id: str | uuid.UUID) -> set[str]:
        """Return all permission codes the user has."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        user = await self.user_repo.get_with_role_and_permissions(str(user_id))
        if not user:
            return set()

        permissions: set[str] = set()

        # Add role permissions
        if user.role:
            for permission in user.role.permissions:
                permissions.add(permission.code)

        # Apply user-specific overrides
        from sqlalchemy import select

        override_query = select(UserPermission).where(UserPermission.user_id == user_id)
        override_result = await self.session.execute(override_query)
        overrides = override_result.scalars().all()

        for override in overrides:
            # Fetch the permission code
            perm_query = select(Permission).where(Permission.id == override.permission_id)
            perm_result = await self.session.execute(perm_query)
            perm = perm_result.scalars().first()

            if perm:
                if override.is_granted:
                    permissions.add(perm.code)
                else:
                    permissions.discard(perm.code)

        return permissions
