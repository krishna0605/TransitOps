from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DatabaseSession
from app.contracts.permissions import Permission
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.db.models.platform import Membership, User

bearer = HTTPBearer(auto_error=False)

ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "Fleet Manager": frozenset(Permission),
    "Dispatcher": frozenset(
        {
            Permission.VEHICLE_VIEW,
            Permission.DRIVER_VIEW,
            Permission.TRIP_VIEW,
            Permission.TRIP_CREATE,
            Permission.TRIP_UPDATE,
            Permission.TRIP_DISPATCH,
            Permission.TRIP_COMPLETE,
            Permission.TRIP_CANCEL,
            Permission.NOTIFICATION_VIEW,
        }
    ),
    "Safety Officer": frozenset(
        {
            Permission.DRIVER_VIEW,
            Permission.DRIVER_CREATE,
            Permission.DRIVER_UPDATE,
            Permission.DRIVER_SUSPEND,
            Permission.DRIVER_RESTORE,
            Permission.DOCUMENT_VIEW,
            Permission.DOCUMENT_CREATE,
            Permission.DOCUMENT_DELETE,
            Permission.NOTIFICATION_VIEW,
        }
    ),
    "Financial Analyst": frozenset(
        {
            Permission.FUEL_VIEW,
            Permission.FUEL_CREATE,
            Permission.EXPENSE_VIEW,
            Permission.EXPENSE_CREATE,
            Permission.EXPENSE_APPROVE,
            Permission.REPORT_VIEW,
            Permission.REPORT_EXPORT,
            Permission.NOTIFICATION_VIEW,
        }
    ),
}


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    role: str


async def _development_principal(session: AsyncSession) -> Principal | None:
    membership = (await session.execute(select(Membership).limit(1))).scalar_one_or_none()
    if membership is None:
        return None
    return Principal(
        user_id=membership.user_id,
        organization_id=membership.organization_id,
        membership_id=membership.id,
        role=membership.role,
    )


async def current_principal(
    session: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    settings = get_settings()
    if credentials is None and settings.app_env != "production":
        principal = await _development_principal(session)
        if principal is not None:
            return principal
    if credentials is None:
        raise AppError(
            code="AUTHENTICATION_REQUIRED",
            message="Authentication is required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        claims = decode_access_token(settings, credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AppError(
            code="INVALID_ACCESS_TOKEN",
            message="The access token is invalid or expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc
    membership = await session.get(Membership, claims.membership_id)
    user = await session.get(User, claims.user_id)
    if (
        membership is None
        or user is None
        or membership.organization_id != claims.organization_id
        or membership.user_id != claims.user_id
        or membership.status != "ACTIVE"
        or user.status != "ACTIVE"
    ):
        raise AppError(
            code="SESSION_REVOKED",
            message="This session is no longer active.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return Principal(user.id, membership.organization_id, membership.id, membership.role)


CurrentPrincipal = Annotated[Principal, Depends(current_principal)]


def require_permission(permission: Permission):  # type: ignore[no-untyped-def]
    async def dependency(principal: CurrentPrincipal) -> Principal:
        if permission not in ROLE_PERMISSIONS.get(principal.role, frozenset()):
            raise AppError(
                code="PERMISSION_DENIED",
                message="You do not have permission to perform this action.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return principal

    return dependency


IdempotencyKey = Annotated[str | None, Header(alias="Idempotency-Key", max_length=128)]
