from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import AwareDateTime, Page
from app.contracts.dto.notifications import NotificationFilters, NotificationRead


class NotificationRepository(Protocol):
    async def get_by_id(self, notification_id: UUID) -> NotificationRead | None: ...

    async def list_for_user(
        self, user_id: UUID, filters: NotificationFilters
    ) -> Page[NotificationRead]: ...

    async def mark_read(
        self, notification_id: UUID, user_id: UUID, read_at: AwareDateTime
    ) -> NotificationRead: ...
