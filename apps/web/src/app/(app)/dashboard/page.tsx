import type { Metadata } from "next";

import { KpiCard } from "@/components/shared/kpi-card";
import { PageHeader } from "@/components/shared/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
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
import { dashboardKpis, trips, vehicleStatusBreakdown } from "@/lib/mock-data";

export const metadata: Metadata = { title: "Dashboard" };

const FILTERS = [
  { label: "Vehicle Type", options: ["All", "Van", "Truck", "Mini"] },
  { label: "Status", options: ["All", "Available", "On Trip", "In Shop"] },
  { label: "Region", options: ["All", "North", "South", "East", "West"] },
];

export default function DashboardPage() {
  const totalActive = vehicleStatusBreakdown.reduce((sum, s) => sum + s.count, 0);

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Fleet, trips, and driver activity at a glance."
      />

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        {FILTERS.map((filter) => (
          <Select key={filter.label} defaultValue="All">
            <SelectTrigger className="w-[170px]">
              <span className="text-muted-foreground">{filter.label}:</span>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {filter.options.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ))}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-7">
        {dashboardKpis.map((kpi) => (
          <KpiCard
            key={kpi.label}
            label={kpi.label}
            value={kpi.value}
            tone={kpi.tone}
          />
        ))}
      </div>

      {/* Recent trips + vehicle status */}
      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Recent trips</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Trip</TableHead>
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Driver</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">ETA</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {trips.map((trip) => (
                  <TableRow key={trip.id}>
                    <TableCell className="font-medium">{trip.code}</TableCell>
                    <TableCell>{trip.vehicle}</TableCell>
                    <TableCell>{trip.driver}</TableCell>
                    <TableCell>
                      <StatusBadge status={trip.status} />
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {trip.eta}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vehicle status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {vehicleStatusBreakdown.map((item) => (
              <div key={item.status} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <StatusBadge status={item.status} />
                  </span>
                  <span className="tabular-nums text-muted-foreground">
                    {item.count}
                  </span>
                </div>
                <Progress value={(item.count / totalActive) * 100} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
