"use client";

import { type components, unwrapApiResponse } from "@transitops/api-client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { transitOpsClient } from "@/lib/api/transitops-client";

type ApiVehicle = components["schemas"]["VehicleRead"];
type ApiDriver = components["schemas"]["DriverRead"];
type ApiTrip = components["schemas"]["TripRead"];
type ApiMaintenance = components["schemas"]["MaintenanceRead"];
type ApiFuel = components["schemas"]["FuelRead"];
type ApiExpense = components["schemas"]["ExpenseRead"];

export type Vehicle = Omit<
  ApiVehicle,
  "max_capacity_kg" | "odometer" | "acquisition_cost"
> & { max_capacity_kg: number; odometer: number; acquisition_cost: number };
export type VehicleCreate = Omit<
  components["schemas"]["VehicleCreate"],
  "max_capacity_kg" | "odometer" | "acquisition_cost"
> & { max_capacity_kg: number; odometer?: number; acquisition_cost: number };
export type Driver = Omit<ApiDriver, "safety_score"> & {
  safety_score: number;
};
export type DriverCreate = Omit<
  components["schemas"]["DriverCreate"],
  "safety_score"
> & { safety_score?: number };
export type DriverStatusUpdate = {
  status: "Available" | "Off Duty" | "Suspended";
  version: number;
};
export type Trip = Omit<
  ApiTrip,
  "cargo_weight_kg" | "planned_distance_km" | "final_odometer"
> & {
  cargo_weight_kg: number;
  planned_distance_km: number;
  final_odometer: number | null;
};
export type TripCreate = Omit<
  components["schemas"]["TripCreate"],
  "cargo_weight_kg" | "planned_distance_km"
> & { cargo_weight_kg: number; planned_distance_km: number };
export type Maintenance = Omit<ApiMaintenance, "cost"> & { cost: number };
export type MaintenanceCreate = {
  vehicle_id: string;
  trip_id?: string | null;
  service_type: string;
  cost: number;
  service_date?: string | null;
  status?: "Active" | "Completed";
};
export type FuelLog = Omit<ApiFuel, "liters" | "cost" | "odometer"> & {
  liters: number;
  cost: number;
  odometer: number | null;
};
export type FuelCreate = Omit<
  components["schemas"]["FuelCreate"],
  "liters" | "cost" | "odometer"
> & { liters: number; cost: number; odometer?: number | null };
export type Expense = Omit<ApiExpense, "amount"> & { amount: number };
export type ExpenseCreate = Omit<
  components["schemas"]["ExpenseCreate"],
  "amount" | "category"
> & {
  amount: number;
  category: "Toll" | "Parking" | "Insurance" | "Permit" | "Other";
};

const STATUS_LABELS: Record<string, string> = {
  AVAILABLE: "Available",
  ON_TRIP: "On Trip",
  IN_SHOP: "In Shop",
  RETIRED: "Retired",
  OFF_DUTY: "Off Duty",
  SUSPENDED: "Suspended",
  DRAFT: "Draft",
  DISPATCHED: "Dispatched",
  COMPLETED: "Completed",
  CANCELLED: "Cancelled",
  ACTIVE: "Active",
};

const statusLabel = (value: string) => STATUS_LABELS[value] ?? value;
const numeric = (value: string | number | null | undefined) =>
  Number(value ?? 0);

const queryKeys = {
  vehicles: ["vehicles"] as const,
  drivers: ["drivers"] as const,
  trips: ["trips"] as const,
  maintenance: ["maintenance"] as const,
  fuel: ["fuel"] as const,
  expenses: ["expenses"] as const,
};

async function request<T>(
  response: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  return unwrapApiResponse(await response);
}

function useInvalidateOperationalData() {
  const queryClient = useQueryClient();
  return () =>
    Promise.all(
      Object.values(queryKeys).map((queryKey) =>
        queryClient.invalidateQueries({ queryKey }),
      ),
    );
}

export function useVehicles() {
  return useQuery({
    queryKey: queryKeys.vehicles,
    queryFn: async () =>
      (await request(transitOpsClient.GET("/api/v1/vehicles"))).map((item) => ({
        ...item,
        status: statusLabel(item.status),
        max_capacity_kg: numeric(item.max_capacity_kg),
        odometer: numeric(item.odometer),
        acquisition_cost: numeric(item.acquisition_cost),
      })),
  });
}

export function useDrivers(dispatchable = false) {
  return useQuery({
    queryKey: [...queryKeys.drivers, { dispatchable }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/drivers", {
          params: { query: { dispatchable } },
        }),
      ).then((items) =>
        items.map((item) => ({
          ...item,
          status: statusLabel(item.status),
          safety_score: numeric(item.safety_score),
        })),
      ),
  });
}

export function useTrips(vehicleId?: string) {
  return useQuery({
    queryKey: [...queryKeys.trips, { vehicleId }],
    queryFn: () =>
      request(transitOpsClient.GET("/api/v1/trips")).then((items) =>
        items.map((item) => ({
          ...item,
          status: statusLabel(item.status),
          cargo_weight_kg: numeric(item.cargo_weight_kg),
          planned_distance_km: numeric(item.planned_distance_km),
          final_odometer:
            item.final_odometer === null ? null : numeric(item.final_odometer),
        })),
      ),
  });
}

export function useMaintenance(vehicleId?: string) {
  return useQuery({
    queryKey: [...queryKeys.maintenance, { vehicleId }],
    queryFn: () =>
      request(transitOpsClient.GET("/api/v1/maintenance")).then((items) =>
        items.map((item) => ({
          ...item,
          status: statusLabel(item.status),
          cost: numeric(item.cost),
        })),
      ),
  });
}

export function useFuel(vehicleId?: string) {
  return useQuery({
    queryKey: [...queryKeys.fuel, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/fuel", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ).then((items) =>
        items.map((item) => ({
          ...item,
          liters: numeric(item.liters),
          cost: numeric(item.cost),
          odometer: item.odometer === null ? null : numeric(item.odometer),
        })),
      ),
  });
}

export function useExpenses(vehicleId?: string) {
  return useQuery({
    queryKey: [...queryKeys.expenses, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/expenses", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ).then((items) =>
        items.map((item) => ({ ...item, amount: numeric(item.amount) })),
      ),
  });
}

export function useCreateVehicle() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: VehicleCreate) =>
      request(
        transitOpsClient.POST("/api/v1/vehicles", {
          body: {
            ...body,
            max_capacity_kg: String(body.max_capacity_kg),
            acquisition_cost: String(body.acquisition_cost),
            odometer: String(body.odometer ?? 0),
          },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateDriver() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: DriverCreate) =>
      request(
        transitOpsClient.POST("/api/v1/drivers", {
          body: { ...body, safety_score: String(body.safety_score ?? 100) },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useUpdateDriverStatus() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: ({
      driverId,
      body,
    }: {
      driverId: string;
      body: DriverStatusUpdate;
    }) =>
      request(
        transitOpsClient.PATCH("/api/v1/drivers/{driver_id}/status", {
          params: { path: { driver_id: driverId } },
          body: {
            status: body.status.replace(" ", "_").toUpperCase() as
              "AVAILABLE" | "OFF_DUTY" | "SUSPENDED",
            version: body.version,
          },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateTrip() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: TripCreate) =>
      request(
        transitOpsClient.POST("/api/v1/trips", {
          body: {
            ...body,
            cargo_weight_kg: String(body.cargo_weight_kg),
            planned_distance_km: String(body.planned_distance_km),
          },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useTripAction() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: async ({
      tripId,
      action,
      finalOdometer,
      version,
    }: {
      tripId: string;
      action: "dispatch" | "complete" | "cancel";
      finalOdometer?: number;
      version: number;
    }) => {
      if (action === "dispatch") {
        return request(
          transitOpsClient.POST("/api/v1/trips/{trip_id}/dispatch", {
            params: { path: { trip_id: tripId } },
            headers: { "Idempotency-Key": `dispatch-${tripId}` },
          }),
        );
      }
      if (action === "complete") {
        return request(
          transitOpsClient.POST("/api/v1/trips/{trip_id}/complete", {
            params: { path: { trip_id: tripId } },
            body: { final_odometer: String(finalOdometer ?? 0), version },
            headers: { "Idempotency-Key": `complete-${tripId}` },
          }),
        );
      }
      return request(
        transitOpsClient.POST("/api/v1/trips/{trip_id}/cancel", {
          params: { path: { trip_id: tripId } },
          body: { reason: "Cancelled by dispatcher", version },
        }),
      );
    },
    onSuccess: invalidate,
  });
}

export function useCreateMaintenance() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: MaintenanceCreate) =>
      request(
        transitOpsClient.POST("/api/v1/maintenance", {
          body: {
            vehicle_id: body.vehicle_id,
            trip_id: body.trip_id,
            service_type: body.service_type,
            priority: "NORMAL",
            cost: String(body.cost),
            service_date: body.service_date,
          },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCloseMaintenance() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: ({
      maintenanceId,
      version,
    }: {
      maintenanceId: string;
      version: number;
    }) =>
      request(
        transitOpsClient.POST("/api/v1/maintenance/{maintenance_id}/close", {
          params: { path: { maintenance_id: maintenanceId } },
          body: { version },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateFuel() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: FuelCreate) =>
      request(
        transitOpsClient.POST("/api/v1/fuel", {
          body: {
            ...body,
            liters: String(body.liters),
            cost: String(body.cost),
            odometer: body.odometer == null ? null : String(body.odometer),
          },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateExpense() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: ExpenseCreate) =>
      request(
        transitOpsClient.POST("/api/v1/expenses", {
          body: {
            ...body,
            category: body.category.toUpperCase() as
              "TOLL" | "PARKING" | "INSURANCE" | "PERMIT" | "OTHER",
            amount: String(body.amount),
          },
        }),
      ),
    onSuccess: invalidate,
  });
}
