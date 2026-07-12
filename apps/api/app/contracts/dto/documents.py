from datetime import date
from uuid import UUID

from pydantic import Field

from app.contracts.dto.common import AwareDateTime, ContractModel
from app.contracts.enums import DocumentType


class DocumentCreate(ContractModel):
    document_type: DocumentType
    document_number: str | None = Field(default=None, max_length=120)
    vehicle_id: UUID | None = None
    driver_id: UUID | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    storage_key: str = Field(min_length=1, max_length=500)
    original_filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=120)
    size_bytes: int = Field(gt=0)


class DocumentRead(ContractModel):
    id: UUID
    document_type: DocumentType
    document_number: str | None
    vehicle_id: UUID | None
    driver_id: UUID | None
    issue_date: date | None
    expiry_date: date | None
    original_filename: str
    content_type: str
    size_bytes: int
    uploaded_by: UUID
    uploaded_at: AwareDateTime


class SignedUploadResponse(ContractModel):
    storage_key: str
    upload_url: str
    expires_at: AwareDateTime
    required_headers: dict[str, str] = Field(default_factory=dict)


class SignedDownloadResponse(ContractModel):
    download_url: str
    expires_at: AwareDateTime
