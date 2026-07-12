import {
  ArrowRight,
  BarChart3,
  Fuel,
  Gauge,
  Route,
  ShieldCheck,
  Truck,
  Users,
  Wrench,
} from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const FEATURES = [
  {
    icon: Truck,
    title: "Vehicle registry",
    description:
      "A single master list of vehicles with capacity, odometer, and lifecycle status.",
  },
  {
    icon: Users,
    title: "Driver & safety",
    description:
      "Track licenses, expiry, safety scores, and duty status in one compliance view.",
  },
  {
    icon: Route,
    title: "Trip dispatch",
    description:
      "Assign available vehicles and drivers with capacity and eligibility checks built in.",
  },
  {
    icon: Wrench,
    title: "Maintenance",
    description:
      "Log service records; vehicles move to the shop and out of dispatch automatically.",
  },
  {
    icon: Fuel,
    title: "Fuel & expenses",
    description:
      "Capture fuel and other costs, and roll them up into operational cost per vehicle.",
  },
  {
    icon: BarChart3,
    title: "Analytics",
    description:
      "Fuel efficiency, fleet utilization, operational cost, and vehicle ROI at a glance.",
  },
];

const KPIS = [
  { label: "Active vehicles", value: "53" },
  { label: "Active trips", value: "18" },
  { label: "Drivers on duty", value: "26" },
  { label: "Fleet utilization", value: "81%" },
];

export default function HomePage() {
  return (
    <main>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pt-16 pb-8 lg:px-8 lg:pt-24">
        <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <Badge variant="outline" className="mb-5 gap-1.5">
              <span className="bg-brand size-1.5 rounded-full" />
              Smart Transport Operations
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight text-balance sm:text-6xl">
              Run your entire fleet from one clean workspace.
            </h1>
            <p className="text-muted-foreground mt-6 max-w-xl text-lg leading-8">
              TransitOps digitizes vehicles, drivers, dispatch, maintenance, and
              expenses — with the business rules enforced for you and live
              operational insight built in.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href="/dashboard">
                  Demo App
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/about">Learn more</Link>
              </Button>
            </div>
            <div className="text-muted-foreground mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm">
              <span className="inline-flex items-center gap-2">
                <ShieldCheck className="size-4 text-emerald-600" />
                Rules enforced in code
              </span>
              <span className="inline-flex items-center gap-2">
                <Gauge className="size-4 text-blue-600" />
                Real-time KPIs
              </span>
            </div>
          </div>

          {/* KPI preview panel */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardDescription>Live fleet snapshot</CardDescription>
              <CardTitle>Operations at a glance</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              {KPIS.map((kpi) => (
                <div key={kpi.label} className="bg-card rounded-lg border p-4">
                  <p className="text-3xl font-semibold tracking-tight">
                    {kpi.value}
                  </p>
                  <p className="text-muted-foreground mt-1 text-sm">
                    {kpi.label}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight">
            Everything the operation needs
          </h2>
          <p className="text-muted-foreground mt-3">
            Six modules that cover the full lifecycle, from registration to
            reporting.
          </p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <Card key={feature.title} className="h-full">
              <CardHeader>
                <div className="bg-brand/10 text-brand mb-2 grid size-10 place-items-center rounded-lg">
                  <feature.icon className="size-5" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-6 pb-20 lg:px-8">
        <Card className="bg-primary text-primary-foreground overflow-hidden">
          <CardContent className="flex flex-col items-start gap-4 p-8 sm:flex-row sm:items-center sm:justify-between sm:p-10">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">
                Ready to dispatch your first trip?
              </h2>
              <p className="text-primary-foreground/80 mt-2">
                Sign in and start managing your fleet in minutes.
              </p>
            </div>
            <Button asChild size="lg" variant="secondary">
              <Link href="/login">
                Get started
                <ArrowRight className="size-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
