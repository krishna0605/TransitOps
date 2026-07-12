"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  type AuthSession,
  clearSession,
  getSession,
  SESSION_STORAGE_KEY,
  setSession,
} from "@/lib/auth/session";

type AuthContextValue = {
  /** Current signed-in user, or null when logged out. */
  user: AuthSession | null;
  /** True once the session has been read from localStorage on the client. */
  hydrated: boolean;
  /** Persist a session (called by the login form after a 200). */
  login: (session: AuthSession) => void;
  /** Clear the session (called by the user menu on sign out). */
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const [user, setUser] = useState<AuthSession | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Read the persisted session after mount to avoid an SSR hydration mismatch.
  useEffect(() => {
    setUser(getSession());
    setHydrated(true);

    // Keep the session in sync across tabs.
    function onStorage(event: StorageEvent) {
      if (event.key === SESSION_STORAGE_KEY) {
        setUser(getSession());
      }
    }
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const login = useCallback((session: AuthSession) => {
    setSession(session);
    setUser(session);
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, hydrated, login, logout }),
    [user, hydrated, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
