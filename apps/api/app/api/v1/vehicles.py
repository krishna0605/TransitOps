"""Vehicle registry endpoints (Screen 2).

Exposes the fleet master list plus the dispatch-eligible subset. ``reg_no`` is the
identifier surfaced to the UI; ``name_model`` is an internal label only.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Query, status
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import DatabaseSession
from app.api.v1.common import ORMModel
from app.core.exceptions import AppError
from app.db.constants import VEHICLE_TYPES
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

VehicleType = Literal["Van", "Truck", "Mini"]
VehicleStatus = Literal["Available", "On Trip", "In Shop", "Retired"]


class VehicleRead(ORMModel):
    vehicle_id: int
    reg_no: str
    name_model: str
    type: str
    max_capacity_kg: float
    odometer: int
    acquisition_cost: float
    status: str


class VehicleCreate(ORMModel):
    reg_no: str = Field(min_length=1, max_length=32)
    name_model: str = Field(min_length=1, max_length=64)
    type: VehicleType
    max_capacity_kg: float = Field(gt=0)
    acquisition_cost: float = Field(ge=0)
    odometer: int = Field(default=0, ge=0)


@router.get("", response_model=list[VehicleRead])
async def list_vehicles(
    session: DatabaseSession,
    dispatchable: Annotated[bool, Query()] = False,
) -> list[Vehicle]:
    """List vehicles, newest first. ``dispatchable=true`` returns only the pool
    eligible for trip dispatch (Available; never Retired or In Shop)."""
    statement = select(Vehicle).order_by(Vehicle.vehicle_id.desc())
    if dispatchable:
        statement = statement.where(Vehicle.status == "Available")
    result = await session.execute(statement)
    return list(result.scalars().all())


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, session: DatabaseSession) -> Vehicle:
    """Register a new vehicle. ``reg_no`` must be unique."""
    if payload.type not in VEHICLE_TYPES:  # defensive; Literal already constrains input
        raise AppError(code="INVALID_VEHICLE_TYPE", message="Unknown vehicle type.")

    vehicle = Vehicle(
        reg_no=payload.reg_no.strip().upper(),
        name_model=payload.name_model.strip(),
        type=payload.type,
        max_capacity_kg=payload.max_capacity_kg,
        acquisition_cost=payload.acquisition_cost,
        odometer=payload.odometer,
        status="Available",
    )
    session.add(vehicle)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(
            code="VEHICLE_REG_NO_TAKEN",
            message=f"Registration number {vehicle.reg_no} is already in use.",
            status_code=status.HTTP_409_CONFLICT,
        ) from exc
    await session.refresh(vehicle)
    return vehicle
