from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from app.contracts.dto.common import (
    ContractModel,
    EntityRead,
    Measurement,
    Money,
    PositiveMeasurement,
)
from app.contracts.enums import VehicleStatus
from app.contracts.filters import ListFilters, validate_sort_field

VEHICLE_SORT_FIELDS = frozenset(
    {"created_at", "updated_at", "name", "registration_number", "status", "current_odometer_km"}
)


class VehicleCreate(ContractModel):
    registration_number: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=120)
    vehicle_type: str = Field(min_length=1, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    manufacturing_year: int | None = Field(default=None, ge=1900, le=2100)
    max_load_kg: PositiveMeasurement
    current_odometer_km: Measurement = Decimal("0")
    acquisition_cost: Money
    currency: str = Field(default="INR", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    region_id: UUID


class VehicleUpdate(ContractModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    manufacturing_year: int | None = Field(default=None, ge=1900, le=2100)
    max_load_kg: PositiveMeasurement | None = None
    acquisition_cost: Money | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    region_id: UUID | None = None
    version: int = Field(ge=1)


class VehicleSummary(ContractModel):
    id: UUID
    registration_number: str
    name: str
    vehicle_type: str
    max_load_kg: Measurement
    current_odometer_km: Measurement
    status: VehicleStatus
    region_id: UUID
    version: int = Field(ge=1)


class VehicleRead(EntityRead):
    registration_number: str
    name: str
    vehicle_type: str
    manufacturer: str | None
    model: str | None
    manufacturing_year: int | None
    max_load_kg: Measurement
    current_odometer_km: Measurement
    acquisition_cost: Money
    currency: str
    status: VehicleStatus
    region_id: UUID


class VehicleFilters(ListFilters):
    status: VehicleStatus | None = None
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, VEHICLE_SORT_FIELDS)


class OdometerCorrectionRequest(ContractModel):
    new_odometer_km: Measurement
    reason: str = Field(min_length=3, max_length=500)
    version: int = Field(ge=1)
