"use client";

import { type components, unwrapApiResponse } from "@transitops/api-client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { transitOpsClient } from "@/lib/api/transitops-client";

export type Vehicle = components["schemas"]["VehicleRead"];
export type VehicleCreate = components["schemas"]["VehicleCreate"];
export type Driver = components["schemas"]["DriverRead"];
export type DriverCreate = components["schemas"]["DriverCreate"];
export type DriverStatusUpdate = components["schemas"]["DriverStatusUpdate"];
export type Trip = components["schemas"]["TripRead"];
export type TripCreate = components["schemas"]["TripCreate"];
export type Maintenance = components["schemas"]["MaintenanceRead"];
export type MaintenanceCreate = components["schemas"]["MaintenanceCreate"];
export type FuelLog = components["schemas"]["FuelRead"];
export type FuelCreate = components["schemas"]["FuelCreate"];
export type Expense = components["schemas"]["ExpenseRead"];
export type ExpenseCreate = components["schemas"]["ExpenseCreate"];

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
    queryFn: () => request(transitOpsClient.GET("/api/v1/vehicles")),
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
      ),
  });
}

export function useTrips(vehicleId?: number) {
  return useQuery({
    queryKey: [...queryKeys.trips, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/trips", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ),
  });
}

export function useMaintenance(vehicleId?: number) {
  return useQuery({
    queryKey: [...queryKeys.maintenance, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/maintenance", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ),
  });
}

export function useFuel(vehicleId?: number) {
  return useQuery({
    queryKey: [...queryKeys.fuel, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/fuel", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ),
  });
}

export function useExpenses(vehicleId?: number) {
  return useQuery({
    queryKey: [...queryKeys.expenses, { vehicleId }],
    queryFn: () =>
      request(
        transitOpsClient.GET("/api/v1/expenses", {
          params: { query: vehicleId ? { vehicle_id: vehicleId } : {} },
        }),
      ),
  });
}

export function useCreateVehicle() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: VehicleCreate) =>
      request(transitOpsClient.POST("/api/v1/vehicles", { body })),
    onSuccess: invalidate,
  });
}

export function useCreateDriver() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: DriverCreate) =>
      request(transitOpsClient.POST("/api/v1/drivers", { body })),
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
      driverId: number;
      body: DriverStatusUpdate;
    }) =>
      request(
        transitOpsClient.PATCH("/api/v1/drivers/{driver_id}/status", {
          params: { path: { driver_id: driverId } },
          body,
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateTrip() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: TripCreate) =>
      request(transitOpsClient.POST("/api/v1/trips", { body })),
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
    }: {
      tripId: number;
      action: "dispatch" | "complete" | "cancel";
      finalOdometer?: number;
    }) => {
      if (action === "dispatch") {
        return request(
          transitOpsClient.POST("/api/v1/trips/{trip_id}/dispatch", {
            params: { path: { trip_id: tripId } },
          }),
        );
      }
      if (action === "complete") {
        return request(
          transitOpsClient.POST("/api/v1/trips/{trip_id}/complete", {
            params: { path: { trip_id: tripId } },
            body: { final_odometer: finalOdometer ?? null },
          }),
        );
      }
      return request(
        transitOpsClient.POST("/api/v1/trips/{trip_id}/cancel", {
          params: { path: { trip_id: tripId } },
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
      request(transitOpsClient.POST("/api/v1/maintenance", { body })),
    onSuccess: invalidate,
  });
}

export function useCloseMaintenance() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (maintenanceId: number) =>
      request(
        transitOpsClient.POST("/api/v1/maintenance/{maintenance_id}/close", {
          params: { path: { maintenance_id: maintenanceId } },
        }),
      ),
    onSuccess: invalidate,
  });
}

export function useCreateFuel() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: FuelCreate) =>
      request(transitOpsClient.POST("/api/v1/fuel", { body })),
    onSuccess: invalidate,
  });
}

export function useCreateExpense() {
  const invalidate = useInvalidateOperationalData();
  return useMutation({
    mutationFn: (body: ExpenseCreate) =>
      request(transitOpsClient.POST("/api/v1/expenses", { body })),
    onSuccess: invalidate,
  });
}
