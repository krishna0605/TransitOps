"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Logo } from "@/components/brand/logo";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import { appNav } from "@/config/nav";
import { useAuth } from "@/lib/auth/auth-context";

export function AppSidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  // RBAC: show items with no role restriction, or those that include the
  // current role. Until the session hydrates (user null), show unrestricted
  // items only so we never flash screens a role shouldn't see.
  const items = appNav.filter(
    (item) => !item.roles || (user ? item.roles.includes(user.role) : false),
  );

  return (
    <Sidebar collapsible="offcanvas">
      <SidebarHeader className="h-16 justify-center border-b px-4">
        <Link
          href="/"
          aria-label="TransitOps"
          className="flex items-center in-data-[collapsible=icon]:justify-center"
        >
          <Logo />
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => {
                const active =
                  pathname === item.href ||
                  pathname.startsWith(`${item.href}/`);
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={active}
                      tooltip={item.title}
                    >
                      <Link href={item.href}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
