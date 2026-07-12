import type { Metadata } from "next";

import { DriversView } from "@/components/app/drivers/drivers-view";

export const metadata: Metadata = { title: "Drivers" };

export default function DriversPage() {
  return <DriversView />;
}
