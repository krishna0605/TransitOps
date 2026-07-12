"use client";

import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useCloseMaintenance,
  useCreateMaintenance,
  useMaintenance,
  useVehicles,
} from "@/lib/api/hooks";

const EMPTY = {
  vehicle: "",
  service: "",
  cost: "",
  date: "",
  status: "Active",
};

export function MaintenanceView() {
  const maintenanceQuery = useMaintenance();
  const vehiclesQuery = useVehicles();
  const createMaintenance = useCreateMaintenance();
  const closeMaintenance = useCloseMaintenance();
  const logs = maintenanceQuery.data ?? [];
  const vehicles = vehiclesQuery.data ?? [];
  const [form, setForm] = useState(EMPTY);

  function set(field: keyof typeof EMPTY, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function save() {
    if (!form.vehicle || !form.service || !form.cost) {
      toast.error("Vehicle, service type, and cost are required.");
      return;
    }
    try {
      await createMaintenance.mutateAsync({
        vehicle_id: form.vehicle,
        service_type: form.service,
        cost: Number(form.cost),
        service_date: form.date || null,
        status: form.status as "Active" | "Completed",
        trip_id: null,
      });
      toast.success("Maintenance logged");
      setForm(EMPTY);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not log maintenance.",
      );
    }
  }

  async function close(maintenanceId: string, version: number) {
    try {
      await closeMaintenance.mutateAsync({ maintenanceId, version });
      toast.success("Maintenance closed", {
        description: "Vehicle returned to Available",
      });
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not close maintenance.",
      );
    }
  }

  return (
    <>
      <PageHeader
        title="Maintenance"
        description="Log service records. Active records move a vehicle to In Shop."
      />

      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Log service record</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Vehicle</Label>
              <Select
                value={form.vehicle}
                onValueChange={(v) => set("vehicle", v)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select vehicle" />
                </SelectTrigger>
                <SelectContent>
                  {vehicles.map((v) => (
                    <SelectItem key={v.vehicle_id} value={String(v.vehicle_id)}>
                      {v.name_model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Service type</Label>
              <Input
                value={form.service}
                onChange={(e) => set("service", e.target.value)}
                placeholder="Oil Change"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Cost (₹)</Label>
                <Input
                  type="number"
                  value={form.cost}
                  onChange={(e) => set("cost", e.target.value)}
                  placeholder="2500"
                />
              </div>
              <div className="space-y-2">
                <Label>Date</Label>
                <Input
                  type="date"
                  value={form.date}
                  onChange={(e) => set("date", e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <Select
                value={form.status}
                onValueChange={(v) => set("status", v)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Active">Active (In Shop)</SelectItem>
                  <SelectItem value="Completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={save} className="w-full">
              Save record
            </Button>
            <p className="text-muted-foreground text-xs">
              Active → vehicle set to In Shop and hidden from dispatch. Closing
              → vehicle returns to Available (unless Retired).
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Service log</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead className="text-right">Cost</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.maintenance_id}>
                    <TableCell className="font-medium">
                      {log.vehicle_reg_no}
                    </TableCell>
                    <TableCell>{log.service_type}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      ₹{log.cost.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {log.service_date}
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        status={
                          log.status === "Active" ? "In Shop" : "Completed"
                        }
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      {log.status === "Active" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => close(log.maintenance_id, log.version)}
                        >
                          Close
                        </Button>
                      ) : (
                        <span className="text-muted-foreground text-xs">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
