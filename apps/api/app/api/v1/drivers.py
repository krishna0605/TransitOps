from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.driver import Driver

router = APIRouter(prefix="/drivers", tags=["drivers"])


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    driver_id: UUID
    name: str
    license_no: str
    license_category: str
    license_expiry: date
    contact: str
    safety_score: Decimal
    status: str
    version: int


class DriverCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    license_no: str = Field(min_length=2, max_length=64)
    license_category: Literal["LMV", "HMV"]
    license_expiry: date
    contact: str = Field(min_length=3, max_length=80)
    safety_score: Decimal = Field(default=Decimal(100), ge=0, le=100)


class DriverUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    license_expiry: date
    contact: str = Field(min_length=3, max_length=80)
    safety_score: Decimal = Field(ge=0, le=100)
    version: int = Field(ge=1)


class DriverStatusUpdate(BaseModel):
    status: Literal["AVAILABLE", "OFF_DUTY", "SUSPENDED"]
    version: int = Field(ge=1)


async def _driver(
    session: DatabaseSession, organization_id: UUID, driver_id: UUID, *, lock: bool = False
) -> Driver:
    statement = select(Driver).where(
        Driver.id == driver_id,
        Driver.organization_id == organization_id,
        Driver.archived_at.is_(None),
    )
    if lock:
        statement = statement.with_for_update()
    driver = (await session.execute(statement)).scalar_one_or_none()
    if driver is None:
        raise AppError(code="DRIVER_NOT_FOUND", message="Driver was not found.", status_code=404)
    return driver


@router.get("", response_model=list[DriverRead])
async def list_drivers(
    principal: CurrentPrincipal,
    session: DatabaseSession,
    dispatchable: Annotated[bool, Query()] = False,
    search: Annotated[str | None, Query(max_length=80)] = None,
) -> list[Driver]:
    statement = select(Driver).where(
        Driver.organization_id == principal.organization_id, Driver.archived_at.is_(None)
    )
    if dispatchable:
        statement = statement.where(
            Driver.status == "AVAILABLE", Driver.license_expiry >= date.today()
        )
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(Driver.name.ilike(pattern), Driver.license_no.ilike(pattern))
        )
    return list((await session.execute(statement.order_by(Driver.created_at.desc()))).scalars())


@router.get("/{driver_id}", response_model=DriverRead)
async def get_driver(
    driver_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> Driver:
    return await _driver(session, principal.organization_id, driver_id)


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> Driver:
    if payload.license_expiry < date.today():
        raise AppError(code="LICENSE_EXPIRED", message="License expiry must be in the future.")
    driver = Driver(
        organization_id=principal.organization_id,
        name=payload.name.strip(),
        license_no=payload.license_no.strip().upper(),
        license_category=payload.license_category,
        license_expiry=payload.license_expiry,
        contact=payload.contact.strip(),
        safety_score=payload.safety_score,
    )
    session.add(driver)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(
            code="DRIVER_LICENSE_TAKEN",
            message="License number is already in use.",
            status_code=409,
        ) from exc
    await session.refresh(driver)
    return driver


@router.patch("/{driver_id}", response_model=DriverRead)
async def update_driver(
    driver_id: UUID, payload: DriverUpdate, principal: CurrentPrincipal, session: DatabaseSession
) -> Driver:
    driver = await _driver(session, principal.organization_id, driver_id, lock=True)
    if driver.version != payload.version:
        raise AppError(
            code="STALE_VERSION", message="Driver was updated elsewhere.", status_code=409
        )
    driver.name = payload.name.strip()
    driver.license_expiry = payload.license_expiry
    driver.contact = payload.contact.strip()
    driver.safety_score = payload.safety_score
    driver.version += 1
    await session.commit()
    await session.refresh(driver)
    return driver


@router.patch("/{driver_id}/status", response_model=DriverRead)
async def update_driver_status(
    driver_id: UUID,
    payload: DriverStatusUpdate,
    principal: CurrentPrincipal,
    session: DatabaseSession,
) -> Driver:
    driver = await _driver(session, principal.organization_id, driver_id, lock=True)
    if driver.status == "ON_TRIP":
        raise AppError(
            code="DRIVER_ON_TRIP",
            message="An assigned driver cannot change status.",
            status_code=409,
        )
    if driver.version != payload.version:
        raise AppError(
            code="STALE_VERSION", message="Driver was updated elsewhere.", status_code=409
        )
    driver.status = payload.status
    driver.version += 1
    await session.commit()
    await session.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=204)
async def archive_driver(
    driver_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> None:
    driver = await _driver(session, principal.organization_id, driver_id, lock=True)
    if driver.status == "ON_TRIP":
        raise AppError(
            code="DRIVER_ON_TRIP", message="An assigned driver cannot be archived.", status_code=409
        )
    driver.archived_at = datetime.now(UTC)
    driver.status = "OFF_DUTY"
    driver.version += 1
    await session.commit()
