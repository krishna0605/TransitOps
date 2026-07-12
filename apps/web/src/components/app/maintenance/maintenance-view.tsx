"use client";

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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  type Maintenance,
  maintenanceLogs as seedLogs,
  vehicles,
} from "@/lib/mock-data";

const EMPTY = { vehicle: "", service: "", cost: "", date: "", status: "Active" };

export function MaintenanceView() {
  const [logs, setLogs] = useState<Maintenance[]>(seedLogs);
  const [form, setForm] = useState(EMPTY);

  function set(field: keyof typeof EMPTY, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function save() {
    if (!form.vehicle || !form.service || !form.cost) {
      toast.error("Vehicle, service type, and cost are required.");
      return;
    }
    setLogs((prev) => [
      {
        id: Math.max(0, ...prev.map((l) => l.id)) + 1,
        vehicle: form.vehicle,
        service: form.service,
        cost: Number(form.cost) || 0,
        date: form.date || new Date().toISOString().slice(0, 10),
        status: form.status === "Completed" ? "Completed" : "Active",
      },
      ...prev,
    ]);
    toast.success("Maintenance logged", {
      description:
        form.status === "Active"
          ? `${form.vehicle} moved to In Shop`
          : form.vehicle,
    });
    setForm(EMPTY);
  }

  function close(id: number) {
    setLogs((prev) =>
      prev.map((l) => (l.id === id ? { ...l, status: "Completed" } : l)),
    );
    toast.success("Maintenance closed", {
      description: "Vehicle returned to Available",
    });
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
                    <SelectItem key={v.id} value={v.nameModel}>
                      {v.nameModel}
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
            <p className="text-xs text-muted-foreground">
              Active → vehicle set to In Shop and hidden from dispatch. Closing →
              vehicle returns to Available (unless Retired).
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
                  <TableRow key={log.id}>
                    <TableCell className="font-medium">{log.vehicle}</TableCell>
                    <TableCell>{log.service}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      ₹{log.cost.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {log.date}
                    </TableCell>
                    <TableCell>
                      <StatusBadge
                        status={log.status === "Active" ? "In Shop" : "Completed"}
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      {log.status === "Active" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => close(log.id)}
                        >
                          Close
                        </Button>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
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
