from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import Measure, Money, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class FuelLog(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "fuel_logs"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"), index=True)
    vehicle_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("vehicles.id"), index=True)
    trip_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("trips.id"), index=True)
    fuel_date: Mapped[date] = mapped_column(Date, nullable=False)
    liters: Mapped[Decimal] = mapped_column(Measure, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Money, nullable=False)
    odometer: Mapped[Decimal | None] = mapped_column(Measure)

    @property
    def fuel_id(self) -> UUID:
        return self.id
