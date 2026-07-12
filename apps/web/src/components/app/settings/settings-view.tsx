"use client";

import {
  Building2,
  Check,
  Eye,
  Minus,
  ScrollText,
  ShieldCheck,
  Users,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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

type Access = "Full" | "View" | "None";

const MODULES = ["Fleet", "Drivers", "Trips", "Fuel & Exp.", "Analytics"];

const MATRIX: { role: string; access: Access[] }[] = [
  { role: "Fleet Manager", access: ["Full", "Full", "None", "None", "Full"] },
  { role: "Dispatcher", access: ["View", "None", "Full", "None", "None"] },
  { role: "Safety Officer", access: ["None", "Full", "View", "None", "None"] },
  {
    role: "Financial Analyst",
    access: ["View", "None", "None", "Full", "Full"],
  },
];

const AUDIT_LOG: { actor: string; action: string; at: string }[] = [
  {
    actor: "Dispatcher",
    action: "changed Trip TR001 status → Dispatched",
    at: "2026-07-12 09:14",
  },
  {
    actor: "Fleet Manager",
    action: "marked Vehicle GJ-01-AB-1234 as In Service",
    at: "2026-07-12 08:47",
  },
  {
    actor: "Safety Officer",
    action: "flagged Driver D-208 for license renewal",
    at: "2026-07-11 17:32",
  },
  {
    actor: "Financial Analyst",
    action: "approved Fuel expense EXP-5591 (₹4,820)",
    at: "2026-07-11 15:06",
  },
  {
    actor: "Super Admin",
    action: "updated role permissions for Dispatcher",
    at: "2026-07-11 11:20",
  },
  {
    actor: "Super Admin",
    action: "changed currency preference → INR",
    at: "2026-07-10 18:58",
  },
];

function AccessCell({ access }: { access: Access }) {
  if (access === "Full") {
    return (
      <Badge className="gap-1 border-transparent bg-emerald-600 text-white hover:bg-emerald-600 dark:bg-emerald-500 dark:text-emerald-950">
        <Check className="size-3.5" />
        Full
      </Badge>
    );
  }
  if (access === "View") {
    return (
      <Badge
        variant="outline"
        className="gap-1 border-blue-500/50 text-blue-600 dark:border-blue-400/50 dark:text-blue-400"
      >
        <Eye className="size-3.5" />
        View
      </Badge>
    );
  }
  return (
    <Badge
      variant="secondary"
      className="text-muted-foreground gap-1 bg-muted"
    >
      <Minus className="size-3.5" />
      None
    </Badge>
  );
}

export function SettingsView() {
  const [company, setCompany] = useState("Gandhinagar Logistics LLP");
  const [currency, setCurrency] = useState("INR");
  const [distanceUnit, setDistanceUnit] = useState("km");

  return (
    <>
      <PageHeader
        title="System Administration"
        description="Elevated control panel — organization configuration, access governance, and activity oversight."
        actions={
          <Badge className="gap-1.5 border-transparent bg-brand px-3 py-1 text-sm text-brand-foreground">
            <ShieldCheck className="size-4" />
            Super Admin
          </Badge>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <span className="bg-brand/10 text-brand grid size-9 place-items-center rounded-lg">
                <Building2 className="size-4.5" />
              </span>
              <div className="space-y-0.5">
                <CardTitle>Organization Settings</CardTitle>
                <CardDescription>Organization-wide preferences.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Company name</Label>
              <Input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Currency</Label>
                <Select value={currency} onValueChange={setCurrency}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INR">₹ INR</SelectItem>
                    <SelectItem value="USD">$ USD</SelectItem>
                    <SelectItem value="EUR">€ EUR</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Distance unit</Label>
                <Select value={distanceUnit} onValueChange={setDistanceUnit}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="km">Kilometers</SelectItem>
                    <SelectItem value="mi">Miles</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button onClick={() => toast.success("Settings saved")}>
              Save changes
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <span className="bg-brand/10 text-brand grid size-9 place-items-center rounded-lg">
                <ShieldCheck className="size-4.5" />
              </span>
              <div className="space-y-0.5">
                <CardTitle>Access Governance</CardTitle>
                <CardDescription>
                  Authoritative matrix of what each role can do across modules.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-emerald-600 dark:bg-emerald-500" />
                Full access
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="size-2 rounded-full border border-blue-500/60" />
                View-only
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-muted-foreground/40" />
                No access
              </span>
            </div>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>
                      <span className="inline-flex items-center gap-1.5">
                        <Users className="size-3.5" />
                        Role
                      </span>
                    </TableHead>
                    {MODULES.map((module) => (
                      <TableHead key={module}>{module}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {MATRIX.map((row) => (
                    <TableRow key={row.role}>
                      <TableCell className="font-medium">{row.role}</TableCell>
                      {row.access.map((access, index) => (
                        <TableCell key={MODULES[index]}>
                          <AccessCell access={access} />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center gap-2">
            <span className="bg-brand/10 text-brand grid size-9 place-items-center rounded-lg">
              <ScrollText className="size-4.5" />
            </span>
            <div className="space-y-0.5">
              <CardTitle className="flex items-center gap-2">
                Audit Log
                <Badge
                  variant="secondary"
                  className="text-muted-foreground font-normal"
                >
                  Static demo
                </Badge>
              </CardTitle>
              <CardDescription>
                Recent privileged and role activity across the organization.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <ul className="divide-y">
            {AUDIT_LOG.map((entry) => (
              <li
                key={`${entry.at}-${entry.action}`}
                className="flex flex-col gap-1 px-6 py-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <span className="text-sm">
                  <span className="font-medium">{entry.actor}</span>{" "}
                  <span className="text-muted-foreground">{entry.action}</span>
                </span>
                <span className="text-muted-foreground text-xs tabular-nums">
                  {entry.at}
                </span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </>
  );
}
