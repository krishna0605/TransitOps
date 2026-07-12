"""Seed one demo login user per TransitOps role.

Run from the repository root:

    .venv/Scripts/python.exe scripts/seed_demo.py

Creates (idempotently) a "TransitOps" organization and four users, one per
role, all sharing the password ``transitops``. Safe to run repeatedly.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the API package importable and ensure ``apps/api/.env`` is discovered by
# pydantic-settings (it reads the .env relative to the process CWD).
API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
sys.path.insert(0, str(API_DIR))
os.chdir(API_DIR)

import asyncio  # noqa: E402

from sqlalchemy import select  # noqa: E402

import app.db.models  # noqa: E402,F401  (registers every table on Base.metadata)
from app.core.database import engine, session_factory  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.models.platform import (  # noqa: E402
    Membership,
    Organization,
    OrganizationSettings,
    User,
)

# (email, display name, role, password) — role strings must match the app's ROLE_NAMES.
# Each role gets its own distinct login.
SEED_USERS: list[tuple[str, str, str, str]] = [
    ("fleet.manager@transitops.app", "Fleet Manager", "Fleet Manager", "Fleet@2026"),
    ("dispatcher@transitops.app", "Dana Dispatcher", "Dispatcher", "Dispatch@2026"),
    ("safety.officer@transitops.app", "Sam Safety", "Safety Officer", "Safety@2026"),
    ("finance.analyst@transitops.app", "Fin Analyst", "Financial Analyst", "Finance@2026"),
]


async def main() -> None:
    # Ensure the application schema exists. The bundled Alembic migration is
    # stale relative to the current models, so create any missing tables from
    # the ORM metadata (idempotent — existing tables are left untouched).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        # Ensure the demo organization exists.
        org = (
            await session.execute(
                select(Organization).where(Organization.slug == "transitops")
            )
        ).scalar_one_or_none()
        if org is None:
            org = Organization(name="TransitOps", slug="transitops")
            session.add(org)
            await session.flush()
            session.add(OrganizationSettings(organization_id=org.id))

        # Ensure each demo user + membership exists.
        for email, name, role, password in SEED_USERS:
            user = (
                await session.execute(select(User).where(User.email == email))
            ).scalar_one_or_none()
            if user is None:
                user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    status="ACTIVE",
                )
                session.add(user)
                await session.flush()

            membership = (
                await session.execute(
                    select(Membership).where(
                        Membership.organization_id == org.id,
                        Membership.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()
            if membership is None:
                session.add(
                    Membership(
                        organization_id=org.id,
                        user_id=user.id,
                        role=role,
                        status="ACTIVE",
                    )
                )

        await session.commit()

    print("Seeded demo users:")
    for email, _name, role, password in SEED_USERS:
        print(f"  {role:<18} | {email:<32} | password: {password}")
    print("\nAll of the above belong to org 'TransitOps'.")


if __name__ == "__main__":
    # On Windows the default ProactorEventLoop is incompatible with psycopg's
    # async mode; force the SelectorEventLoop policy before running.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
