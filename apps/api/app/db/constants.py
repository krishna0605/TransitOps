"""Canonical enumerated values shared by models, migrations, and API contracts.

These tuples are the single source of truth for the status/category/type domains
described in the ER schema. Models render them into CHECK constraints, and the
application layer can import the same tuples to validate input and build dropdowns,
guaranteeing the database and the API agree on the allowed values.
"""

ROLE_NAMES: tuple[str, ...] = (
    "Fleet Manager",
    "Dispatcher",
    "Safety Officer",
    "Financial Analyst",
)
VEHICLE_TYPES: tuple[str, ...] = ("Van", "Truck", "Mini")
VEHICLE_STATUSES: tuple[str, ...] = ("Available", "On Trip", "In Shop", "Retired")
DRIVER_STATUSES: tuple[str, ...] = ("Available", "On Trip", "Off Duty", "Suspended")
LICENSE_CATEGORIES: tuple[str, ...] = ("LMV", "HMV")
TRIP_STATUSES: tuple[str, ...] = ("Draft", "Dispatched", "Completed", "Cancelled")
MAINTENANCE_STATUSES: tuple[str, ...] = ("Active", "Completed")
EXPENSE_CATEGORIES: tuple[str, ...] = ("Toll", "Maintenance", "Other")
EXPENSE_STATUSES: tuple[str, ...] = ("Available", "Completed")


def in_check(column: str, values: tuple[str, ...]) -> str:
    """Render a SQL ``column IN ('a', 'b', ...)`` predicate for a CHECK constraint."""
    rendered = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({rendered})"
