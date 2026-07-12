from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.exceptions import AppError


async def enforce_rate_limit(key: str, *, limit: int, window_seconds: int) -> None:
    client = Redis.from_url(get_settings().redis_url, decode_responses=True)
    try:
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, window_seconds)
        if count > limit:
            raise AppError(
                code="RATE_LIMITED", message="Too many requests. Try again later.", status_code=429
            )
    finally:
        await client.aclose()
