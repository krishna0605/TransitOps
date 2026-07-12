"""initial schema

Creates the full TransitOps domain schema (role, user, vehicle, driver, trip,
maintenance_log, fuel_log, expense) with unique/foreign-key/check constraints and
indexes, then seeds the four fixed RBAC roles.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE_NAMES = ("Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst")


def upgrade() -> None:
    op.create_table(
        "role",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("role_name", sa.String(), nullable=False),
        sa.CheckConstraint(
            "role_name IN ('Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst')",
            name=op.f("ck_role_role_name_valid"),
        ),
        sa.PrimaryKeyConstraint("role_id", name=op.f("pk_role")),
        sa.UniqueConstraint("role_name", name=op.f("uq_role_role_name")),
    )

    op.create_table(
        "vehicle",
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("reg_no", sa.String(), nullable=False),
        sa.Column("name_model", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("max_capacity_kg", sa.Float(), nullable=False),
        sa.Column("odometer", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("acquisition_cost", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), server_default=sa.text("'Available'"), nullable=False),
        sa.CheckConstraint("type IN ('Van', 'Truck', 'Mini')", name=op.f("ck_vehicle_type_valid")),
        sa.CheckConstraint(
            "status IN ('Available', 'On Trip', 'In Shop', 'Retired')",
            name=op.f("ck_vehicle_status_valid"),
        ),
        sa.PrimaryKeyConstraint("vehicle_id", name=op.f("pk_vehicle")),
        sa.UniqueConstraint("reg_no", name=op.f("uq_vehicle_reg_no")),
    )
    op.create_index(op.f("ix_vehicle_status"), "vehicle", ["status"], unique=False)

    op.create_table(
        "driver",
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("license_no", sa.String(), nullable=False),
        sa.Column("license_category", sa.String(), nullable=False),
        sa.Column("license_expiry", sa.Date(), nullable=False),
        sa.Column("contact", sa.String(), nullable=False),
        sa.Column("safety_score", sa.Float(), server_default=sa.text("100"), nullable=False),
        sa.Column("status", sa.String(), server_default=sa.text("'Available'"), nullable=False),
        sa.CheckConstraint(
            "license_category IN ('LMV', 'HMV')", name=op.f("ck_driver_license_category_valid")
        ),
        sa.CheckConstraint(
            "status IN ('Available', 'On Trip', 'Off Duty', 'Suspended')",
            name=op.f("ck_driver_status_valid"),
        ),
        sa.PrimaryKeyConstraint("driver_id", name=op.f("pk_driver")),
        sa.UniqueConstraint("license_no", name=op.f("uq_driver_license_no")),
    )
    op.create_index(op.f("ix_driver_status"), "driver", ["status"], unique=False)

    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["role.role_id"], name=op.f("fk_user_role_id_role")),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user")),
        sa.UniqueConstraint("email", name=op.f("uq_user_email")),
    )
    op.create_index(op.f("ix_user_role_id"), "user", ["role_id"], unique=False)

    op.create_table(
        "trip",
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("destination", sa.String(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("dispatched_by", sa.Integer(), nullable=True),
        sa.Column("cargo_weight_kg", sa.Float(), nullable=False),
        sa.Column("planned_distance_km", sa.Float(), nullable=False),
        sa.Column("final_odometer", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), server_default=sa.text("'Draft'"), nullable=False),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('Draft', 'Dispatched', 'Completed', 'Cancelled')",
            name=op.f("ck_trip_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"], ["vehicle.vehicle_id"], name=op.f("fk_trip_vehicle_id_vehicle")
        ),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["driver.driver_id"], name=op.f("fk_trip_driver_id_driver")
        ),
        sa.ForeignKeyConstraint(
            ["dispatched_by"], ["user.user_id"], name=op.f("fk_trip_dispatched_by_user")
        ),
        sa.PrimaryKeyConstraint("trip_id", name=op.f("pk_trip")),
    )
    op.create_index(op.f("ix_trip_vehicle_id"), "trip", ["vehicle_id"], unique=False)
    op.create_index(op.f("ix_trip_driver_id"), "trip", ["driver_id"], unique=False)
    op.create_index(op.f("ix_trip_dispatched_by"), "trip", ["dispatched_by"], unique=False)
    op.create_index(op.f("ix_trip_status"), "trip", ["status"], unique=False)

    op.create_table(
        "maintenance_log",
        sa.Column("maintenance_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("service_type", sa.String(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.CheckConstraint(
            "status IN ('Active', 'Completed')", name=op.f("ck_maintenance_log_status_valid")
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.vehicle_id"],
            name=op.f("fk_maintenance_log_vehicle_id_vehicle"),
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"], ["trip.trip_id"], name=op.f("fk_maintenance_log_trip_id_trip")
        ),
        sa.PrimaryKeyConstraint("maintenance_id", name=op.f("pk_maintenance_log")),
    )
    op.create_index(
        op.f("ix_maintenance_log_vehicle_id"), "maintenance_log", ["vehicle_id"], unique=False
    )
    op.create_index(
        op.f("ix_maintenance_log_trip_id"), "maintenance_log", ["trip_id"], unique=False
    )
    op.create_index(op.f("ix_maintenance_log_status"), "maintenance_log", ["status"], unique=False)

    op.create_table(
        "fuel_log",
        sa.Column("fuel_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("fuel_date", sa.Date(), nullable=False),
        sa.Column("liters", sa.Float(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["vehicle_id"], ["vehicle.vehicle_id"], name=op.f("fk_fuel_log_vehicle_id_vehicle")
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"], ["trip.trip_id"], name=op.f("fk_fuel_log_trip_id_trip")
        ),
        sa.PrimaryKeyConstraint("fuel_id", name=op.f("pk_fuel_log")),
    )
    op.create_index(op.f("ix_fuel_log_vehicle_id"), "fuel_log", ["vehicle_id"], unique=False)
    op.create_index(op.f("ix_fuel_log_trip_id"), "fuel_log", ["trip_id"], unique=False)

    op.create_table(
        "expense",
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("maintenance_id", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), server_default=sa.text("'Available'"), nullable=False),
        sa.CheckConstraint(
            "category IN ('Toll', 'Maintenance', 'Other')", name=op.f("ck_expense_category_valid")
        ),
        sa.CheckConstraint(
            "status IN ('Available', 'Completed')", name=op.f("ck_expense_status_valid")
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"], ["vehicle.vehicle_id"], name=op.f("fk_expense_vehicle_id_vehicle")
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"], ["trip.trip_id"], name=op.f("fk_expense_trip_id_trip")
        ),
        sa.ForeignKeyConstraint(
            ["maintenance_id"],
            ["maintenance_log.maintenance_id"],
            name=op.f("fk_expense_maintenance_id_maintenance_log"),
        ),
        sa.PrimaryKeyConstraint("expense_id", name=op.f("pk_expense")),
        sa.UniqueConstraint("maintenance_id", name=op.f("uq_expense_maintenance_id")),
    )
    op.create_index(op.f("ix_expense_vehicle_id"), "expense", ["vehicle_id"], unique=False)
    op.create_index(op.f("ix_expense_trip_id"), "expense", ["trip_id"], unique=False)
    op.create_index(op.f("ix_expense_category"), "expense", ["category"], unique=False)

    # Seed the four fixed RBAC roles (ER schema / Screen 8 permission matrix).
    op.bulk_insert(
        sa.table("role", sa.column("role_name", sa.String())),
        [{"role_name": name} for name in ROLE_NAMES],
    )


def downgrade() -> None:
    # Reverse dependency order; dropping a table also drops its indexes/constraints.
    op.drop_table("expense")
    op.drop_table("fuel_log")
    op.drop_table("maintenance_log")
    op.drop_table("trip")
    op.drop_table("user")
    op.drop_table("driver")
    op.drop_table("vehicle")
    op.drop_table("role")
