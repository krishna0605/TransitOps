from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.expense import Expense
from app.db.models.maintenance_log import MaintenanceLog
from app.db.models.platform import AuditLog, OrganizationSettings, OutboxEvent
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


class MaintenanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    maintenance_id: UUID
    vehicle_id: UUID
    vehicle_reg_no: str
    trip_id: UUID | None
    service_type: str
    priority: str
    cost: Decimal
    service_date: date
    status: str
    version: int


class MaintenanceCreate(BaseModel):
    vehicle_id: UUID
    trip_id: UUID | None = None
    service_type: str = Field(min_length=2, max_length=100)
    priority: Literal["LOW", "NORMAL", "HIGH", "CRITICAL"] = "NORMAL"
    cost: Decimal = Field(ge=0)
    service_date: date | None = None


class MaintenanceTransition(BaseModel):
    version: int = Field(ge=1)


async def _load(session: DatabaseSession, organization_id: UUID, maintenance_id: UUID, *, lock: bool = False) -> MaintenanceLog:
    statement = select(MaintenanceLog).where(
        MaintenanceLog.id == maintenance_id, MaintenanceLog.organization_id == organization_id
    )
    if lock:
        statement = statement.with_for_update()
    record = (await session.execute(statement)).scalar_one_or_none()
    if record is None:
        raise AppError(code="MAINTENANCE_NOT_FOUND", message="Maintenance record was not found.", status_code=404)
    return record


async def _read(session: DatabaseSession, record: MaintenanceLog) -> MaintenanceRead:
    vehicle = await session.get(Vehicle, record.vehicle_id)
    assert vehicle is not None
    return MaintenanceRead(
        maintenance_id=record.id,
        vehicle_id=record.vehicle_id,
        vehicle_reg_no=vehicle.reg_no,
        trip_id=record.trip_id,
        service_type=record.service_type,
        priority=record.priority,
        cost=record.cost,
        service_date=record.service_date,
        status=record.status,
        version=record.version,
    )


@router.get("", response_model=list[MaintenanceRead])
async def list_maintenance(principal: CurrentPrincipal, session: DatabaseSession) -> list[MaintenanceRead]:
    records = list(
        (
            await session.execute(
                select(MaintenanceLog)
                .where(MaintenanceLog.organization_id == principal.organization_id)
                .order_by(MaintenanceLog.created_at.desc())
            )
        ).scalars()
    )
    return [await _read(session, record) for record in records]


@router.post("", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    payload: MaintenanceCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> MaintenanceRead:
    vehicle = (
        await session.execute(
            select(Vehicle)
            .where(Vehicle.id == payload.vehicle_id, Vehicle.organization_id == principal.organization_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if vehicle is None:
        raise AppError(code="VEHICLE_NOT_FOUND", message="Vehicle was not found.", status_code=404)
    if vehicle.status in {"ON_TRIP", "IN_SHOP", "RETIRED"}:
        raise AppError(code="VEHICLE_UNAVAILABLE", message="Vehicle cannot enter maintenance.", status_code=409)
    if payload.trip_id:
        trip = await session.get(Trip, payload.trip_id)
        if trip is None or trip.organization_id != principal.organization_id or trip.vehicle_id != vehicle.id:
            raise AppError(code="TRIP_VEHICLE_MISMATCH", message="Trip does not belong to this vehicle.", status_code=409)
    active = (
        await session.execute(
            select(MaintenanceLog).where(
                MaintenanceLog.organization_id == principal.organization_id,
                MaintenanceLog.vehicle_id == vehicle.id,
                MaintenanceLog.status == "ACTIVE",
            )
        )
    ).scalar_one_or_none()
    if active:
        raise AppError(code="MAINTENANCE_ALREADY_ACTIVE", message="Vehicle already has active maintenance.", status_code=409)
    record = MaintenanceLog(
        organization_id=principal.organization_id,
        vehicle_id=vehicle.id,
        trip_id=payload.trip_id,
        service_type=payload.service_type.strip(),
        priority=payload.priority,
        cost=payload.cost,
        service_date=payload.service_date or date.today(),
    )
    session.add(record)
    await session.flush()
    currency = await session.get(OrganizationSettings, principal.organization_id)
    session.add(
        Expense(
            organization_id=principal.organization_id,
            vehicle_id=vehicle.id,
            trip_id=payload.trip_id,
            maintenance_id=record.id,
            category="MAINTENANCE",
            amount=payload.cost,
            currency=currency.currency if currency else "INR",
            status="APPROVED",
            approved_by=principal.user_id,
            approved_at=datetime.now(UTC),
        )
    )
    vehicle.status = "IN_SHOP"
    session.add_all(
        [
            AuditLog(organization_id=principal.organization_id, actor_id=principal.user_id, action="created", entity_type="maintenance", entity_id=record.id),
            OutboxEvent(organization_id=principal.organization_id, event_type="maintenance.created", aggregate_type="maintenance", aggregate_id=record.id, payload={"maintenance_id": str(record.id)}),
        ]
    )
    await session.commit()
    return await _read(session, record)


async def _transition(
    maintenance_id: UUID,
    payload: MaintenanceTransition,
    principal: CurrentPrincipal,
    session: DatabaseSession,
    target: str,
) -> MaintenanceRead:
    record = await _load(session, principal.organization_id, maintenance_id, lock=True)
    if record.status != "ACTIVE" or record.version != payload.version:
        raise AppError(code="MAINTENANCE_CONFLICT", message="Maintenance cannot transition.", status_code=409)
    vehicle = (
        await session.execute(select(Vehicle).where(Vehicle.id == record.vehicle_id).with_for_update())
    ).scalar_one()
    record.status = target
    record.closed_at = datetime.now(UTC)
    record.version += 1
    if vehicle.status == "IN_SHOP":
        vehicle.status = "AVAILABLE"
    session.add(AuditLog(organization_id=principal.organization_id, actor_id=principal.user_id, action=target.lower(), entity_type="maintenance", entity_id=record.id))
    await session.commit()
    return await _read(session, record)


@router.post("/{maintenance_id}/close", response_model=MaintenanceRead)
async def close_maintenance(maintenance_id: UUID, payload: MaintenanceTransition, principal: CurrentPrincipal, session: DatabaseSession) -> MaintenanceRead:
    return await _transition(maintenance_id, payload, principal, session, "COMPLETED")


@router.post("/{maintenance_id}/cancel", response_model=MaintenanceRead)
async def cancel_maintenance(maintenance_id: UUID, payload: MaintenanceTransition, principal: CurrentPrincipal, session: DatabaseSession) -> MaintenanceRead:
    return await _transition(maintenance_id, payload, principal, session, "CANCELLED")
