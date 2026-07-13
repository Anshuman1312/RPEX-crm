from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class LeadStatus(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lead_status"

    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
