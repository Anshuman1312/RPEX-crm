from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import build_password_hash

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_USERS}))])
async def create_user(payload: UserCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    auth_repo = AuthRepository(db)
    role = await auth_repo.get_role_by_name(payload.role_name)
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=build_password_hash(payload.password),
        role_id=role.id,
        is_active=True,
    )
    result = await UserRepository(db).create(user)
    return {"id": str(result.id), "email": result.email, "role_id": str(result.role_id)}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_USERS}))])
async def list_users(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    users = await UserRepository(db).list_users()
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "role_id": str(u.role_id),
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]
