"""
Service layer for notification management business logic.

Handles: sending, bulk sending, preferences, templates, marking read/archived.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import NotFoundException, ValidationException
from app.models.notification import Notification, NotificationPreference, NotificationTemplate
from app.repositories.notification_repository import (
    NotificationRepository, NotificationPreferenceRepository, NotificationTemplateRepository
)
from app.utils.enums import NotificationType, NotificationChannel
from app.utils.numbering import NumberingService


class NotificationService:
    """Service for notification operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NotificationRepository(session)
        self.pref_repo = NotificationPreferenceRepository(session)
        self.template_repo = NotificationTemplateRepository(session)

    # ── Send Notifications ────────────────────────────────────────────

    async def send(
        self,
        user_id: UUID,
        type_: NotificationType,
        title: str,
        body: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        priority: int = 0,
        action_url: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Notification:
        """Send a single notification to a user."""
        # Check user preference
        enabled = await self.pref_repo.is_channel_enabled(user_id, type_, channel)
        if not enabled:
            logger.debug(f"Notification suppressed by preference | user={user_id} | type={type_.value}")
            # Still create IN_APP as fallback if other channel blocked
            if channel != NotificationChannel.IN_APP:
                channel = NotificationChannel.IN_APP

        notification = Notification(
            user_id=user_id,
            type=type_,
            channel=channel,
            title=title,
            body=body,
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
            action_url=action_url,
            metadata=metadata or {},
        )
        self.session.add(notification)
        await self.session.flush()

        logger.info(f"Notification created | user={user_id} | type={type_.value}")

        return notification

    async def send_bulk(
        self,
        user_ids: List[UUID],
        type_: NotificationType,
        title: str,
        body: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        priority: int = 0,
        action_url: Optional[str] = None,
    ) -> List[Notification]:
        """Send notification to multiple users."""
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                type=type_,
                channel=channel,
                title=title,
                body=body,
                entity_type=entity_type,
                entity_id=entity_id,
                priority=priority,
                action_url=action_url,
                metadata={},
            )
            self.session.add(notification)
            notifications.append(notification)

        await self.session.flush()

        logger.info(f"Bulk notification sent | users={len(user_ids)} | type={type_.value}")

        return notifications

    async def send_from_template(
        self,
        user_id: UUID,
        template_name: str,
        variables: dict,
        channel: Optional[NotificationChannel] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        priority: int = 0,
    ) -> Notification:
        """Send notification using a template with variable substitution."""
        template = await self.template_repo.get_by_name(template_name)
        if not template:
            raise NotFoundException(f"Notification template '{template_name}' not found")

        # Render template
        title = template.title_template
        body = template.body_template
        for key, value in variables.items():
            placeholder = f"{{{{ {key} }}}}"
            title = title.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        effective_channel = channel or template.channel

        return await self.send(
            user_id=user_id,
            type_=template.notification_type,
            title=title,
            body=body,
            channel=effective_channel,
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
        )

    # ── Read/Archive Management ───────────────────────────────────────

    async def get_user_notifications(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None,
        is_archived: bool = False,
        types: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user."""
        type_enums = None
        if types:
            type_enums = [NotificationType[t.upper()] for t in types if t]

        return await self.repo.get_user_notifications(
            user_id=user_id,
            is_read=is_read,
            is_archived=is_archived,
            types=type_enums,
            skip=skip,
            limit=limit,
        )

    async def get_unread_count(self, user_id: UUID) -> dict:
        """Get unread count breakdown for a user."""
        return await self.repo.count_unread(user_id)

    async def mark_read(self, notification_ids: List[UUID], user_id: UUID) -> int:
        """Mark notifications as read."""
        count = await self.repo.mark_read(notification_ids, user_id)
        logger.info(f"Marked {count} notifications as read | user={user_id}")
        return count

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for user."""
        count = await self.repo.mark_all_read(user_id)
        logger.info(f"Marked all notifications as read | user={user_id} | count={count}")
        return count

    async def mark_archived(self, notification_ids: List[UUID], user_id: UUID) -> int:
        """Archive notifications."""
        count = await self.repo.mark_archived(notification_ids, user_id)
        logger.info(f"Archived {count} notifications | user={user_id}")
        return count

    async def delete_notification(self, notification_id: UUID, user_id: UUID) -> None:
        """Soft delete a notification."""
        notification = await self.repo.get(notification_id)
        if not notification or notification.user_id != user_id:
            raise NotFoundException(f"Notification {notification_id} not found")

        notification.is_deleted = True
        notification.deleted_at = datetime.utcnow()

    # ── Preferences ───────────────────────────────────────────────────

    async def get_user_preferences(self, user_id: UUID) -> List[NotificationPreference]:
        """Get all notification preferences for a user."""
        return await self.pref_repo.get_user_preferences(user_id)

    async def update_preference(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        **kwargs,
    ) -> NotificationPreference:
        """Update or create a notification preference."""
        pref = await self.pref_repo.upsert_preference(user_id, notification_type, **kwargs)
        logger.info(f"Preference updated | user={user_id} | type={notification_type.value}")
        return pref

    # ── Templates ─────────────────────────────────────────────────────

    async def create_template(
        self,
        name: str,
        notification_type: NotificationType,
        channel: NotificationChannel,
        title_template: str,
        body_template: str,
        variables: Optional[List[str]] = None,
    ) -> NotificationTemplate:
        """Create a notification template."""
        existing = await self.template_repo.get_by_name(name)
        if existing:
            raise ValidationException(f"Template '{name}' already exists")

        template = NotificationTemplate(
            name=name,
            notification_type=notification_type,
            channel=channel,
            title_template=title_template,
            body_template=body_template,
            variables=variables or [],
        )
        self.session.add(template)
        await self.session.flush()

        logger.info(f"Notification template created | name={name}")

        return template

    async def get_templates(self, active_only: bool = True) -> List[NotificationTemplate]:
        """Get all templates."""
        return await self.template_repo.list_all(active_only)

    async def update_template(self, template_id: UUID, **kwargs) -> NotificationTemplate:
        """Update a template."""
        template = await self.template_repo.get(template_id)
        if not template:
            raise NotFoundException(f"Template {template_id} not found")

        allowed = {"title_template", "body_template", "variables", "is_active"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(template, key, value)

        return template

    # ── Statistics ────────────────────────────────────────────────────

    async def get_statistics(self) -> dict:
        """Get notification statistics."""
        from sqlalchemy import func, select
        from app.models.notification import Notification

        total_query = select(func.count(Notification.id)).where(Notification.is_deleted == False)
        total = (await self.session.execute(total_query)).scalars().first() or 0

        unread_query = select(func.count(Notification.id)).where(
            and_(Notification.is_read == False, Notification.is_deleted == False)
        )
        unread = (await self.session.execute(unread_query)).scalars().first() or 0

        archived_query = select(func.count(Notification.id)).where(
            and_(Notification.is_archived == True, Notification.is_deleted == False)
        )
        archived = (await self.session.execute(archived_query)).scalars().first() or 0

        by_type = await self.repo.count_by_type()
        by_channel = await self.repo.count_by_channel()

        return {
            "total_sent": total,
            "unread_count": unread,
            "read_count": total - unread,
            "archived_count": archived,
            "by_type": by_type,
            "by_channel": by_channel,
        }


def and_(*clauses):
    """SQLAlchemy and_ helper."""
    from sqlalchemy import and_ as _and_
    return _and_(*clauses)
