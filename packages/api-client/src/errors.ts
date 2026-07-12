export interface ApiErrorPayload {
  code: string;
  message: string;
  details: Record<string, unknown>;
  request_id: string;
}

export class ApiContractError extends Error {
  constructor(
    public readonly status: number,
    public readonly payload: ApiErrorPayload,
  ) {
    super(payload.message);
    this.name = "ApiContractError";
  }
}

interface ApiResult<T> {
  data?: T;
  error?: unknown;
  response: Response;
}

function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<ApiErrorPayload>;
  return (
    typeof candidate.code === "string" &&
    typeof candidate.message === "string" &&
    typeof candidate.request_id === "string" &&
    typeof candidate.details === "object" &&
    candidate.details !== null
  );
}

export function unwrapApiResponse<T>({
  data,
  error,
  response,
}: ApiResult<T>): T {
  if (response.ok) return data as T;

  const fallback: ApiErrorPayload = {
    code: "HTTP_ERROR",
    message: `Request failed with status ${response.status}.`,
    details: {},
    request_id: response.headers.get("x-request-id") ?? "unknown",
  };
  throw new ApiContractError(
    response.status,
    isApiErrorPayload(error) ? error : fallback,
  );
}
