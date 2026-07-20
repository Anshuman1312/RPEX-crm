import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lead import Lead
from app.models.inventory_unit import InventoryUnit
from app.models.finance_ledger_entry import FinanceLedgerEntry, ExpenseLedger

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview_metrics(self):
        # 1. Inventory Stats
        inventory_stmt = select(
            InventoryUnit.booking_status, 
            func.count(InventoryUnit.id)
        ).group_by(InventoryUnit.booking_status)
        inventory_res = await self.db.execute(inventory_stmt)
        inventory_stats = dict(inventory_res.all())

        # 2. Lead Stats (Total and Today)
        today = datetime.now(timezone.utc).date()
        total_leads = await self.db.execute(select(func.count(Lead.id)))
        today_leads = await self.db.execute(
            select(func.count(Lead.id)).where(func.date(Lead.created_at) == today)
        )

        # 3. Finance Stats (Collections Today)
        today_collections = await self.db.execute(
            select(func.sum(FinanceLedgerEntry.amount))
            .where(and_(
                func.date(FinanceLedgerEntry.entry_date) == today,
                FinanceLedgerEntry.entry_type == "COLLECTION" # Or whatever your type is
            ))
        )

        return {
            "inventory": {
                "total": sum(inventory_stats.values()),
                "available": inventory_stats.get("AVAILABLE", 0),
                "sold": inventory_stats.get("BOOKED", 0) + inventory_stats.get("REGISTERED", 0),
                "reserved": inventory_stats.get("BLOCKED", 0)
            },
            "leads": {
                "total": total_leads.scalar_one() or 0,
                "today": today_leads.scalar_one() or 0
            },
            "collections_today": today_collections.scalar_one() or 0
        }