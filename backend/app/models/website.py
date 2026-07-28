from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import BaseModelMixin


class Website(Base, BaseModelMixin):
    __tablename__ = "websites"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
