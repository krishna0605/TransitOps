"use client";

import { Download } from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";

import { KpiCard } from "@/components/shared/kpi-card";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useExpenses,
  useFuel,
  useMaintenance,
  useTrips,
  useVehicles,
} from "@/lib/api/hooks";

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function exportCsv(rows: { month: string; value: number }[]) {
  const header = "month,revenue\n";
  const values = rows.map((row) => `${row.month},${row.value}`).join("\n");
  const blob = new Blob([header + values], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "transitops-analytics.csv";
  link.click();
  URL.revokeObjectURL(url);
  toast.success("CSV exported");
}

export function AnalyticsView() {
  const fuel = useFuel().data ?? [];
  const expenses = useExpenses().data ?? [];
  const maintenance = useMaintenance().data ?? [];
  const trips = useTrips().data ?? [];
  const vehicles = useVehicles().data ?? [];
  const costBreakdown = [
    {
      category: "Fuel",
      value: fuel.reduce((total, item) => total + item.cost, 0),
    },
    {
      category: "Maintenance",
      value: maintenance.reduce((total, item) => total + item.cost, 0),
    },
    {
      category: "Other",
      value: expenses.reduce((total, item) => total + item.amount, 0),
    },
  ];
  const costliestVehicles = vehicles
    .map((vehicle) => ({
      vehicle: vehicle.name_model,
      cost: fuel
        .filter((item) => item.vehicle_id === vehicle.vehicle_id)
        .reduce((total, item) => total + item.cost, 0),
    }))
    .sort((left, right) => right.cost - left.cost)
    .slice(0, 5);
  const monthlyRevenue = [
    {
      month: "Current",
      value: trips.reduce((total, item) => total + item.planned_distance_km, 0),
    },
  ];
  const analyticsKpis = [
    { label: "Fuel logs", value: String(fuel.length) },
    {
      label: "Fleet utilization",
      value: `${vehicles.length ? Math.round((vehicles.filter((item) => item.status === "On Trip").length / vehicles.length) * 100) : 0}%`,
    },
    {
      label: "Operational cost",
      value: `₹${costBreakdown.reduce((total, item) => total + item.value, 0).toLocaleString()}`,
    },
    {
      label: "Completed trips",
      value: String(trips.filter((item) => item.status === "Completed").length),
    },
  ];
  return (
    <>
      <PageHeader
        title="Analytics"
        description="Fuel efficiency, utilization, operational cost, and ROI."
        actions={
          <Button variant="outline" onClick={() => exportCsv(monthlyRevenue)}>
            <Download className="size-4" />
            Export CSV
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {analyticsKpis.map((kpi) => (
          <KpiCard key={kpi.label} label={kpi.label} value={kpi.value} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Monthly revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={monthlyRevenue}>
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  axisLine={false}
                  fontSize={12}
                  stroke="var(--muted-foreground)"
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  fontSize={12}
                  stroke="var(--muted-foreground)"
                  width={32}
                />
                <Tooltip
                  cursor={{ fill: "var(--muted)" }}
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius)",
                    color: "var(--popover-foreground)",
                  }}
                />
                <Bar
                  dataKey="value"
                  fill="var(--chart-1)"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top costliest vehicles</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={costliestVehicles} layout="vertical">
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="vehicle"
                  tickLine={false}
                  axisLine={false}
                  fontSize={12}
                  stroke="var(--muted-foreground)"
                  width={80}
                />
                <Tooltip
                  cursor={{ fill: "var(--muted)" }}
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius)",
                    color: "var(--popover-foreground)",
                  }}
                />
                <Bar dataKey="cost" radius={[0, 6, 6, 0]}>
                  {costliestVehicles.map((entry, index) => (
                    <Cell
                      key={entry.vehicle}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Cost breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid items-center gap-6 sm:grid-cols-[280px_1fr]">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={costBreakdown}
                    dataKey="value"
                    nameKey="category"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={2}
                  >
                    {costBreakdown.map((entry, index) => (
                      <Cell
                        key={entry.category}
                        fill={CHART_COLORS[index % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)",
                      color: "var(--popover-foreground)",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <ul className="space-y-3">
                {costBreakdown.map((entry, index) => (
                  <li
                    key={entry.category}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="flex items-center gap-2">
                      <span
                        className="size-3 rounded-sm"
                        style={{
                          background: CHART_COLORS[index % CHART_COLORS.length],
                        }}
                      />
                      {entry.category}
                    </span>
                    <span className="font-medium tabular-nums">
                      ₹{entry.value.toLocaleString()}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
