import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Tone = "default" | "success" | "warning" | "info";

const ACCENT: Record<Tone, string> = {
  default: "border-l-border",
  success: "border-l-emerald-500",
  warning: "border-l-amber-500",
  info: "border-l-blue-500",
};

export function KpiCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: Tone;
}) {
  return (
    <Card className={cn("border-l-4", ACCENT[tone])}>
      <CardContent className="p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
      </CardContent>
    </Card>
  );
}
