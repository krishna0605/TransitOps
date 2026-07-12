"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ThemeToggle } from "@/components/app/theme-toggle";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { marketingNav } from "@/config/nav";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="bg-background/80 sticky top-0 z-40 border-b backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6 lg:px-8">
        <Link href="/" aria-label="TransitOps home">
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {marketingNav.map((item) => {
            const active = pathname === item.href;
            return (
              <Button
                key={item.href}
                asChild
                variant="ghost"
                size="sm"
                className={cn(active && "bg-accent text-accent-foreground")}
              >
                <Link href={item.href}>{item.title}</Link>
              </Button>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button
            asChild
            variant="ghost"
            size="sm"
            className="hidden sm:inline-flex"
          >
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild size="sm">
            <Link href="/dashboard">Demo App</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
