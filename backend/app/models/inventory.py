# backend/app/models/inventory.py
import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.postgres import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.database.types import GUID

class PlotInventory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plot_inventory"
    
    plot_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    area_sqft: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    facing: Mapped[str | None] = mapped_column(String(20)) # East, West, etc.
    is_corner: Mapped[bool] = mapped_column(Boolean, default=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    plc_charges: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0) # Preferential Location Charges
    
    # Available, Blocked, Booked, Registered, Cancelled
    status: Mapped[str] = mapped_column(String(20), default="Available", index=True)
    
    # Relationship to booking/customer if sold
    current_customer_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("customers.id"), nullable=True)
    assigned_sales_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)