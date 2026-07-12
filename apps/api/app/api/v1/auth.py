"""Authentication endpoints (Screen 0).

Provides a single password login used by the web sign-in form. Passwords are
verified against argon2 hashes stored on the ``user`` table via pwdlib. The
authoritative role is read from the joined ``role`` row and returned to the
client, which uses it to drive RBAC (sidebar + landing screen).

A lightweight in-memory lockout guards against brute force: after five
consecutive failed attempts for an email the account is locked (HTTP 423) until
a successful login or a process restart resets the counter.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.dependencies import DatabaseSession
from app.core.exceptions import AppError
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

_password_hasher = PasswordHash.recommended()

# Max consecutive failures before an email is locked out.
_MAX_FAILED_ATTEMPTS = 5

# Module-level, in-memory failure counter keyed by (lower-cased) email.
# Resets on a successful login or on process restart. Intentionally not
# persisted — this is a demo-grade brute-force guard, not a security control.
_failed_attempts: dict[str, int] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    name: str
    email: str
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, session: DatabaseSession) -> LoginResponse:
    """Verify credentials and return the user's identity + authoritative role."""
    email = payload.email.strip().lower()

    if _failed_attempts.get(email, 0) >= _MAX_FAILED_ATTEMPTS:
        raise AppError(
            code="ACCOUNT_LOCKED",
            message="Account locked after 5 failed attempts. Try again later.",
            status_code=status.HTTP_423_LOCKED,
        )

    result = await session.execute(
        select(User).options(joinedload(User.role)).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    password_ok = user is not None and _password_hasher.verify(
        payload.password, user.password_hash
    )

    if user is None or not password_ok:
        # Count this failure. Once it reaches the max, the *next* request is
        # rejected up-front with 423 (so the 6th attempt after 5 failures locks).
        _failed_attempts[email] = _failed_attempts.get(email, 0) + 1
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Incorrect email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Success — clear any prior failures for this email.
    _failed_attempts.pop(email, None)

    return LoginResponse(name=user.name, email=user.email, role=user.role.role_name)
