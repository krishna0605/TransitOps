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

const ALL_ROLES = [
  "Fleet Manager",
  "Dispatcher",
  "Safety Officer",
  "Financial Analyst",
];

export const appNav: AppNavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard, roles: ALL_ROLES },
  {
    title: "Fleet",
    href: "/fleet",
    icon: Truck,
    roles: ["Fleet Manager", "Dispatcher", "Financial Analyst"],
  },
  {
    title: "Drivers",
    href: "/drivers",
    icon: Users,
    roles: ["Fleet Manager", "Safety Officer"],
  },
  {
    title: "Trips",
    href: "/trips",
    icon: Route,
    roles: ["Dispatcher", "Safety Officer"],
  },
  { title: "Maintenance", href: "/maintenance", icon: Wrench, roles: ["Fleet Manager"] },
  {
    title: "Fuel & Expenses",
    href: "/fuel-expenses",
    icon: Fuel,
    roles: ["Financial Analyst"],
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    roles: ["Fleet Manager", "Financial Analyst"],
  },
  { title: "Settings", href: "/settings", icon: Settings, roles: ALL_ROLES },
];

export const marketingNav = [
  { title: "Home", href: "/" },
  { title: "About", href: "/about" },
  { title: "Contact", href: "/contact" },
];
