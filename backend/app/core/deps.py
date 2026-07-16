from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # 1. Import selectinload

from app.core.redis import redis_client
from app.core.security import TokenError, decode_token
from app.database.postgres import get_db
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWTBearer",
    description="Use /api/v1/auth/login to get access token. Send as: Bearer <access_token>",
)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token jti")

    is_blacklisted = await redis_client.get(f"blacklist:{jti}")
    if is_blacklisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    # 2. Update query to eagerly load the 'role' relationship
    stmt = (
        select(User)
        .options(selectinload(User.role))  # This ensures current_user.role is available
        .where(User.id == payload.get("sub"), User.is_active.is_(True))
    )
    
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_permissions(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> set[str]:
    # 3. This line will now work because current_user.role is already loaded
    if current_user.role and current_user.role.name in {"ADMIN", "SUPER_ADMIN"}:
        rows = await db.execute(select(Permission.name))
        return set(rows.scalars().all())

    stmt = (
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == current_user.role_id)
    )
    rows = await db.execute(stmt)
    return set(rows.scalars().all())


def require_permissions(required_permissions: set[str]) -> Callable:
    async def permission_guard(
        current_user: CurrentUser,
        permissions: Annotated[set[str], Depends(get_current_permissions)],
    ) -> User:
        if not required_permissions.issubset(permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return permission_guard