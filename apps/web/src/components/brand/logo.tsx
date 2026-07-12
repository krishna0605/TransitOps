import Image from "next/image";

import { cn } from "@/lib/utils";
import { publicEnv } from "@/config/env";

/**
 * Brand mark: the real TransitOps logo plus the app name text.
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
      <Image
        src="/logo.png"
        alt="TransitOps"
        width={32}
        height={32}
        priority
        className="size-8 rounded-md object-contain"
      />
      {showText && (
        <span className="text-base font-semibold tracking-tight">
          {publicEnv.NEXT_PUBLIC_APP_NAME}
        </span>
      )}
    </span>
  );
}
