# TransitOps Endpoint Catalogue

This catalogue records intended application contracts. Only routes mounted in FastAPI are part of the
runtime OpenAPI document. Planned routes are not implemented as placeholder `501` endpoints.

| Method | Path                                  | Permission                 | Request                     | Response                      | Success | Idempotent              | Transaction |
| ------ | ------------------------------------- | -------------------------- | --------------------------- | ----------------------------- | ------: | ----------------------- | ----------- |
| POST   | `/auth/login`                         | Public                     | `LoginRequest`              | `TokenResponse`               |     200 | No                      | Yes         |
| POST   | `/auth/refresh`                       | Public/session             | Cookie                      | `TokenResponse`               |     200 | Rotation-safe           | Yes         |
| POST   | `/auth/logout`                        | Authenticated              | Cookie                      | None                          |     204 | Yes                     | Yes         |
| GET    | `/auth/me`                            | Authenticated              | None                        | `CurrentUserResponse`         |     200 | Yes                     | No          |
| GET    | `/vehicles`                           | `vehicle:view`             | `VehicleFilters`            | `Page[VehicleSummary]`        |     200 | Yes                     | No          |
| POST   | `/vehicles`                           | `vehicle:create`           | `VehicleCreate`             | `VehicleRead`                 |     201 | No                      | Yes         |
| GET    | `/vehicles/{id}`                      | `vehicle:view`             | None                        | `VehicleRead`                 |     200 | Yes                     | No          |
| PATCH  | `/vehicles/{id}`                      | `vehicle:update`           | `VehicleUpdate`             | `VehicleRead`                 |     200 | No                      | Yes         |
| POST   | `/vehicles/{id}/retire`               | `vehicle:retire`           | Version/reason              | `VehicleRead`                 |     200 | Required                | Yes         |
| POST   | `/vehicles/{id}/odometer-corrections` | `vehicle:correct_odometer` | `OdometerCorrectionRequest` | `VehicleRead`                 |     200 | Required                | Yes         |
| GET    | `/drivers`                            | `driver:view`              | `DriverFilters`             | `Page[DriverSummary]`         |     200 | Yes                     | No          |
| POST   | `/drivers`                            | `driver:create`            | `DriverCreate`              | `DriverRead`                  |     201 | No                      | Yes         |
| GET    | `/drivers/{id}`                       | `driver:view`              | None                        | `DriverRead`                  |     200 | Yes                     | No          |
| PATCH  | `/drivers/{id}`                       | `driver:update`            | `DriverUpdate`              | `DriverRead`                  |     200 | No                      | Yes         |
| POST   | `/drivers/{id}/suspend`               | `driver:suspend`           | `DriverStatusChangeRequest` | `DriverRead`                  |     200 | Required                | Yes         |
| POST   | `/drivers/{id}/restore`               | `driver:restore`           | `DriverStatusChangeRequest` | `DriverRead`                  |     200 | Required                | Yes         |
| GET    | `/trips`                              | `trip:view`                | `TripFilters`               | `Page[TripSummary]`           |     200 | Yes                     | No          |
| POST   | `/trips`                              | `trip:create`              | `TripDraftCreate`           | `TripRead`                    |     201 | No                      | Yes         |
| GET    | `/trips/{id}`                         | `trip:view`                | None                        | `TripRead`                    |     200 | Yes                     | No          |
| PATCH  | `/trips/{id}`                         | `trip:update`              | `TripDraftUpdate`           | `TripRead`                    |     200 | No                      | Yes         |
| POST   | `/trips/{id}/dispatch`                | `trip:dispatch`            | `TripDispatchRequest`       | `TripRead`                    |     200 | Required                | Yes, atomic |
| POST   | `/trips/{id}/complete`                | `trip:complete`            | `TripCompletionRequest`     | `TripRead`                    |     200 | Required                | Yes, atomic |
| POST   | `/trips/{id}/cancel`                  | `trip:cancel`              | `TripCancellationRequest`   | `TripRead`                    |     200 | Required for dispatched | Yes, atomic |
| GET    | `/trips/{id}/history`                 | `trip:view`                | None                        | `Page[TripStatusHistoryRead]` |     200 | Yes                     | No          |
| GET    | `/maintenance`                        | `maintenance:view`         | `MaintenanceFilters`        | `Page[MaintenanceSummary]`    |     200 | Yes                     | No          |
| POST   | `/maintenance`                        | `maintenance:create`       | `MaintenanceCreate`         | `MaintenanceRead`             |     201 | Required                | Yes, atomic |
| GET    | `/maintenance/{id}`                   | `maintenance:view`         | None                        | `MaintenanceRead`             |     200 | Yes                     | No          |
| POST   | `/maintenance/{id}/close`             | `maintenance:close`        | `MaintenanceCloseRequest`   | `MaintenanceRead`             |     200 | Required                | Yes, atomic |
| GET    | `/fuel-logs`                          | `fuel:view`                | Filters                     | `Page[FuelLogRead]`           |     200 | Yes                     | No          |
| POST   | `/fuel-logs`                          | `fuel:create`              | `FuelLogCreate`             | `FuelLogRead`                 |     201 | No                      | Yes         |
| GET    | `/expenses`                           | `expense:view`             | `ExpenseFilters`            | `Page[ExpenseRead]`           |     200 | Yes                     | No          |
| POST   | `/expenses`                           | `expense:create`           | `ExpenseCreate`             | `ExpenseRead`                 |     201 | No                      | Yes         |
| POST   | `/expenses/{id}/review`               | `expense:approve`          | `ExpenseReviewRequest`      | `ExpenseRead`                 |     200 | Required                | Yes         |
| GET    | `/dashboard/kpis`                     | `report:view`              | `DashboardFilters`          | `DashboardKpiResponse`        |     200 | Yes                     | No          |
| GET    | `/reports/fleet-utilization`          | `report:view`              | `DashboardFilters`          | `FleetUtilizationResponse`    |     200 | Yes                     | No          |
| GET    | `/reports/fuel-efficiency`            | `report:view`              | `DashboardFilters`          | `FuelEfficiencyResponse`      |     200 | Yes                     | No          |
| GET    | `/reports/operational-cost`           | `report:view`              | `DashboardFilters`          | `OperationalCostResponse`     |     200 | Yes                     | No          |
| GET    | `/reports/vehicles/{id}/roi`          | `report:view`              | `DashboardFilters`          | `VehicleRoiResponse`          |     200 | Yes                     | No          |
| GET    | `/reports/trips/{id}/profitability`   | `report:view`              | None                        | `TripProfitabilityResponse`   |     200 | Yes                     | No          |
| POST   | `/reports/exports`                    | `report:export`            | `ReportExportRequest`       | Export status                 |     202 | Required                | Yes         |
| GET    | `/reports/exports/{id}`               | `report:export`            | None                        | Export status                 |     200 | Yes                     | No          |
| POST   | `/documents/upload-url`               | `document:create`          | File metadata               | `SignedUploadResponse`        |     200 | No                      | No          |
| POST   | `/documents`                          | `document:create`          | `DocumentCreate`            | `DocumentRead`                |     201 | Required                | Yes         |
| GET    | `/documents/{id}/download-url`        | `document:view`            | None                        | `SignedDownloadResponse`      |     200 | Yes                     | No          |
| DELETE | `/documents/{id}`                     | `document:delete`          | None                        | None                          |     204 | Yes                     | Yes         |
| GET    | `/notifications`                      | `notification:view`        | `NotificationFilters`       | `Page[NotificationRead]`      |     200 | Yes                     | No          |
| POST   | `/notifications/{id}/read`            | `notification:view`        | None                        | `NotificationRead`            |     200 | Yes                     | Yes         |
| GET    | `/audit-logs`                         | `audit:view`               | Filters                     | Paginated audit entries       |     200 | Yes                     | No          |

Common failures include `VALIDATION_ERROR`, `PERMISSION_DENIED`, `RESOURCE_NOT_FOUND`,
`RESOURCE_VERSION_CONFLICT`, `INVALID_STATE_TRANSITION`, and domain-specific conflict codes.
