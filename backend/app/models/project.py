import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base
from app.database.types import GUID, JSONType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_name", "name"),
        Index("ix_projects_status", "project_status"),
        Index("ix_projects_location", "location"),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    developer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sole_selling_partner: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    google_maps_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_status: Mapped[str] = mapped_column(String(64), nullable=False, default="PLANNING")

    total_inventory: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sold_inventory: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    price_list: Mapped[list[dict] | dict] = mapped_column(JSONType, default=list, nullable=False)
    payment_plans: Mapped[list[dict] | dict] = mapped_column(JSONType, default=list, nullable=False)
    documents: Mapped[list[dict] | dict] = mapped_column(JSONType, default=list, nullable=False)
    gallery: Mapped[list[dict] | dict] = mapped_column(JSONType, default=list, nullable=False)
    videos: Mapped[list[dict] | dict] = mapped_column(JSONType, default=list, nullable=False)
    brochure: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)

    legal_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    amenities: Mapped[list[str] | dict] = mapped_column(JSONType, default=list, nullable=False)
    nearby_landmarks: Mapped[list[str] | dict] = mapped_column(JSONType, default=list, nullable=False)

    created_by: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
