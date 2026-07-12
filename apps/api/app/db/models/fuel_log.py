from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.trip import Trip
    from app.db.models.vehicle import Vehicle


class FuelLog(Base):
    __tablename__ = "fuel_log"

    fuel_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.vehicle_id"), nullable=False, index=True
    )
    # Set when the fuel was logged as part of a specific trip; null for depot fills.
    trip_id: Mapped[int | None] = mapped_column(
        ForeignKey("trip.trip_id"), nullable=True, index=True
    )
    fuel_date: Mapped[date] = mapped_column(Date, nullable=False)
    liters: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)

    vehicle: Mapped[Vehicle] = relationship(back_populates="fuel_logs")
    trip: Mapped[Trip | None] = relationship(back_populates="fuel_logs")
