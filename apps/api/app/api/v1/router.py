from fastapi import APIRouter

from app.api.v1 import auth, drivers, finance, health, maintenance, organizations, trips, vehicles

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(organizations.router)
router.include_router(vehicles.router)
router.include_router(drivers.router)
router.include_router(trips.router)
router.include_router(maintenance.router)
router.include_router(finance.router)
