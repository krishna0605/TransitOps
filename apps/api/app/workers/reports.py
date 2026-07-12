import csv
import io
from datetime import UTC, datetime, timedelta
from uuid import UUID

import dramatiq
from sqlalchemy import select

from app.core.database import session_factory
from app.db.models.expense import Expense
from app.db.models.platform import Notification, ReportExport
from app.infrastructure.storage import S3Storage
from app.workers.broker import broker as broker


@dramatiq.actor(max_retries=5, min_backoff=5_000)
async def generate_report(report_id: str) -> None:
    async with session_factory() as session:
        report = await session.get(ReportExport, UUID(report_id), with_for_update=True)
        if report is None or report.status == "COMPLETED":
            return
        report.status = "PROCESSING"
        await session.commit()
        try:
            expenses = list(
                (
                    await session.execute(
                        select(Expense).where(
                            Expense.organization_id == report.organization_id,
                            Expense.status == "APPROVED",
                        )
                    )
                ).scalars()
            )
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["expense_id", "category", "amount", "currency", "created_at"])
            for expense in expenses:
                writer.writerow(
                    [
                        expense.id,
                        expense.category,
                        expense.amount,
                        expense.currency,
                        expense.created_at.isoformat(),
                    ]
                )
            key = f"{report.organization_id}/reports/{report.id}.csv"
            S3Storage().upload(key, output.getvalue().encode(), "text/csv")
            report.object_key = key
            report.status = "COMPLETED"
            report.expires_at = datetime.now(UTC) + timedelta(days=7)
            session.add(
                Notification(
                    organization_id=report.organization_id,
                    user_id=report.requested_by,
                    type="REPORT_READY",
                    title="Report ready",
                    message="Your TransitOps export is ready.",
                    payload={"report_id": str(report.id)},
                )
            )
            await session.commit()
        except Exception as exc:
            report.status = "FAILED"
            report.error = type(exc).__name__
            await session.commit()
            raise
