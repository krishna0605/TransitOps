from enum import StrEnum

import pytest

from app.contracts.enums import (
    DocumentType,
    DriverStatus,
    ExpenseApprovalStatus,
    ExpenseCategory,
    MaintenancePriority,
    MaintenanceStatus,
    NotificationType,
    ReportExportStatus,
    TripStatus,
    UserStatus,
    VehicleStatus,
)


@pytest.mark.parametrize(
    "enum_type",
    [
        UserStatus,
        VehicleStatus,
        DriverStatus,
        TripStatus,
        MaintenanceStatus,
        ExpenseCategory,
        ExpenseApprovalStatus,
        MaintenancePriority,
        DocumentType,
        NotificationType,
        ReportExportStatus,
    ],
)
def test_domain_enums_use_unique_uppercase_wire_values(enum_type: type[StrEnum]) -> None:
    values = [member.value for member in enum_type]
    assert len(values) == len(set(values))
    assert all(value == value.upper() for value in values)


def test_trip_status_has_only_supported_lifecycle_states() -> None:
    assert {status.value for status in TripStatus} == {
        "DRAFT",
        "DISPATCHED",
        "COMPLETED",
        "CANCELLED",
    }
