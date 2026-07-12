"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, CircleAlert, CircleCheck } from "lucide-react";

import { apiRequest } from "@/lib/api/client";

interface HealthResponse {
  name: string;
  environment: string;
  version: string;
  status: "ok";
}

export function HealthStatus() {
  const health = useQuery({
    queryKey: ["api-health"],
    queryFn: () => apiRequest<HealthResponse>("/health"),
  });

  return (
    <aside
      className="rounded-2xl border bg-white p-6 shadow-sm"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <Activity className="size-5 text-slate-700" aria-hidden="true" />
        <h2 className="font-semibold">Workspace status</h2>
      </div>
      <dl className="mt-6 space-y-4 text-sm">
        <StatusRow label="Web application" status="healthy" />
        <StatusRow
          label="FastAPI service"
          status={
            health.isPending
              ? "checking"
              : health.isSuccess
                ? "healthy"
                : "unavailable"
          }
        />
      </dl>
      {health.isSuccess ? (
        <p className="mt-6 rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
          API {health.data.version} · {health.data.environment}
        </p>
      ) : null}
    </aside>
  );
}

function StatusRow({
  label,
  status,
}: {
  label: string;
  status: "healthy" | "checking" | "unavailable";
}) {
  const healthy = status === "healthy";
  const Icon = healthy
    ? CircleCheck
    : status === "unavailable"
      ? CircleAlert
      : Activity;

  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-slate-600">{label}</dt>
      <dd className="inline-flex items-center gap-2 font-medium capitalize">
        <Icon
          className={
            healthy ? "size-4 text-emerald-600" : "size-4 text-amber-600"
          }
          aria-hidden="true"
        />
        {status}
      </dd>
    </div>
  );
}
