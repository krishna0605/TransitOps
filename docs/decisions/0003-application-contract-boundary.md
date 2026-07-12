# ADR 0003: Application contract boundary

- Status: accepted
- Date: 2026-07-12

## Context

TransitOps application services need stable interfaces while persistence work proceeds independently.
Allowing services or API routers to depend directly on SQLAlchemy models would couple public API
behavior to database implementation details and make isolated business-rule testing difficult.

## Decision

Application services depend on asynchronous repository and unit-of-work protocols defined under
`app.contracts`. Contract DTOs use Pydantic for validation and serialization but do not import
FastAPI, SQLAlchemy, Alembic, or persistence modules.

Repository implementations map persistence records to contract DTOs. Repositories never commit;
application services explicitly commit successful workflows through the unit of work.

## Consequences

- Services can be tested with in-memory protocol implementations.
- Persistence models never become public API response types.
- Mapping code is explicit and must be tested once persistence implementations exist.
- Contract changes require coordinated review because they affect both application and persistence work.
