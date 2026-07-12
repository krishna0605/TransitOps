"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, useReducedMotion } from "motion/react";

import { AppSidebar } from "@/components/app/app-sidebar";
import { AppTopbar } from "@/components/app/app-topbar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { useAuth } from "@/lib/auth/auth-context";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { setSidebarOpen } from "@/store/ui-slice";

function readSidebarPreference() {
  return !document.cookie
    .split(";")
    .some((value) => value.trim() === "sidebar_state=false");
}

export function AppShell({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const dispatch = useAppDispatch();
  const router = useRouter();
  const { user, hydrated } = useAuth();
  const sidebarOpen = useAppSelector((state) => state.ui.sidebarOpen);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    dispatch(setSidebarOpen(readSidebarPreference()));
  }, [dispatch]);

  // Route-level guard: a logged-out visitor to any /(app) route goes to /login.
  // This is the only guard — logged-in users may deep-link to any screen.
  useEffect(() => {
    if (hydrated && !user) {
      router.replace("/login");
    }
  }, [hydrated, user, router]);

  return (
    <SidebarProvider
      open={sidebarOpen}
      onOpenChange={(open) => dispatch(setSidebarOpen(open))}
    >
      <AppSidebar />
      <SidebarInset>
        <AppTopbar />
        <motion.div
          initial={reduceMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: reduceMotion ? 0 : 0.18 }}
          className="min-w-0 flex-1 space-y-6 overflow-x-hidden p-4 sm:p-6"
        >
          {children}
        </motion.div>
      </SidebarInset>
    </SidebarProvider>
  );
}
