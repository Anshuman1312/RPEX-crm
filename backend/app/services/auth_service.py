from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    InvalidTokenException,
    TokenExpiredException,
    AccountDisabledException,
    DuplicateEntryException,
    ValidationException,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_token,
)
from app.models.user import User, UserSession, LoginHistory
from app.repositories.user_repository import (
    UserRepository,
    UserSessionRepository,
    LoginHistoryRepository,
)
from app.repositories.auth_repository import AuthRepository


class AuthService:
    """
    Authentication and authorization business logic.

    Handles:
      - User login with credentials
      - JWT token generation and validation
      - Refresh token rotation
      - Session management
      - Login history tracking
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = UserSessionRepository(session)
        self.history_repo = LoginHistoryRepository(session)
        self.repo = AuthRepository(session)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repo.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationException("Invalid email or password.")
        if hasattr(user, "is_active") and not user.is_active:
            raise AuthenticationException("User account is inactive.")
        return user

    async def register_user(self, name: str, email: str, password: str, phone: str, role_name: str = "SALES") -> User:
        existing_user = await self.repo.get_user_by_email(email)
        if existing_user:
            raise DuplicateEntryException("User", "email")

        requested_role = role_name.upper().strip()
        role = await self.repo.get_role_by_name(requested_role)
        if not role:
            raise ValidationException(f"Invalid role: {role_name}")

        user_kwargs = {
            "email": email,
            "phone": phone,
            "password_hash": hash_password(password),
            "role_id": role.id,
            "employee_code": f"EMP-{uuid.uuid4().hex[:10].upper()}",
        }
        if hasattr(User, "full_name"):
            user_kwargs["full_name"] = name
        if hasattr(User, "name"):
            user_kwargs["name"] = name
        if hasattr(User, "is_active"):
            user_kwargs["is_active"] = True

        user = User(**user_kwargs)
        return await self.repo.create_user(user)

    async def issue_tokens(self, user_id: str) -> dict[str, str]:
        from app.core.security import decode_access_token
        from app.core.redis import redis_client, RedisManager
        
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        # Decode refresh token to get JTI and expiry
        try:
            refresh_payload = decode_refresh_token(refresh_token)
            jti = refresh_payload.get("jti")
            exp = refresh_payload.get("exp", 0)
        except (TokenExpiredException, InvalidTokenException) as exc:
            from loguru import logger
            logger.error(f"Failed to decode refresh token: {exc}")
            raise AuthenticationException("Failed to generate refresh token")
        
        # Calculate TTL from expiry time
        ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
        
        # Store refresh token mapping in Redis if available
        if jti and RedisManager.is_available():
            try:
                await RedisManager.set_with_ttl(f"refresh:{jti}", user_id, ttl)
            except Exception as exc:
                from loguru import logger
                logger.warning(f"Failed to cache refresh token in Redis: {exc} - continuing without cache")
                # Don't fail the entire operation if Redis is down
        
        return {"access_token": access_token, "refresh_token": refresh_token}


    async def login(
        self,
        email: str,
        password: str,
        device_type: str | None = None,
        device_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """
        Authenticate user and return (access_token, refresh_token).

        Raises:
            AuthenticationException: invalid credentials
            AccountDisabledException: user not active/verified
        """
        # ── Fetch user by email ────────────────────────────────────────────
        user = await self.user_repo.get_by_email(email.lower())
        if not user:
            # Log failed attempt
            await self.history_repo.create(
                ip_address=ip_address,
                device_type=device_type,
                user_agent=user_agent,
                status="failed",
                failure_reason="user_not_found",
            )
            raise AuthenticationException("Invalid email or password.")

        # ── Verify password ────────────────────────────────────────────────
        if not verify_password(password, user.password_hash):
            await self.history_repo.create(
                user_id=user.id,
                ip_address=ip_address,
                device_type=device_type,
                user_agent=user_agent,
                status="failed",
                failure_reason="invalid_password",
            )
            raise AuthenticationException("Invalid email or password.")

        # ── Check account status ───────────────────────────────────────────
        if user.status != "active":
            await self.history_repo.create(
                user_id=user.id,
                ip_address=ip_address,
                device_type=device_type,
                user_agent=user_agent,
                status="blocked",
                failure_reason=f"account_{user.status}",
            )
            raise AccountDisabledException()

        if not user.is_verified:
            await self.history_repo.create(
                user_id=user.id,
                ip_address=ip_address,
                device_type=device_type,
                user_agent=user_agent,
                status="blocked",
                failure_reason="account_not_verified",
            )
            raise AccountDisabledException()

        # ── Generate tokens ───────────────────────────────────────────────
        access_token = create_access_token(str(user.id), {"email": user.email})
        refresh_token = create_refresh_token(str(user.id))

        # ── Store session ──────────────────────────────────────────────────
        refresh_token_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await self.session_repo.create(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            device_type=device_type,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        # ── Log successful login ───────────────────────────────────────────
        user.last_login_at = datetime.now(timezone.utc)
        await self.history_repo.create(
            user_id=user.id,
            ip_address=ip_address,
            device_type=device_type,
            user_agent=user_agent,
            status="success",
        )

        await self.session.flush()

        return access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Exchange a refresh token for a new access token.

        Optionally rotate the refresh token (store new hash in Redis/DB).

        Raises:
            InvalidTokenException: token invalid
            TokenExpiredException: token expired
        """
        # ── Decode and validate refresh token ──────────────────────────────
        try:
            payload = decode_refresh_token(refresh_token)
        except (TokenExpiredException, InvalidTokenException):
            raise

        user_id = uuid.UUID(payload["sub"])
        token_hash = hash_token(refresh_token)

        # ── Verify session exists and is active ────────────────────────────
        session = await self.session_repo.get_active_session_by_token_hash(token_hash)
        if not session:
            raise InvalidTokenException()

        # ── Verify user still exists and is active ────────────────────────
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.status != "active":
            raise InvalidTokenException()

        # ── Generate new access token ──────────────────────────────────────
        new_access_token = create_access_token(str(user_id), {"email": user.email})

        # ── Optionally rotate refresh token (if enabled) ───────────────────
        if settings.REFRESH_TOKEN_ROTATE:
            # Invalidate old session
            await self.session_repo.logout_session(str(session.id))
            # Create new session with new refresh token
            new_refresh_token = create_refresh_token(str(user_id))
            new_token_hash = hash_token(new_refresh_token)
            expires_at = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
            await self.session_repo.create(
                user_id=user_id,
                refresh_token_hash=new_token_hash,
                device_type=session.device_type,
                device_id=session.device_id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                expires_at=expires_at,
            )
            await self.session.flush()

        # Update last activity
        session.last_activity_at = datetime.now(timezone.utc)

        return new_access_token

    async def logout(self, user_id: str, session_id: str | None = None) -> None:
        """
        Logout user session(s).

        If session_id provided, logout only that session.
        Otherwise, logout all sessions.
        """
        if session_id:
            await self.session_repo.logout_session(session_id)
        else:
            await self.session_repo.logout_all_user_sessions(user_id)

        await self.session.flush()

    async def verify_refresh_token(self, refresh_token: str) -> dict:
        """
        Verify refresh token is valid and return payload.

        Raises InvalidTokenException or TokenExpiredException.
        """
        return decode_refresh_token(refresh_token)

    async def verify_user_session(self, user_id: str, session_id: str) -> bool:
        """Check if a session belongs to the user and is active."""
        session = await self.session_repo.get_by_id(session_id)
        return session is not None and session.user_id == uuid.UUID(user_id) and session.is_active


class UserService:
    """User management business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_user(
        self,
        email: str,
        phone: str,
        full_name: str,
        password: str,
        employee_code: str,
        department_id: str | None = None,
        designation_id: str | None = None,
        role_id: str | None = None,
        created_by: uuid.UUID | None = None,
    ) -> User:
        """
        Create new user.

        Raises:
            DuplicateEntryException: if email or employee_code already exists
        """
        # Check for existing user
        existing_by_email = await self.user_repo.get_by_email(email.lower())
        if existing_by_email:
            raise DuplicateEntryException("User", "email")

        existing_by_code = await self.user_repo.get_by_employee_code(employee_code)
        if existing_by_code:
            raise DuplicateEntryException("User", "employee_code")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = await self.user_repo.create(
            email=email.lower(),
            phone=phone,
            full_name=full_name,
            password_hash=password_hash,
            employee_code=employee_code,
            department_id=uuid.UUID(department_id) if department_id else None,
            designation_id=uuid.UUID(designation_id) if designation_id else None,
            role_id=uuid.UUID(role_id) if role_id else None,
            status="active",
            is_verified=False,  # Requires email verification
            created_by=created_by,
        )

        await self.session.flush()
        return user

    async def get_user(self, user_id: str) -> User | None:
        """Fetch user by ID."""
        return await self.user_repo.get_by_id(uuid.UUID(user_id))

    async def get_user_with_permissions(self, user_id: str) -> User | None:
        """Fetch user with role and permissions (for auth checks)."""
        return await self.user_repo.get_with_role_and_permissions(uuid.UUID(user_id))

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        role_id: uuid.UUID | None = None,
        department_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> tuple[list[User], int]:
        """List users with count and eager relations."""
        users = await self.user_repo.list_with_relations(
            skip=skip,
            limit=limit,
            search=search,
            role_id=role_id,
            department_id=department_id,
            status=status,
        )
        count = await self.user_repo.count_with_filters(
            search=search,
            role_id=role_id,
            department_id=department_id,
            status=status,
        )
        return users, count

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> User:
        """
        Change user password.

        Raises:
            AuthenticationException: if old password is incorrect
        """
        user = await self.user_repo.get_or_404(uuid.UUID(user_id), "User")

        if not verify_password(old_password, user.password_hash):
            raise AuthenticationException("Current password is incorrect.")

        user.password_hash = hash_password(new_password)
        await self.session.flush()
        return user

    async def verify_user(self, user_id: str) -> User:
        """Mark user as verified."""
        return await self.user_repo.update(uuid.UUID(user_id), is_verified=True, status="active")

    async def suspend_user(self, user_id: str) -> User:
        """Suspend user account."""
        return await self.user_repo.update(uuid.UUID(user_id), status="suspended")
