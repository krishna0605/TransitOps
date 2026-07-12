from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, update

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.models.platform import ContactSubmission, Document, Notification, ReportExport
from app.infrastructure.rate_limit import enforce_rate_limit
from app.infrastructure.storage import S3Storage
from app.workers.reports import generate_report

router = APIRouter(tags=["platform"])

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png", "text/csv"}


class DocumentCreate(BaseModel):
    entity_type: str = Field(pattern=r"^(vehicle|driver|trip|maintenance|expense)$")
    entity_id: UUID
    document_type: str = Field(min_length=2, max_length=40)
    filename: str = Field(min_length=1, max_length=255)
    content_type: str
    size_bytes: int = Field(gt=0)


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    upload_url: str
    expires_in: int = 900


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    topic: str = Field(min_length=2, max_length=80)
    message: str = Field(min_length=10, max_length=5000)


class ExportCreate(BaseModel):
    report_type: str = Field(pattern=r"^(expenses|analytics)$")
    filters: dict[str, object] = Field(default_factory=dict)


@router.post("/documents", response_model=DocumentUploadResponse, status_code=201)
async def initiate_document(
    payload: DocumentCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> DocumentUploadResponse:
    settings = get_settings()
    if (
        payload.content_type not in ALLOWED_CONTENT_TYPES
        or payload.size_bytes > settings.max_upload_bytes
    ):
        raise AppError(
            code="INVALID_DOCUMENT",
            message="Document type or size is not allowed.",
            status_code=422,
        )
    safe_name = Path(payload.filename).name
    document_id = uuid4()
    key = f"{principal.organization_id}/documents/{document_id}/{safe_name}"
    document = Document(
        id=document_id,
        organization_id=principal.organization_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        document_type=payload.document_type,
        object_key=key,
        filename=safe_name,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
    )
    session.add(document)
    await session.commit()
    return DocumentUploadResponse(
        document_id=document.id, upload_url=S3Storage().presign_upload(key, payload.content_type)
    )


@router.post("/documents/{document_id}/complete", response_model=None)
async def complete_document(
    document_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> Document:
    document = (
        await session.execute(
            select(Document)
            .where(
                Document.id == document_id, Document.organization_id == principal.organization_id
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if document is None:
        raise AppError(
            code="DOCUMENT_NOT_FOUND", message="Document was not found.", status_code=404
        )
    if not S3Storage().exists(document.object_key):
        raise AppError(
            code="UPLOAD_NOT_FOUND", message="Uploaded object was not found.", status_code=409
        )
    document.uploaded = True
    await session.commit()
    return document


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> dict[str, str]:
    document = (
        await session.execute(
            select(Document).where(
                Document.id == document_id,
                Document.organization_id == principal.organization_id,
                Document.uploaded.is_(True),
            )
        )
    ).scalar_one_or_none()
    if document is None:
        raise AppError(
            code="DOCUMENT_NOT_FOUND", message="Document was not found.", status_code=404
        )
    return {"download_url": S3Storage().presign_download(document.object_key, document.filename)}


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> None:
    document = (
        await session.execute(
            select(Document).where(
                Document.id == document_id, Document.organization_id == principal.organization_id
            )
        )
    ).scalar_one_or_none()
    if document is None:
        raise AppError(
            code="DOCUMENT_NOT_FOUND", message="Document was not found.", status_code=404
        )
    S3Storage().delete(document.object_key)
    await session.delete(document)
    await session.commit()


@router.get("/notifications", response_model=None)
async def list_notifications(
    principal: CurrentPrincipal, session: DatabaseSession
) -> list[Notification]:
    return list(
        (
            await session.execute(
                select(Notification)
                .where(
                    Notification.organization_id == principal.organization_id,
                    (Notification.user_id == principal.user_id) | (Notification.user_id.is_(None)),
                )
                .order_by(Notification.created_at.desc())
            )
        ).scalars()
    )


@router.post("/notifications/{notification_id}/read", response_model=None)
async def read_notification(
    notification_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> Notification:
    notification = (
        await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.organization_id == principal.organization_id,
            )
        )
    ).scalar_one_or_none()
    if notification is None:
        raise AppError(
            code="NOTIFICATION_NOT_FOUND", message="Notification was not found.", status_code=404
        )
    notification.read_at = datetime.now(UTC)
    await session.commit()
    return notification


@router.post("/notifications/read-all", status_code=204)
async def read_all_notifications(principal: CurrentPrincipal, session: DatabaseSession) -> None:
    await session.execute(
        update(Notification)
        .where(
            Notification.organization_id == principal.organization_id,
            Notification.user_id == principal.user_id,
            Notification.read_at.is_(None),
        )
        .values(read_at=datetime.now(UTC))
    )
    await session.commit()


@router.post("/report-exports", status_code=202, response_model=None)
async def create_export(
    payload: ExportCreate, principal: CurrentPrincipal, session: DatabaseSession
) -> ReportExport:
    report = ReportExport(
        organization_id=principal.organization_id,
        requested_by=principal.user_id,
        report_type=payload.report_type,
        filters=payload.filters,
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    generate_report.send(str(report.id))
    return report


@router.get("/report-exports/{report_id}", response_model=None)
async def get_export(
    report_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> ReportExport:
    report = (
        await session.execute(
            select(ReportExport).where(
                ReportExport.id == report_id,
                ReportExport.organization_id == principal.organization_id,
            )
        )
    ).scalar_one_or_none()
    if report is None:
        raise AppError(code="REPORT_NOT_FOUND", message="Report was not found.", status_code=404)
    return report


@router.get("/report-exports/{report_id}/download")
async def download_export(
    report_id: UUID, principal: CurrentPrincipal, session: DatabaseSession
) -> dict[str, str]:
    report = await get_export(report_id, principal, session)
    if report.status != "COMPLETED" or not report.object_key:
        raise AppError(code="REPORT_NOT_READY", message="Report is not ready.", status_code=409)
    return {
        "download_url": S3Storage().presign_download(report.object_key, f"{report.report_type}.csv")
    }


@router.post("/contact-submissions", status_code=status.HTTP_202_ACCEPTED)
async def create_contact(
    payload: ContactCreate, request: Request, session: DatabaseSession
) -> dict[str, str]:
    address = request.client.host if request.client else "unknown"
    address_hash = sha256(address.encode()).hexdigest()
    await enforce_rate_limit(f"contact:{address_hash}", limit=5, window_seconds=3600)
    session.add(
        ContactSubmission(
            name=payload.name.strip(),
            email=payload.email.lower(),
            topic=payload.topic.strip(),
            message=payload.message.strip(),
            source_ip_hash=address_hash,
        )
    )
    await session.commit()
    return {"status": "accepted"}
