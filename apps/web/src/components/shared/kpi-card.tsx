import Link from "next/link";

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
  href,
}: {
  label: string;
  value: string;
  tone?: Tone;
  href?: string;
}) {
  const card = (
    <Card
      className={cn(
        "border-l-4",
        ACCENT[tone],
        href &&
          "hover:border-ring hover:shadow-md focus-visible:border-ring focus-visible:ring-ring/50 h-full cursor-pointer transition-shadow focus-visible:ring-[3px] focus-visible:outline-none",
      )}
    >
      <CardContent className="p-4">
        <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          {label}
        </p>
        <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link href={href} className="block rounded-xl">
        {card}
      </Link>
    );
  }

  return card;
}
