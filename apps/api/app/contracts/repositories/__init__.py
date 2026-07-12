"""Asynchronous repository protocols consumed by application services."""

from app.contracts.repositories.documents import DocumentRepository
from app.contracts.repositories.drivers import DriverRepository
from app.contracts.repositories.expenses import ExpenseRepository
from app.contracts.repositories.fuel import FuelLogRepository
from app.contracts.repositories.maintenance import MaintenanceRepository
from app.contracts.repositories.notifications import NotificationRepository
from app.contracts.repositories.reports import ReportRepository
from app.contracts.repositories.trips import TripRepository
from app.contracts.repositories.users import RefreshTokenRepository, UserRepository
from app.contracts.repositories.vehicles import VehicleRepository

__all__ = [
    "DocumentRepository",
    "DriverRepository",
    "ExpenseRepository",
    "FuelLogRepository",
    "MaintenanceRepository",
    "NotificationRepository",
    "RefreshTokenRepository",
    "ReportRepository",
    "TripRepository",
    "UserRepository",
    "VehicleRepository",
]
