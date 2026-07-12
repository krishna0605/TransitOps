import { cn } from "@/lib/utils";
import { publicEnv } from "@/config/env";

/**
 * Placeholder brand mark. The visual identity (logo + colors) is not finalized,
 * so this is a neutral geometric mark driven by the swappable `--brand` token.
 * Replace the inner mark with the real logo once it exists — nothing else needs
 * to change.
 */
export function Logo({
  className,
  showText = true,
}: {
  className?: string;
  showText?: boolean;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span
        aria-hidden="true"
        className="grid size-8 place-items-center rounded-lg bg-brand text-brand-foreground shadow-sm"
      >
        <span className="grid grid-cols-2 gap-0.5">
          <span className="size-1.5 rounded-[2px] bg-brand-foreground" />
          <span className="size-1.5 rounded-[2px] bg-brand-foreground/40" />
          <span className="size-1.5 rounded-[2px] bg-brand-foreground/40" />
          <span className="size-1.5 rounded-[2px] bg-brand-foreground" />
        </span>
      </span>
      {showText && (
        <span className="text-base font-semibold tracking-tight">
          {publicEnv.NEXT_PUBLIC_APP_NAME}
        </span>
      )}
    </span>
  );
}
