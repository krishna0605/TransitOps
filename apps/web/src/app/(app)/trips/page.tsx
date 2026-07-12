import type { Metadata } from "next";
import { Suspense } from "react";

import { TripDispatcher } from "@/components/app/trips/trip-dispatcher";

export const metadata: Metadata = { title: "Trips" };

export default function TripsPage() {
  return (
    <Suspense>
      <TripDispatcher />
    </Suspense>
  );
}
