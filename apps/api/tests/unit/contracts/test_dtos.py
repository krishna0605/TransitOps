from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts.dto.auth import LoginRequest
from app.contracts.dto.drivers import DriverCreate
from app.contracts.dto.finance import ExpenseReviewRequest
from app.contracts.dto.trips import TripDraftCreate
from app.contracts.dto.vehicles import VehicleCreate, VehicleFilters, VehicleUpdate


def test_vehicle_contract_preserves_decimal_values() -> None:
    vehicle = VehicleCreate(
        registration_number="MH-01-AB-1234",
        name="Van 05",
        vehicle_type="VAN",
        max_load_kg=Decimal("500.000"),
        current_odometer_km=Decimal("12500.125"),
        acquisition_cost=Decimal("850000.50"),
        region_id=uuid4(),
    )
    payload = vehicle.model_dump(mode="json")
    assert payload["max_load_kg"] == "500.000"
    assert payload["acquisition_cost"] == "850000.50"


def test_generic_vehicle_update_cannot_change_status() -> None:
    assert "status" not in VehicleUpdate.model_fields


def test_vehicle_filters_reject_unknown_sort_field() -> None:
    with pytest.raises(ValidationError, match="sort_by must be one of"):
        VehicleFilters(sort_by="acquisition_cost_internal")


def test_trip_contract_normalizes_schedule_to_utc() -> None:
    start = datetime(2026, 7, 12, 10, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    trip = TripDraftCreate(
        source="Pune",
        destination="Mumbai",
        region_id=uuid4(),
        cargo_weight_kg=Decimal("450"),
        planned_distance_km=Decimal("150"),
        planned_start_at=start,
        planned_end_at=start + timedelta(hours=4),
    )
    assert trip.planned_start_at == datetime(2026, 7, 12, 4, 30, tzinfo=UTC)


def test_trip_contract_rejects_invalid_schedule() -> None:
    start = datetime(2026, 7, 12, 10, 0, tzinfo=UTC)
    with pytest.raises(ValidationError, match="planned_end_at must be after planned_start_at"):
        TripDraftCreate(
            source="Pune",
            destination="Mumbai",
            region_id=uuid4(),
            cargo_weight_kg=Decimal("450"),
            planned_distance_km=Decimal("150"),
            planned_start_at=start,
            planned_end_at=start,
        )


def test_rejected_expense_requires_reason() -> None:
    with pytest.raises(ValidationError, match="rejection_reason is required"):
        ExpenseReviewRequest(approved=False, version=1)


def test_login_and_driver_email_are_validated() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="invalid", password="password123")
    with pytest.raises(ValidationError):
        DriverCreate(
            employee_number="D-001",
            name="Alex",
            license_number="LIC-001",
            license_category="LMV",
            license_expiry_date=date(2027, 7, 12),
            phone="1234567890",
            email="invalid",
            region_id=uuid4(),
        )
