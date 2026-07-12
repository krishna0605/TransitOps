from enum import StrEnum


class Permission(StrEnum):
    USER_MANAGE = "user:manage"
    ROLE_MANAGE = "role:manage"

    VEHICLE_VIEW = "vehicle:view"
    VEHICLE_CREATE = "vehicle:create"
    VEHICLE_UPDATE = "vehicle:update"
    VEHICLE_RETIRE = "vehicle:retire"
    VEHICLE_CORRECT_ODOMETER = "vehicle:correct_odometer"

    DRIVER_VIEW = "driver:view"
    DRIVER_CREATE = "driver:create"
    DRIVER_UPDATE = "driver:update"
    DRIVER_SUSPEND = "driver:suspend"
    DRIVER_RESTORE = "driver:restore"

    TRIP_VIEW = "trip:view"
    TRIP_CREATE = "trip:create"
    TRIP_UPDATE = "trip:update"
    TRIP_DISPATCH = "trip:dispatch"
    TRIP_COMPLETE = "trip:complete"
    TRIP_CANCEL = "trip:cancel"

    MAINTENANCE_VIEW = "maintenance:view"
    MAINTENANCE_CREATE = "maintenance:create"
    MAINTENANCE_CLOSE = "maintenance:close"

    FUEL_VIEW = "fuel:view"
    FUEL_CREATE = "fuel:create"

    EXPENSE_VIEW = "expense:view"
    EXPENSE_CREATE = "expense:create"
    EXPENSE_APPROVE = "expense:approve"

    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"

    DOCUMENT_VIEW = "document:view"
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_DELETE = "document:delete"

    NOTIFICATION_VIEW = "notification:view"
    AUDIT_VIEW = "audit:view"


ALL_PERMISSIONS = frozenset(Permission)
