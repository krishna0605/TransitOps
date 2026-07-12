export const APP_ROLES = [
  "Fleet Manager",
  "Dispatcher",
  "Safety Officer",
  "Financial Analyst",
] as const;

export type AppRole = (typeof APP_ROLES)[number];

/** Fallback when no role has been selected yet (full access, avoids lockout). */
export const DEFAULT_ROLE: AppRole = "Fleet Manager";

/** localStorage key holding the role chosen at login. */
export const ROLE_STORAGE_KEY = "transitops.role";

export function isAppRole(value: unknown): value is AppRole {
  return (
    typeof value === "string" && (APP_ROLES as readonly string[]).includes(value)
  );
}

const ROLE_PROFILES: Record<AppRole, { name: string; initials: string }> = {
  "Fleet Manager": { name: "Fleet Manager", initials: "FM" },
  Dispatcher: { name: "Dispatch Desk", initials: "DD" },
  "Safety Officer": { name: "Safety Officer", initials: "SO" },
  "Financial Analyst": { name: "Finance Analyst", initials: "FA" },
};

export function roleProfile(role: AppRole) {
  return ROLE_PROFILES[role];
}
