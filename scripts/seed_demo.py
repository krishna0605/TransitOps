"""Seed demo data into the TransitOps Postgres DB.

Idempotent: deletes existing child->parent rows (except roles) and reseeds.
Run with:
  PYTHONPATH="apps/api" .venv/Scripts/python.exe scripts/seed_demo.py

Volume is scaled up (12 vehicles, 9 drivers, ~45 trips, ~45 fuel logs,
~45 maintenance logs, ~50 expenses) with all dates spread across the last
~3 months (2026-04-15 .. 2026-07-12) so Screen 7 analytics plots multiple
months. Generation is deterministic (fixed RNG seed) so re-runs are stable.
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone

from pwdlib import PasswordHash
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.models.driver import Driver
from app.db.models.expense import Expense
from app.db.models.fuel_log import FuelLog
from app.db.models.maintenance_log import MaintenanceLog
from app.db.models.role import Role
from app.db.models.trip import Trip
from app.db.models.user import User
from app.db.models.vehicle import Vehicle

DATABASE_URL = "postgresql+psycopg://transitops:transitops@localhost:5432/transitops"

# --- Date window for analytics spread (last ~3 months) ---
WINDOW_START = date(2026, 4, 15)
WINDOW_END = date(2026, 7, 12)
WINDOW_DAYS = (WINDOW_END - WINDOW_START).days  # 88

# Deterministic RNG so re-runs produce identical data.
rng = random.Random(20260712)

ROUTES = [
    ("Mumbai", "Pune", 150),
    ("Pune", "Nashik", 210),
    ("Mumbai", "Nashik", 165),
    ("Mumbai", "Surat", 280),
    ("Pune", "Nagpur", 710),
    ("Nashik", "Aurangabad", 190),
    ("Mumbai", "Ahmedabad", 530),
    ("Pune", "Kolhapur", 235),
    ("Thane", "Lonavala", 80),
    ("Mumbai", "Vadodara", 420),
    ("Nagpur", "Amravati", 155),
    ("Surat", "Rajkot", 250),
]

SERVICE_TYPES = [
    "Brake pad replacement", "Engine oil change", "Tyre rotation",
    "Clutch overhaul", "Air filter replacement", "Suspension repair",
    "Battery replacement", "Coolant flush", "Gearbox service",
    "Wheel alignment", "AC compressor repair", "Wiring harness fix",
]


def utc(d: date, hh: int = 0, mm: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=timezone.utc)


def rand_day(max_offset: int = WINDOW_DAYS) -> date:
    """A random day within the analytics window."""
    return WINDOW_START + timedelta(days=rng.randint(0, max_offset))


def main() -> None:
    engine = create_engine(DATABASE_URL)
    hasher = PasswordHash.recommended()
    pw_hash = hasher.hash("Test1234!")

    with Session(engine) as session:
        # --- Idempotent cleanup: child -> parent, never touch roles ---
        for model in (Expense, FuelLog, MaintenanceLog, Trip, User, Vehicle, Driver):
            session.query(model).delete()
        session.flush()

        # --- Roles lookup (already seeded) ---
        roles = {r.role_name: r.role_id for r in session.scalars(select(Role)).all()}

        # --- 1. Users (one per role) -- KEEP EXACTLY: real auth depends on these ---
        users = [
            User(name="Fatima Sheikh", email="fleet.manager@transitops.test",
                 password_hash=pw_hash, role_id=roles["Fleet Manager"]),
            User(name="Dan Ortiz", email="dispatcher@transitops.test",
                 password_hash=pw_hash, role_id=roles["Dispatcher"]),
            User(name="Sara Khan", email="safety.officer@transitops.test",
                 password_hash=pw_hash, role_id=roles["Safety Officer"]),
            User(name="Farhan Ali", email="financial.analyst@transitops.test",
                 password_hash=pw_hash, role_id=roles["Financial Analyst"]),
        ]
        session.add_all(users)
        session.flush()
        dispatcher = users[1]

        # --- 2. Vehicles (12; every status covered) ---
        v_avail = Vehicle(reg_no="MH12AB1234", name_model="Tata Ace Gold", type="Mini",
                          max_capacity_kg=750, odometer=42000, acquisition_cost=550000,
                          status="Available")
        v_ontrip = Vehicle(reg_no="MH14CD5678", name_model="Ashok Leyland Dost", type="Van",
                           max_capacity_kg=1500, odometer=88500, acquisition_cost=920000,
                           status="On Trip")
        v_shop = Vehicle(reg_no="MH04EF9012", name_model="Eicher Pro 2049", type="Truck",
                         max_capacity_kg=5000, odometer=134200, acquisition_cost=1850000,
                         status="In Shop")
        v_retired = Vehicle(reg_no="MH01GH3456", name_model="Mahindra Bolero Pik-Up", type="Van",
                            max_capacity_kg=1200, odometer=210500, acquisition_cost=780000,
                            status="Retired")
        v_avail2 = Vehicle(reg_no="MH12JK7890", name_model="Tata 407", type="Truck",
                           max_capacity_kg=2500, odometer=65300, acquisition_cost=1100000,
                           status="Available")
        # Extra fleet for volume (status spread preserved across the whole set).
        v_extra = [
            Vehicle(reg_no="MH12LM2345", name_model="Tata Intra V30", type="Mini",
                    max_capacity_kg=1000, odometer=31000, acquisition_cost=720000,
                    status="Available"),
            Vehicle(reg_no="MH14NO6789", name_model="Mahindra Furio 7", type="Truck",
                    max_capacity_kg=4200, odometer=98700, acquisition_cost=1650000,
                    status="Available"),
            Vehicle(reg_no="MH02PQ1122", name_model="Ashok Leyland Bada Dost", type="Van",
                    max_capacity_kg=1700, odometer=54600, acquisition_cost=980000,
                    status="On Trip"),
            Vehicle(reg_no="MH03RS3344", name_model="Eicher Pro 3015", type="Truck",
                    max_capacity_kg=6000, odometer=121000, acquisition_cost=2100000,
                    status="Available"),
            Vehicle(reg_no="MH05TU5566", name_model="Force Traveller Delivery", type="Van",
                    max_capacity_kg=1350, odometer=76200, acquisition_cost=890000,
                    status="In Shop"),
            Vehicle(reg_no="MH06VW7788", name_model="Tata Yodha Pik-Up", type="Mini",
                    max_capacity_kg=850, odometer=47800, acquisition_cost=610000,
                    status="Available"),
            Vehicle(reg_no="MH07XY9900", name_model="Mahindra Jeeto", type="Mini",
                    max_capacity_kg=700, odometer=198400, acquisition_cost=480000,
                    status="Retired"),
        ]
        vehicles = [v_avail, v_ontrip, v_shop, v_retired, v_avail2, *v_extra]
        session.add_all(vehicles)
        session.flush()
        # Vehicles usable for new trips (exclude Retired / In Shop).
        active_vehicles = [v for v in vehicles if v.status in ("Available", "On Trip")]

        # --- 3. Drivers (9; keep expired + suspended edge cases) ---
        d_expired = Driver(name="Ravi Kumar", license_no="DLLMV2019001", license_category="LMV",
                           license_expiry=date(2025, 1, 15), contact="+91-9876500001",
                           safety_score=72.0, status="Available")
        d_suspended = Driver(name="Imran Shaikh", license_no="DLHMV2021002", license_category="HMV",
                             license_expiry=date(2027, 8, 30), contact="+91-9876500002",
                             safety_score=61.0, status="Suspended")
        d_valid1 = Driver(name="Priya Nair", license_no="DLLMV2023003", license_category="LMV",
                          license_expiry=date(2028, 5, 20), contact="+91-9876500003",
                          safety_score=96.5, status="Available")
        d_valid2 = Driver(name="Suresh Patil", license_no="DLHMV2022004", license_category="HMV",
                          license_expiry=date(2029, 11, 10), contact="+91-9876500004",
                          safety_score=88.0, status="On Trip")
        d_extra = [
            Driver(name="Anjali Deshmukh", license_no="DLLMV2020005", license_category="LMV",
                   license_expiry=date(2026, 12, 5), contact="+91-9876500005",
                   safety_score=83.5, status="Available"),
            Driver(name="Vikram Rao", license_no="DLHMV2019006", license_category="HMV",
                   license_expiry=date(2027, 3, 18), contact="+91-9876500006",
                   safety_score=90.0, status="Available"),
            Driver(name="Neha Gupta", license_no="DLLMV2024007", license_category="LMV",
                   license_expiry=date(2029, 6, 25), contact="+91-9876500007",
                   safety_score=94.0, status="Off Duty"),
            Driver(name="Arjun Mehta", license_no="DLHMV2023008", license_category="HMV",
                   license_expiry=date(2028, 9, 12), contact="+91-9876500008",
                   safety_score=78.5, status="Available"),
            Driver(name="Kiran Joshi", license_no="DLHMV2021009", license_category="HMV",
                   license_expiry=date(2030, 2, 28), contact="+91-9876500009",
                   safety_score=85.0, status="On Trip"),
        ]
        drivers = [d_expired, d_suspended, d_valid1, d_valid2, *d_extra]
        session.add_all(drivers)
        session.flush()
        # Drivers eligible to be assigned to new trips (valid license, not suspended).
        active_drivers = [d_valid1, d_valid2, *d_extra]

        # --- 4. Trips (explicit status coverage + generated volume, ~45 total) ---
        # The four explicit trips preserve every status AND anchor the demo
        # attribution chain (t_completed carries fuel + maintenance + expense).
        t_completed = Trip(
            source="Mumbai", destination="Pune", vehicle_id=v_avail.vehicle_id,
            driver_id=d_valid1.driver_id, dispatched_by=dispatcher.user_id,
            cargo_weight_kg=600, planned_distance_km=150, final_odometer=42160,
            status="Completed", dispatched_at=utc(date(2026, 7, 8), 6, 30),
            completed_at=utc(date(2026, 7, 8), 12, 15),
        )
        t_dispatched = Trip(
            source="Mumbai", destination="Nashik", vehicle_id=v_ontrip.vehicle_id,
            driver_id=d_valid2.driver_id, dispatched_by=dispatcher.user_id,
            cargo_weight_kg=1300, planned_distance_km=165, final_odometer=None,
            status="Dispatched", dispatched_at=utc(date(2026, 7, 12), 5, 45),
            completed_at=None,
        )
        t_draft = Trip(
            source="Pune", destination="Nagpur", vehicle_id=v_avail2.vehicle_id,
            driver_id=d_valid1.driver_id, dispatched_by=None,
            cargo_weight_kg=2000, planned_distance_km=710, final_odometer=None,
            status="Draft", dispatched_at=None, completed_at=None,
        )
        t_cancelled = Trip(
            source="Mumbai", destination="Surat", vehicle_id=v_avail2.vehicle_id,
            driver_id=d_valid2.driver_id, dispatched_by=dispatcher.user_id,
            cargo_weight_kg=1800, planned_distance_km=280, final_odometer=None,
            status="Cancelled", dispatched_at=None, completed_at=None,
        )
        trips = [t_completed, t_dispatched, t_draft, t_cancelled]

        # Generated trips: weighted toward Completed/Dispatched for chart volume.
        gen_statuses = (["Completed"] * 24 + ["Dispatched"] * 11
                        + ["Draft"] * 3 + ["Cancelled"] * 3)  # 41 -> 45 total
        rng.shuffle(gen_statuses)
        for status in gen_statuses:
            src, dst, dist = rng.choice(ROUTES)
            veh = rng.choice(active_vehicles)
            drv = rng.choice(active_drivers)
            cargo = float(rng.randint(300, int(veh.max_capacity_kg)))
            dispatched_at = completed_at = None
            final_odo = None
            dispatched_by = None
            if status in ("Completed", "Dispatched"):
                # Keep a little room so Completed's completed_at stays in-window.
                day = rand_day(WINDOW_DAYS - 1)
                dispatched_at = utc(day, rng.randint(4, 11), rng.choice((0, 15, 30, 45)))
                dispatched_by = dispatcher.user_id
                if status == "Completed":
                    completed_at = dispatched_at + timedelta(hours=rng.randint(4, 10))
                    final_odo = veh.odometer + int(dist) + rng.randint(5, 120)
            elif status == "Cancelled":
                dispatched_by = dispatcher.user_id
            trips.append(Trip(
                source=src, destination=dst, vehicle_id=veh.vehicle_id,
                driver_id=drv.driver_id, dispatched_by=dispatched_by,
                cargo_weight_kg=cargo, planned_distance_km=float(dist),
                final_odometer=final_odo, status=status,
                dispatched_at=dispatched_at, completed_at=completed_at,
            ))
        session.add_all(trips)
        session.flush()

        # Trips that actually ran (usable for fuel/maintenance/expense linking).
        active_trips = [t for t in trips if t.dispatched_at is not None]
        completed_trips = [t for t in trips if t.status == "Completed"]

        # --- 5. Fuel logs (~45; roughly half trip-linked, rest depot fills) ---
        fuels = [
            # Explicit demo fuel on the star Completed trip.
            FuelLog(vehicle_id=v_avail.vehicle_id, trip_id=t_completed.trip_id,
                    fuel_date=date(2026, 7, 8), liters=28.5, cost=2565.0),
            FuelLog(vehicle_id=v_ontrip.vehicle_id, trip_id=t_dispatched.trip_id,
                    fuel_date=date(2026, 7, 12), liters=45.0, cost=4050.0),
        ]
        for _ in range(43):
            if active_trips and rng.random() < 0.5:
                trip = rng.choice(active_trips)
                veh_id = trip.vehicle_id
                trip_id = trip.trip_id
                fdate = trip.dispatched_at.date()
            else:
                veh_id = rng.choice(vehicles).vehicle_id
                trip_id = None
                fdate = rand_day()
            liters = round(rng.uniform(20.0, 70.0), 1)
            cost = round(liters * rng.uniform(88.0, 96.0), 1)
            fuels.append(FuelLog(vehicle_id=veh_id, trip_id=trip_id,
                                 fuel_date=fdate, liters=liters, cost=cost))
        session.add_all(fuels)
        session.flush()

        # --- 6. Maintenance logs (~45; some trip-linked; Active/Completed mix) ---
        # Trip-linked maintenance on the star trip -> drives the auto-linked expense.
        m_trip = MaintenanceLog(
            vehicle_id=v_avail.vehicle_id, trip_id=t_completed.trip_id,
            service_type="Brake pad replacement", cost=3200.0,
            service_date=date(2026, 7, 8), status="Completed",
        )
        # Active maintenance matching the In Shop vehicle.
        m_active = MaintenanceLog(
            vehicle_id=v_shop.vehicle_id, trip_id=None,
            service_type="Engine overhaul", cost=45000.0,
            service_date=date(2026, 7, 11), status="Active",
        )
        maints = [m_trip, m_active]
        # Track (maintenance, trip) pairs that should auto-post a Maintenance expense.
        auto_link_targets: list[tuple[MaintenanceLog, Trip]] = [(m_trip, t_completed)]
        for _ in range(43):
            if completed_trips and rng.random() < 0.4:
                trip = rng.choice(completed_trips)
                veh_id = trip.vehicle_id
                trip_id = trip.trip_id
                mdate = trip.dispatched_at.date()
                status = "Completed"
            else:
                veh_id = rng.choice(vehicles).vehicle_id
                trip_id = None
                mdate = rand_day()
                status = "Completed" if rng.random() < 0.7 else "Active"
            cost = round(rng.uniform(800.0, 48000.0), 1)
            m = MaintenanceLog(
                vehicle_id=veh_id, trip_id=trip_id,
                service_type=rng.choice(SERVICE_TYPES), cost=cost,
                service_date=mdate, status=status,
            )
            maints.append(m)
            # A fraction of trip-linked completed jobs auto-post a maintenance expense.
            if trip_id is not None and status == "Completed" and rng.random() < 0.5:
                auto_link_targets.append((m, trip))
        session.add_all(maints)
        session.flush()

        # --- 7. Expenses (~50; Toll/Maintenance/Other; auto-linked maint expenses) ---
        expenses: list[Expense] = []
        # Auto-linked maintenance expenses: trip_id + maintenance_id BOTH set (1:1).
        for m, trip in auto_link_targets:
            expenses.append(Expense(
                vehicle_id=m.vehicle_id, trip_id=trip.trip_id,
                maintenance_id=m.maintenance_id, category="Maintenance",
                amount=m.cost, status="Completed",
            ))
        # Tolls attributed to trips that ran.
        for trip in active_trips:
            if rng.random() < 0.7:
                expenses.append(Expense(
                    vehicle_id=trip.vehicle_id, trip_id=trip.trip_id,
                    maintenance_id=None, category="Toll",
                    amount=round(rng.uniform(80.0, 650.0), 1),
                    status="Completed" if trip.status == "Completed" else "Available",
                ))
        # Vehicle-only maintenance-category expenses (not auto-linked).
        for _ in range(6):
            expenses.append(Expense(
                vehicle_id=rng.choice(vehicles).vehicle_id, trip_id=None,
                maintenance_id=None, category="Maintenance",
                amount=round(rng.uniform(1500.0, 46000.0), 1), status="Available",
            ))
        # Misc "Other" expenses.
        for _ in range(8):
            expenses.append(Expense(
                vehicle_id=rng.choice(vehicles).vehicle_id, trip_id=None,
                maintenance_id=None, category="Other",
                amount=round(rng.uniform(200.0, 3000.0), 1),
                status="Completed" if rng.random() < 0.5 else "Available",
            ))
        session.add_all(expenses)
        session.flush()

        session.commit()

        # --- Summary ---
        def count(model) -> int:
            return session.scalar(select(func.count()).select_from(model))

        print("=== Seed complete: row counts ===")
        for label, model in (
            ("role (untouched)", Role), ("user", User), ("vehicle", Vehicle),
            ("driver", Driver), ("trip", Trip), ("fuel_log", FuelLog),
            ("maintenance_log", MaintenanceLog), ("expense", Expense),
        ):
            print(f"  {label:20s}: {count(model)}")

        print("\n=== Key demo references ===")
        print(f"  Completed trip_id (linked fuel+maint+expense): {t_completed.trip_id}")
        print(f"  Dispatched trip_id: {t_dispatched.trip_id}")
        print(f"  Draft trip_id: {t_draft.trip_id}")
        print(f"  Cancelled trip_id: {t_cancelled.trip_id}")
        print(f"  Trip-linked maintenance_id: {m_trip.maintenance_id} (status Completed)")
        print(f"  Active maintenance_id: {m_active.maintenance_id} (In Shop vehicle {v_shop.reg_no})")
        auto_exp = next(e for e in expenses if e.maintenance_id == m_trip.maintenance_id)
        print(f"  Auto-linked expense_id: {auto_exp.expense_id} "
              f"(trip {auto_exp.trip_id}, maintenance {auto_exp.maintenance_id})")
        n_auto = sum(1 for e in expenses if e.maintenance_id is not None)
        print(f"  Total auto-linked maintenance expenses (trip_id+maintenance_id): {n_auto}")
        print(f"  In Shop vehicle: {v_shop.reg_no} (id {v_shop.vehicle_id})")
        print(f"  Retired vehicle: {v_retired.reg_no} (id {v_retired.vehicle_id})")
        print(f"  Expired-license driver: {d_expired.name} (id {d_expired.driver_id})")
        print(f"  Suspended driver: {d_suspended.name} (id {d_suspended.driver_id})")

        # Date-range diagnostics (analytics spread).
        tmin = session.scalar(select(func.min(Trip.dispatched_at)))
        tmax = session.scalar(select(func.max(Trip.completed_at)))
        fmin = session.scalar(select(func.min(FuelLog.fuel_date)))
        fmax = session.scalar(select(func.max(FuelLog.fuel_date)))
        print("\n=== Date spread (for Screen 7 analytics) ===")
        print(f"  trip dispatched_at .. completed_at: {tmin} .. {tmax}")
        print(f"  fuel_date range: {fmin} .. {fmax}")


if __name__ == "__main__":
    main()
