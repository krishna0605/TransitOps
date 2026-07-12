/**
 * Client-side auth session + RBAC derivation.
 *
 * The authoritative role comes from the backend login response. We persist a
 * minimal session in localStorage and derive, from the RBAC matrix (mockup
 * Screen 8), each role's landing screen and the set of nav hrefs it may see.
 *
 * RBAC is enforced at the sidebar-nav + landing level only (see app-shell for
 * the single logged-out -> /login guard); we intentionally do NOT hard-block
 * logged-in users from deep-linking into individual screens.
 */

export const ROLES = [
  "Fleet Manager",
  "Dispatcher",
  "Safety Officer",
  "Financial Analyst",
] as const;

export type Role = (typeof ROLES)[number];

export type AuthSession = {
  name: string;
  email: string;
  role: Role;
};

const STORAGE_KEY = "transitops.session";

/** Landing screen a role is sent to after a successful login. */
export const ROLE_LANDING: Record<Role, string> = {
  "Fleet Manager": "/fleet",
  Dispatcher: "/dashboard",
  "Safety Officer": "/drivers",
  "Financial Analyst": "/fuel-expenses",
};

/**
 * Nav hrefs each role may see in the sidebar. Derived from the RBAC matrix:
 * View or Full => visible; None => hidden. Dashboard + Settings are visible to
 * all roles; Maintenance is grouped with Fleet for the Fleet Manager only.
 */
export const ROLE_ALLOWED_HREFS: Record<Role, readonly string[]> = {
  "Fleet Manager": [
    "/dashboard",
    "/fleet",
    "/drivers",
    "/maintenance",
    "/analytics",
    "/settings",
  ],
  Dispatcher: ["/dashboard", "/fleet", "/trips", "/settings"],
  "Safety Officer": ["/dashboard", "/drivers", "/trips", "/settings"],
  "Financial Analyst": [
    "/dashboard",
    "/fleet",
    "/fuel-expenses",
    "/analytics",
    "/settings",
  ],
};

export function isRole(value: unknown): value is Role {
  return typeof value === "string" && (ROLES as readonly string[]).includes(value);
}

export function landingForRole(role: Role): string {
  return ROLE_LANDING[role] ?? "/dashboard";
}

/** Read the persisted session, or null when logged out / unavailable. */
export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<AuthSession>;
    if (
      typeof parsed?.name === "string" &&
      typeof parsed?.email === "string" &&
      isRole(parsed?.role)
    ) {
      return { name: parsed.name, email: parsed.email, role: parsed.role };
    }
    return null;
  } catch {
    return null;
  }
}

export function setSession(session: AuthSession): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}

export const SESSION_STORAGE_KEY = STORAGE_KEY;
