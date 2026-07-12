# 0005: Backend platform completion

- Status: Accepted
- Date: 2026-07-12

## Context

TransitOps has stable frontend contracts but its runtime API still persists directly from route
handlers and implements only part of the documented platform. The backend must support multiple
organizations, transactional workflows, background work, object storage, and reproducible
deployment without weakening the existing contract and layout checks.

## Decision

TransitOps remains a FastAPI and SQLAlchemy modular monolith backed by PostgreSQL. The application
uses UUID identifiers, UTC timestamps, exact numeric columns for financial and measurement data,
tenant-scoped uniqueness, optimistic versions, soft archival, and one unit of work per command.

The authenticated organization is derived from a signed access token. Every tenant-owned query is
scoped by that organization, and cross-tenant identifiers are reported as not found. Refresh tokens
are opaque, rotated on use, stored only as hashes, and delivered through secure HTTP-only cookies.

Operational mutations accept idempotency keys and write audit and outbox records in the same
database transaction. Dramatiq consumes Redis-backed work for exports and notifications. Documents
and generated reports use an S3-compatible storage adapter, with MinIO as the local implementation.

OpenAPI is the public frontend contract. Collection responses use standard pagination, errors use a
stable problem-details shape, monetary values serialize as decimal strings, and stale optimistic
versions return conflicts.

## Boundaries

- Routers translate HTTP requests and responses only.
- Application services enforce workflows and own transaction boundaries.
- Repositories never commit or roll back.
- Infrastructure adapters implement persistence, queue, rate-limit, and storage ports.
- API startup never applies database migrations.
- The API, migration, and worker processes use one immutable container image.

## Consequences

The development database is rebuilt from a canonical migration. Redis and S3-compatible storage
become required platform dependencies. Existing web layout checks remain independent blocking CI
gates, while generated API artifacts prevent contract drift.
