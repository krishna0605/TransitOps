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
          <p className="text-muted-foreground max-w-xs text-sm">
            Smart transport operations — fleet, dispatch, maintenance, and
            finance in one place.
          </p>
        </div>
        <nav className="text-muted-foreground flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {marketingNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.title}
            </Link>
          ))}
          <Link
            href="/login"
            className="hover:text-foreground transition-colors"
          >
            Sign in
          </Link>
        </nav>
      </div>
      <div className="border-t py-4">
        <p className="text-muted-foreground mx-auto max-w-6xl px-6 text-xs lg:px-8">
          © {year} TransitOps. Built for the hackathon.
        </p>
      </div>
    </footer>
  );
}
