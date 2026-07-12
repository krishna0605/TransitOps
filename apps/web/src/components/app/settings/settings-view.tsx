"use client";

import { Check, Eye, Minus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
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
  { role: "Financial Analyst", access: ["View", "None", "None", "Full", "Full"] },
];

function AccessCell({ access }: { access: Access }) {
  if (access === "Full") {
    return (
      <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
        <Check className="size-4" />
        <span className="text-xs">Full</span>
      </span>
    );
  }
  if (access === "View") {
    return (
      <span className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400">
        <Eye className="size-4" />
        <span className="text-xs">View</span>
      </span>
    );
  }
  return <Minus className="size-4 text-muted-foreground" />;
}

export function SettingsView() {
  const [company, setCompany] = useState("Gandhinagar Logistics LLP");
  const [currency, setCurrency] = useState("INR");
  const [distanceUnit, setDistanceUnit] = useState("km");

  return (
    <>
      <PageHeader
        title="Settings"
        description="Organization preferences and role-based access."
      />

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader>
            <CardTitle>General</CardTitle>
            <CardDescription>Organization-wide preferences.</CardDescription>
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
            <CardTitle>Role-based access</CardTitle>
            <CardDescription>
              Reference matrix of what each role can do.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Role</TableHead>
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
          </CardContent>
        </Card>
      </div>
    </>
  );
}
