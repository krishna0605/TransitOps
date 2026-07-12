"use client";

import { Fuel, Plus, Receipt } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  useCreateExpense,
  useCreateFuel,
  useExpenses,
  useFuel,
  useMaintenance,
  useVehicles,
} from "@/lib/api/hooks";

export function FuelExpenseView() {
  const fuelQuery = useFuel();
  const expensesQuery = useExpenses();
  const maintenanceQuery = useMaintenance();
  const vehiclesQuery = useVehicles();
  const createFuel = useCreateFuel();
  const createExpense = useCreateExpense();
  const fuel = fuelQuery.data ?? [];
  const expenses = expensesQuery.data ?? [];
  const vehicles = vehiclesQuery.data ?? [];
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
    const maintTotal = (maintenanceQuery.data ?? []).reduce(
      (sum, item) => sum + item.cost,
      0,
    );
    return fuelTotal + maintTotal;
  }, [fuel]);

  async function addFuel() {
    if (!fuelForm.vehicle || !fuelForm.liters || !fuelForm.cost) {
      toast.error("Vehicle, liters, and cost are required.");
      return;
    }
    try {
      await createFuel.mutateAsync({
        vehicle_id: Number(fuelForm.vehicle),
        fuel_date: fuelForm.date || null,
        liters: Number(fuelForm.liters),
        cost: Number(fuelForm.cost),
        trip_id: null,
      });
      toast.success("Fuel logged");
      setFuelForm({ vehicle: "", date: "", liters: "", cost: "" });
      setFuelOpen(false);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not log fuel.",
      );
    }
  }

  async function addExpense() {
    if (!expenseForm.vehicle) {
      toast.error("Vehicle is required.");
      return;
    }
    try {
      const toll = Number(expenseForm.toll) || 0;
      const other = Number(expenseForm.other) || 0;
      await Promise.all([
        ...(toll
          ? [
              createExpense.mutateAsync({
                vehicle_id: Number(expenseForm.vehicle),
                trip_id: expenseForm.trip ? Number(expenseForm.trip) : null,
                category: "Toll",
                amount: toll,
              }),
            ]
          : []),
        ...(other
          ? [
              createExpense.mutateAsync({
                vehicle_id: Number(expenseForm.vehicle),
                trip_id: expenseForm.trip ? Number(expenseForm.trip) : null,
                category: "Other",
                amount: other,
              }),
            ]
          : []),
      ]);
      toast.success("Expense added");
      setExpenseForm({ trip: "", vehicle: "", toll: "", other: "" });
      setExpenseOpen(false);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not add expense.",
      );
    }
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
                          <SelectItem
                            key={v.vehicle_id}
                            value={String(v.vehicle_id)}
                          >
                            {v.name_model}
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
                          <SelectItem
                            key={v.vehicle_id}
                            value={String(v.vehicle_id)}
                          >
                            {v.name_model}
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
            <Fuel className="text-muted-foreground size-4" />
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
                <TableRow key={f.fuel_id}>
                  <TableCell className="font-medium">
                    {f.vehicle_reg_no}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {f.fuel_date}
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
            <Receipt className="text-muted-foreground size-4" />
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
                <TableRow key={e.expense_id}>
                  <TableCell className="font-medium">
                    {e.trip_label ?? "—"}
                  </TableCell>
                  <TableCell>{e.vehicle_reg_no}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{(e.category === "Toll" ? e.amount : 0).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{(e.category === "Other" ? e.amount : 0).toLocaleString()}
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

      <Card className="border-l-brand border-l-4">
        <CardContent className="flex items-center justify-between p-6">
          <div>
            <p className="text-muted-foreground text-sm">
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
