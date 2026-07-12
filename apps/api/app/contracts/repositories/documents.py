from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.documents import DocumentCreate, DocumentRead
from app.contracts.filters import ListFilters


class DocumentRepository(Protocol):
    async def get_by_id(self, document_id: UUID) -> DocumentRead | None: ...

    async def list(self, filters: ListFilters) -> Page[DocumentRead]: ...

    async def create(self, data: DocumentCreate, uploaded_by: UUID) -> DocumentRead: ...

    async def archive(self, document_id: UUID, archived_by: UUID) -> None: ...
