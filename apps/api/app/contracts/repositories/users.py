from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import EmailStr

from app.contracts.dto.auth import (
    CurrentUserResponse,
    RefreshTokenCreate,
    RefreshTokenRecord,
    UserCredentialRecord,
)


class UserRepository(Protocol):
    async def get_by_id(self, user_id: UUID) -> CurrentUserResponse | None: ...

    async def get_credentials_by_email(self, email: EmailStr) -> UserCredentialRecord | None: ...

    async def record_login_attempt(
        self,
        *,
        email: EmailStr,
        succeeded: bool,
        ip_address: str | None,
        occurred_at: datetime,
    ) -> None: ...


class RefreshTokenRepository(Protocol):
    async def get_by_id(self, token_id: UUID) -> RefreshTokenRecord | None: ...

    async def create(self, data: RefreshTokenCreate) -> RefreshTokenRecord: ...

    async def revoke(self, token_id: UUID, revoked_at: datetime) -> None: ...
