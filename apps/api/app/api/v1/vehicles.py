from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vehicle_id: UUID
    reg_no: str
    name_model: str
    type: str
    max_capacity_kg: Decimal
    odometer: Decimal
    acquisition_cost: Decimal
    status: str
    version: int


class VehicleCreate(BaseModel):
    reg_no: str = Field(min_length=1, max_length=32)
    name_model: str = Field(min_length=1, max_length=80)
    type: Literal["Van", "Truck", "Mini"]
    max_capacity_kg: Decimal = Field(gt=0)
    acquisition_cost: Decimal = Field(ge=0)
    odometer: Decimal = Field(default=Decimal(0), ge=0)


class VehicleUpdate(BaseModel):
    name_model: str = Field(min_length=1, max_length=80)
    max_capacity_kg: Decimal = Field(gt=0)
    acquisition_cost: Decimal = Field(ge=0)
    version: int = Field(ge=1)


async def _vehicle(session: DatabaseSession, organization_id: UUID, vehicle_id: UUID, *, lock: bool = False) -> Vehicle:
    statement = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.organization_id == organization_id,
        Vehicle.archived_at.is_(None),
    )
    if lock:
        statement = statement.with_for_update()
    vehicle = (await session.execute(statement)).scalar_one_or_none()
    if vehicle is None:
        raise AppError(code="VEHICLE_NOT_FOUND", message="Vehicle was not found.", status_code=404)
    return vehicle


@router.get("", response_model=list[VehicleRead])
async def list_vehicles(
    principal: CurrentPrincipal,
    session: DatabaseSession,
    dispatchable: Annotated[bool, Query()] = False,
    search: Annotated[str | None, Query(max_length=80)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Vehicle]:
    statement = select(Vehicle).where(
        Vehicle.organization_id == principal.organization_id, Vehicle.archived_at.is_(None)
    )
    if dispatchable:
        statement = statement.where(Vehicle.status == "AVAILABLE")
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(or_(Vehicle.reg_no.ilike(pattern), Vehicle.name_model.ilike(pattern)))
    result = await session.execute(statement.order_by(Vehicle.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars())


@router.get("/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(vehicle_id: UUID, principal: CurrentPrincipal, session: DatabaseSession) -> Vehicle:
    return await _vehicle(session, principal.organization_id, vehicle_id)


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, principal: CurrentPrincipal, session: DatabaseSession) -> Vehicle:
    vehicle = Vehicle(
        organization_id=principal.organization_id,
        reg_no=payload.reg_no.strip().upper(),
        name_model=payload.name_model.strip(),
        type=payload.type,
        max_capacity_kg=payload.max_capacity_kg,
        acquisition_cost=payload.acquisition_cost,
        odometer=payload.odometer,
    )
    session.add(vehicle)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(code="VEHICLE_REG_NO_TAKEN", message="Registration number is already in use.", status_code=409) from exc
    await session.refresh(vehicle)
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: UUID, payload: VehicleUpdate, principal: CurrentPrincipal, session: DatabaseSession
) -> Vehicle:
    vehicle = await _vehicle(session, principal.organization_id, vehicle_id, lock=True)
    if vehicle.version != payload.version:
        raise AppError(code="STALE_VERSION", message="Vehicle was updated elsewhere.", status_code=409)
    vehicle.name_model = payload.name_model.strip()
    vehicle.max_capacity_kg = payload.max_capacity_kg
    vehicle.acquisition_cost = payload.acquisition_cost
    vehicle.version += 1
    await session.commit()
    await session.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
async def archive_vehicle(vehicle_id: UUID, principal: CurrentPrincipal, session: DatabaseSession) -> None:
    vehicle = await _vehicle(session, principal.organization_id, vehicle_id, lock=True)
    if vehicle.status in {"ON_TRIP", "IN_SHOP"}:
        raise AppError(code="VEHICLE_IN_USE", message="An active vehicle cannot be archived.", status_code=409)
    vehicle.archived_at = datetime.now(UTC)
    vehicle.status = "RETIRED"
    vehicle.version += 1
    await session.commit()
