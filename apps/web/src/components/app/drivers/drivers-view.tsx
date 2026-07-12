"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Search } from "lucide-react";
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
import { cn } from "@/lib/utils";
import {
  useCreateDriver,
  useDrivers,
  useUpdateDriverStatus,
} from "@/lib/api/hooks";

const DRIVER_STATUSES = [
  "Available",
  "On Trip",
  "Off Duty",
  "Suspended",
] as const;

const driverSchema = z.object({
  name: z.string().min(2, "Name is required."),
  licenseNo: z.string().min(3, "License number is required."),
  category: z.enum(["LMV", "HMV"]),
  expiry: z.string().regex(/^\d{2}\/\d{4}$/, "Use MM/YYYY."),
  contact: z.string().min(5, "Contact is required."),
});

type DriverValues = z.infer<typeof driverSchema>;

function safetyColor(score: number) {
  if (score >= 90) return "bg-emerald-500";
  if (score >= 75) return "bg-amber-500";
  return "bg-red-500";
}

export function DriversView() {
  const driversQuery = useDrivers();
  const createDriver = useCreateDriver();
  const updateDriverStatus = useUpdateDriverStatus();
  const items = driversQuery.data;
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [open, setOpen] = useState(false);

  const form = useForm<DriverValues>({
    resolver: zodResolver(driverSchema),
    defaultValues: {
      name: "",
      licenseNo: "",
      category: "LMV",
      expiry: "",
      contact: "",
    },
  });

  const filtered = useMemo(
    () =>
      (items ?? []).filter((d) => {
        const matchesStatus =
          statusFilter === "All" || d.status === statusFilter;
        const q = search.trim().toLowerCase();
        const matchesSearch =
          q === "" ||
          d.name.toLowerCase().includes(q) ||
          d.license_no.toLowerCase().includes(q);
        return matchesStatus && matchesSearch;
      }),
    [items, search, statusFilter],
  );

  async function changeStatus(
    driverId: number,
    status: (typeof DRIVER_STATUSES)[number],
  ) {
    try {
      await updateDriverStatus.mutateAsync({ driverId, body: { status } });
      toast.success("Driver status updated", { description: status });
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not update driver.",
      );
    }
  }

  async function onSubmit(values: DriverValues) {
    try {
      await createDriver.mutateAsync({
        name: values.name,
        license_no: values.licenseNo,
        license_category: values.category,
        license_expiry: `20${values.expiry.slice(3)}-${values.expiry.slice(0, 2)}-01`,
        contact: values.contact,
        safety_score: 100,
      });
      toast.success("Driver added", { description: values.name });
      form.reset();
      setOpen(false);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not add driver.",
      );
    }
  }

  return (
    <>
      <PageHeader
        title="Drivers & safety"
        description="Driver profiles, license validity, and safety scores."
        actions={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="size-4" />
                Add driver
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add driver</DialogTitle>
                <DialogDescription>
                  Create a driver profile. Safety score starts at 100.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form
                  id="add-driver-form"
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="grid gap-4 sm:grid-cols-2"
                >
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Alex" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="licenseNo"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>License no.</FormLabel>
                        <FormControl>
                          <Input placeholder="DL-00000" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Category</FormLabel>
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
                            <SelectItem value="LMV">LMV</SelectItem>
                            <SelectItem value="HMV">HMV</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="expiry"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>License expiry</FormLabel>
                        <FormControl>
                          <Input placeholder="MM/YYYY" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="contact"
                    render={({ field }) => (
                      <FormItem className="sm:col-span-2">
                        <FormLabel>Contact</FormLabel>
                        <FormControl>
                          <Input placeholder="98765xxxxx" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </form>
              </Form>
              <DialogFooter>
                <Button type="submit" form="add-driver-form">
                  Save driver
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-xs">
          <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name or license…"
            className="pl-8"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[160px]">
            <span className="text-muted-foreground">Status:</span>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All</SelectItem>
            {DRIVER_STATUSES.map((s) => (
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
                <TableHead>Driver</TableHead>
                <TableHead>License no.</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Expiry</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Safety</TableHead>
                <TableHead className="w-[150px]">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((d) => (
                <TableRow key={d.driver_id}>
                  <TableCell className="font-medium">{d.name}</TableCell>
                  <TableCell>{d.license_no}</TableCell>
                  <TableCell>{d.license_category}</TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1.5",
                        "font-medium text-red-600",
                      )}
                    >
                      {d.license_expiry}
                    </span>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {d.contact}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="bg-muted h-1.5 w-16 overflow-hidden rounded-full">
                        <div
                          className={cn(
                            "h-full rounded-full",
                            safetyColor(d.safety_score),
                          )}
                          style={{ width: `${d.safety_score}%` }}
                        />
                      </div>
                      <span className="text-muted-foreground text-sm tabular-nums">
                        {d.safety_score}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Select
                      value={d.status}
                      onValueChange={(v) =>
                        changeStatus(
                          d.driver_id,
                          v as (typeof DRIVER_STATUSES)[number],
                        )
                      }
                    >
                      <SelectTrigger
                        className="h-8 w-full border-none bg-transparent p-0 shadow-none focus-visible:ring-0"
                        aria-label="Change status"
                      >
                        <StatusBadge status={d.status} />
                      </SelectTrigger>
                      <SelectContent>
                        {DRIVER_STATUSES.map((s) => (
                          <SelectItem key={s} value={s}>
                            {s}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <p className="text-muted-foreground text-sm">
        Rule: an expired license or Suspended status blocks a driver from trip
        assignment.
      </p>
    </>
  );
}
