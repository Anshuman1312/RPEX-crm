from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Website(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "websites"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    leads = relationship("Lead", back_populates="website")
