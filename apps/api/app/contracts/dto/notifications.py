from uuid import UUID

from pydantic import field_validator

from app.contracts.dto.common import AwareDateTime, ContractModel
from app.contracts.enums import NotificationType
from app.contracts.filters import ListFilters, validate_sort_field

NOTIFICATION_SORT_FIELDS = frozenset({"created_at", "read_at", "notification_type"})


class NotificationRead(ContractModel):
    id: UUID
    notification_type: NotificationType
    title: str
    message: str
    entity_type: str | None
    entity_id: UUID | None
    read_at: AwareDateTime | None
    created_at: AwareDateTime


class NotificationFilters(ListFilters):
    notification_type: NotificationType | None = None
    unread_only: bool = False

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, NOTIFICATION_SORT_FIELDS)
