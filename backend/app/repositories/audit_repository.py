from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, user_id: str | None, module: str, action: str, old_value: dict | None, new_value: dict | None) -> None:
        row = AuditLog(user_id=user_id, module=module, action=action, old_value=old_value, new_value=new_value)
        self.db.add(row)
        await self.db.commit()
