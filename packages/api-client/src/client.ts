import createClient, { type Middleware } from "openapi-fetch";

import type { paths } from "./generated/schema";

export interface TransitOpsClientOptions {
  baseUrl: string;
  getAccessToken?: () => Promise<string | null> | string | null;
  timeoutMs?: number;
  fetch?: typeof globalThis.fetch;
}

export function createTransitOpsClient({
  baseUrl,
  getAccessToken,
  timeoutMs = 8_000,
  fetch: configuredFetch = globalThis.fetch,
}: TransitOpsClientOptions) {
  const fetchWithTimeout: typeof globalThis.fetch = async (input, init) => {
    const requestSignal =
      input instanceof Request ? input.signal : init?.signal;
    const timeoutSignal = AbortSignal.timeout(timeoutMs);
    const signal = requestSignal
      ? AbortSignal.any([requestSignal, timeoutSignal])
      : timeoutSignal;
    return configuredFetch(input, { ...init, signal });
  };

  const client = createClient<paths>({
    baseUrl: baseUrl.replace(/\/$/, ""),
    credentials: "include",
    fetch: fetchWithTimeout,
    headers: { Accept: "application/json" },
  });

  if (getAccessToken) {
    const authMiddleware: Middleware = {
      async onRequest({ request }) {
        const token = await getAccessToken();
        if (!token) return;
        const headers = new Headers(request.headers);
        headers.set("Authorization", `Bearer ${token}`);
        return new Request(request, { headers });
      },
    };
    client.use(authMiddleware);
  }

  return client;
}
