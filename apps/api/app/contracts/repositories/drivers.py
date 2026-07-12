from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.drivers import (
    DriverCreate,
    DriverFilters,
    DriverRead,
    DriverStatusChangeRequest,
    DriverSummary,
    DriverUpdate,
)


class DriverRepository(Protocol):
    async def get_by_id(self, driver_id: UUID) -> DriverRead | None: ...

    async def get_by_employee_number(self, employee_number: str) -> DriverRead | None: ...

    async def get_by_license_number(self, license_number: str) -> DriverRead | None: ...

    async def list(self, filters: DriverFilters) -> Page[DriverSummary]: ...

    async def create(self, data: DriverCreate) -> DriverRead: ...

    async def update(self, driver_id: UUID, data: DriverUpdate) -> DriverRead: ...

    async def change_status(
        self, driver_id: UUID, data: DriverStatusChangeRequest, changed_by: UUID
    ) -> DriverRead: ...

    async def archive(self, driver_id: UUID, *, changed_by: UUID, reason: str) -> None: ...

    async def lock_for_update(self, driver_id: UUID) -> DriverRead | None: ...

    async def list_dispatch_candidates(self, filters: DriverFilters) -> Sequence[DriverSummary]: ...
