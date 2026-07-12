from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a timezone offset")
    return value.astimezone(UTC)


AwareDateTime = Annotated[datetime, AfterValidator(_to_utc)]
Money = Annotated[Decimal, Field(max_digits=14, decimal_places=2, ge=0)]
PositiveMoney = Annotated[Decimal, Field(max_digits=14, decimal_places=2, gt=0)]
Measurement = Annotated[Decimal, Field(max_digits=14, decimal_places=3, ge=0)]
PositiveMeasurement = Annotated[Decimal, Field(max_digits=14, decimal_places=3, gt=0)]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class IdentifiedModel(ContractModel):
    id: UUID


class VersionedModel(IdentifiedModel):
    version: int = Field(ge=1)


class AuditFields(ContractModel):
    created_at: AwareDateTime
    updated_at: AwareDateTime


class Page[T](ContractModel):
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
