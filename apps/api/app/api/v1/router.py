from fastapi import APIRouter

from app.api.v1 import drivers, health, vehicles

router = APIRouter()
router.include_router(health.router)
router.include_router(vehicles.router)
router.include_router(drivers.router)
