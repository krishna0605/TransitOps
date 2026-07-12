from fastapi import APIRouter

from app.api.v1 import drivers, finance, health, maintenance, trips, vehicles

router = APIRouter()
router.include_router(health.router)
router.include_router(vehicles.router)
router.include_router(drivers.router)
router.include_router(trips.router)
router.include_router(maintenance.router)
router.include_router(finance.router)
