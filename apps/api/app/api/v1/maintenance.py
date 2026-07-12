"""Maintenance endpoints (Screen 5).

Creating an Active record moves its vehicle to In Shop. When a record is linked
to a trip, a matching Maintenance expense row is auto-posted (schema rule 11):
same trip and vehicle, amount equal to the maintenance cost, and
``expense.maintenance_id`` pointing back at the record. Records with no trip only
affect vehicle-level cost totals, so no expense row is created.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Query, status
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import DatabaseSession
from app.api.v1.common import ORMModel, get_or_404
from app.core.exceptions import AppError
from app.db.models.expense import Expense
from app.db.models.maintenance_log import MaintenanceLog
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

MaintenanceStatus = Literal["Active", "Completed"]


class MaintenanceRead(ORMModel):
    maintenance_id: int
    vehicle_id: int
    vehicle_reg_no: str
    trip_id: int | None
    service_type: str
    cost: float
    service_date: date
    status: str
    # Set when this record auto-posted a linked expense (trip-scoped records).
    linked_expense_id: int | None


class MaintenanceCreate(ORMModel):
    vehicle_id: int
    trip_id: int | None = None
    service_type: str = Field(min_length=1, max_length=120)
    cost: float = Field(ge=0)
    service_date: date | None = None
    status: MaintenanceStatus = "Active"


def _serialize(log: MaintenanceLog) -> MaintenanceRead:
    return MaintenanceRead(
        maintenance_id=log.maintenance_id,
        vehicle_id=log.vehicle_id,
        vehicle_reg_no=log.vehicle.reg_no,
        trip_id=log.trip_id,
        service_type=log.service_type,
        cost=log.cost,
        service_date=log.service_date,
        status=log.status,
        linked_expense_id=log.expense.expense_id if log.expense is not None else None,
    )


async def _load(session: DatabaseSession, maintenance_id: int) -> MaintenanceLog:
    statement = (
        select(MaintenanceLog)
        .where(MaintenanceLog.maintenance_id == maintenance_id)
        .options(selectinload(MaintenanceLog.vehicle), selectinload(MaintenanceLog.expense))
    )
    log = (await session.execute(statement)).scalar_one_or_none()
    if log is None:
        raise AppError(
            code="MAINTENANCE_NOT_FOUND",
            message=f"Maintenance record {maintenance_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return log


@router.get("", response_model=list[MaintenanceRead])
async def list_maintenance(
    session: DatabaseSession,
    vehicle_id: Annotated[int | None, Query()] = None,
) -> list[MaintenanceRead]:
    """List maintenance records newest first, optionally scoped to a vehicle."""
    statement = (
        select(MaintenanceLog)
        .options(selectinload(MaintenanceLog.vehicle), selectinload(MaintenanceLog.expense))
        .order_by(MaintenanceLog.maintenance_id.desc())
    )
    if vehicle_id is not None:
        statement = statement.where(MaintenanceLog.vehicle_id == vehicle_id)
    logs = (await session.execute(statement)).scalars().all()
    return [_serialize(log) for log in logs]


@router.post("", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    payload: MaintenanceCreate, session: DatabaseSession
) -> MaintenanceRead:
    """Log a maintenance record and apply its side effects.

    Active -> vehicle set to In Shop. trip_id set -> auto-post a Maintenance
    expense linked back to this record (only when the trip belongs to the
    vehicle).
    """
    vehicle = await get_or_404(session, Vehicle, payload.vehicle_id, entity="vehicle")

    if payload.trip_id is not None:
        trip = await get_or_404(session, Trip, payload.trip_id, entity="trip")
        if trip.vehicle_id != vehicle.vehicle_id:
            raise AppError(
                code="TRIP_VEHICLE_MISMATCH",
                message="The selected trip does not belong to this vehicle.",
            )

    log = MaintenanceLog(
        vehicle_id=vehicle.vehicle_id,
        trip_id=payload.trip_id,
        service_type=payload.service_type.strip(),
        cost=payload.cost,
        service_date=payload.service_date or date.today(),
        status=payload.status,
    )
    session.add(log)
    await session.flush()  # assign maintenance_id before linking the expense

    # Rule 9: an Active record puts the vehicle In Shop (out of the dispatch pool).
    if log.status == "Active" and vehicle.status != "Retired":
        vehicle.status = "In Shop"

    # Rule 11: trip-linked maintenance auto-posts a matching Maintenance expense.
    if log.trip_id is not None:
        session.add(
            Expense(
                vehicle_id=vehicle.vehicle_id,
                trip_id=log.trip_id,
                maintenance_id=log.maintenance_id,
                category="Maintenance",
                amount=log.cost,
                status="Available",
            )
        )

    await session.commit()
    return _serialize(await _load(session, log.maintenance_id))


@router.post("/{maintenance_id}/close", response_model=MaintenanceRead)
async def close_maintenance(maintenance_id: int, session: DatabaseSession) -> MaintenanceRead:
    """Complete a maintenance record. The vehicle returns to Available unless it
    was Retired (rule 10)."""
    log = await _load(session, maintenance_id)
    if log.status == "Completed":
        raise AppError(
            code="MAINTENANCE_ALREADY_CLOSED",
            message="This maintenance record is already completed.",
        )
    log.status = "Completed"
    if log.vehicle.status == "In Shop":
        log.vehicle.status = "Available"
    await session.commit()
    return _serialize(await _load(session, maintenance_id))
