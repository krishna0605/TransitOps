from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import EXPENSE_CATEGORIES, EXPENSE_STATUSES, in_check

if TYPE_CHECKING:
    from app.db.models.maintenance_log import MaintenanceLog
    from app.db.models.trip import Trip
    from app.db.models.vehicle import Vehicle


class Expense(Base):
    __tablename__ = "expense"
    __table_args__ = (
        CheckConstraint(in_check("category", EXPENSE_CATEGORIES), name="category_valid"),
        CheckConstraint(in_check("status", EXPENSE_STATUSES), name="status_valid"),
    )

    expense_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.vehicle_id"), nullable=False, index=True
    )
    trip_id: Mapped[int | None] = mapped_column(
        ForeignKey("trip.trip_id"), nullable=True, index=True
    )
    # Set ONLY when this row was auto-posted from a maintenance record.
    # unique -> enforces the optional one-to-one with maintenance_log
    # (Postgres allows many NULLs under a UNIQUE constraint).
    maintenance_id: Mapped[int | None] = mapped_column(
        ForeignKey("maintenance_log.maintenance_id"), nullable=True, unique=True
    )
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'Available'"))

    vehicle: Mapped[Vehicle] = relationship(back_populates="expenses")
    trip: Mapped[Trip | None] = relationship(back_populates="expenses")
    maintenance_log: Mapped[MaintenanceLog | None] = relationship(back_populates="expense")
