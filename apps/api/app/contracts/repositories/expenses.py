from typing import Protocol
from uuid import UUID

from app.contracts.dto.common import Page
from app.contracts.dto.finance import (
    ExpenseCreate,
    ExpenseFilters,
    ExpenseRead,
    ExpenseReviewRequest,
)


class ExpenseRepository(Protocol):
    async def get_by_id(self, expense_id: UUID) -> ExpenseRead | None: ...

    async def list(self, filters: ExpenseFilters) -> Page[ExpenseRead]: ...

    async def create(self, data: ExpenseCreate, created_by: UUID) -> ExpenseRead: ...

    async def review(
        self, expense_id: UUID, data: ExpenseReviewRequest, reviewed_by: UUID
    ) -> ExpenseRead: ...
