"""Trip dispatcher endpoints (Screen 4).

Owns the trip lifecycle Draft -> Dispatched -> Completed / Cancelled and the
state-machine side effects on vehicle and driver status. Dispatch enforces the
capacity rule and refuses to double-book a vehicle or driver that is On Trip.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import DatabaseSession
from app.api.v1.common import ORMModel, get_or_404
from app.core.exceptions import AppError
from app.db.models.driver import Driver
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/trips", tags=["trips"])


class TripRead(ORMModel):
    trip_id: int
    source: str
    destination: str
    vehicle_id: int
    vehicle_reg_no: str
    vehicle_name_model: str
    driver_id: int
    driver_name: str
    cargo_weight_kg: float
    planned_distance_km: float
    final_odometer: int | None
    status: str
    dispatched_at: datetime | None
    completed_at: datetime | None


class TripCreate(ORMModel):
    source: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    vehicle_id: int
    driver_id: int
    cargo_weight_kg: float = Field(gt=0)
    planned_distance_km: float = Field(gt=0)


class TripComplete(ORMModel):
    # Optional; defaults to odometer + planned distance when omitted.
    final_odometer: int | None = Field(default=None, ge=0)


def _serialize(trip: Trip) -> TripRead:
    return TripRead(
        trip_id=trip.trip_id,
        source=trip.source,
        destination=trip.destination,
        vehicle_id=trip.vehicle_id,
        vehicle_reg_no=trip.vehicle.reg_no,
        vehicle_name_model=trip.vehicle.name_model,
        driver_id=trip.driver_id,
        driver_name=trip.driver.name,
        cargo_weight_kg=trip.cargo_weight_kg,
        planned_distance_km=trip.planned_distance_km,
        final_odometer=trip.final_odometer,
        status=trip.status,
        dispatched_at=trip.dispatched_at,
        completed_at=trip.completed_at,
    )


async def _load(session: DatabaseSession, trip_id: int) -> Trip:
    statement = (
        select(Trip)
        .where(Trip.trip_id == trip_id)
        .options(selectinload(Trip.vehicle), selectinload(Trip.driver))
    )
    trip = (await session.execute(statement)).scalar_one_or_none()
    if trip is None:
        raise AppError(
            code="TRIP_NOT_FOUND",
            message=f"Trip {trip_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return trip


@router.get("", response_model=list[TripRead])
async def list_trips(
    session: DatabaseSession,
    vehicle_id: Annotated[int | None, Query()] = None,
) -> list[TripRead]:
    """List trips newest first. ``vehicle_id`` scopes results to one vehicle,
    which powers the optional trip pickers on the fuel and maintenance screens."""
    statement = (
        select(Trip)
        .options(selectinload(Trip.vehicle), selectinload(Trip.driver))
        .order_by(Trip.trip_id.desc())
    )
    if vehicle_id is not None:
        statement = statement.where(Trip.vehicle_id == vehicle_id)
    trips = (await session.execute(statement)).scalars().all()
    return [_serialize(t) for t in trips]


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(payload: TripCreate, session: DatabaseSession) -> TripRead:
    """Create a Draft trip. Dispatch happens as a separate, validated step."""
    vehicle = await get_or_404(session, Vehicle, payload.vehicle_id, entity="vehicle")
    driver = await get_or_404(session, Driver, payload.driver_id, entity="driver")
    trip = Trip(
        source=payload.source.strip(),
        destination=payload.destination.strip(),
        vehicle_id=vehicle.vehicle_id,
        driver_id=driver.driver_id,
        cargo_weight_kg=payload.cargo_weight_kg,
        planned_distance_km=payload.planned_distance_km,
        status="Draft",
    )
    session.add(trip)
    await session.commit()
    return _serialize(await _load(session, trip.trip_id))


@router.post("/{trip_id}/dispatch", response_model=TripRead)
async def dispatch_trip(trip_id: int, session: DatabaseSession) -> TripRead:
    """Draft -> Dispatched. Enforces capacity, vehicle/driver availability, and
    the no-double-booking rule, then flags both resources On Trip."""
    trip = await _load(session, trip_id)
    if trip.status != "Draft":
        raise AppError(
            code="TRIP_NOT_DRAFT",
            message=f"Only Draft trips can be dispatched (trip is {trip.status}).",
        )

    vehicle, driver = trip.vehicle, trip.driver

    over_by = trip.cargo_weight_kg - vehicle.max_capacity_kg
    if over_by > 0:
        raise AppError(
            code="CAPACITY_EXCEEDED",
            message=f"Capacity exceeded by {over_by:g} kg -> dispatch blocked.",
            details={
                "cargo_weight_kg": trip.cargo_weight_kg,
                "max_capacity_kg": vehicle.max_capacity_kg,
                "over_by_kg": over_by,
            },
        )

    if vehicle.status != "Available":
        raise AppError(
            code="VEHICLE_UNAVAILABLE",
            message=f"Vehicle {vehicle.reg_no} is {vehicle.status}, not Available.",
        )
    if driver.status != "Available":
        raise AppError(
            code="DRIVER_UNAVAILABLE",
            message=f"Driver {driver.name} is {driver.status}, not Available.",
        )
    if driver.license_expiry < date.today():
        raise AppError(
            code="DRIVER_LICENSE_EXPIRED",
            message=f"Driver {driver.name}'s licence has expired.",
        )

    trip.status = "Dispatched"
    trip.dispatched_at = datetime.now(UTC)
    vehicle.status = "On Trip"
    driver.status = "On Trip"
    await session.commit()
    return _serialize(await _load(session, trip_id))


@router.post("/{trip_id}/complete", response_model=TripRead)
async def complete_trip(
    trip_id: int, payload: TripComplete, session: DatabaseSession
) -> TripRead:
    """Dispatched -> Completed. Writes final_odometer, rolls the vehicle
    odometer forward, and returns vehicle and driver to Available."""
    trip = await _load(session, trip_id)
    if trip.status != "Dispatched":
        raise AppError(
            code="TRIP_NOT_DISPATCHED",
            message=f"Only Dispatched trips can be completed (trip is {trip.status}).",
        )

    vehicle, driver = trip.vehicle, trip.driver
    final_odometer = payload.final_odometer
    if final_odometer is None:
        final_odometer = vehicle.odometer + round(trip.planned_distance_km)
    if final_odometer < vehicle.odometer:
        raise AppError(
            code="ODOMETER_REGRESSION",
            message="Final odometer cannot be less than the current odometer.",
            details={"current_odometer": vehicle.odometer, "final_odometer": final_odometer},
        )

    trip.status = "Completed"
    trip.final_odometer = final_odometer
    trip.completed_at = datetime.now(UTC)
    vehicle.odometer = final_odometer
    vehicle.status = "Available"
    driver.status = "Available"
    await session.commit()
    return _serialize(await _load(session, trip_id))


@router.post("/{trip_id}/cancel", response_model=TripRead)
async def cancel_trip(trip_id: int, session: DatabaseSession) -> TripRead:
    """Cancel a Draft or Dispatched trip. A dispatched trip releases its
    vehicle and driver back to Available."""
    trip = await _load(session, trip_id)
    if trip.status in ("Completed", "Cancelled"):
        raise AppError(
            code="TRIP_NOT_CANCELLABLE",
            message=f"A {trip.status} trip cannot be cancelled.",
        )

    if trip.status == "Dispatched":
        if trip.vehicle.status == "On Trip":
            trip.vehicle.status = "Available"
        if trip.driver.status == "On Trip":
            trip.driver.status = "Available"

    trip.status = "Cancelled"
    await session.commit()
    return _serialize(await _load(session, trip_id))
