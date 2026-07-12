"""Shared helpers for the versioned domain routers.

The domain slices under ``app/api/v1`` operate directly on the ORM models via the
async session dependency. This module provides the small pieces they all share:
an ORM-friendly Pydantic base and a not-found helper that raises the project's
standard :class:`AppError`.
"""

from __future__ import annotations

from fastapi import status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.db.base import Base


class ORMModel(BaseModel):
    """Response base that reads attributes straight off SQLAlchemy models."""

    model_config = ConfigDict(from_attributes=True)


async def get_or_404[ModelT: Base](
    session: AsyncSession,
    model: type[ModelT],
    pk: int,
    *,
    entity: str,
) -> ModelT:
    """Return a row by primary key or raise a 404 ``AppError``."""
    instance = await session.get(model, pk)
    if instance is None:
        raise AppError(
            code=f"{entity.upper()}_NOT_FOUND",
            message=f"{entity.capitalize()} {pk} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return instance
