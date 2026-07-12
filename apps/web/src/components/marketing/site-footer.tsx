import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { marketingNav } from "@/config/nav";

export function SiteFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <div className="space-y-2">
          <Logo />
          <p className="max-w-xs text-sm text-muted-foreground">
            Smart transport operations — fleet, dispatch, maintenance, and
            finance in one place.
          </p>
        </div>
        <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
          {marketingNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="transition-colors hover:text-foreground"
            >
              {item.title}
            </Link>
          ))}
          <Link
            href="/login"
            className="transition-colors hover:text-foreground"
          >
            Sign in
          </Link>
        </nav>
      </div>
      <div className="border-t py-4">
        <p className="mx-auto max-w-6xl px-6 text-xs text-muted-foreground lg:px-8">
          © {year} TransitOps. Built for the hackathon.
        </p>
      </div>
    </footer>
  );
}
