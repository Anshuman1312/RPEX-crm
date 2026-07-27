"""
Invoice service layer with business logic.

Key features:
- Invoice generation from bookings
- GST calculation (0-18%)
- Payment tracking and reconciliation
- Ledger entry creation
- Financial reporting
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.models.invoice import Invoice, InvoiceItem, FinanceLedgerEntry, InvoicePaymentMapping
from app.models.booking import Booking, BookingPaymentPlan
from app.repositories.invoice_repository import (
    InvoiceRepository,
    InvoiceItemRepository,
    FinanceLedgerRepository,
    InvoicePaymentMappingRepository,
)
from app.repositories.booking_repository import BookingRepository
from app.utils.enums import PaymentStatus
from app.utils.numbering import NumberingService


class InvoiceService:
    """Invoice and finance management service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.invoice_repo = InvoiceRepository(session)
        self.item_repo = InvoiceItemRepository(session)
        self.ledger_repo = FinanceLedgerRepository(session)
        self.mapping_repo = InvoicePaymentMappingRepository(session)
        self.booking_repo = BookingRepository(session)
        self.numbering_service = NumberingService(session)

    # ── Invoice CRUD ──────────────────────────────────────────────────

    async def create_invoice(
        self,
        customer_id: str,
        due_date: datetime,
        items: List[Dict[str, Any]],
        booking_id: Optional[str] = None,
        project_id: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: str = "system",
    ) -> Invoice:
        """Create invoice with items."""
        if not items:
            raise ValidationException("Invoice must have at least one item")

        # Calculate totals
        subtotal = Decimal(0)
        gst_total = Decimal(0)

        for item in items:
            amount = Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
            gst_rate = Decimal(str(item.get("gst_rate", 0)))
            gst_amount = amount * (gst_rate / 100)

            subtotal += amount
            gst_total += gst_amount

        total_amount = subtotal + gst_total

        # Generate invoice number
        invoice_number = await self.numbering_service.get_next_number("INV")

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            booking_id=booking_id,
            customer_id=customer_id,
            project_id=project_id,
            invoice_date=datetime.utcnow(),
            due_date=due_date,
            subtotal=subtotal,
            gst_amount=gst_total,
            total_amount=total_amount,
            payment_status=PaymentStatus.PENDING.value,
            invoice_status="DRAFT",
            notes=notes,
            created_by=created_by,
        )
        self.session.add(invoice)
        await self.session.flush()

        # Create invoice items
        for idx, item in enumerate(items):
            amount = Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
            gst_rate = Decimal(str(item.get("gst_rate", 0)))
            gst_amount = amount * (gst_rate / 100)
            item_total = amount + gst_amount

            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                description=item["description"],
                quantity=item.get("quantity", 1),
                unit_price=Decimal(str(item["unit_price"])),
                amount=amount,
                gst_rate=gst_rate,
                gst_amount=gst_amount,
                item_total=item_total,
                order_index=idx,
                created_by=created_by,
            )
            self.session.add(invoice_item)

        await self.session.flush()
        return invoice

    async def get_invoice(self, invoice_id: str) -> Invoice:
        """Get invoice with items."""
        invoice = await self.invoice_repo.get_with_items(invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice {invoice_id} not found")
        return invoice

    async def list_invoices(
        self,
        customer_id: Optional[str] = None,
        payment_statuses: Optional[List[str]] = None,
        invoice_statuses: Optional[List[str]] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[List[Invoice], int]:
        """List invoices with filtering."""
        return await self.invoice_repo.list_with_filter(
            customer_id=customer_id,
            payment_statuses=payment_statuses,
            invoice_statuses=invoice_statuses,
            search=search,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def update_invoice(self, invoice_id: str, **kwargs) -> Invoice:
        """Update invoice (only draft invoices)."""
        invoice = await self.get_invoice(invoice_id)

        if invoice.invoice_status != "DRAFT":
            raise ValidationException(f"Cannot update invoice in {invoice.invoice_status} status")

        allowed_fields = ["due_date", "notes"]
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(invoice, field, kwargs[field])

        invoice.updated_at = datetime.utcnow()
        return invoice

    async def delete_invoice(self, invoice_id: str) -> None:
        """Soft delete invoice (only draft)."""
        invoice = await self.get_invoice(invoice_id)
        if invoice.invoice_status != "DRAFT":
            raise ValidationException(f"Cannot delete invoice in {invoice.invoice_status} status")
        await self.invoice_repo.soft_delete(invoice_id)

    # ── Invoice Status ────────────────────────────────────────────────

    async def send_invoice(self, invoice_id: str) -> Invoice:
        """Mark invoice as sent."""
        invoice = await self.get_invoice(invoice_id)

        if invoice.invoice_status != "DRAFT":
            raise ValidationException(f"Cannot send invoice in {invoice.invoice_status} status")

        invoice.invoice_status = "SENT"
        invoice.sent_on = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()

        # Create ledger entry for invoice
        ledger = FinanceLedgerEntry(
            invoice_id=invoice_id,
            entry_date=datetime.utcnow(),
            entry_type="INVOICE",
            description=f"Invoice {invoice.invoice_number}",
            debit_amount=invoice.total_amount,
            account_code="AR",  # Accounts Receivable
            created_by="system",
        )
        self.session.add(ledger)

        return invoice

    async def cancel_invoice(self, invoice_id: str) -> Invoice:
        """Cancel invoice."""
        invoice = await self.get_invoice(invoice_id)

        if invoice.invoice_status in ["PAID"]:
            raise ValidationException(f"Cannot cancel paid invoice")

        invoice.invoice_status = "CANCELLED"
        invoice.updated_at = datetime.utcnow()

        return invoice

    # ── Payment Processing ────────────────────────────────────────────

    async def record_payment(
        self,
        invoice_id: str,
        amount: Decimal,
        payment_date: datetime,
        payment_method: str,
        transaction_ref: str,
        notes: Optional[str] = None,
    ) -> Invoice:
        """Record payment received against invoice."""
        invoice = await self.get_invoice(invoice_id)

        if invoice.invoice_status == "CANCELLED":
            raise ValidationException("Cannot record payment on cancelled invoice")

        # Check overpayment
        new_paid = invoice.paid_amount + amount
        if new_paid > invoice.total_amount:
            raise ValidationException(
                f"Payment exceeds invoice total. Invoice: {invoice.total_amount}, "
                f"Already paid: {invoice.paid_amount}, New payment: {amount}"
            )

        invoice.paid_amount = new_paid
        invoice.updated_at = datetime.utcnow()

        # Update payment status
        remaining = invoice.total_amount - new_paid
        if remaining == 0:
            invoice.payment_status = PaymentStatus.PAID.value
            invoice.paid_on = payment_date
        elif new_paid > 0:
            invoice.payment_status = PaymentStatus.PARTIALLY_PAID.value
        else:
            invoice.payment_status = PaymentStatus.PENDING.value

        # Create ledger entry for payment
        ledger = FinanceLedgerEntry(
            invoice_id=invoice_id,
            entry_date=payment_date,
            entry_type="PAYMENT",
            description=f"Payment for {invoice.invoice_number}",
            credit_amount=amount,
            account_code="CASH",
            reference_number=transaction_ref,
            remarks=notes,
            created_by="system",
        )
        self.session.add(ledger)

        return invoice

    # ── Invoice Items ─────────────────────────────────────────────────

    async def add_item(
        self,
        invoice_id: str,
        description: str,
        quantity: int,
        unit_price: Decimal,
        gst_rate: Decimal = Decimal(0),
    ) -> InvoiceItem:
        """Add item to invoice (draft only)."""
        invoice = await self.get_invoice(invoice_id)

        if invoice.invoice_status != "DRAFT":
            raise ValidationException("Can only add items to draft invoices")

        # Calculate amounts
        amount = Decimal(str(quantity)) * unit_price
        gst_amount = amount * (gst_rate / 100)
        item_total = amount + gst_amount

        # Get next order index
        items = await self.item_repo.get_invoice_items(invoice_id)
        order_index = len(items)

        item = InvoiceItem(
            invoice_id=invoice_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            item_total=item_total,
            order_index=order_index,
            created_by="system",
        )
        self.session.add(item)

        # Recalculate invoice totals
        await self._recalculate_invoice_totals(invoice_id)

        await self.session.flush()
        return item

    async def _recalculate_invoice_totals(self, invoice_id: str) -> None:
        """Recalculate invoice subtotal and GST."""
        invoice = await self.get_invoice(invoice_id)
        items = await self.item_repo.get_invoice_items(invoice_id)

        subtotal = sum(item.amount for item in items)
        gst_total = sum(item.gst_amount for item in items)
        total = subtotal + gst_total

        invoice.subtotal = subtotal
        invoice.gst_amount = gst_total
        invoice.total_amount = total
        invoice.updated_at = datetime.utcnow()

    async def get_invoice_items(self, invoice_id: str) -> List[InvoiceItem]:
        """Get items for invoice."""
        return await self.item_repo.get_invoice_items(invoice_id)

    # ── Payment Mapping ───────────────────────────────────────────────

    async def map_to_payment_plan(
        self,
        invoice_id: str,
        payment_plan_id: str,
        mapped_amount: Decimal,
    ) -> InvoicePaymentMapping:
        """Map invoice to booking payment plan."""
        invoice = await self.get_invoice(invoice_id)

        # Validate amount
        unmapped_total = invoice.total_amount - await self.mapping_repo.get_mapping_total(invoice_id)
        if mapped_amount > unmapped_total:
            raise ValidationException(
                f"Cannot map {mapped_amount}. Unmapped amount: {unmapped_total}"
            )

        mapping = InvoicePaymentMapping(
            invoice_id=invoice_id,
            payment_plan_id=payment_plan_id,
            mapped_amount=mapped_amount,
            created_by="system",
        )
        self.session.add(mapping)
        await self.session.flush()
        return mapping

    async def get_invoice_mappings(self, invoice_id: str) -> List[InvoicePaymentMapping]:
        """Get payment plan mappings for invoice."""
        return await self.mapping_repo.get_invoice_mappings(invoice_id)

    # ── Financial Reports ─────────────────────────────────────────────

    async def get_invoice_statistics(self) -> Dict[str, Any]:
        """Get invoice statistics."""
        status_counts = await self.invoice_repo.count_by_payment_status()
        total_receivable = await self.invoice_repo.get_total_receivable()
        total_revenue = await self.invoice_repo.get_total_revenue()

        return {
            "total_revenue": total_revenue,
            "total_receivable": total_receivable,
            "by_payment_status": status_counts,
            "overdue_count": len(await self.invoice_repo.get_overdue_invoices()),
        }

    async def get_customer_invoice_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's invoice summary."""
        invoices = await self.invoice_repo.get_customer_invoices(customer_id)

        total_amount = sum(inv.total_amount for inv in invoices)
        paid_amount = sum(inv.paid_amount for inv in invoices)
        pending_amount = total_amount - paid_amount

        return {
            "customer_id": customer_id,
            "total_invoices": len(invoices),
            "total_amount": float(total_amount),
            "paid_amount": float(paid_amount),
            "pending_amount": float(pending_amount),
        }

    async def get_ledger_balance(self, date_from: Optional[datetime] = None) -> Dict[str, Any]:
        """Get financial ledger balance."""
        total_debit = await self.ledger_repo.get_total_debit(date_from)
        total_credit = await self.ledger_repo.get_total_credit(date_from)
        balance = total_debit - total_credit

        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance": balance,
            "as_of": datetime.utcnow().isoformat(),
        }

    async def get_overdue_invoices(self) -> List[Invoice]:
        """Get overdue invoices."""
        return await self.invoice_repo.get_overdue_invoices()

    async def get_invoices_due_soon(self, days: int = 7) -> List[Invoice]:
        """Get invoices due soon."""
        return await self.invoice_repo.get_invoices_due_soon(days)
