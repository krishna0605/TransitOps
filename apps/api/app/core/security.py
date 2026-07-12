from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings

password_hash = PasswordHash.recommended()


@dataclass(frozen=True)
class AccessClaims:
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    role: str
    session_id: UUID


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return password_hash.verify(password, encoded)


def create_access_token(settings: Settings, claims: AccessClaims) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": str(claims.user_id),
        "org": str(claims.organization_id),
        "membership": str(claims.membership_id),
        "role": claims.role,
        "sid": str(claims.session_id),
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
        "exp": expires_at,
    }
    token = jwt.encode(
        payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm
    )
    return token, expires_at


def decode_access_token(settings: Settings, token: str) -> AccessClaims:
    payload = jwt.decode(
        token, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm]
    )
    return AccessClaims(
        user_id=UUID(payload["sub"]),
        organization_id=UUID(payload["org"]),
        membership_id=UUID(payload["membership"]),
        role=payload["role"],
        session_id=UUID(payload["sid"]),
    )


def new_refresh_token() -> tuple[str, str]:
    token = token_urlsafe(48)
    return token, sha256(token.encode()).hexdigest()
