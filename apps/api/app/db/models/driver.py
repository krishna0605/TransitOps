from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class Driver(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("organization_id", "license_no", name="uq_driver_org_license"),
        Index("ix_driver_org_status", "organization_id", "status"),
    )

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    license_no: Mapped[str] = mapped_column(String(64), nullable=False)
    license_category: Mapped[str] = mapped_column(String(20), nullable=False)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    contact: Mapped[str] = mapped_column(String(80), nullable=False)
    safety_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=100)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="AVAILABLE")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def driver_id(self) -> UUID:
        return self.id
