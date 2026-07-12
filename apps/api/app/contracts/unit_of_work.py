from types import TracebackType
from typing import Protocol, Self

from app.contracts.repositories import (
    DocumentRepository,
    DriverRepository,
    ExpenseRepository,
    FuelLogRepository,
    MaintenanceRepository,
    NotificationRepository,
    RefreshTokenRepository,
    ReportRepository,
    TripRepository,
    UserRepository,
    VehicleRepository,
)


class UnitOfWork(Protocol):
    users: UserRepository
    refresh_tokens: RefreshTokenRepository
    vehicles: VehicleRepository
    drivers: DriverRepository
    trips: TripRepository
    maintenance: MaintenanceRepository
    fuel_logs: FuelLogRepository
    expenses: ExpenseRepository
    documents: DocumentRepository
    notifications: NotificationRepository
    reports: ReportRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
