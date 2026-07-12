"use client";

import { KpiCard } from "@/components/shared/kpi-card";
import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useDrivers, useTrips, useVehicles } from "@/lib/api/hooks";

export function DashboardView() {
  const vehicles = useVehicles().data ?? [];
  const drivers = useDrivers().data ?? [];
  const trips = useTrips().data ?? [];
  const statuses = ["Available", "On Trip", "In Shop", "Retired"];
  const total = Math.max(vehicles.length, 1);
  const kpis = [
    {
      label: "Active vehicles",
      value: String(vehicles.length),
      tone: "default" as const,
      href: "/fleet?status=active",
    },
    {
      label: "Available vehicles",
      value: String(
        vehicles.filter((item) => item.status === "Available").length,
      ),
      tone: "success" as const,
      href: "/fleet?status=Available",
    },
    {
      label: "In maintenance",
      value: String(
        vehicles.filter((item) => item.status === "In Shop").length,
      ),
      tone: "warning" as const,
      href: "/fleet?status=In+Shop",
    },
    {
      label: "Active trips",
      value: String(
        trips.filter((item) => item.status === "Dispatched").length,
      ),
      tone: "info" as const,
      href: "/trips?status=Dispatched",
    },
    {
      label: "Draft trips",
      value: String(trips.filter((item) => item.status === "Draft").length),
      tone: "default" as const,
      href: "/trips?status=Draft",
    },
    {
      label: "Available drivers",
      value: String(
        drivers.filter((item) => item.status === "Available").length,
      ),
      tone: "success" as const,
      href: "/drivers?status=Available",
    },
  ];

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Fleet, trips, and driver activity at a glance."
      />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.label} {...kpi} />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Recent trips</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {trips.slice(0, 6).map((trip) => (
              <div
                key={trip.trip_id}
                className="flex items-center justify-between gap-3 border-b pb-3 text-sm"
              >
                <span>
                  {trip.source} → {trip.destination}
                </span>
                <StatusBadge status={trip.status} />
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Vehicle status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {statuses.map((status) => {
              const count = vehicles.filter(
                (item) => item.status === status,
              ).length;
              return (
                <div key={status} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <StatusBadge status={status} />
                    <span>{count}</span>
                  </div>
                  <Progress value={(count / total) * 100} />
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
