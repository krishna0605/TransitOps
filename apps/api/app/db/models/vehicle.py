from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import VEHICLE_STATUSES, VEHICLE_TYPES, in_check

if TYPE_CHECKING:
    from app.db.models.expense import Expense
    from app.db.models.fuel_log import FuelLog
    from app.db.models.maintenance_log import MaintenanceLog
    from app.db.models.trip import Trip


class Vehicle(Base):
    __tablename__ = "vehicle"
    __table_args__ = (
        CheckConstraint(in_check("type", VEHICLE_TYPES), name="type_valid"),
        CheckConstraint(in_check("status", VEHICLE_STATUSES), name="status_valid"),
    )

    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    # reg_no is the identifier shown in the UI (never name_model).
    reg_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name_model: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    max_capacity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    odometer: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    acquisition_cost: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, index=True, server_default=text("'Available'")
    )

    trips: Mapped[list[Trip]] = relationship(back_populates="vehicle")
    maintenance_logs: Mapped[list[MaintenanceLog]] = relationship(back_populates="vehicle")
    fuel_logs: Mapped[list[FuelLog]] = relationship(back_populates="vehicle")
    expenses: Mapped[list[Expense]] = relationship(back_populates="vehicle")
