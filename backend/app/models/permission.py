from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
