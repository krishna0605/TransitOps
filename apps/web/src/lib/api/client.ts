import { publicEnv } from "@/config/env";

export interface ApiErrorPayload {
  code: string;
  message: string;
  details: Record<string, unknown>;
  request_id: string;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly payload: ApiErrorPayload,
  ) {
    super(payload.message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = 8_000, ...requestInit } = options;
  const response = await fetch(`${publicEnv.NEXT_PUBLIC_API_BASE_URL}${path}`, {
    ...requestInit,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...requestInit.headers,
    },
    signal: requestInit.signal ?? AbortSignal.timeout(timeoutMs),
  });

  if (!response.ok) {
    const fallback: ApiErrorPayload = {
      code: "HTTP_ERROR",
      message: `Request failed with status ${response.status}.`,
      details: {},
      request_id: response.headers.get("x-request-id") ?? "unknown",
    };
    const payload = (await response
      .json()
      .catch(() => fallback)) as ApiErrorPayload;
    throw new ApiError(response.status, payload);
  }

  return (await response.json()) as T;
}
