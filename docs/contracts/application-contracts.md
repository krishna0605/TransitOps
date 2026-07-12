# TransitOps Application Contracts

## Purpose

The application contract layer defines stable vocabulary, validated data shapes, repository behavior,
and transaction ownership for TransitOps. It separates application services from database and HTTP
framework implementation details.

Phase 0 adds contracts and documentation only. It does not add operational routes, database models,
migrations, persistence queries, authentication behavior, or frontend business screens.

## System boundary

```mermaid
flowchart LR
    UI["Next.js UI"]
    Client["Generated TypeScript API Client"]
    Router["FastAPI Routers"]
    Service["Application Services"]
    Policy["Business Policies"]
    Contract["Repository and Unit-of-Work Contracts"]
    Persistence["Persistence Implementations"]
    DB[("PostgreSQL")]

    UI --> Client
    Client --> Router
    Router --> Service
    Service --> Policy
    Service --> Contract
    Contract -. "implemented by" .-> Persistence
    Persistence --> DB
```

## Request lifecycle

```mermaid
sequenceDiagram
    participant UI as Next.js UI
    participant Client as Typed API Client
    participant API as FastAPI Router
    participant Service as Application Service
    participant UoW as Unit of Work
    participant Repo as Repository Implementation
    participant DB as PostgreSQL

    UI->>Client: Validated form data
    Client->>API: Typed HTTP request
    API->>API: Pydantic validation
    API->>Service: Application command
    Service->>Service: Permission and business policy
    Service->>UoW: Begin transaction
    Service->>Repo: Contract method
    Repo->>DB: Query or mutation
    DB-->>Repo: Persistence result
    Repo-->>Service: Contract object
    Service->>UoW: Commit or rollback
    Service-->>API: Application result
    API-->>Client: Typed response
    Client-->>UI: Query cache update
```

## Dependency rules

```mermaid
flowchart TD
    Core["Core infrastructure"]
    Contracts["Application contracts"]
    Modules["Application modules"]
    API["API routers"]
    DB["Persistence layer"]

    API --> Modules
    Modules --> Contracts
    Modules --> Core
    DB --> Contracts
    DB --> Core

    Contracts -. "must not import" .-> DB
    Contracts -. "must not import" .-> API
```

The `app.contracts` package may import the Python standard library and Pydantic. It must not import
FastAPI, SQLAlchemy, Alembic, `app.api`, or `app.db`.

## Contract responsibilities

- DTOs define transport-neutral validated inputs and outputs.
- Repository protocols describe application-required behavior instead of generic CRUD.
- List methods accept typed filters and return typed pages.
- Explicit methods represent row-locking requirements.
- Repositories never expose sessions, SQL expressions, or ORM models.
- Repositories never commit transactions.
- Services explicitly commit successful workflows through the unit of work.
- Context exit rolls back unfinished or failed work.

## Unit-of-work lifecycle

```mermaid
sequenceDiagram
    participant Service
    participant UoW
    participant Repository
    participant Database

    Service->>UoW: async with uow
    UoW->>Database: begin transaction
    Service->>Repository: read/write through contract
    Repository->>Database: execute
    alt workflow succeeds
        Service->>UoW: commit()
        UoW->>Database: commit
    else workflow fails
        Service->>UoW: rollback()
        UoW->>Database: rollback
    end
```

Automatic commit on context exit is prohibited.

## Validation strategy

- Architecture tests reject forbidden imports.
- Strict mypy checks protocol compatibility.
- Fake repositories and a fake unit of work validate service-facing usability.
- Serialization tests cover UUID, decimal, datetime, date, and enum behavior.
- OpenAPI generation and TypeScript generation are checked for deterministic output.
