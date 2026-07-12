# ADR 0001: Modular monolith

- Status: accepted
- Date: 2026-07-12

## Context

TransitOps needs transactional dispatch, maintenance, and financial workflows under a short delivery
timeline. Splitting these operations across independently deployed services would add coordination and
failure modes before the domain is stable.

## Decision

Use a Next.js frontend and one FastAPI modular monolith backed by PostgreSQL. Feature packages retain
clear boundaries, while state-changing workflows share one database transaction.

## Consequences

- The first version is easier to develop, test, deploy, and debug.
- PostgreSQL remains the authoritative source of operational state.
- Modules can be extracted later only when scale or ownership provides evidence for doing so.
