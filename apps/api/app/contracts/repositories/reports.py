from typing import Protocol
from uuid import UUID

from app.contracts.dto.reports import (
    DashboardFilters,
    DashboardKpiResponse,
    FleetUtilizationResponse,
    FuelEfficiencyResponse,
    OperationalCostResponse,
    TripProfitabilityResponse,
    VehicleRoiResponse,
)


class ReportRepository(Protocol):
    async def dashboard_kpis(self, filters: DashboardFilters) -> DashboardKpiResponse: ...

    async def fleet_utilization(self, filters: DashboardFilters) -> FleetUtilizationResponse: ...

    async def fuel_efficiency(self, filters: DashboardFilters) -> FuelEfficiencyResponse: ...

    async def operational_cost(self, filters: DashboardFilters) -> OperationalCostResponse: ...

    async def vehicle_roi(
        self, vehicle_id: UUID, filters: DashboardFilters
    ) -> VehicleRoiResponse: ...

    async def trip_profitability(self, trip_id: UUID) -> TripProfitabilityResponse: ...
