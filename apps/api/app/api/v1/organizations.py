from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.platform import Membership, Organization, OrganizationSettings

router = APIRouter(tags=["organizations"])


class OrganizationUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    version: int = Field(ge=1)


class SettingsUpdate(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    distance_unit: str = Field(pattern=r"^(km|mi)$")
    timezone: str = Field(min_length=3, max_length=64)
    version: int = Field(ge=1)


@router.get("/organizations/current", response_model=None)
async def current_organization(
    principal: CurrentPrincipal, session: DatabaseSession
) -> Organization:
    organization = await session.get(Organization, principal.organization_id)
    if organization is None:
        raise AppError(
            code="ORGANIZATION_NOT_FOUND", message="Organization was not found.", status_code=404
        )
    return organization


@router.patch("/organizations/current", response_model=None)
async def update_organization(
    payload: OrganizationUpdate, principal: CurrentPrincipal, session: DatabaseSession
) -> Organization:
    organization = await session.get(Organization, principal.organization_id, with_for_update=True)
    assert organization is not None
    if organization.version != payload.version:
        raise AppError(
            code="STALE_VERSION", message="Organization was updated elsewhere.", status_code=409
        )
    organization.name = payload.name.strip()
    organization.version += 1
    await session.commit()
    await session.refresh(organization)
    return organization


@router.get("/organizations/current/settings", response_model=None)
async def current_settings(
    principal: CurrentPrincipal, session: DatabaseSession
) -> OrganizationSettings:
    settings = await session.get(OrganizationSettings, principal.organization_id)
    if settings is None:
        raise AppError(
            code="SETTINGS_NOT_FOUND", message="Settings were not found.", status_code=404
        )
    return settings


@router.patch("/organizations/current/settings", response_model=None)
async def update_settings(
    payload: SettingsUpdate, principal: CurrentPrincipal, session: DatabaseSession
) -> OrganizationSettings:
    settings = await session.get(
        OrganizationSettings, principal.organization_id, with_for_update=True
    )
    assert settings is not None
    if settings.version != payload.version:
        raise AppError(
            code="STALE_VERSION", message="Settings were updated elsewhere.", status_code=409
        )
    settings.currency = payload.currency
    settings.distance_unit = payload.distance_unit
    settings.timezone = payload.timezone
    settings.version += 1
    await session.commit()
    await session.refresh(settings)
    return settings


@router.get("/memberships", response_model=None)
async def list_memberships(
    principal: CurrentPrincipal, session: DatabaseSession
) -> list[Membership]:
    return list(
        (
            await session.execute(
                select(Membership).where(Membership.organization_id == principal.organization_id)
            )
        ).scalars()
    )
