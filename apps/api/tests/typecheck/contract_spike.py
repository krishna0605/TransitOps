"""Static-only protocol spike checked by mypy; this module is not executed by pytest."""

from typing import assert_type
from uuid import UUID

from app.contracts.dto.vehicles import VehicleRead
from app.contracts.repositories.vehicles import VehicleRepository


async def service_probe(repository: VehicleRepository, vehicle_id: UUID) -> VehicleRead | None:
    vehicle = await repository.get_by_id(vehicle_id)
    assert_type(vehicle, VehicleRead | None)
    return vehicle
