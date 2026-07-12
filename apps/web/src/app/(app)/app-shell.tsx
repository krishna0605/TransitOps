"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { motion, useReducedMotion } from "motion/react";

import { AppSidebar } from "@/components/app/app-sidebar";
import { AppTopbar } from "@/components/app/app-topbar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { canAccessPath, navItemsForRole } from "@/config/nav";
import { isAppRole, ROLE_STORAGE_KEY } from "@/config/roles";
import { setRole } from "@/store/auth-slice";
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
  const sidebarOpen = useAppSelector((state) => state.ui.sidebarOpen);
  const role = useAppSelector((state) => state.auth.role);
  const reduceMotion = useReducedMotion();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    dispatch(setSidebarOpen(readSidebarPreference()));
  }, [dispatch]);

  useEffect(() => {
    const stored = window.localStorage.getItem(ROLE_STORAGE_KEY);
    if (isAppRole(stored)) {
      dispatch(setRole(stored));
    }
  }, [dispatch]);

  useEffect(() => {
    if (!canAccessPath(role, pathname)) {
      router.replace(navItemsForRole(role)[0]?.href ?? "/dashboard");
    }
  }, [role, pathname, router]);

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
