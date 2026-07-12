"use client";

import { Fuel, Plus, Receipt } from "lucide-react";
import { useMemo, useState } from "react";
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
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
  type Expense,
  expenses as seedExpenses,
  type FuelLog,
  fuelLogs as seedFuel,
  maintenanceLogs,
  vehicles,
} from "@/lib/mock-data";

export function FuelExpenseView() {
  const [fuel, setFuel] = useState<FuelLog[]>(seedFuel);
  const [expenses, setExpenses] = useState<Expense[]>(seedExpenses);
  const [fuelOpen, setFuelOpen] = useState(false);
  const [expenseOpen, setExpenseOpen] = useState(false);

  const [fuelForm, setFuelForm] = useState({
    vehicle: "",
    date: "",
    liters: "",
    cost: "",
  });
  const [expenseForm, setExpenseForm] = useState({
    trip: "",
    vehicle: "",
    toll: "",
    other: "",
  });

  // Operational cost = fuel + maintenance (per schema).
  const operationalCost = useMemo(() => {
    const fuelTotal = fuel.reduce((sum, f) => sum + f.cost, 0);
    const maintTotal = maintenanceLogs.reduce((sum, m) => sum + m.cost, 0);
    return fuelTotal + maintTotal;
  }, [fuel]);

  function addFuel() {
    if (!fuelForm.vehicle || !fuelForm.liters || !fuelForm.cost) {
      toast.error("Vehicle, liters, and cost are required.");
      return;
    }
    setFuel((prev) => [
      {
        id: Math.max(0, ...prev.map((f) => f.id)) + 1,
        vehicle: fuelForm.vehicle,
        date: fuelForm.date || new Date().toISOString().slice(0, 10),
        liters: Number(fuelForm.liters) || 0,
        cost: Number(fuelForm.cost) || 0,
      },
      ...prev,
    ]);
    toast.success("Fuel logged", { description: fuelForm.vehicle });
    setFuelForm({ vehicle: "", date: "", liters: "", cost: "" });
    setFuelOpen(false);
  }

  function addExpense() {
    if (!expenseForm.vehicle) {
      toast.error("Vehicle is required.");
      return;
    }
    const toll = Number(expenseForm.toll) || 0;
    const other = Number(expenseForm.other) || 0;
    setExpenses((prev) => [
      {
        id: Math.max(0, ...prev.map((e) => e.id)) + 1,
        trip: expenseForm.trip || "—",
        vehicle: expenseForm.vehicle,
        toll,
        other,
        amount: toll + other,
        status: "Available",
      },
      ...prev,
    ]);
    toast.success("Expense added", { description: expenseForm.vehicle });
    setExpenseForm({ trip: "", vehicle: "", toll: "", other: "" });
    setExpenseOpen(false);
  }

  return (
    <>
      <PageHeader
        title="Fuel & expenses"
        description="Fuel logs, tolls, and other costs rolled into operational cost."
        actions={
          <div className="flex gap-2">
            <Dialog open={fuelOpen} onOpenChange={setFuelOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Fuel className="size-4" />
                  Log fuel
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Log fuel</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2 sm:col-span-2">
                    <Label>Vehicle</Label>
                    <Select
                      value={fuelForm.vehicle}
                      onValueChange={(v) =>
                        setFuelForm((p) => ({ ...p, vehicle: v }))
                      }
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
                    <Label>Date</Label>
                    <Input
                      type="date"
                      value={fuelForm.date}
                      onChange={(e) =>
                        setFuelForm((p) => ({ ...p, date: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Liters</Label>
                    <Input
                      type="number"
                      value={fuelForm.liters}
                      onChange={(e) =>
                        setFuelForm((p) => ({ ...p, liters: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <Label>Cost (₹)</Label>
                    <Input
                      type="number"
                      value={fuelForm.cost}
                      onChange={(e) =>
                        setFuelForm((p) => ({ ...p, cost: e.target.value }))
                      }
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={addFuel}>Save fuel log</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog open={expenseOpen} onOpenChange={setExpenseOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="size-4" />
                  Add expense
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add expense</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Trip</Label>
                    <Input
                      value={expenseForm.trip}
                      onChange={(e) =>
                        setExpenseForm((p) => ({ ...p, trip: e.target.value }))
                      }
                      placeholder="TR001"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Vehicle</Label>
                    <Select
                      value={expenseForm.vehicle}
                      onValueChange={(v) =>
                        setExpenseForm((p) => ({ ...p, vehicle: v }))
                      }
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Vehicle" />
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
                    <Label>Toll (₹)</Label>
                    <Input
                      type="number"
                      value={expenseForm.toll}
                      onChange={(e) =>
                        setExpenseForm((p) => ({ ...p, toll: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Other (₹)</Label>
                    <Input
                      type="number"
                      value={expenseForm.other}
                      onChange={(e) =>
                        setExpenseForm((p) => ({ ...p, other: e.target.value }))
                      }
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={addExpense}>Save expense</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Fuel className="size-4 text-muted-foreground" />
            Fuel logs
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vehicle</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Liters</TableHead>
                <TableHead className="text-right">Cost</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {fuel.map((f) => (
                <TableRow key={f.id}>
                  <TableCell className="font-medium">{f.vehicle}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {f.date}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {f.liters} L
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{f.cost.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Receipt className="size-4 text-muted-foreground" />
            Other expenses (toll / other)
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Trip</TableHead>
                <TableHead>Vehicle</TableHead>
                <TableHead className="text-right">Toll</TableHead>
                <TableHead className="text-right">Other</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {expenses.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="font-medium">{e.trip}</TableCell>
                  <TableCell>{e.vehicle}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{e.toll.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{e.other.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-medium tabular-nums">
                    ₹{e.amount.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={e.status} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-brand">
        <CardContent className="flex items-center justify-between p-6">
          <div>
            <p className="text-sm text-muted-foreground">
              Total operational cost (auto) — Fuel + Maintenance
            </p>
            <p className="mt-1 text-3xl font-semibold tabular-nums">
              ₹{operationalCost.toLocaleString()}
            </p>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
