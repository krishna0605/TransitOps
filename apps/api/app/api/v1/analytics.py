from datetime import date, datetime, time
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import case, func, select

from app.api.auth import CurrentPrincipal
from app.api.dependencies import DatabaseSession
from app.db.models.expense import Expense
from app.db.models.fuel_log import FuelLog
from app.db.models.maintenance_log import MaintenanceLog
from app.db.models.trip import Trip
from app.db.models.vehicle import Vehicle

router = APIRouter(tags=["analytics"])


class DashboardSummary(BaseModel):
    total_vehicles: int
    available_vehicles: int
    in_maintenance: int
    active_trips: int
    completed_trips: int
    pending_expenses: int


class AnalyticsOverview(BaseModel):
    completed_trips: int
    total_distance_km: Decimal
    fuel_liters: Decimal
    fuel_cost: Decimal
    maintenance_cost: Decimal
    other_approved_cost: Decimal
    operational_cost: Decimal
    average_cost_per_trip: Decimal
    fleet_utilization_percent: Decimal
    fuel_efficiency_km_per_liter: Decimal


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(
    principal: CurrentPrincipal, session: DatabaseSession
) -> DashboardSummary:
    vehicle_counts = (
        await session.execute(
            select(
                func.count(Vehicle.id),
                func.sum(case((Vehicle.status == "AVAILABLE", 1), else_=0)),
                func.sum(case((Vehicle.status == "IN_SHOP", 1), else_=0)),
            ).where(
                Vehicle.organization_id == principal.organization_id, Vehicle.archived_at.is_(None)
            )
        )
    ).one()
    trip_counts = (
        await session.execute(
            select(
                func.sum(case((Trip.status == "DISPATCHED", 1), else_=0)),
                func.sum(case((Trip.status == "COMPLETED", 1), else_=0)),
            ).where(Trip.organization_id == principal.organization_id)
        )
    ).one()
    pending = await session.scalar(
        select(func.count(Expense.id)).where(
            Expense.organization_id == principal.organization_id, Expense.status == "PENDING"
        )
    )
    return DashboardSummary(
        total_vehicles=vehicle_counts[0] or 0,
        available_vehicles=vehicle_counts[1] or 0,
        in_maintenance=vehicle_counts[2] or 0,
        active_trips=trip_counts[0] or 0,
        completed_trips=trip_counts[1] or 0,
        pending_expenses=pending or 0,
    )


@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def analytics_overview(
    principal: CurrentPrincipal,
    session: DatabaseSession,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> AnalyticsOverview:
    trip_filters = [Trip.organization_id == principal.organization_id, Trip.status == "COMPLETED"]
    expense_filters = [
        Expense.organization_id == principal.organization_id,
        Expense.status == "APPROVED",
    ]
    fuel_filters = [FuelLog.organization_id == principal.organization_id]
    maintenance_filters = [MaintenanceLog.organization_id == principal.organization_id]
    if date_from:
        start = datetime.combine(date_from, time.min)
        trip_filters.append(Trip.completed_at >= start)
        expense_filters.append(Expense.created_at >= start)
        fuel_filters.append(FuelLog.fuel_date >= date_from)
        maintenance_filters.append(MaintenanceLog.service_date >= date_from)
    if date_to:
        end = datetime.combine(date_to, time.max)
        trip_filters.append(Trip.completed_at <= end)
        expense_filters.append(Expense.created_at <= end)
        fuel_filters.append(FuelLog.fuel_date <= date_to)
        maintenance_filters.append(MaintenanceLog.service_date <= date_to)

    completed, distance = (
        await session.execute(
            select(func.count(Trip.id), func.coalesce(func.sum(Trip.planned_distance_km), 0)).where(
                *trip_filters
            )
        )
    ).one()
    liters, fuel_cost = (
        await session.execute(
            select(
                func.coalesce(func.sum(FuelLog.liters), 0), func.coalesce(func.sum(FuelLog.cost), 0)
            ).where(*fuel_filters)
        )
    ).one()
    maintenance_cost = await session.scalar(
        select(func.coalesce(func.sum(MaintenanceLog.cost), 0)).where(*maintenance_filters)
    )
    total_approved = await session.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(*expense_filters)
    )
    other_cost = max(
        Decimal(total_approved or 0) - Decimal(fuel_cost or 0) - Decimal(maintenance_cost or 0),
        Decimal(0),
    )
    operational = Decimal(total_approved or 0)
    total_vehicles = await session.scalar(
        select(func.count(Vehicle.id)).where(
            Vehicle.organization_id == principal.organization_id, Vehicle.archived_at.is_(None)
        )
    )
    active_vehicles = await session.scalar(
        select(func.count(func.distinct(Trip.vehicle_id))).where(*trip_filters)
    )
    completed_count = int(completed or 0)
    liters_value = Decimal(liters or 0)
    distance_value = Decimal(distance or 0)
    return AnalyticsOverview(
        completed_trips=completed_count,
        total_distance_km=distance_value,
        fuel_liters=liters_value,
        fuel_cost=Decimal(fuel_cost or 0),
        maintenance_cost=Decimal(maintenance_cost or 0),
        other_approved_cost=other_cost,
        operational_cost=operational,
        average_cost_per_trip=operational / completed_count if completed_count else Decimal(0),
        fleet_utilization_percent=(Decimal(active_vehicles or 0) / Decimal(total_vehicles or 1))
        * 100,
        fuel_efficiency_km_per_liter=distance_value / liters_value if liters_value else Decimal(0),
    )
