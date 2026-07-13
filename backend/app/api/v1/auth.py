from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.database.postgres import get_db
from app.models.role import Role
from app.repositories.audit_repository import AuditRepository
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest = Body(
        ...,
        openapi_examples={
            "sales": {
                "summary": "Register a sales user",
                "value": {
                    "name": "Rahul Sharma",
                    "email": "rahul@company.com",
                    "password": "StrongPass@123",
                    "role_name": "SALES",
                },
            }
        },
    ),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(AuthRepository(db))
    user = await auth_service.register_user(payload.name, payload.email, payload.password, payload.role_name)
    role = await db.get(Role, user.role_id)
    await AuditRepository(db).log(str(user.id), "auth", "register", None, {"email": user.email, "role": role.name if role else None})
    return RegisterResponse(user_id=str(user.id), email=user.email, role=role.name if role else "UNKNOWN")


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest = Body(
        ...,
        openapi_examples={
            "default": {"summary": "Email/password login", "value": {"email": "admin@rpex.local", "password": "admin12345"}}
        },
    ),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(AuthRepository(db))
    user = await auth_service.authenticate(payload.email, payload.password)
    tokens = await auth_service.issue_tokens(str(user.id))

    await AuditRepository(db).log(str(user.id), "auth", "login", None, {"email": payload.email, "at": datetime.now(timezone.utc).isoformat()})
    role = await db.get(Role, user.role_id)
    return TokenResponse(**tokens, role=role.name if role else None)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest = Body(
        ...,
        openapi_examples={"default": {"summary": "Rotate refresh token", "value": {"refresh_token": "<refresh-token>"}}},
    ),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(AuthRepository(db))
    tokens = await auth_service.rotate_refresh_token(payload.refresh_token)
    return TokenResponse(**tokens)


@router.post("/logout")
async def logout(
    current_user: CurrentUser,
    payload: LogoutRequest = Body(
        ...,
        openapi_examples={
            "default": {"summary": "Logout and revoke tokens", "value": {"refresh_token": "<refresh-token>"}}
        },
    ),
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

    access_token = authorization.split(" ", 1)[1]
    auth_service = AuthService(AuthRepository(db))
    await auth_service.revoke_tokens(access_token, payload.refresh_token)
    await AuditRepository(db).log(str(current_user.id), "auth", "logout", None, {"user_id": str(current_user.id)})
    return {"message": "Logged out"}


@router.get("/me")
async def me(current_user: CurrentUser):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role_id": str(current_user.role_id),
        "role": current_user.role.name if current_user.role else None,
        "is_active": current_user.is_active,
    }
