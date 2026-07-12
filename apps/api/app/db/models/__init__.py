"""Domain models for TransitOps.

Importing this package registers every table on ``Base.metadata`` and configures
the ORM mappers. Alembic's ``env.py`` imports it so autogenerate can see the full
schema, and application code can import the models from here.
"""

from app.db.base import Base
from app.db.models.driver import Driver
from app.db.models.expense import Expense
from app.db.models.fuel_log import FuelLog
from app.db.models.maintenance_log import MaintenanceLog
from app.db.models.role import Role
from app.db.models.trip import Trip
from app.db.models.user import User
from app.db.models.vehicle import Vehicle

__all__ = [
    "Base",
    "Driver",
    "Expense",
    "FuelLog",
    "MaintenanceLog",
    "Role",
    "Trip",
    "User",
    "Vehicle",
]
