from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Float, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import DRIVER_STATUSES, LICENSE_CATEGORIES, in_check

if TYPE_CHECKING:
    from app.db.models.trip import Trip


class Driver(Base):
    __tablename__ = "driver"
    __table_args__ = (
        CheckConstraint(
            in_check("license_category", LICENSE_CATEGORIES), name="license_category_valid"
        ),
        CheckConstraint(in_check("status", DRIVER_STATUSES), name="status_valid"),
    )

    driver_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    license_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    license_category: Mapped[str] = mapped_column(String, nullable=False)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    contact: Mapped[str] = mapped_column(String, nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("100"))
    status: Mapped[str] = mapped_column(
        String, nullable=False, index=True, server_default=text("'Available'")
    )

    trips: Mapped[list[Trip]] = relationship(back_populates="driver")
