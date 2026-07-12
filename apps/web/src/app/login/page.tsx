import type { Metadata } from "next";

import { LoginForm } from "@/components/auth/login-form";
import { Logo } from "@/components/brand/logo";

export const metadata: Metadata = {
  title: "Sign in",
  description: "Sign in to your TransitOps account.",
};

const ROLES = [
  "Fleet Manager",
  "Dispatcher",
  "Safety Officer",
  "Financial Analyst",
];

const ROLE_ACCESS = [
  "Fleet Manager → Fleet, Maintenance",
  "Dispatcher → Dashboard, Trips",
  "Safety Officer → Drivers, Compliance",
  "Financial Analyst → Fuel & Expenses, Analytics",
];

export default function LoginPage() {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between bg-slate-950 p-10 text-slate-100 lg:flex">
        <div className="text-slate-50">
          <Logo />
          <p className="mt-2 text-sm text-slate-400">
            Smart Transport Operations Platform
          </p>
        </div>

        <div>
          <p className="text-sm font-medium text-slate-300">
            One login, four roles:
          </p>
          <ul className="mt-4 space-y-3">
            {ROLES.map((role) => (
              <li key={role} className="flex items-center gap-3 text-slate-200">
                <span className="bg-brand size-1.5 rounded-full" />
                {role}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-slate-500">TRANSITOPS © 2026 · RBAC</p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <div className="lg:hidden">
            <Logo />
          </div>
          <div className="mt-6 lg:mt-0">
            <h1 className="text-2xl font-semibold tracking-tight">
              Sign in to your account
            </h1>
            <p className="text-muted-foreground mt-1 text-sm">
              Enter your credentials to continue.
            </p>
          </div>

          <div className="mt-8">
            <LoginForm />
          </div>

          <div className="bg-muted/40 mt-8 rounded-lg border p-4">
            <p className="text-sm font-medium">Access is scoped by role</p>
            <ul className="text-muted-foreground mt-2 space-y-1 text-sm">
              {ROLE_ACCESS.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
