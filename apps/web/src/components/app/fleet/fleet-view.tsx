"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Search } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
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
import { useCreateVehicle, useVehicles } from "@/lib/api/hooks";

const TYPES = ["Van", "Truck", "Mini"] as const;
const STATUSES = ["Available", "On Trip", "In Shop", "Retired"] as const;

const vehicleSchema = z.object({
  regNo: z.string().min(4, "Registration number is required."),
  nameModel: z.string().min(1, "Name/model is required."),
  type: z.enum(TYPES),
  capacityKg: z.number().positive("Capacity must be greater than 0."),
  acquisitionCost: z.number().nonnegative("Cost cannot be negative."),
});

type VehicleValues = z.infer<typeof vehicleSchema>;

export function FleetView() {
  const vehiclesQuery = useVehicles();
  const createVehicle = useCreateVehicle();
  const items = vehiclesQuery.data;
  const searchParams = useSearchParams();
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState(
    () => searchParams.get("status") ?? "All",
  );
  const [open, setOpen] = useState(false);

  const form = useForm<VehicleValues>({
    resolver: zodResolver(vehicleSchema),
    defaultValues: {
      regNo: "",
      nameModel: "",
      type: "Van",
      capacityKg: 500,
      acquisitionCost: 0,
    },
  });

  const filtered = useMemo(
    () =>
      (items ?? []).filter((v) => {
        const matchesType = typeFilter === "All" || v.type === typeFilter;
        const matchesStatus =
          statusFilter === "All"
            ? true
            : statusFilter === "active"
              ? v.status !== "Retired"
              : v.status === statusFilter;
        const q = search.trim().toLowerCase();
        const matchesSearch =
          q === "" ||
          v.reg_no.toLowerCase().includes(q) ||
          v.name_model.toLowerCase().includes(q);
        return matchesType && matchesStatus && matchesSearch;
      }),
    [items, search, typeFilter, statusFilter],
  );

  async function onSubmit(values: VehicleValues) {
    try {
      await createVehicle.mutateAsync({
        reg_no: values.regNo,
        name_model: values.nameModel,
        type: values.type,
        max_capacity_kg: values.capacityKg,
        odometer: 0,
        acquisition_cost: values.acquisitionCost,
      });
      toast.success("Vehicle added", {
        description: values.regNo.toUpperCase(),
      });
      form.reset();
      setOpen(false);
    } catch (error) {
      form.setError("regNo", {
        message:
          error instanceof Error ? error.message : "Could not add vehicle.",
      });
    }
  }

  return (
    <>
      <PageHeader
        title="Vehicle registry"
        description="Master list of fleet vehicles. Registration number must be unique."
        actions={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="size-4" />
                Add vehicle
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add vehicle</DialogTitle>
                <DialogDescription>
                  Register a new vehicle. It starts as Available.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4"
                  id="add-vehicle-form"
                >
                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="regNo"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Registration no.</FormLabel>
                          <FormControl>
                            <Input placeholder="GJ01AB0000" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="nameModel"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name / model</FormLabel>
                          <FormControl>
                            <Input placeholder="VAN-10" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Type</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            value={field.value}
                          >
                            <FormControl>
                              <SelectTrigger className="w-full">
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {TYPES.map((t) => (
                                <SelectItem key={t} value={t}>
                                  {t}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="capacityKg"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Max capacity (kg)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              name={field.name}
                              ref={field.ref}
                              onBlur={field.onBlur}
                              value={
                                Number.isNaN(field.value) ? "" : field.value
                              }
                              onChange={(e) =>
                                field.onChange(e.target.valueAsNumber)
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="acquisitionCost"
                      render={({ field }) => (
                        <FormItem className="sm:col-span-2">
                          <FormLabel>Acquisition cost (₹)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              name={field.name}
                              ref={field.ref}
                              onBlur={field.onBlur}
                              value={
                                Number.isNaN(field.value) ? "" : field.value
                              }
                              onChange={(e) =>
                                field.onChange(e.target.valueAsNumber)
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </form>
              </Form>
              <DialogFooter>
                <Button type="submit" form="add-vehicle-form">
                  Save vehicle
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-xs">
          <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reg. no. or model…"
            className="pl-8"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[150px]">
            <span className="text-muted-foreground">Type:</span>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            {TYPES.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[160px]">
            <span className="text-muted-foreground">Status:</span>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            <SelectItem value="active">Active (in service)</SelectItem>
            {STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="text-muted-foreground ml-auto text-sm">
          {filtered.length} of {items?.length ?? 0}
        </span>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reg. no.</TableHead>
                <TableHead>Name / model</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-right">Capacity</TableHead>
                <TableHead className="text-right">Odometer</TableHead>
                <TableHead className="text-right">Acq. cost</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((v) => (
                <TableRow key={v.vehicle_id}>
                  <TableCell className="font-medium">{v.reg_no}</TableCell>
                  <TableCell>{v.name_model}</TableCell>
                  <TableCell>{v.type}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {v.max_capacity_kg.toLocaleString()} kg
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {v.odometer.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    ₹{v.acquisition_cost.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={v.status} />
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    className="text-muted-foreground py-10 text-center"
                  >
                    No vehicles match your filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <p className="text-muted-foreground text-sm">
        Rule: registration number must be unique · Retired and In Shop vehicles
        are hidden from the trip dispatcher.
      </p>
    </>
  );
}
