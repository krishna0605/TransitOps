import type { Metadata } from "next";
import {
  BadgeDollarSign,
  ClipboardCheck,
  Route,
  ShieldCheck,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "About",
  description:
    "TransitOps digitizes the full transport operations lifecycle for logistics teams.",
};

const ROLES = [
  {
    icon: Route,
    title: "Fleet Manager",
    description:
      "Oversees fleet assets, maintenance, vehicle lifecycle, and operational efficiency.",
  },
  {
    icon: ClipboardCheck,
    title: "Dispatcher",
    description:
      "Creates trips, assigns vehicles and drivers, and monitors active deliveries.",
  },
  {
    icon: ShieldCheck,
    title: "Safety Officer",
    description:
      "Ensures driver compliance, tracks license validity, and monitors safety scores.",
  },
  {
    icon: BadgeDollarSign,
    title: "Financial Analyst",
    description:
      "Reviews operational expenses, fuel consumption, maintenance costs, and profitability.",
  },
];

export default function AboutPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16 lg:px-8">
      <div className="max-w-2xl">
        <p className="text-sm font-medium text-brand">About TransitOps</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight sm:text-5xl">
          Operations without the spreadsheets.
        </h1>
        <p className="mt-6 text-lg leading-8 text-muted-foreground">
          Many logistics companies still run on spreadsheets and paper
          logbooks, which leads to scheduling conflicts, missed maintenance,
          expired licenses, and poor visibility. TransitOps replaces that with a
          single system that manages the complete lifecycle of transport
          operations — from vehicle registration and driver management to
          dispatch, maintenance, fuel logging, and analytics.
        </p>
      </div>

      <section className="mt-16">
        <h2 className="text-2xl font-semibold tracking-tight">
          Built for four roles
        </h2>
        <p className="mt-2 text-muted-foreground">
          Access is scoped by role, so each team sees exactly what they need.
        </p>
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {ROLES.map((role) => (
            <Card key={role.title}>
              <CardHeader>
                <div className="mb-2 grid size-10 place-items-center rounded-lg bg-brand/10 text-brand">
                  <role.icon className="size-5" />
                </div>
                <CardTitle className="text-lg">{role.title}</CardTitle>
                <CardDescription>{role.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section className="mt-16">
        <h2 className="text-2xl font-semibold tracking-tight">How it works</h2>
        <ol className="mt-6 space-y-4">
          {[
            "Register vehicles and drivers with their capacity, license, and status.",
            "Dispatch a trip — capacity and eligibility rules are checked automatically.",
            "Vehicle and driver statuses flip to On Trip, then back to Available on completion.",
            "Log maintenance and fuel; costs roll up into per-vehicle analytics and ROI.",
          ].map((step, index) => (
            <li key={step} className="flex gap-4">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-brand text-sm font-semibold text-brand-foreground">
                {index + 1}
              </span>
              <p className="pt-1 text-muted-foreground">{step}</p>
            </li>
          ))}
        </ol>
      </section>

      <Card className="mt-16 bg-muted/40">
        <CardContent className="p-6">
          <p className="text-sm text-muted-foreground">
            Built during an 8-hour hackathon on a Next.js + FastAPI + PostgreSQL
            stack, with role-based access control and the mandatory business
            rules enforced in the backend.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
