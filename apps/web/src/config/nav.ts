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

export type AppNavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
  /** Roles this item is primarily scoped to (see mockup Screen 8 RBAC matrix). */
  roles?: string[];
};

export const appNav: AppNavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Fleet", href: "/fleet", icon: Truck },
  { title: "Drivers", href: "/drivers", icon: Users },
  { title: "Trips", href: "/trips", icon: Route },
  { title: "Maintenance", href: "/maintenance", icon: Wrench },
  { title: "Fuel & Expenses", href: "/fuel-expenses", icon: Fuel },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Settings", href: "/settings", icon: Settings },
];

export const marketingNav = [
  { title: "Home", href: "/" },
  { title: "About", href: "/about" },
  { title: "Contact", href: "/contact" },
];
