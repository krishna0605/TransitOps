from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import Measure, Money, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class Vehicle(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("organization_id", "reg_no", name="uq_vehicle_org_reg_no"),
        CheckConstraint("max_capacity_kg > 0", name="capacity_positive"),
        CheckConstraint("odometer >= 0", name="odometer_nonnegative"),
        CheckConstraint("acquisition_cost >= 0", name="acquisition_cost_nonnegative"),
        Index("ix_vehicle_org_status", "organization_id", "status"),
    )

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"))
    reg_no: Mapped[str] = mapped_column(String(32), nullable=False)
    name_model: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    max_capacity_kg: Mapped[Decimal] = mapped_column(Measure, nullable=False)
    odometer: Mapped[Decimal] = mapped_column(Measure, nullable=False, default=0)
    acquisition_cost: Mapped[Decimal] = mapped_column(Money, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="AVAILABLE")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def vehicle_id(self) -> UUID:
        return self.id
