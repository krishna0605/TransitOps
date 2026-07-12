# TransitOps Ownership

This document records collaboration boundaries; it does not enforce GitHub review rules.

## Database ownership — Kavish (`@kavish0001`)

- `apps/api/app/db/models/`
- `apps/api/migrations/versions/`
- Domain schema constraints and indexes
- Database seed infrastructure

The scaffold intentionally leaves these locations empty of domain definitions.

## Primary application ownership

- Next.js frontend
- FastAPI routers
- Application services and business policies
- Authentication and RBAC
- Client integrations and automated tests

## Shared review areas

- `apps/api/app/core/database.py`
- API and persistence data contracts
- Transaction boundaries
- Migration review

Changes in a shared area should be coordinated before implementation. `CODEOWNERS` is intentionally
deferred until the team agrees on mandatory review rules.
