from __future__ import annotations

from enum import Enum
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import SystemSetting


class NumberingPrefix(str, Enum):
    """Prefixes for sequential numbering."""

    LEAD = "LEAD"
    CUSTOMER = "CUST"
    PROJECT = "PROJ"
    BOOKING = "BKG"
    INVOICE = "INV"
    PAYMENT = "PAY"
    FOLLOWUP = "FUP"
    TASK = "TSK"
    QUOTE = "QT"
    PROPOSAL = "PROP"


class NumberingService:
    """
    Sequential numbering service for business entities.

    Uses database counter to ensure uniqueness across concurrent requests.
    Format: PREFIX-NNNNNN (e.g., LEAD-000001, CUST-000042)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_next_number(self, prefix: NumberingPrefix | str) -> str:
        """
        Get next sequential number for a prefix.

        Increments counter atomically and returns formatted number.
        """
        if isinstance(prefix, NumberingPrefix):
            prefix = prefix.value

        setting_key = f"counter_{prefix}"

        # ── Try to fetch and increment existing counter ───────────────────
        from sqlalchemy import update

        stmt = (
            update(SystemSetting)
            .where(SystemSetting.key == setting_key)
            .values(int_value=SystemSetting.int_value + 1)
            .returning(SystemSetting.int_value)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        row = result.first()
        if row:
            next_counter = row[0]
        else:
            # ── Initialize new counter if doesn't exist ─────────────────────
            setting = SystemSetting(
                key=setting_key,
                int_value=1,
                description=f"Sequential counter for {prefix} numbers",
            )
            self.session.add(setting)
            await self.session.flush()
            next_counter = 1

        return f"{prefix}-{next_counter:06d}"

    async def get_next_numbers(self, prefix: NumberingPrefix | str, count: int) -> list[str]:
        """Get multiple sequential numbers (batch)."""
        return [await self.get_next_number(prefix) for _ in range(count)]

    async def reset_counter(self, prefix: NumberingPrefix | str) -> None:
        """Reset counter to 0 (admin only, for testing/migrations)."""
        if isinstance(prefix, NumberingPrefix):
            prefix = prefix.value

        setting_key = f"counter_{prefix}"

        from sqlalchemy import update

        stmt = (
            update(SystemSetting)
            .where(SystemSetting.key == setting_key)
            .values(int_value=0)
        )

        await self.session.execute(stmt)
        await self.session.flush()
