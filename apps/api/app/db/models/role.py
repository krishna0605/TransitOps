from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constants import ROLE_NAMES, in_check

if TYPE_CHECKING:
    from app.db.models.user import User


class Role(Base):
    __tablename__ = "role"
    __table_args__ = (CheckConstraint(in_check("role_name", ROLE_NAMES), name="role_name_valid"),)

    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    users: Mapped[list[User]] = relationship(back_populates="role")
