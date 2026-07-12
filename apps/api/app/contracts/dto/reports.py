from uuid import UUID

from pydantic import Field

from app.contracts.dto.common import AwareDateTime, ContractModel, Measurement, Money, SignedMoney
from app.contracts.enums import ReportExportStatus
from app.contracts.filters import ListFilters


class DashboardFilters(ListFilters):
    vehicle_type: str | None = None


class DashboardKpiResponse(ContractModel):
    active_vehicles: int = Field(ge=0)
    available_vehicles: int = Field(ge=0)
    vehicles_in_maintenance: int = Field(ge=0)
    active_trips: int = Field(ge=0)
    pending_trips: int = Field(ge=0)
    drivers_on_duty: int = Field(ge=0)
    fleet_utilization_percent: float | None = Field(default=None, ge=0, le=100)


class FleetUtilizationResponse(ContractModel):
    on_trip_vehicles: int = Field(ge=0)
    serviceable_vehicles: int = Field(ge=0)
    utilization_percent: float | None = Field(default=None, ge=0, le=100)


class FuelEfficiencyResponse(ContractModel):
    distance_km: Measurement
    fuel_liters: Measurement
    km_per_liter: float | None = Field(default=None, ge=0)


class OperationalCostResponse(ContractModel):
    core_operational_cost: Money
    total_operating_cost: Money
    currency: str


class VehicleRoiResponse(ContractModel):
    vehicle_id: UUID
    revenue: Money
    core_operational_cost: Money
    acquisition_cost: Money
    roi_percent: float | None
    currency: str


class TripProfitabilityResponse(ContractModel):
    trip_id: UUID
    revenue: Money
    fuel_cost: Money
    other_expenses: Money
    profit: SignedMoney
    currency: str


class ReportExportRequest(ContractModel):
    report_type: str = Field(min_length=1, max_length=64)
    format: str = Field(pattern=r"^(CSV|PDF)$")
    filters: dict[str, str | int | bool | None] = Field(default_factory=dict)


class ReportExportStatusResponse(ContractModel):
    id: UUID
    status: ReportExportStatus
    download_url: str | None
    error_code: str | None
    created_at: AwareDateTime
    completed_at: AwareDateTime | None
