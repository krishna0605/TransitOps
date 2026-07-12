from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import TRIP_STATUSES, in_check

if TYPE_CHECKING:
    from app.db.models.driver import Driver
    from app.db.models.expense import Expense
    from app.db.models.fuel_log import FuelLog
    from app.db.models.maintenance_log import MaintenanceLog
    from app.db.models.user import User
    from app.db.models.vehicle import Vehicle


class Trip(Base):
    __tablename__ = "trip"
    __table_args__ = (CheckConstraint(in_check("status", TRIP_STATUSES), name="status_valid"),)

    trip_id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.vehicle_id"), nullable=False, index=True
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("driver.driver_id"), nullable=False, index=True
    )
    dispatched_by: Mapped[int | None] = mapped_column(
        ForeignKey("user.user_id"), nullable=True, index=True
    )
    cargo_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    planned_distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    # Set only when the trip is Completed.
    final_odometer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, index=True, server_default=text("'Draft'")
    )
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    vehicle: Mapped[Vehicle] = relationship(back_populates="trips")
    driver: Mapped[Driver] = relationship(back_populates="trips")
    dispatcher: Mapped[User | None] = relationship(back_populates="dispatched_trips")
    maintenance_logs: Mapped[list[MaintenanceLog]] = relationship(back_populates="trip")
    fuel_logs: Mapped[list[FuelLog]] = relationship(back_populates="trip")
    expenses: Mapped[list[Expense]] = relationship(back_populates="trip")
