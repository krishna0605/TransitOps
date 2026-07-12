from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import MAINTENANCE_STATUSES, in_check

if TYPE_CHECKING:
    from app.db.models.expense import Expense
    from app.db.models.trip import Trip
    from app.db.models.vehicle import Vehicle


class MaintenanceLog(Base):
    __tablename__ = "maintenance_log"
    __table_args__ = (
        CheckConstraint(in_check("status", MAINTENANCE_STATUSES), name="status_valid"),
    )

    maintenance_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.vehicle_id"), nullable=False, index=True
    )
    # Set only when this maintenance is tied to a specific trip.
    trip_id: Mapped[int | None] = mapped_column(
        ForeignKey("trip.trip_id"), nullable=True, index=True
    )
    service_type: Mapped[str] = mapped_column(String, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)

    vehicle: Mapped[Vehicle] = relationship(back_populates="maintenance_logs")
    trip: Mapped[Trip | None] = relationship(back_populates="maintenance_logs")
    # Optional one-to-one: an auto-posted expense created when trip_id is set.
    expense: Mapped[Expense | None] = relationship(back_populates="maintenance_log")
