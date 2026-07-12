import { resolve } from "node:path";
import type { NextConfig } from "next";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  devIndicators: false,
  turbopack: {
    // Pin the workspace root to the monorepo root so a stray lockfile elsewhere
    // on the machine can't make Turbopack infer the wrong root (which makes every
    // route 404). Must be the repo root, not apps/web, since `next` is hoisted to
    // the workspace-root node_modules in this pnpm monorepo.
    root: resolve(__dirname, "..", ".."),
  },
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};

export default nextConfig;
