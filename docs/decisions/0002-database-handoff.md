# ADR 0002: Database handoff boundary

- Status: accepted
- Date: 2026-07-12

## Context

Database schema work is owned by Kavish and is expected to proceed in parallel with application work.

## Decision

The initial scaffold provides only the PostgreSQL connection, SQLAlchemy session, Alembic environment,
and readiness contract. Domain models, migrations, constraints, indexes, and seeds are excluded.

## Consequences

- Application and database branches can begin from the same stable scaffold.
- Schema proposals must be reviewed against service transaction requirements before merging.
- SQLite is not supported, avoiding test and production behavior differences.
