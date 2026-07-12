import type { Metadata } from "next";
import { Suspense } from "react";

import { FleetView } from "@/components/app/fleet/fleet-view";

export const metadata: Metadata = { title: "Fleet" };

export default function FleetPage() {
  return (
    <Suspense>
      <FleetView />
    </Suspense>
  );
}
