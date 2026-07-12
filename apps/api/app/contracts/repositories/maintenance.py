from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.maintenance import (
    MaintenanceCloseRequest,
    MaintenanceCreate,
    MaintenanceFilters,
    MaintenanceRead,
    MaintenanceSummary,
)


class MaintenanceRepository(Protocol):
    async def get_by_id(self, maintenance_id: UUID) -> MaintenanceRead | None: ...

    async def list(self, filters: MaintenanceFilters) -> Page[MaintenanceSummary]: ...

    async def get_active_for_vehicle(self, vehicle_id: UUID) -> MaintenanceRead | None: ...

    async def create(self, data: MaintenanceCreate, created_by: UUID) -> MaintenanceRead: ...

    async def close(
        self, maintenance_id: UUID, data: MaintenanceCloseRequest, closed_by: UUID
    ) -> MaintenanceRead: ...

    async def lock_for_update(self, maintenance_id: UUID) -> MaintenanceRead | None: ...
