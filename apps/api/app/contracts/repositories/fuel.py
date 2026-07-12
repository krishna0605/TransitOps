from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.finance import FuelLogCreate, FuelLogRead
from app.contracts.filters import ListFilters


class FuelLogRepository(Protocol):
    async def get_by_id(self, fuel_log_id: UUID) -> FuelLogRead | None: ...

    async def list(self, filters: ListFilters) -> Page[FuelLogRead]: ...

    async def create(self, data: FuelLogCreate, created_by: UUID) -> FuelLogRead: ...
