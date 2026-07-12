from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import Money, TimestampMixin, UUIDPrimaryKeyMixin, VersionMixin


class Expense(UUIDPrimaryKeyMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "expenses"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id"), index=True)
    vehicle_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("vehicles.id"), index=True)
    trip_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("trips.id"), index=True)
    maintenance_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("maintenance_logs.id"), unique=True
    )
    fuel_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("fuel_logs.id"), unique=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Money, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    description: Mapped[str | None] = mapped_column(String(500))
    approved_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(String(500))

    @property
    def expense_id(self) -> UUID:
        return self.id
