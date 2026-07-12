import {
  BarChart3,
  Fuel,
  LayoutDashboard,
  type LucideIcon,
  Route,
  Settings,
  Truck,
  Users,
  Wrench,
} from "lucide-react";

import type { AppRole } from "@/config/roles";

export type AppNavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
  /** Roles allowed to see/use this item. Omit = all roles. */
  roles?: AppRole[];
};

export const appNav: AppNavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  {
    title: "Fleet",
    href: "/fleet",
    icon: Truck,
    roles: ["Fleet Manager", "Dispatcher"],
  },
  {
    title: "Drivers",
    href: "/drivers",
    icon: Users,
    roles: ["Fleet Manager", "Dispatcher", "Safety Officer"],
  },
  {
    title: "Trips",
    href: "/trips",
    icon: Route,
    roles: ["Fleet Manager", "Dispatcher"],
  },
  {
    title: "Maintenance",
    href: "/maintenance",
    icon: Wrench,
    roles: ["Fleet Manager"],
  },
  {
    title: "Fuel & Expenses",
    href: "/fuel-expenses",
    icon: Fuel,
    roles: ["Fleet Manager", "Financial Analyst"],
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    roles: ["Fleet Manager", "Financial Analyst"],
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    roles: ["Fleet Manager"],
  },
];

export function navItemsForRole(role: AppRole): AppNavItem[] {
  return appNav.filter((item) => !item.roles || item.roles.includes(role));
}

export function canAccessPath(role: AppRole, pathname: string): boolean {
  const match = appNav.find(
    (item) => pathname === item.href || pathname.startsWith(`${item.href}/`),
  );
  if (!match) return true;
  return !match.roles || match.roles.includes(role);
}

export const marketingNav = [
  { title: "Home", href: "/" },
  { title: "About", href: "/about" },
  { title: "Contact", href: "/contact" },
];
