"""Fuel & expense endpoints (Screen 6).

Fuel logs and manual expenses can each optionally attach to a trip; when they do,
the trip must belong to the chosen vehicle (the UI picker is scoped the same way).
Manual expenses cover Toll and Other only — Maintenance expenses are posted
automatically from the maintenance screen and never entered by hand here.
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
from app.db.models.fuel_log import FuelLog
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(tags=["finance"])

ManualExpenseCategory = Literal["Toll", "Other"]


def _trip_label(trip: Trip | None) -> str | None:
    return f"{trip.source} → {trip.destination}" if trip is not None else None


# --------------------------------------------------------------------------- fuel


class FuelRead(ORMModel):
    fuel_id: int
    vehicle_id: int
    vehicle_reg_no: str
    trip_id: int | None
    trip_label: str | None
    fuel_date: date
    liters: float
    cost: float


class FuelCreate(ORMModel):
    vehicle_id: int
    trip_id: int | None = None
    fuel_date: date | None = None
    liters: float = Field(gt=0)
    cost: float = Field(ge=0)


def _serialize_fuel(log: FuelLog) -> FuelRead:
    return FuelRead(
        fuel_id=log.fuel_id,
        vehicle_id=log.vehicle_id,
        vehicle_reg_no=log.vehicle.reg_no,
        trip_id=log.trip_id,
        trip_label=_trip_label(log.trip),
        fuel_date=log.fuel_date,
        liters=log.liters,
        cost=log.cost,
    )


async def _validate_trip_for_vehicle(
    session: DatabaseSession, trip_id: int | None, vehicle_id: int
) -> None:
    if trip_id is None:
        return
    trip = await get_or_404(session, Trip, trip_id, entity="trip")
    if trip.vehicle_id != vehicle_id:
        raise AppError(
            code="TRIP_VEHICLE_MISMATCH",
            message="The selected trip does not belong to this vehicle.",
        )


@router.get("/fuel", response_model=list[FuelRead])
async def list_fuel(
    session: DatabaseSession,
    vehicle_id: Annotated[int | None, Query()] = None,
) -> list[FuelRead]:
    """List fuel logs newest first, optionally scoped to a vehicle."""
    statement = (
        select(FuelLog)
        .options(selectinload(FuelLog.vehicle), selectinload(FuelLog.trip))
        .order_by(FuelLog.fuel_id.desc())
    )
    if vehicle_id is not None:
        statement = statement.where(FuelLog.vehicle_id == vehicle_id)
    logs = (await session.execute(statement)).scalars().all()
    return [_serialize_fuel(log) for log in logs]


@router.post("/fuel", response_model=FuelRead, status_code=status.HTTP_201_CREATED)
async def create_fuel(payload: FuelCreate, session: DatabaseSession) -> FuelRead:
    """Log fuel for a vehicle, optionally attributed to one of its trips."""
    vehicle = await get_or_404(session, Vehicle, payload.vehicle_id, entity="vehicle")
    await _validate_trip_for_vehicle(session, payload.trip_id, vehicle.vehicle_id)
    log = FuelLog(
        vehicle_id=vehicle.vehicle_id,
        trip_id=payload.trip_id,
        fuel_date=payload.fuel_date or date.today(),
        liters=payload.liters,
        cost=payload.cost,
    )
    session.add(log)
    await session.commit()
    statement = (
        select(FuelLog)
        .where(FuelLog.fuel_id == log.fuel_id)
        .options(selectinload(FuelLog.vehicle), selectinload(FuelLog.trip))
    )
    return _serialize_fuel((await session.execute(statement)).scalar_one())


# ------------------------------------------------------------------------ expense


class ExpenseRead(ORMModel):
    expense_id: int
    vehicle_id: int
    vehicle_reg_no: str
    trip_id: int | None
    trip_label: str | None
    maintenance_id: int | None
    category: str
    amount: float
    status: str


class ExpenseCreate(ORMModel):
    vehicle_id: int
    trip_id: int | None = None
    category: ManualExpenseCategory = "Toll"
    amount: float = Field(gt=0)


def _serialize_expense(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        expense_id=expense.expense_id,
        vehicle_id=expense.vehicle_id,
        vehicle_reg_no=expense.vehicle.reg_no,
        trip_id=expense.trip_id,
        trip_label=_trip_label(expense.trip),
        maintenance_id=expense.maintenance_id,
        category=expense.category,
        amount=expense.amount,
        status=expense.status,
    )


@router.get("/expenses", response_model=list[ExpenseRead])
async def list_expenses(
    session: DatabaseSession,
    vehicle_id: Annotated[int | None, Query()] = None,
) -> list[ExpenseRead]:
    """List expenses newest first, optionally scoped to a vehicle. Includes both
    manual (Toll/Other) and auto-posted Maintenance rows."""
    statement = (
        select(Expense)
        .options(selectinload(Expense.vehicle), selectinload(Expense.trip))
        .order_by(Expense.expense_id.desc())
    )
    if vehicle_id is not None:
        statement = statement.where(Expense.vehicle_id == vehicle_id)
    expenses = (await session.execute(statement)).scalars().all()
    return [_serialize_expense(e) for e in expenses]


@router.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(payload: ExpenseCreate, session: DatabaseSession) -> ExpenseRead:
    """Record a manual Toll or Other expense. Maintenance expenses are posted
    automatically from the maintenance screen, so they cannot be created here."""
    vehicle = await get_or_404(session, Vehicle, payload.vehicle_id, entity="vehicle")
    await _validate_trip_for_vehicle(session, payload.trip_id, vehicle.vehicle_id)
    expense = Expense(
        vehicle_id=vehicle.vehicle_id,
        trip_id=payload.trip_id,
        maintenance_id=None,
        category=payload.category,
        amount=payload.amount,
        status="Available",
    )
    session.add(expense)
    await session.commit()
    statement = (
        select(Expense)
        .where(Expense.expense_id == expense.expense_id)
        .options(selectinload(Expense.vehicle), selectinload(Expense.trip))
    )
    return _serialize_expense((await session.execute(statement)).scalar_one())
