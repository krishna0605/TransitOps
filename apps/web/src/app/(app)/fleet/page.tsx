import type { Metadata } from "next";

import { FleetView } from "@/components/app/fleet/fleet-view";

export const metadata: Metadata = { title: "Fleet" };

export default function FleetPage() {
  return <FleetView />;
}
