from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.vehicles import (
    OdometerCorrectionRequest,
    VehicleCreate,
    VehicleFilters,
    VehicleRead,
    VehicleSummary,
    VehicleUpdate,
)


class VehicleRepository(Protocol):
    async def get_by_id(self, vehicle_id: UUID) -> VehicleRead | None: ...

    async def get_by_registration(self, registration_number: str) -> VehicleRead | None: ...

    async def list(self, filters: VehicleFilters) -> Page[VehicleSummary]: ...

    async def create(self, data: VehicleCreate) -> VehicleRead: ...

    async def update(self, vehicle_id: UUID, data: VehicleUpdate) -> VehicleRead: ...

    async def correct_odometer(
        self, vehicle_id: UUID, data: OdometerCorrectionRequest, changed_by: UUID
    ) -> VehicleRead: ...

    async def archive(self, vehicle_id: UUID, *, changed_by: UUID, reason: str) -> None: ...

    async def lock_for_update(self, vehicle_id: UUID) -> VehicleRead | None: ...

    async def list_dispatch_candidates(
        self, filters: VehicleFilters
    ) -> Sequence[VehicleSummary]: ...
