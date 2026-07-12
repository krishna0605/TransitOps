from datetime import date
from uuid import UUID

from pydantic import Field, model_validator

from app.contracts.dto.common import ContractModel
from app.contracts.enums import SortOrder


class ListFilters(ContractModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
    search: str | None = Field(default=None, min_length=1, max_length=100)
    region_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    created_by: UUID | None = None
    archived: bool = False
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC

    @model_validator(mode="after")
    def validate_date_range(self) -> "ListFilters":
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError("date_from must be on or before date_to")
        return self


def validate_sort_field(value: str, allowed_fields: frozenset[str]) -> str:
    if value not in allowed_fields:
        allowed = ", ".join(sorted(allowed_fields))
        raise ValueError(f"sort_by must be one of: {allowed}")
    return value
