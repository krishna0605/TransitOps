import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * Maps every domain status value (vehicle / driver / trip / maintenance /
 * expense) to a consistent, theme-aware pill. Colors are semantic (green = good,
 * blue = active, amber = attention, red = blocked/stopped, slate = neutral) and
 * deliberately independent of the brand color, which is still undecided.
 */
const STATUS_STYLES: Record<string, string> = {
  // shared "good / available"
  Available: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  Completed: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  // active / in-progress
  "On Trip": "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  Dispatched: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  Active: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  // attention / maintenance
  "In Shop": "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  // blocked / stopped
  Retired: "bg-red-500/15 text-red-700 dark:text-red-400",
  Suspended: "bg-red-500/15 text-red-700 dark:text-red-400",
  Cancelled: "bg-red-500/15 text-red-700 dark:text-red-400",
  // neutral
  Draft: "bg-muted text-muted-foreground",
  "Off Duty": "bg-muted text-muted-foreground",
};

export function StatusBadge({
  status,
  className,
}: {
  status: string;
  className?: string;
}) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "border-transparent font-medium",
        STATUS_STYLES[status] ?? "bg-muted text-muted-foreground",
        className,
      )}
    >
      {status}
    </Badge>
  );
}
