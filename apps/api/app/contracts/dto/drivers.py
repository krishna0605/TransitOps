from datetime import date
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.contracts.dto.common import ContractModel, EntityRead
from app.contracts.enums import DriverStatus
from app.contracts.filters import ListFilters, validate_sort_field

DRIVER_SORT_FIELDS = frozenset(
    {"created_at", "updated_at", "name", "employee_number", "license_expiry_date", "status"}
)


class DriverCreate(ContractModel):
    employee_number: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=120)
    license_number: str = Field(min_length=1, max_length=64)
    license_category: str = Field(min_length=1, max_length=64)
    license_expiry_date: date
    phone: str = Field(min_length=7, max_length=32)
    email: EmailStr | None = None
    safety_score: int = Field(default=100, ge=0, le=100)
    region_id: UUID


class DriverUpdate(ContractModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    license_number: str | None = Field(default=None, min_length=1, max_length=64)
    license_category: str | None = Field(default=None, min_length=1, max_length=64)
    license_expiry_date: date | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    email: EmailStr | None = None
    safety_score: int | None = Field(default=None, ge=0, le=100)
    region_id: UUID | None = None
    version: int = Field(ge=1)


class DriverSummary(ContractModel):
    id: UUID
    employee_number: str
    name: str
    license_category: str
    license_expiry_date: date
    safety_score: int
    status: DriverStatus
    region_id: UUID
    version: int = Field(ge=1)


class DriverRead(EntityRead):
    employee_number: str
    name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    phone: str
    email: EmailStr | None
    safety_score: int
    status: DriverStatus
    region_id: UUID


class DriverFilters(ListFilters):
    status: DriverStatus | None = None
    license_category: str | None = Field(default=None, min_length=1, max_length=64)
    license_expiring_before: date | None = None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, DRIVER_SORT_FIELDS)


class DriverStatusChangeRequest(ContractModel):
    reason: str = Field(min_length=3, max_length=500)
    version: int = Field(ge=1)
