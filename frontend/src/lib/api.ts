import type {
  ContextPushResponse,
  HealthResponse,
  MetadataResponse,
  ReplyResponse,
  TickResponse,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(
      (data as { detail?: string; reason?: string })?.detail ||
        (data as { reason?: string })?.reason ||
        `Request failed (${response.status})`,
      response.status,
      data,
    );
  }

  return data as T;
}

export const api = {
  health: () => request<HealthResponse>("/v1/healthz"),

  metadata: () => request<MetadataResponse>("/v1/metadata"),

  pushContext: (body: {
    scope: string;
    context_id: string;
    version: number;
    payload: Record<string, unknown>;
    delivered_at: string;
  }) =>
    request<ContextPushResponse>("/v1/context", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  tick: (body: { now: string; available_triggers: string[] }) =>
    request<TickResponse>("/v1/tick", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  reply: (body: {
    conversation_id: string;
    merchant_id: string;
    customer_id?: string | null;
    from_role: string;
    message: string;
    received_at: string;
    turn_number: number;
  }) =>
    request<ReplyResponse>("/v1/reply", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

export { ApiError };
