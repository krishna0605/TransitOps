from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.expense import Expense
from app.db.models.fuel_log import FuelLog
from app.db.models.platform import AuditLog, OrganizationSettings
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(tags=["finance"])


class FuelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    fuel_id: UUID
    vehicle_id: UUID
    vehicle_reg_no: str
    trip_id: UUID | None
    fuel_date: date
    liters: Decimal
    cost: Decimal
    odometer: Decimal | None
    version: int


class FuelCreate(BaseModel):
    vehicle_id: UUID
    trip_id: UUID | None = None
    fuel_date: date | None = None
    liters: Decimal = Field(gt=0)
    cost: Decimal = Field(ge=0)
    odometer: Decimal | None = Field(default=None, ge=0)


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: UUID
    vehicle_id: UUID | None
    trip_id: UUID | None
    maintenance_id: UUID | None
    fuel_id: UUID | None
    category: str
    amount: Decimal
    currency: str
    status: str
    description: str | None
    version: int
    vehicle_reg_no: str | None = None
    trip_label: str | None = None


class ExpenseCreate(BaseModel):
    vehicle_id: UUID | None = None
    trip_id: UUID | None = None
    category: Literal["TOLL", "PARKING", "INSURANCE", "PERMIT", "OTHER"]
    amount: Decimal = Field(gt=0)
    description: str | None = Field(default=None, max_length=500)


class ExpenseDecision(BaseModel):
    version: int = Field(ge=1)
    reason: str | None = Field(default=None, max_length=500)


async def _vehicle(
    session: DatabaseSession, organization_id: UUID, vehicle_id: UUID, *, lock: bool = False
) -> Vehicle:
    statement = select(Vehicle).where(
        Vehicle.id == vehicle_id, Vehicle.organization_id == organization_id
    )
    if lock:
        statement = statement.with_for_update()
    vehicle = (await session.execute(statement)).scalar_one_or_none()
    if vehicle is None:
        raise AppError(code="VEHICLE_NOT_FOUND", message="Vehicle was not found.", status_code=404)
    return vehicle


async def _validate_trip(
    session: DatabaseSession, organization_id: UUID, trip_id: UUID | None, vehicle_id: UUID | None
) -> None:
    if trip_id is None:
        return
    trip = await session.get(Trip, trip_id)
    if trip is None or trip.organization_id != organization_id or trip.vehicle_id != vehicle_id:
        raise AppError(
            code="TRIP_VEHICLE_MISMATCH",
            message="Trip does not belong to this vehicle.",
            status_code=409,
        )


async def _fuel_read(session: DatabaseSession, log: FuelLog) -> FuelRead:
    vehicle = await session.get(Vehicle, log.vehicle_id)
    assert vehicle is not None
    return FuelRead(
        fuel_id=log.id,
        vehicle_id=vehicle.id,
        vehicle_reg_no=vehicle.reg_no,
        trip_id=log.trip_id,
        fuel_date=log.fuel_date,
        liters=log.liters,
        cost=log.cost,
        odometer=log.odometer,
        version=log.version,
    )


@router.get("/fuel", response_model=list[FuelRead])
async def list_fuel(
    principal: CurrentPrincipal,
    session: DatabaseSession,
    vehicle_id: Annotated[UUID | None, Query()] = None,
) -> list[FuelRead]:
    statement = select(FuelLog).where(FuelLog.organization_id == principal.organization_id)
    if vehicle_id:
        statement = statement.where(FuelLog.vehicle_id == vehicle_id)
    logs = list((await session.execute(statement.order_by(FuelLog.created_at.desc()))).scalars())
    return [await _fuel_read(session, log) for log in logs]


@router.post("/fuel", response_model=FuelRead, status_code=status.HTTP_201_CREATED)
async def create_fuel(
    payload: FuelCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> FuelRead:
    vehicle = await _vehicle(session, principal.organization_id, payload.vehicle_id, lock=True)
    await _validate_trip(session, principal.organization_id, payload.trip_id, vehicle.id)
    if payload.odometer is not None and payload.odometer < vehicle.odometer:
        raise AppError(
            code="ODOMETER_REGRESSION", message="Odometer cannot decrease.", status_code=409
        )
    log = FuelLog(
        organization_id=principal.organization_id,
        **payload.model_dump(exclude={"fuel_date"}),
        fuel_date=payload.fuel_date or date.today(),
    )
    session.add(log)
    await session.flush()
    settings = await session.get(OrganizationSettings, principal.organization_id)
    session.add(
        Expense(
            organization_id=principal.organization_id,
            vehicle_id=vehicle.id,
            trip_id=payload.trip_id,
            fuel_id=log.id,
            category="FUEL",
            amount=payload.cost,
            currency=settings.currency if settings else "INR",
            status="APPROVED",
            approved_by=principal.user_id,
            approved_at=datetime.now(UTC),
        )
    )
    if payload.odometer is not None:
        vehicle.odometer = payload.odometer
    await session.commit()
    return await _fuel_read(session, log)


@router.get("/expenses", response_model=list[ExpenseRead])
async def list_expenses(
    principal: CurrentPrincipal,
    session: DatabaseSession,
    vehicle_id: Annotated[UUID | None, Query()] = None,
) -> list[Expense]:
    statement = select(Expense).where(Expense.organization_id == principal.organization_id)
    if vehicle_id:
        statement = statement.where(Expense.vehicle_id == vehicle_id)
    return list((await session.execute(statement.order_by(Expense.created_at.desc()))).scalars())


@router.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    payload: ExpenseCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> Expense:
    if payload.vehicle_id:
        await _vehicle(session, principal.organization_id, payload.vehicle_id)
    await _validate_trip(session, principal.organization_id, payload.trip_id, payload.vehicle_id)
    settings = await session.get(OrganizationSettings, principal.organization_id)
    expense = Expense(
        organization_id=principal.organization_id,
        currency=settings.currency if settings else "INR",
        **payload.model_dump(),
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def _decide(
    expense_id: UUID,
    payload: ExpenseDecision,
    principal: CurrentPrincipal,
    session: DatabaseSession,
    target: str,
) -> Expense:
    expense = (
        await session.execute(
            select(Expense)
            .where(Expense.id == expense_id, Expense.organization_id == principal.organization_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if expense is None:
        raise AppError(code="EXPENSE_NOT_FOUND", message="Expense was not found.", status_code=404)
    if expense.status != "PENDING" or expense.version != payload.version:
        raise AppError(
            code="EXPENSE_CONFLICT", message="Expense cannot be decided.", status_code=409
        )
    expense.status = target
    expense.version += 1
    if target == "APPROVED":
        expense.approved_by = principal.user_id
        expense.approved_at = datetime.now(UTC)
    else:
        expense.rejection_reason = payload.reason
    session.add(
        AuditLog(
            organization_id=principal.organization_id,
            actor_id=principal.user_id,
            action=target.lower(),
            entity_type="expense",
            entity_id=expense.id,
        )
    )
    await session.commit()
    await session.refresh(expense)
    return expense


@router.post("/expenses/{expense_id}/approve", response_model=ExpenseRead)
async def approve_expense(
    expense_id: UUID,
    payload: ExpenseDecision,
    principal: CurrentPrincipal,
    session: DatabaseSession,
) -> Expense:
    return await _decide(expense_id, payload, principal, session, "APPROVED")


@router.post("/expenses/{expense_id}/reject", response_model=ExpenseRead)
async def reject_expense(
    expense_id: UUID,
    payload: ExpenseDecision,
    principal: CurrentPrincipal,
    session: DatabaseSession,
) -> Expense:
    return await _decide(expense_id, payload, principal, session, "REJECTED")
