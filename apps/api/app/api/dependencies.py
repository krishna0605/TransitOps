from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


async def database_session() -> AsyncIterator[AsyncSession]:
    """Compatibility dependency for feature modules added in later slices."""
    async for session in get_db_session():
        yield session
