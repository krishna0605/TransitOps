from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field

from app.contracts.dto.common import ContractModel
from app.contracts.enums import UserStatus
from app.contracts.permissions import Permission


class LoginRequest(ContractModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class PermissionSummary(ContractModel):
    name: Permission
    description: str | None = None


class RoleSummary(ContractModel):
    id: UUID
    name: str = Field(min_length=1, max_length=64)
    permissions: list[Permission] = Field(default_factory=list)


class CurrentUserResponse(ContractModel):
    id: UUID
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    status: UserStatus
    roles: list[RoleSummary]
    permissions: list[Permission]


class TokenResponse(ContractModel):
    access_token: str = Field(min_length=1)
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(gt=0)
    user: CurrentUserResponse
