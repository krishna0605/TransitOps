import type { Metadata } from "next";

import { FuelExpenseView } from "@/components/app/fuel-expenses/fuel-expense-view";

export const metadata: Metadata = { title: "Fuel & Expenses" };

export default function FuelExpensesPage() {
  return <FuelExpenseView />;
}
