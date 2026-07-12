from datetime import UTC, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.auth import CurrentPrincipal, IdempotencyKey
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.driver import Driver
from app.db.models.platform import AuditLog, IdempotencyRecord, OutboxEvent
from app.db.models.trip import Trip, TripStatusHistory
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/trips", tags=["trips"])


class TripRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trip_id: UUID
    source: str
    destination: str
    vehicle_id: UUID
    vehicle_reg_no: str
    driver_id: UUID
    driver_name: str
    cargo_weight_kg: Decimal
    planned_distance_km: Decimal
    final_odometer: Decimal | None
    status: str
    dispatched_at: datetime | None
    completed_at: datetime | None
    version: int


class TripCreate(BaseModel):
    source: str = Field(min_length=2, max_length=160)
    destination: str = Field(min_length=2, max_length=160)
    vehicle_id: UUID
    driver_id: UUID
    cargo_weight_kg: Decimal = Field(gt=0)
    planned_distance_km: Decimal = Field(gt=0)


class TripUpdate(TripCreate):
    version: int = Field(ge=1)


class TripComplete(BaseModel):
    final_odometer: Decimal = Field(ge=0)
    version: int = Field(ge=1)


class TripCancel(BaseModel):
    reason: str = Field(min_length=2, max_length=500)
    version: int = Field(ge=1)


async def _load_trip(session: DatabaseSession, organization_id: UUID, trip_id: UUID, *, lock: bool = False) -> Trip:
    statement = select(Trip).where(Trip.id == trip_id, Trip.organization_id == organization_id)
    if lock:
        statement = statement.with_for_update()
    trip = (await session.execute(statement)).scalar_one_or_none()
    if trip is None:
        raise AppError(code="TRIP_NOT_FOUND", message="Trip was not found.", status_code=404)
    return trip


async def _read(session: DatabaseSession, trip: Trip) -> TripRead:
    vehicle = await session.get(Vehicle, trip.vehicle_id)
    driver = await session.get(Driver, trip.driver_id)
    assert vehicle is not None and driver is not None
    return TripRead(
        trip_id=trip.id,
        source=trip.source,
        destination=trip.destination,
        vehicle_id=vehicle.id,
        vehicle_reg_no=vehicle.reg_no,
        driver_id=driver.id,
        driver_name=driver.name,
        cargo_weight_kg=trip.cargo_weight_kg,
        planned_distance_km=trip.planned_distance_km,
        final_odometer=trip.final_odometer,
        status=trip.status,
        dispatched_at=trip.dispatched_at,
        completed_at=trip.completed_at,
        version=trip.version,
    )


async def _resources(
    session: DatabaseSession, organization_id: UUID, vehicle_id: UUID, driver_id: UUID, *, lock: bool
) -> tuple[Vehicle, Driver]:
    vehicle_statement = select(Vehicle).where(
        Vehicle.id == vehicle_id, Vehicle.organization_id == organization_id, Vehicle.archived_at.is_(None)
    )
    driver_statement = select(Driver).where(
        Driver.id == driver_id, Driver.organization_id == organization_id, Driver.archived_at.is_(None)
    )
    if lock:
        vehicle_statement = vehicle_statement.with_for_update()
        driver_statement = driver_statement.with_for_update()
    vehicle = (await session.execute(vehicle_statement)).scalar_one_or_none()
    driver = (await session.execute(driver_statement)).scalar_one_or_none()
    if vehicle is None or driver is None:
        raise AppError(code="ASSIGNMENT_NOT_FOUND", message="Vehicle or driver was not found.", status_code=404)
    return vehicle, driver


def _event(session: DatabaseSession, principal: CurrentPrincipal, trip: Trip, action: str) -> None:
    now = datetime.now(UTC)
    session.add_all(
        [
            AuditLog(
                organization_id=principal.organization_id,
                actor_id=principal.user_id,
                action=action,
                entity_type="trip",
                entity_id=trip.id,
                payload={"status": trip.status},
            ),
            OutboxEvent(
                organization_id=principal.organization_id,
                event_type=f"trip.{action}",
                aggregate_type="trip",
                aggregate_id=trip.id,
                payload={"trip_id": str(trip.id), "status": trip.status},
            ),
        ]
    )
    session.add(
        TripStatusHistory(
            organization_id=principal.organization_id,
            trip_id=trip.id,
            to_status=trip.status,
            actor_id=principal.user_id,
            created_at=now,
        )
    )


async def _idempotent_trip(
    session: DatabaseSession, organization_id: UUID, key: str | None, operation: str
) -> Trip | None:
    if not key:
        return None
    record = (
        await session.execute(
            select(IdempotencyRecord).where(
                IdempotencyRecord.organization_id == organization_id,
                IdempotencyRecord.key == key,
                IdempotencyRecord.operation == operation,
            )
        )
    ).scalar_one_or_none()
    if record and record.response_body and "trip_id" in record.response_body:
        return await _load_trip(session, organization_id, UUID(str(record.response_body["trip_id"])))
    return None


def _remember_idempotency(
    session: DatabaseSession,
    organization_id: UUID,
    key: str | None,
    operation: str,
    trip_id: UUID,
) -> None:
    if key:
        session.add(
            IdempotencyRecord(
                organization_id=organization_id,
                key=key,
                operation=operation,
                request_hash=sha256(f"{operation}:{trip_id}".encode()).hexdigest(),
                response_status=200,
                response_body={"trip_id": str(trip_id)},
                expires_at=datetime.now(UTC) + timedelta(days=1),
            )
        )


@router.get("", response_model=list[TripRead])
async def list_trips(principal: CurrentPrincipal, session: DatabaseSession) -> list[TripRead]:
    trips = list(
        (
            await session.execute(
                select(Trip)
                .where(Trip.organization_id == principal.organization_id)
                .order_by(Trip.created_at.desc())
            )
        ).scalars()
    )
    return [await _read(session, trip) for trip in trips]


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(trip_id: UUID, principal: CurrentPrincipal, session: DatabaseSession) -> TripRead:
    return await _read(session, await _load_trip(session, principal.organization_id, trip_id))


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(payload: TripCreate, principal: CurrentPrincipal, session: DatabaseSession) -> TripRead:
    vehicle, driver = await _resources(
        session, principal.organization_id, payload.vehicle_id, payload.driver_id, lock=False
    )
    if payload.cargo_weight_kg > vehicle.max_capacity_kg:
        raise AppError(code="CAPACITY_EXCEEDED", message="Cargo exceeds vehicle capacity.", status_code=409)
    trip = Trip(organization_id=principal.organization_id, **payload.model_dump())
    session.add(trip)
    await session.flush()
    _event(session, principal, trip, "created")
    await session.commit()
    return await _read(session, trip)


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: UUID, payload: TripUpdate, principal: CurrentPrincipal, session: DatabaseSession
) -> TripRead:
    trip = await _load_trip(session, principal.organization_id, trip_id, lock=True)
    if trip.status != "DRAFT":
        raise AppError(code="TRIP_NOT_EDITABLE", message="Only draft trips can be updated.", status_code=409)
    if trip.version != payload.version:
        raise AppError(code="STALE_VERSION", message="Trip was updated elsewhere.", status_code=409)
    vehicle, _ = await _resources(
        session, principal.organization_id, payload.vehicle_id, payload.driver_id, lock=False
    )
    if payload.cargo_weight_kg > vehicle.max_capacity_kg:
        raise AppError(code="CAPACITY_EXCEEDED", message="Cargo exceeds vehicle capacity.", status_code=409)
    for field, value in payload.model_dump(exclude={"version"}).items():
        setattr(trip, field, value)
    trip.version += 1
    await session.commit()
    return await _read(session, trip)


@router.post("/{trip_id}/dispatch", response_model=TripRead)
async def dispatch_trip(
    trip_id: UUID,
    principal: CurrentPrincipal,
    session: DatabaseSession,
    idempotency_key: IdempotencyKey = None,
) -> TripRead:
    existing = await _idempotent_trip(session, principal.organization_id, idempotency_key, "trip.dispatch")
    if existing:
        return await _read(session, existing)
    trip = await _load_trip(session, principal.organization_id, trip_id, lock=True)
    vehicle, driver = await _resources(
        session, principal.organization_id, trip.vehicle_id, trip.driver_id, lock=True
    )
    if trip.status != "DRAFT" or vehicle.status != "AVAILABLE" or driver.status != "AVAILABLE":
        raise AppError(code="DISPATCH_CONFLICT", message="Trip resources are no longer available.", status_code=409)
    if driver.license_expiry < datetime.now(UTC).date():
        raise AppError(code="LICENSE_EXPIRED", message="Driver license has expired.", status_code=409)
    trip.status = "DISPATCHED"
    trip.dispatched_at = datetime.now(UTC)
    trip.dispatched_by = principal.user_id
    trip.version += 1
    vehicle.status = "ON_TRIP"
    driver.status = "ON_TRIP"
    _event(session, principal, trip, "dispatched")
    _remember_idempotency(session, principal.organization_id, idempotency_key, "trip.dispatch", trip.id)
    await session.commit()
    return await _read(session, trip)


@router.post("/{trip_id}/complete", response_model=TripRead)
async def complete_trip(
    trip_id: UUID,
    payload: TripComplete,
    principal: CurrentPrincipal,
    session: DatabaseSession,
    idempotency_key: IdempotencyKey = None,
) -> TripRead:
    existing = await _idempotent_trip(session, principal.organization_id, idempotency_key, "trip.complete")
    if existing:
        return await _read(session, existing)
    trip = await _load_trip(session, principal.organization_id, trip_id, lock=True)
    vehicle, driver = await _resources(
        session, principal.organization_id, trip.vehicle_id, trip.driver_id, lock=True
    )
    if trip.status != "DISPATCHED":
        raise AppError(code="TRIP_NOT_DISPATCHED", message="Only dispatched trips can complete.", status_code=409)
    if trip.version != payload.version or payload.final_odometer < vehicle.odometer:
        raise AppError(code="INVALID_ODOMETER_OR_VERSION", message="Final odometer or version is invalid.", status_code=409)
    trip.status = "COMPLETED"
    trip.completed_at = datetime.now(UTC)
    trip.final_odometer = payload.final_odometer
    trip.version += 1
    vehicle.odometer = payload.final_odometer
    vehicle.status = "AVAILABLE"
    driver.status = "AVAILABLE"
    _event(session, principal, trip, "completed")
    _remember_idempotency(session, principal.organization_id, idempotency_key, "trip.complete", trip.id)
    await session.commit()
    return await _read(session, trip)


@router.post("/{trip_id}/cancel", response_model=TripRead)
async def cancel_trip(
    trip_id: UUID, payload: TripCancel, principal: CurrentPrincipal, session: DatabaseSession
) -> TripRead:
    trip = await _load_trip(session, principal.organization_id, trip_id, lock=True)
    if trip.status not in {"DRAFT", "DISPATCHED"} or trip.version != payload.version:
        raise AppError(code="TRIP_CANNOT_CANCEL", message="Trip cannot be cancelled.", status_code=409)
    if trip.status == "DISPATCHED":
        vehicle, driver = await _resources(
            session, principal.organization_id, trip.vehicle_id, trip.driver_id, lock=True
        )
        vehicle.status = "AVAILABLE"
        driver.status = "AVAILABLE"
    trip.status = "CANCELLED"
    trip.cancelled_at = datetime.now(UTC)
    trip.version += 1
    _event(session, principal, trip, "cancelled")
    await session.commit()
    return await _read(session, trip)
