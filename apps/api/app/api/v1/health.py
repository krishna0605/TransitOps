from typing import Literal

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.database import check_database
from app.core.exceptions import ErrorResponse

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    name: str
    environment: str
    version: str
    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"
    database: Literal["ready", "skipped"]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        name=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse}},
)
async def readiness(request: Request) -> ReadinessResponse | JSONResponse:
    settings = get_settings()
    if not settings.database_check_on_startup:
        return ReadinessResponse(database="skipped")

    if await check_database():
        return ReadinessResponse(database="ready")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "code": "DATABASE_UNAVAILABLE",
            "message": "PostgreSQL is not ready.",
            "details": {},
            "request_id": request.state.request_id,
        },
    )
