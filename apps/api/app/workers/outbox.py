from datetime import UTC, datetime, timedelta

import dramatiq
from sqlalchemy import select

from app.core.database import session_factory
from app.db.models.platform import Notification, OutboxEvent
from app.workers.broker import broker as broker


@dramatiq.actor(max_retries=5, min_backoff=5_000)
async def drain_outbox() -> int:
    processed = 0
    async with session_factory() as session:
        events = list(
            (
                await session.execute(
                    select(OutboxEvent)
                    .where(
                        OutboxEvent.processed_at.is_(None),
                        OutboxEvent.available_at <= datetime.now(UTC),
                    )
                    .with_for_update(skip_locked=True)
                    .limit(100)
                )
            ).scalars()
        )
        for event in events:
            try:
                if event.event_type in {"trip.cancelled", "maintenance.created"}:
                    session.add(
                        Notification(
                            organization_id=event.organization_id,
                            type="SYSTEM",
                            title=event.event_type.replace(".", " ").title(),
                            message="An operational workflow changed.",
                            payload=event.payload,
                        )
                    )
                event.processed_at = datetime.now(UTC)
                processed += 1
            except Exception as exc:
                event.attempts += 1
                event.last_error = type(exc).__name__
                event.available_at = datetime.now(UTC) + timedelta(
                    seconds=min(3600, 2**event.attempts)
                )
        await session.commit()
    return processed
