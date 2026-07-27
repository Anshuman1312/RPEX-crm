"""
Repository layer for notification data access.

Repositories:
- NotificationRepository: Notification CRUD and delivery tracking
- NotificationPreferenceRepository: User preference management
- NotificationTemplateRepository: Template CRUD
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, asc, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.notification import Notification, NotificationPreference, NotificationTemplate
from app.utils.enums import NotificationType, NotificationChannel


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notification operations."""

    async def get_user_notifications(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None,
        is_archived: bool = False,
        types: Optional[List[NotificationType]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a user."""
        filters = [
            Notification.user_id == user_id,
            Notification.is_archived == is_archived,
            Notification.is_deleted == False,
        ]
        if is_read is not None:
            filters.append(Notification.is_read == is_read)
        if types:
            filters.append(Notification.type.in_(types))

        count_query = select(func.count(Notification.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Notification)
            .where(and_(*filters))
            .order_by(desc(Notification.priority), desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        notifications = result.scalars().all()

        return notifications, total

    async def count_unread(self, user_id: UUID) -> dict:
        """Count unread notifications for a user by priority."""
        query = select(
            Notification.priority,
            func.count(Notification.id)
        ).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_archived == False,
                Notification.is_deleted == False,
            )
        ).group_by(Notification.priority)

        result = await self.session.execute(query)
        by_priority = dict(result.all() or [])

        total = sum(by_priority.values())
        return {
            "total": total,
            "critical": by_priority.get(3, 0),
            "high": by_priority.get(2, 0),
            "medium": by_priority.get(1, 0),
            "low": by_priority.get(0, 0),
        }

    async def mark_read(
        self, notification_ids: List[UUID], user_id: UUID
    ) -> int:
        """Mark notifications as read. Returns count updated."""
        from sqlalchemy import update
        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all unread notifications as read for a user."""
        from sqlalchemy import update
        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_archived == False,
                )
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def mark_archived(
        self, notification_ids: List[UUID], user_id: UUID
    ) -> int:
        """Archive notifications. Returns count updated."""
        from sqlalchemy import update
        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id,
                )
            )
            .values(is_archived=True, archived_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Notification], int]:
        """Get notifications for a specific entity."""
        filters = [
            Notification.entity_type == entity_type,
            Notification.entity_id == entity_id,
            Notification.is_deleted == False,
        ]

        count_query = select(func.count(Notification.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Notification)
            .where(and_(*filters))
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        notifications = result.scalars().all()

        return notifications, total

    async def count_by_type(self) -> dict:
        """Count notifications by type."""
        query = (
            select(Notification.type, func.count(Notification.id))
            .where(Notification.is_deleted == False)
            .group_by(Notification.type)
        )
        result = await self.session.execute(query)
        return {t.value if hasattr(t, "value") else t: c for t, c in result.all()}

    async def count_by_channel(self) -> dict:
        """Count notifications by channel."""
        query = (
            select(Notification.channel, func.count(Notification.id))
            .where(Notification.is_deleted == False)
            .group_by(Notification.channel)
        )
        result = await self.session.execute(query)
        return {ch.value if hasattr(ch, "value") else ch: c for ch, c in result.all()}


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    """Repository for notification preference operations."""

    async def get_user_preferences(
        self, user_id: UUID
    ) -> List[NotificationPreference]:
        """Get all preferences for a user."""
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        ).order_by(asc(NotificationPreference.notification_type))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_preference(
        self, user_id: UUID, notification_type: NotificationType
    ) -> Optional[NotificationPreference]:
        """Get user preference for a notification type."""
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def upsert_preference(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        **kwargs,
    ) -> NotificationPreference:
        """Create or update a preference."""
        existing = await self.get_preference(user_id, notification_type)
        if existing:
            for key, value in kwargs.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            return existing
        else:
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=notification_type,
                **{k: v for k, v in kwargs.items() if v is not None},
            )
            self.session.add(pref)
            await self.session.flush()
            return pref

    async def is_channel_enabled(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        channel: NotificationChannel,
    ) -> bool:
        """Check if a channel is enabled for user/type combination."""
        pref = await self.get_preference(user_id, notification_type)
        if not pref:
            # Default: in_app enabled, others disabled
            return channel == NotificationChannel.IN_APP

        channel_map = {
            NotificationChannel.IN_APP: pref.in_app_enabled,
            NotificationChannel.EMAIL: pref.email_enabled,
            NotificationChannel.SMS: pref.sms_enabled,
            NotificationChannel.PUSH: pref.push_enabled,
            NotificationChannel.WHATSAPP: pref.whatsapp_enabled,
        }
        return channel_map.get(channel, False)


class NotificationTemplateRepository(BaseRepository[NotificationTemplate]):
    """Repository for notification template operations."""

    async def get_by_name(self, name: str) -> Optional[NotificationTemplate]:
        """Get template by name."""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.name == name,
                NotificationTemplate.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_type_and_channel(
        self,
        notification_type: NotificationType,
        channel: NotificationChannel,
    ) -> Optional[NotificationTemplate]:
        """Get active template for a type+channel combination."""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.notification_type == notification_type,
                NotificationTemplate.channel == channel,
                NotificationTemplate.is_active == True,
                NotificationTemplate.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_all(
        self,
        active_only: bool = True,
    ) -> List[NotificationTemplate]:
        """List all templates."""
        filters = [NotificationTemplate.is_deleted == False]
        if active_only:
            filters.append(NotificationTemplate.is_active == True)

        query = (
            select(NotificationTemplate)
            .where(and_(*filters))
            .order_by(asc(NotificationTemplate.notification_type))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
