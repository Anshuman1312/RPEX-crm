"""
Audit service — writes immutable audit log entries and provides query interface.

Usage:
    audit = AuditService(session)
    await audit.log(
        action="lead.created",
        entity_type="lead",
        entity_id=lead.id,
        entity_display=lead.lead_number,
        description=f"Lead {lead.lead_number} created",
        user_id=current_user.id,
        user_email=current_user.email,
        new_value={"status": "new", "source": "walk_in"},
        request=request,   # optional FastAPI Request
    )
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Tuple
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditLogRepository
from app.schemas.audit import AuditLogResponse, AuditLogListResponse, AuditLogStats


class AuditService:
    """Write-and-read service for the immutable audit trail."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuditLogRepository(session)

    # ── Writing ───────────────────────────────────────────────────────

    async def log(
        self,
        action: str,
        entity_type: str,
        description: str,
        entity_id: Optional[UUID] = None,
        entity_display: Optional[str] = None,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        changes: Optional[dict] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        request: Optional[Request] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        # Extract request context if provided
        if request is not None:
            ip_address = ip_address or self._get_client_ip(request)
            user_agent = user_agent or request.headers.get("user-agent")
            correlation_id = correlation_id or request.headers.get("x-correlation-id")
            request_path = request_path or str(request.url.path)
            request_method = request_method or request.method

        entry = await self.repo.create(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_display=entity_display,
            description=description,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            request_path=request_path,
            request_method=request_method,
            extra_data=metadata or {},
        )

        logger.debug(f"Audit | {action} | {entity_type}:{entity_id} | user={user_email}")
        return entry

    async def log_failure(
        self,
        action: str,
        entity_type: str,
        description: str,
        error_message: str,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
        request: Optional[Request] = None,
        **kwargs,
    ) -> AuditLog:
        """Log a failed operation."""
        return await self.log(
            action=action,
            entity_type=entity_type,
            description=description,
            user_id=user_id,
            user_email=user_email,
            status="failure",
            error_message=error_message,
            request=request,
            **kwargs,
        )

    def build_changes(self, old: dict, new: dict) -> dict:
        """Compute field-level diff between old and new values."""
        changes = {}
        all_keys = set(old) | set(new)
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                changes[key] = {"from": old_val, "to": new_val}
        return changes

    # ── Reading ───────────────────────────────────────────────────────

    async def get_log(self, log_id: UUID) -> AuditLog:
        """Get a single audit log entry."""
        from app.core.exceptions import NotFoundException
        entry = await self.repo.get(log_id)
        if not entry:
            raise NotFoundException(f"Audit log {log_id} not found")
        return entry

    async def list_logs(
        self,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """Query audit logs with filters."""
        return await self.repo.list_with_filter(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            skip=skip,
            limit=limit,
        )

    async def get_entity_history(
        self, entity_type: str, entity_id: UUID
    ) -> List[AuditLog]:
        """Full audit history for a specific entity."""
        return await self.repo.get_entity_history(entity_type, entity_id)

    async def get_user_activity(
        self, user_id: UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[AuditLog], int]:
        """Audit trail for a specific user."""
        return await self.repo.get_user_activity(user_id, skip, limit)

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Aggregate audit statistics."""
        return await self.repo.get_statistics(start_date, end_date)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract real IP from request, respecting proxy headers."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
