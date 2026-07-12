"""Driver & safety endpoints (Screen 3).

Exposes driver profiles plus the dispatch-eligible subset. A driver is eligible
only when Available and holding a licence that has not expired.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Query, status
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import DatabaseSession
from app.api.v1.common import ORMModel, get_or_404
from app.core.exceptions import AppError
from app.db.models.driver import Driver

router = APIRouter(prefix="/drivers", tags=["drivers"])

LicenseCategory = Literal["LMV", "HMV"]
DriverStatus = Literal["Available", "On Trip", "Off Duty", "Suspended"]


class DriverRead(ORMModel):
    driver_id: int
    name: str
    license_no: str
    license_category: str
    license_expiry: date
    contact: str
    safety_score: float
    status: str


class DriverCreate(ORMModel):
    name: str = Field(min_length=1, max_length=120)
    license_no: str = Field(min_length=1, max_length=32)
    license_category: LicenseCategory
    license_expiry: date
    contact: str = Field(min_length=1, max_length=32)
    safety_score: float = Field(default=100, ge=0, le=100)


class DriverStatusUpdate(ORMModel):
    status: DriverStatus


@router.get("", response_model=list[DriverRead])
async def list_drivers(
    session: DatabaseSession,
    dispatchable: Annotated[bool, Query()] = False,
) -> list[Driver]:
    """List drivers. ``dispatchable=true`` returns only eligible drivers
    (Available with a licence that has not expired)."""
    statement = select(Driver).order_by(Driver.driver_id.desc())
    if dispatchable:
        statement = statement.where(
            Driver.status == "Available", Driver.license_expiry >= date.today()
        )
    result = await session.execute(statement)
    return list(result.scalars().all())


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def create_driver(payload: DriverCreate, session: DatabaseSession) -> Driver:
    """Create a driver profile. ``license_no`` must be unique."""
    driver = Driver(
        name=payload.name.strip(),
        license_no=payload.license_no.strip().upper(),
        license_category=payload.license_category,
        license_expiry=payload.license_expiry,
        contact=payload.contact.strip(),
        safety_score=payload.safety_score,
        status="Available",
    )
    session.add(driver)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(
            code="DRIVER_LICENSE_TAKEN",
            message=f"Licence number {driver.license_no} is already registered.",
            status_code=status.HTTP_409_CONFLICT,
        ) from exc
    await session.refresh(driver)
    return driver


@router.patch("/{driver_id}/status", response_model=DriverRead)
async def update_driver_status(
    driver_id: int, payload: DriverStatusUpdate, session: DatabaseSession
) -> Driver:
    """Manually change a driver's duty status (Screen 3 inline control).

    'On Trip' is managed by the dispatcher and cannot be set by hand here.
    """
    driver = await get_or_404(session, Driver, driver_id, entity="driver")
    if payload.status == "On Trip":
        raise AppError(
            code="DRIVER_STATUS_MANAGED",
            message="'On Trip' is set automatically when a trip is dispatched.",
        )
    if driver.status == "On Trip":
        raise AppError(
            code="DRIVER_ON_TRIP",
            message="Complete or cancel the active trip before changing status.",
        )
    driver.status = payload.status
    await session.commit()
    await session.refresh(driver)
    return driver
