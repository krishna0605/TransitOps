from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def scoped(self, organization_id: UUID) -> Select[tuple[ModelT]]:
        return select(self.model).where(self.model.organization_id == organization_id)

    async def get(self, organization_id: UUID, entity_id: UUID, *, lock: bool = False) -> ModelT | None:
        statement = self.scoped(organization_id).where(self.model.id == entity_id)
        if lock:
            statement = statement.with_for_update()
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def list(self, organization_id: UUID) -> Sequence[ModelT]:
        return (await self.session.execute(self.scoped(organization_id))).scalars().all()

    def add(self, instance: ModelT) -> None:
        self.session.add(instance)
