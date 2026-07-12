from datetime import date
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.contracts.dto.common import (
    AwareDateTime,
    ContractModel,
    Measurement,
    Money,
    PositiveMeasurement,
)
from app.contracts.enums import ExpenseApprovalStatus, ExpenseCategory
from app.contracts.filters import ListFilters, validate_sort_field

EXPENSE_SORT_FIELDS = frozenset({"created_at", "expense_date", "amount", "category", "status"})


class FuelLogCreate(ContractModel):
    vehicle_id: UUID
    trip_id: UUID | None = None
    fuel_date: date
    liters: PositiveMeasurement
    unit_price: Money
    odometer_km: Measurement
    station_name: str | None = Field(default=None, max_length=200)
    receipt_document_id: UUID | None = None


class FuelLogRead(ContractModel):
    id: UUID
    vehicle_id: UUID
    trip_id: UUID | None
    fuel_date: date
    liters: Measurement
    unit_price: Money
    total_cost: Money
    odometer_km: Measurement
    station_name: str | None
    receipt_document_id: UUID | None
    created_by: UUID
    created_at: AwareDateTime


class ExpenseCreate(ContractModel):
    vehicle_id: UUID | None = None
    trip_id: UUID | None = None
    maintenance_id: UUID | None = None
    category: ExpenseCategory
    amount: Money
    currency: str = Field(default="INR", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    expense_date: date
    description: str = Field(min_length=3, max_length=1000)
    vendor: str | None = Field(default=None, max_length=200)
    receipt_document_id: UUID | None = None


class ExpenseRead(ContractModel):
    id: UUID
    vehicle_id: UUID | None
    trip_id: UUID | None
    maintenance_id: UUID | None
    category: ExpenseCategory
    amount: Money
    currency: str
    expense_date: date
    description: str
    vendor: str | None
    receipt_document_id: UUID | None
    approval_status: ExpenseApprovalStatus
    rejection_reason: str | None
    created_by: UUID
    approved_by: UUID | None
    created_at: AwareDateTime
    updated_at: AwareDateTime


class ExpenseReviewRequest(ContractModel):
    approved: bool
    rejection_reason: str | None = Field(default=None, min_length=3, max_length=500)
    version: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "ExpenseReviewRequest":
        if not self.approved and self.rejection_reason is None:
            raise ValueError("rejection_reason is required when an expense is rejected")
        if self.approved and self.rejection_reason is not None:
            raise ValueError("rejection_reason must be omitted when an expense is approved")
        return self


class ExpenseFilters(ListFilters):
    category: ExpenseCategory | None = None
    approval_status: ExpenseApprovalStatus | None = None
    vehicle_id: UUID | None = None
    trip_id: UUID | None = None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        return validate_sort_field(value, EXPENSE_SORT_FIELDS)
