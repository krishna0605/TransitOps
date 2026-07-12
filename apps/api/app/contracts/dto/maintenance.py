from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from app.contracts.dto.common import AwareDateTime, ContractModel, EntityRead, Measurement, Money
from app.contracts.enums import MaintenancePriority, MaintenanceStatus
from app.contracts.filters import ListFilters, validate_sort_field

MAINTENANCE_SORT_FIELDS = frozenset(
    {"created_at", "updated_at", "maintenance_number", "opened_at", "status", "priority"}
)


class MaintenanceCreate(ContractModel):
    vehicle_id: UUID
    maintenance_type: str = Field(min_length=1, max_length=120)
    priority: MaintenancePriority = MaintenancePriority.NORMAL
    description: str = Field(min_length=3, max_length=2000)
    vendor: str | None = Field(default=None, max_length=200)
    odometer_km: Measurement
    estimated_cost: Money = Decimal("0")
    estimated_completion_at: AwareDateTime | None = None


class MaintenanceCloseRequest(ContractModel):
    actual_cost: Money
    next_service_date: date | None = None
    next_service_odometer_km: Measurement | None = None
    notes: str | None = Field(default=None, max_length=2000)
    version: int = Field(ge=1)


class MaintenanceSummary(ContractModel):
    id: UUID
    maintenance_number: str
    vehicle_id: UUID
    maintenance_type: str
    priority: MaintenancePriority
    opened_at: AwareDateTime
    status: MaintenanceStatus
    version: int = Field(ge=1)


class MaintenanceRead(EntityRead):
    maintenance_number: str
    vehicle_id: UUID
    maintenance_type: str
    priority: MaintenancePriority
    description: str
    vendor: str | None
    odometer_km: Measurement
    estimated_cost: Money
    actual_cost: Money | None
    opened_at: AwareDateTime
    estimated_completion_at: AwareDateTime | None
    closed_at: AwareDateTime | None
    next_service_date: date | None
    next_service_odometer_km: Measurement | None
    status: MaintenanceStatus
    created_by: UUID


class MaintenanceFilters(ListFilters):
    status: MaintenanceStatus | None = None
    priority: MaintenancePriority | None = None
    vehicle_id: UUID | None = None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, MAINTENANCE_SORT_FIELDS)
