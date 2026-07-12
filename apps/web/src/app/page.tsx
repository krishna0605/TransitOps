import { BusFront, ShieldCheck, Waypoints } from "lucide-react";

import { HealthStatus } from "@/components/feedback/health-status";
import { publicEnv } from "@/config/env";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16 lg:px-8">
      <section className="grid items-center gap-12 lg:grid-cols-[1.3fr_0.7fr]">
        <div>
          <div className="mb-6 inline-flex items-center gap-3 rounded-full border bg-white px-4 py-2 text-sm font-medium shadow-sm">
            <BusFront className="size-5 text-amber-600" aria-hidden="true" />
            {publicEnv.NEXT_PUBLIC_APP_NAME}
          </div>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-950 sm:text-6xl">
            Transport operations, built on a reliable foundation.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            The TransitOps workspace is ready for fleet, driver, dispatch,
            maintenance, and finance modules. This page verifies the frontend
            and API scaffold before domain development begins.
          </p>
          <div className="mt-8 flex flex-wrap gap-4 text-sm text-slate-600">
            <span className="inline-flex items-center gap-2">
              <ShieldCheck
                className="size-4 text-emerald-600"
                aria-hidden="true"
              />
              Typed and validated
            </span>
            <span className="inline-flex items-center gap-2">
              <Waypoints className="size-4 text-blue-600" aria-hidden="true" />
              Modular monolith
            </span>
          </div>
        </div>

        <HealthStatus />
      </section>
    </main>
  );
}
