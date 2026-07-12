from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import Money, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class MaintenanceLog(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "maintenance_logs"
    __table_args__ = (Index("ix_maintenance_org_status", "organization_id", "status"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    vehicle_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("vehicles.id"), index=True)
    trip_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("trips.id"), index=True)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    cost: Mapped[Decimal] = mapped_column(Money, nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def maintenance_id(self) -> UUID:
        return self.id
