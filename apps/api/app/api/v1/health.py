import asyncio
from typing import Literal

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.database import check_database
from app.core.exceptions import ErrorResponse
from app.infrastructure.storage import S3Storage

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    name: str
    environment: str
    version: str
    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"
    database: Literal["ready", "skipped"]
    redis: Literal["ready", "skipped"]
    storage: Literal["ready", "skipped"]


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
        return ReadinessResponse(database="skipped", redis="skipped", storage="skipped")

    database_ready = await check_database()
    redis_client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        redis_ready = bool(await redis_client.ping())  # type: ignore[misc]
    except Exception:
        redis_ready = False
    finally:
        await redis_client.aclose()
    try:
        storage_ready = (
            await asyncio.to_thread(S3Storage().client.head_bucket, Bucket=settings.s3_bucket)
            is not None
        )
    except Exception:
        storage_ready = False

    if database_ready and redis_ready and storage_ready:
        return ReadinessResponse(database="ready", redis="ready", storage="ready")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "code": "DATABASE_UNAVAILABLE",
            "message": "One or more backend dependencies are not ready.",
            "details": {
                "database": database_ready,
                "redis": redis_ready,
                "storage": storage_ready,
            },
            "request_id": request.state.request_id,
        },
    )
