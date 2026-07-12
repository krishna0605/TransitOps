"use client";

import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  drivers,
  type Trip,
  type TripStatus,
  trips as seedTrips,
  vehicles,
} from "@/lib/mock-data";

const LIFECYCLE: TripStatus[] = [
  "Draft",
  "Dispatched",
  "Completed",
  "Cancelled",
];

const EMPTY = {
  source: "",
  destination: "",
  vehicle: "",
  driver: "",
  cargo: "",
  distance: "",
};

export function TripDispatcher() {
  const [board, setBoard] = useState<Trip[]>(seedTrips);
  const [form, setForm] = useState(EMPTY);

  // Business rules: only Available vehicles and eligible drivers can dispatch.
  const availableVehicles = vehicles.filter((v) => v.status === "Available");
  const availableDrivers = drivers.filter(
    (d) => d.status === "Available" && !d.expired,
  );

  const selectedVehicle = vehicles.find((v) => v.nameModel === form.vehicle);
  const cargo = Number(form.cargo) || 0;
  const capacity = selectedVehicle?.capacityKg ?? 0;
  const over = selectedVehicle ? cargo - capacity : 0;
  const blocked = over > 0;
  const complete =
    form.source &&
    form.destination &&
    form.vehicle &&
    form.driver &&
    form.cargo &&
    form.distance;
  const canDispatch = Boolean(complete) && !blocked;

  function set(field: keyof typeof EMPTY, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function dispatch() {
    if (!complete) {
      toast.error("Complete all fields before dispatching.");
      return;
    }
    if (blocked) {
      toast.error(`Capacity exceeded by ${over} kg.`);
      return;
    }
    const nextNumber = board.length + 1;
    setBoard((prev) => [
      {
        id: Math.max(0, ...prev.map((t) => t.id)) + 1,
        code: `TR${String(nextNumber).padStart(3, "0")}`,
        source: form.source,
        destination: form.destination,
        vehicle: form.vehicle,
        driver: form.driver,
        status: "Dispatched",
        eta: "Just now",
        cargoKg: cargo,
        distanceKm: Number(form.distance) || 0,
      },
      ...prev,
    ]);
    toast.success("Trip dispatched", {
      description: `${form.vehicle} · ${form.driver}`,
    });
    setForm(EMPTY);
  }

  function advance(id: number, status: TripStatus) {
    setBoard((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status, eta: "—" } : t)),
    );
    toast.success(`Trip ${status.toLowerCase()}`);
  }

  return (
    <>
      <PageHeader
        title="Trip dispatcher"
        description="Create trips against available vehicles and drivers."
      />

      {/* Lifecycle */}
      <div className="flex items-center gap-2 text-sm">
        {LIFECYCLE.map((step, index) => (
          <div key={step} className="flex items-center gap-2">
            <span className="flex items-center gap-2 rounded-full border px-3 py-1">
              <span
                className={cn(
                  "size-2 rounded-full",
                  index === 0
                    ? "bg-muted-foreground"
                    : index === 1
                      ? "bg-blue-500"
                      : index === 2
                        ? "bg-emerald-500"
                        : "bg-red-500",
                )}
              />
              {step}
            </span>
            {index < LIFECYCLE.length - 1 ? (
              <span className="text-muted-foreground">→</span>
            ) : null}
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        {/* Create trip */}
        <Card>
          <CardHeader>
            <CardTitle>Create trip</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Source</Label>
                <Input
                  value={form.source}
                  onChange={(e) => set("source", e.target.value)}
                  placeholder="Gandhinagar Depot"
                />
              </div>
              <div className="space-y-2">
                <Label>Destination</Label>
                <Input
                  value={form.destination}
                  onChange={(e) => set("destination", e.target.value)}
                  placeholder="Ahmedabad Hub"
                />
              </div>
              <div className="space-y-2">
                <Label>Vehicle (available only)</Label>
                <Select
                  value={form.vehicle}
                  onValueChange={(v) => set("vehicle", v)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select vehicle" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableVehicles.map((v) => (
                      <SelectItem key={v.id} value={v.nameModel}>
                        {v.nameModel} · {v.capacityKg} kg
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Driver (available only)</Label>
                <Select
                  value={form.driver}
                  onValueChange={(v) => set("driver", v)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select driver" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableDrivers.map((d) => (
                      <SelectItem key={d.id} value={d.name}>
                        {d.name} · {d.category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Cargo weight (kg)</Label>
                <Input
                  type="number"
                  value={form.cargo}
                  onChange={(e) => set("cargo", e.target.value)}
                  placeholder="450"
                />
              </div>
              <div className="space-y-2">
                <Label>Planned distance (km)</Label>
                <Input
                  type="number"
                  value={form.distance}
                  onChange={(e) => set("distance", e.target.value)}
                  placeholder="58"
                />
              </div>
            </div>

            {/* Live capacity check */}
            {selectedVehicle ? (
              <div
                className={cn(
                  "flex items-start gap-2 rounded-lg border p-3 text-sm",
                  blocked
                    ? "border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-400"
                    : "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
                )}
              >
                {blocked ? (
                  <AlertTriangle className="mt-0.5 size-4 shrink-0" />
                ) : (
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0" />
                )}
                <div>
                  <p>
                    Vehicle capacity {capacity} kg · Cargo {cargo} kg
                  </p>
                  <p className="font-medium">
                    {blocked
                      ? `Capacity exceeded by ${over} kg → dispatch blocked`
                      : "Within capacity → ready to dispatch"}
                  </p>
                </div>
              </div>
            ) : null}

            <div className="flex gap-2">
              <Button onClick={dispatch} disabled={!canDispatch}>
                Dispatch
              </Button>
              <Button variant="outline" onClick={() => setForm(EMPTY)}>
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Live board */}
        <Card>
          <CardHeader>
            <CardTitle>Live board</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {board.map((trip) => (
              <div
                key={trip.id}
                className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{trip.code}</span>
                    <StatusBadge status={trip.status} />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {trip.source} → {trip.destination}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {trip.vehicle} · {trip.driver} · {trip.eta}
                  </p>
                </div>
                {trip.status === "Dispatched" ? (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => advance(trip.id, "Completed")}
                    >
                      Complete
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => advance(trip.id, "Cancelled")}
                    >
                      Cancel
                    </Button>
                  </div>
                ) : null}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <p className="text-sm text-muted-foreground">
        On completion: odometer → fuel log → expenses; vehicle and driver return
        to Available.
      </p>
    </>
  );
}
