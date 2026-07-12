from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.contracts.dto.common import (
    AwareDateTime,
    ContractModel,
    EntityRead,
    Measurement,
    Money,
    PositiveMeasurement,
)
from app.contracts.enums import TripStatus
from app.contracts.filters import ListFilters, validate_sort_field

TRIP_SORT_FIELDS = frozenset(
    {"created_at", "updated_at", "trip_number", "planned_start_at", "status"}
)


class TripDraftCreate(ContractModel):
    source: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    region_id: UUID
    cargo_weight_kg: PositiveMeasurement
    planned_distance_km: PositiveMeasurement
    planned_start_at: AwareDateTime | None = None
    planned_end_at: AwareDateTime | None = None
    vehicle_id: UUID | None = None
    driver_id: UUID | None = None

    @model_validator(mode="after")
    def validate_schedule(self) -> "TripDraftCreate":
        if (
            self.planned_start_at is not None
            and self.planned_end_at is not None
            and self.planned_end_at <= self.planned_start_at
        ):
            raise ValueError("planned_end_at must be after planned_start_at")
        return self


class TripDraftUpdate(ContractModel):
    source: str | None = Field(default=None, min_length=1, max_length=200)
    destination: str | None = Field(default=None, min_length=1, max_length=200)
    region_id: UUID | None = None
    cargo_weight_kg: PositiveMeasurement | None = None
    planned_distance_km: PositiveMeasurement | None = None
    planned_start_at: AwareDateTime | None = None
    planned_end_at: AwareDateTime | None = None
    vehicle_id: UUID | None = None
    driver_id: UUID | None = None
    version: int = Field(ge=1)


class TripSummary(ContractModel):
    id: UUID
    trip_number: str
    source: str
    destination: str
    vehicle_id: UUID | None
    driver_id: UUID | None
    planned_start_at: AwareDateTime | None
    status: TripStatus
    version: int = Field(ge=1)


class TripRead(EntityRead):
    trip_number: str
    source: str
    destination: str
    region_id: UUID
    vehicle_id: UUID | None
    driver_id: UUID | None
    cargo_weight_kg: Measurement
    planned_distance_km: Measurement
    actual_distance_km: Measurement | None
    start_odometer_km: Measurement | None
    final_odometer_km: Measurement | None
    fuel_liters: Measurement | None
    actual_revenue: Money | None
    currency: str
    planned_start_at: AwareDateTime | None
    planned_end_at: AwareDateTime | None
    dispatched_at: AwareDateTime | None
    completed_at: AwareDateTime | None
    cancelled_at: AwareDateTime | None
    cancellation_reason: str | None
    status: TripStatus
    created_by: UUID


class TripFilters(ListFilters):
    status: TripStatus | None = None
    vehicle_id: UUID | None = None
    driver_id: UUID | None = None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, TRIP_SORT_FIELDS)


class TripDispatchRequest(ContractModel):
    vehicle_id: UUID
    driver_id: UUID
    version: int = Field(ge=1)


class TripCompletionRequest(ContractModel):
    final_odometer_km: Measurement
    fuel_liters: Measurement = Decimal("0")
    actual_revenue: Money = Decimal("0")
    currency: str = Field(default="INR", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    version: int = Field(ge=1)


class TripCancellationRequest(ContractModel):
    reason: str | None = Field(default=None, min_length=3, max_length=500)
    version: int = Field(ge=1)


class TripStatusHistoryRead(ContractModel):
    id: UUID
    trip_id: UUID
    from_status: TripStatus | None
    to_status: TripStatus
    changed_by: UUID
    reason: str | None
    changed_at: AwareDateTime
