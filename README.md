# TransitOps

Smart transport operations platform for fleet, driver, dispatch, maintenance, and expense management.

This repository contains a Next.js web application and a FastAPI modular monolith. The scaffold
deliberately contains no business entities or schema migrations; database domain work is handed off
separately as described in [docs/ownership.md](docs/ownership.md).

## Workspace

```text
apps/web                 Next.js, React, TypeScript, Tailwind
apps/api                 FastAPI, SQLAlchemy, Alembic
packages/api-client      generated OpenAPI client boundary
infra                    local infrastructure support
docs                     decisions and team ownership
```

PostgreSQL is the source of truth. Redis and MinIO are defined as optional local services but are not
activated by application code in this scaffold.

## Prerequisites

- Node.js 24
- pnpm 11.7
- Python 3.12
- Docker-compatible runtime (optional until database work starts)

## Setup on Windows

```powershell
./scripts/bootstrap.ps1
./.venv/Scripts/Activate.ps1
pnpm dev
```

Manual setup:

```powershell
pnpm install --frozen-lockfile
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r apps/api/requirements.lock
./.venv/Scripts/python.exe -m pip install --no-deps -e apps/api
Copy-Item apps/web/.env.example apps/web/.env.local
Copy-Item apps/api/.env.example apps/api/.env
```

Open the web application at `http://localhost:3000` and the API documentation at
`http://localhost:8000/docs`.

## Local infrastructure

Start PostgreSQL when Docker is available:

```powershell
docker compose up -d postgres
```

Start PostgreSQL, Redis, and MinIO together:

```powershell
docker compose --profile extended up -d
```

The API starts without PostgreSQL while `DATABASE_CHECK_ON_STARTUP=false`. Liveness remains available
at `/health`; versioned health and readiness are exposed under `/api/v1/health`.

## Quality commands

Activate `.venv` first, then run:

```powershell
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
pnpm build
pnpm check
```

The complete Windows validation can also be run through:

```powershell
./scripts/check.ps1
```

## API contract

Generate the OpenAPI document for the future typed client:

```powershell
pnpm api:openapi
pnpm api:types
pnpm api:check
```

Contract documentation:

- [Application contract architecture](docs/contracts/application-contracts.md)
- [API conventions](docs/contracts/api-conventions.md)
- [Endpoint catalogue](docs/contracts/endpoint-catalogue.md)
- [Workflow rules](docs/contracts/workflow-rules.md)
- [KPI definitions](docs/contracts/kpi-definitions.md)

Handled API errors use this shape:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable explanation",
  "details": {},
  "request_id": "request-correlation-id"
}
```

## Troubleshooting

- If `pnpm dev:api` cannot find Python packages, activate `.venv` first.
- If readiness returns `503`, start PostgreSQL or disable the database readiness check locally.
- Docker is not required for frontend/API liveness development.
- Never commit `.env`, `.env.local`, tokens, or production credentials.
