from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest,
)
from app.services.auth_service import AuthService, UserService
from app.utils.response import ok, created
from loguru import logger

router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Login with email and password.

    Returns access token and refresh token.
    """
    auth_service = AuthService(session)

    access_token, refresh_token = await auth_service.login(
        email=request.email,
        password=request.password,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Refresh access token using refresh token.

    If token rotation is enabled, a new refresh token is also issued.
    """
    auth_service = AuthService(session)

    access_token = await auth_service.refresh_access_token(request.refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Logout user (invalidate all sessions)."""
    auth_service = AuthService(session)
    await auth_service.logout(str(current_user.id))

    logger.info(f"User logged out | user_id={current_user.id}")


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get current logged-in user info."""
    # Reload user with permissions
    user_service = UserService(session)
    user = await user_service.get_user_with_permissions(str(current_user.id))

    if not user:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("User")

    return UserResponse.model_validate(user).__dict__


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Change password for current user."""
    if not request.validate_passwords_match():
        from app.core.exceptions import ValidationException

        raise ValidationException("New password and confirmation do not match.", field="confirm_password")

    user_service = UserService(session)
    await user_service.change_password(
        str(current_user.id),
        request.old_password,
        request.new_password,
    )

    logger.info(f"User changed password | user_id={current_user.id}")

    return ok(message="Password changed successfully.")