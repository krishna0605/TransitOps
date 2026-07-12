# TransitOps API Conventions

## Versioning and naming

- Runtime endpoints use the `/api/v1` prefix.
- Resource paths use plural kebab-case nouns.
- JSON fields use snake_case.
- Internal identifiers are UUIDs serialized as strings.
- Trip and maintenance numbers are human-readable identifiers separate from primary keys.
- Generic update endpoints cannot alter workflow status.

Breaking changes require a new API version or an explicitly documented compatibility period. Adding an
optional field is normally backward compatible; removing or changing the meaning of a field is not.

## Dates, times, money, and measurements

- Timestamps are timezone-aware and normalized to UTC.
- Date-only values use `YYYY-MM-DD`.
- Money uses Python `Decimal` and JSON strings with a three-letter uppercase currency code.
- Distances and odometers use kilometres, cargo uses kilograms, and fuel uses litres.
- Unit-bearing fields include the unit in their name, such as `cargo_weight_kg`.

Example:

```json
{
  "amount": "1250.50",
  "currency": "INR",
  "current_odometer_km": "12500.125",
  "created_at": "2026-07-12T04:30:00Z"
}
```

## Pagination and filtering

List endpoints accept:

```text
page=1
page_size=25
search=<text>
sort_by=created_at
sort_order=desc
region_id=<uuid>
date_from=2026-07-01
date_to=2026-07-31
archived=false
```

- `page` is one-based.
- `page_size` is limited to 1–100.
- Sort fields use endpoint-specific allowlists.
- Arbitrary database columns are never accepted.
- Reverse date ranges fail validation.
- Archived records are excluded unless explicitly requested and permitted.

List response:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0
}
```

## Errors

Handled errors use one stable envelope:

```json
{
  "code": "VEHICLE_NOT_AVAILABLE",
  "message": "The selected vehicle is no longer available.",
  "details": {
    "current_state": "ON_TRIP"
  },
  "request_id": "..."
}
```

- Clients branch on `code`, not message text.
- Field-level validation data uses `details.fields`.
- Conflict context may use `details.current_state`.
- Database, stack-trace, credential, and token details are never returned.
- Every handled error includes the request correlation identifier.

## Status codes

| Status | Meaning                                                          |
| -----: | ---------------------------------------------------------------- |
|    200 | Successful read or action returning a resource                   |
|    201 | Resource created                                                 |
|    202 | Background job accepted                                          |
|    204 | Successful action without a body                                 |
|    400 | Malformed application request                                    |
|    401 | Authentication required or invalid                               |
|    403 | Authenticated but not permitted                                  |
|    404 | Resource not found or not visible to the caller                  |
|    409 | Uniqueness, state, version, idempotency, or concurrency conflict |
|    422 | Request validation failed                                        |
|    429 | Rate limit exceeded                                              |
|    500 | Unexpected internal failure                                      |
|    503 | Required dependency is unavailable                               |

## Optimistic concurrency

Mutable operational resources expose a positive integer `version`. Update requests submit the version
they read. A stale version returns `409 RESOURCE_VERSION_CONFLICT`; the server does not silently
overwrite newer data.

## Idempotency

The `Idempotency-Key` header is required later for trip dispatch, completion, dispatched cancellation,
maintenance transitions, and report exports.

- Length: 8–128 characters.
- Supported characters: letters, digits, `.`, `_`, `:`, and `-`.
- Same key and same request returns the original result.
- Same key with different request content returns `409 IDEMPOTENCY_CONFLICT`.
- GET requests do not use idempotency keys.
- State-changing clients do not retry automatically without idempotency protection.

## Client behavior

- Generated OpenAPI types are authoritative for implemented routes.
- The shared client uses an 8-second default timeout and supports cancellation.
- Credentials are included for the future HttpOnly refresh cookie.
- Access tokens are added through a token-provider callback rather than persisted by the client.
- Safe reads may receive a bounded retry at the application-query layer.
- Mutations require explicit user or workflow handling after failures.
