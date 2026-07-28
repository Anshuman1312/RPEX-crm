from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository
from app.utils.numbering import NumberingService


class FinanceService:
    def __init__(self, repo: FinanceRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo
        self.numbering = NumberingService(repo.session)

    async def create_payment(self, payload: dict[str, Any], actor_user_id: str):
        row = await self.repo.create_payment(payload)
        await self.audit_repo.create(
            user_id=payload.get("recorded_by") or actor_user_id,
            action="finance.payment.created",
            entity_type="customer_payment",
            entity_id=row.id,
            entity_display=row.reference_no,
            description=f"Payment recorded for customer {row.customer_id}",
            new_value={"amount": str(row.amount), "status": row.status},
            extra_data={"payment_mode": row.payment_mode},
        )
        return row

    async def create_invoice(self, payload: dict[str, Any], actor_user_id: str):
        items = payload.get("items") or []
        subtotal = Decimal("0")
        gst_amount = Decimal("0")
        for item in items:
            line_amount = Decimal(str(item.get("quantity", 1))) * Decimal(str(item.get("unit_price", 0)))
            line_gst = line_amount * (Decimal(str(item.get("gst_rate", 0))) / Decimal("100"))
            subtotal += line_amount
            gst_amount += line_gst

        row = await self.repo.create_invoice(
            {
                **payload,
                "invoice_number": await self.numbering.get_next_number("INV"),
                "invoice_date": datetime.utcnow(),
                "subtotal": subtotal,
                "gst_amount": gst_amount,
                "total_amount": subtotal + gst_amount,
                "paid_amount": Decimal("0"),
                "payment_status": "PENDING",
                "invoice_status": "DRAFT",
            }
        )
        await self.audit_repo.create(
            user_id=payload.get("created_by") or actor_user_id,
            action="finance.invoice.created",
            entity_type="invoice",
            entity_id=row.id,
            entity_display=row.invoice_number,
            description=f"Invoice {row.invoice_number} created",
            new_value={"amount": str(row.amount), "status": row.status},
            extra_data={"customer_id": str(row.customer_id)},
        )
        return row

    async def create_ledger_entry(self, payload: dict[str, Any], actor_user_id: str):
        row = await self.repo.create_ledger_entry(payload)
        await self.audit_repo.create(
            user_id=payload.get("created_by") or actor_user_id,
            action="finance.ledger.created",
            entity_type="finance_ledger_entry",
            entity_id=row.id,
            entity_display=row.reference_no,
            description=f"Ledger entry {row.entry_type} created",
            new_value={"amount": str(row.amount), "status": row.status},
            extra_data={"entry_type": row.entry_type},
        )
        return row
