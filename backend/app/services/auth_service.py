from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.redis import redis_client
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repo.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return user

    async def register_user(self, name: str, email: str, password: str, role_name: str = "SALES") -> User:
        existing_user = await self.repo.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        requested_role = role_name.upper().strip()
        if requested_role == "ADMIN":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Self-registration cannot create ADMIN users")

        role = await self.repo.get_role_by_name(requested_role)
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
        )
        return await self.repo.create_user(user)

    async def issue_tokens(self, user_id: str) -> dict[str, str]:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        refresh_payload = decode_token(refresh_token)
        ttl = max(int(refresh_payload["exp"] - datetime.now(timezone.utc).timestamp()), 1)
        await redis_client.setex(f"refresh:{refresh_payload['jti']}", ttl, user_id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def rotate_refresh_token(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token(refresh_token)
        except TokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed refresh token")

        exists = await redis_client.get(f"refresh:{jti}")
        if not exists:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or expired")

        await redis_client.delete(f"refresh:{jti}")
        return await self.issue_tokens(user_id)

    async def revoke_tokens(self, access_token: str, refresh_token: str) -> None:
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        access_ttl = max(int(access_payload["exp"] - datetime.now(timezone.utc).timestamp()), 1)
        refresh_ttl = max(int(refresh_payload["exp"] - datetime.now(timezone.utc).timestamp()), 1)

        await redis_client.setex(f"blacklist:{access_payload['jti']}", access_ttl, "1")
        await redis_client.setex(f"blacklist:{refresh_payload['jti']}", refresh_ttl, "1")
        await redis_client.delete(f"refresh:{refresh_payload['jti']}")


def build_password_hash(password: str) -> str:
    return hash_password(password)
