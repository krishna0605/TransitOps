from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Cookie, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import (
    AccessClaims,
    create_access_token,
    hash_password,
    new_refresh_token,
    verify_password,
)
from app.db.models.platform import (
    Membership,
    Organization,
    OrganizationSettings,
    RefreshSession,
    User,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    role: str


class SwitchOrganizationRequest(BaseModel):
    organization_id: UUID


async def _bootstrap_development(session: DatabaseSession) -> None:
    settings = get_settings()
    if settings.app_env == "production":
        return
    if (await session.execute(select(User).limit(1))).scalar_one_or_none() is not None:
        return
    organization = Organization(name="TransitOps", slug="transitops")
    user = User(
        name="TransitOps Admin",
        email="admin@transitops.local",
        password_hash=hash_password("transitops"),
    )
    session.add_all([organization, user])
    await session.flush()
    session.add_all(
        [
            OrganizationSettings(organization_id=organization.id),
            Membership(
                organization_id=organization.id,
                user_id=user.id,
                role="Fleet Manager",
            ),
        ]
    )
    await session.commit()


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.refresh_cookie_name,
        token,
        max_age=settings.refresh_token_days * 86400,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        path=f"{settings.api_v1_prefix}/auth",
    )


async def _issue_session(
    session: DatabaseSession,
    response: Response,
    user: User,
    membership: Membership,
    *,
    family_id: UUID | None = None,
) -> SessionResponse:
    settings = get_settings()
    refresh_token, refresh_hash = new_refresh_token()
    refresh_session = RefreshSession(
        user_id=user.id,
        organization_id=membership.organization_id,
        family_id=family_id or uuid4(),
        token_hash=refresh_hash,
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
    )
    session.add(refresh_session)
    await session.flush()
    access_token, expires_at = create_access_token(
        settings,
        AccessClaims(
            user_id=user.id,
            organization_id=membership.organization_id,
            membership_id=membership.id,
            role=membership.role,
            session_id=refresh_session.id,
        ),
    )
    await session.commit()
    _set_refresh_cookie(response, refresh_token)
    return SessionResponse(
        access_token=access_token,
        expires_at=expires_at,
        user_id=user.id,
        organization_id=membership.organization_id,
        membership_id=membership.id,
        role=membership.role,
    )


@router.post("/login", response_model=SessionResponse)
async def login(payload: LoginRequest, response: Response, session: DatabaseSession) -> SessionResponse:
    await _bootstrap_development(session)
    user = (
        await session.execute(select(User).where(User.email == payload.email.lower()))
    ).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="The email or password is incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    membership = (
        await session.execute(
            select(Membership)
            .where(Membership.user_id == user.id, Membership.status == "ACTIVE")
            .order_by(Membership.created_at)
            .limit(1)
        )
    ).scalar_one_or_none()
    if membership is None or user.status != "ACTIVE":
        raise AppError(code="ACCOUNT_DISABLED", message="This account is not active.", status_code=403)
    return await _issue_session(session, response, user, membership)


@router.post("/refresh", response_model=SessionResponse)
async def refresh(
    response: Response,
    session: DatabaseSession,
    transitops_refresh: str | None = Cookie(default=None),
) -> SessionResponse:
    from hashlib import sha256

    if transitops_refresh is None:
        raise AppError(code="REFRESH_REQUIRED", message="A refresh token is required.", status_code=401)
    token_hash = sha256(transitops_refresh.encode()).hexdigest()
    refresh_session = (
        await session.execute(
            select(RefreshSession).where(RefreshSession.token_hash == token_hash).with_for_update()
        )
    ).scalar_one_or_none()
    if (
        refresh_session is None
        or refresh_session.revoked_at is not None
        or refresh_session.expires_at <= datetime.now(UTC)
    ):
        raise AppError(code="INVALID_REFRESH_TOKEN", message="The refresh token is invalid.", status_code=401)
    refresh_session.revoked_at = datetime.now(UTC)
    user = await session.get(User, refresh_session.user_id)
    membership = (
        await session.execute(
            select(Membership).where(
                Membership.user_id == refresh_session.user_id,
                Membership.organization_id == refresh_session.organization_id,
            )
        )
    ).scalar_one()
    assert user is not None
    return await _issue_session(
        session, response, user, membership, family_id=refresh_session.family_id
    )


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    session: DatabaseSession,
    transitops_refresh: str | None = Cookie(default=None),
) -> None:
    from hashlib import sha256

    if transitops_refresh:
        token_hash = sha256(transitops_refresh.encode()).hexdigest()
        refresh_session = (
            await session.execute(select(RefreshSession).where(RefreshSession.token_hash == token_hash))
        ).scalar_one_or_none()
        if refresh_session is not None:
            refresh_session.revoked_at = datetime.now(UTC)
            await session.commit()
    response.delete_cookie(get_settings().refresh_cookie_name, path="/api/v1/auth")


@router.get("/me")
async def me(principal: CurrentPrincipal) -> dict[str, object]:
    return {
        "user_id": principal.user_id,
        "organization_id": principal.organization_id,
        "membership_id": principal.membership_id,
        "role": principal.role,
    }


@router.post("/switch-organization", response_model=SessionResponse)
async def switch_organization(
    payload: SwitchOrganizationRequest,
    response: Response,
    principal: CurrentPrincipal,
    session: DatabaseSession,
) -> SessionResponse:
    membership = (
        await session.execute(
            select(Membership).where(
                Membership.user_id == principal.user_id,
                Membership.organization_id == payload.organization_id,
                Membership.status == "ACTIVE",
            )
        )
    ).scalar_one_or_none()
    user = await session.get(User, principal.user_id)
    if membership is None or user is None:
        raise AppError(code="MEMBERSHIP_NOT_FOUND", message="Membership was not found.", status_code=404)
    return await _issue_session(session, response, user, membership)
