from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.trips import (
    TripDraftCreate,
    TripDraftUpdate,
    TripFilters,
    TripRead,
    TripStatusHistoryRead,
    TripSummary,
)
from app.contracts.enums import TripStatus


class TripRepository(Protocol):
    async def get_by_id(self, trip_id: UUID) -> TripRead | None: ...

    async def list(self, filters: TripFilters) -> Page[TripSummary]: ...

    async def create_draft(self, data: TripDraftCreate, created_by: UUID) -> TripRead: ...

    async def update_draft(self, trip_id: UUID, data: TripDraftUpdate) -> TripRead: ...

    async def lock_for_update(self, trip_id: UUID) -> TripRead | None: ...

    async def set_status(
        self,
        trip_id: UUID,
        *,
        status: TripStatus,
        changed_by: UUID,
        reason: str | None = None,
    ) -> TripRead: ...

    async def add_status_history(
        self,
        trip_id: UUID,
        *,
        from_status: TripStatus | None,
        to_status: TripStatus,
        changed_by: UUID,
        reason: str | None,
    ) -> TripStatusHistoryRead: ...
