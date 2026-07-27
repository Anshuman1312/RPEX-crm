from __future__ import annotations

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserSession, LoginHistory, Role
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User-specific repository with auth-focused queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email (case-insensitive, respects soft delete)."""
        query = select(self.model).where(
            and_(
                self.model.email == email.lower(),
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_phone(self, phone: str) -> User | None:
        """Fetch user by phone."""
        query = select(self.model).where(
            and_(
                self.model.phone == phone,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_employee_code(self, code: str) -> User | None:
        """Fetch user by employee code."""
        query = select(self.model).where(
            and_(
                self.model.employee_code == code,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_role_and_permissions(self, user_id: str) -> User | None:
        """
        Fetch user with role and all permissions eagerly loaded.

        Used for permission checking to avoid N+1 queries.
        """
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.id == user_id,
                    self.model.is_deleted == False,
                )
            )
            .options(
                selectinload(self.model.role).selectinload(Role.permissions),
                selectinload(self.model.department),
                selectinload(self.model.designation),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_active(self, skip: int = 0, limit: int = 20) -> list[User]:
        """List only active, verified users."""
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.is_deleted == False,
                    self.model.status == "active",
                    self.model.is_verified == True,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class UserSessionRepository(BaseRepository[UserSession]):
    """Repository for user sessions (refresh tokens)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSession)

    async def get_active_session_by_token_hash(self, token_hash: str) -> UserSession | None:
        """Fetch active session by refresh token hash."""
        from datetime import datetime, timezone

        query = select(self.model).where(
            and_(
                self.model.refresh_token_hash == token_hash,
                self.model.is_active == True,
                self.model.expires_at > datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_sessions(self, user_id: str) -> list[UserSession]:
        """Fetch all active sessions for a user."""
        from datetime import datetime, timezone

        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.is_active == True,
                self.model.expires_at > datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def logout_session(self, session_id: str) -> UserSession:
        """Mark a session as inactive."""
        return await self.update(session_id, is_active=False)

    async def logout_all_user_sessions(self, user_id: str) -> int:
        """Logout all sessions for a user. Returns count of sessions updated."""
        from sqlalchemy import update

        stmt = (
            update(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.is_active == True,
                )
            )
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount or 0


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    """Repository for login history (append-only audit log)."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LoginHistory)

    async def get_recent_logins(self, user_id: str, limit: int = 10) -> list[LoginHistory]:
        """Get recent login attempts for a user."""
        from sqlalchemy import desc

        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(desc(self.model.login_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_failed_logins_by_email(self, email: str, hours: int = 1) -> int:
        """Count failed login attempts for an email in the last N hours."""
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import func

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(func.count())
            .select_from(self.model)
            .where(
                and_(
                    self.model.login_at >= cutoff,
                    self.model.status == "failed",
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
