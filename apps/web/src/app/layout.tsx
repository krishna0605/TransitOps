import type { Metadata } from "next";

import { Toaster } from "@/components/ui/sonner";
import { AppProviders } from "@/providers/app-providers";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "TransitOps",
    template: "%s · TransitOps",
  },
  description: "Smart transport operations platform",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
