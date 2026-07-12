import type { Metadata } from "next";

import { TripDispatcher } from "@/components/app/trips/trip-dispatcher";

export const metadata: Metadata = { title: "Trips" };

export default function TripsPage() {
  return <TripDispatcher />;
}
