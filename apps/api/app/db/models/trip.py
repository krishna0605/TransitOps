from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import Measure, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class Trip(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "trips"
    __table_args__ = (Index("ix_trip_org_status", "organization_id", "status"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    source: Mapped[str] = mapped_column(String(160), nullable=False)
    destination: Mapped[str] = mapped_column(String(160), nullable=False)
    vehicle_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("vehicles.id"), index=True)
    driver_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("drivers.id"), index=True)
    dispatched_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    cargo_weight_kg: Mapped[Decimal] = mapped_column(Measure, nullable=False)
    planned_distance_km: Mapped[Decimal] = mapped_column(Measure, nullable=False)
    final_odometer: Mapped[Decimal | None] = mapped_column(Measure)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def trip_id(self) -> UUID:
        return self.id


class TripStatusHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "trip_status_history"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    trip_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("trips.id", ondelete="CASCADE"))
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
