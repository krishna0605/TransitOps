# ADR 0004: OpenAPI client generation

- Status: accepted
- Date: 2026-07-12

## Context

Handwritten frontend API types can drift from FastAPI request and response schemas. Maintaining a
second manual OpenAPI document would create another competing source of truth.

## Decision

FastAPI-generated OpenAPI remains the runtime API source of truth. The repository exports that schema
and generates TypeScript definitions with a pinned OpenAPI generator. Generated files are committed,
must not be edited manually, and are checked for deterministic drift in local validation and CI.

Future endpoints are documented in Markdown until their FastAPI routers exist; placeholder runtime
routes are not created merely to populate OpenAPI.

## Consequences

- Frontend types follow implemented API routes.
- Contract drift is caught before merge.
- Generator upgrades are explicit dependency changes.
- Planned endpoint documentation remains separate from the runtime API until implementation.
