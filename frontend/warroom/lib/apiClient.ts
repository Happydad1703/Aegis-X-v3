/**
 * API fetch wrapper: timeout, retry, error normalization.
 * No business logic; no API keys. Only NEXT_PUBLIC_API_BASE_URL.
 */

const BASE = typeof window !== "undefined" ? (process.env.NEXT_PUBLIC_API_BASE_URL ?? "") : process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const TIMEOUT_MS = 15_000;
const RETRIES = 2;

export type ApiError = { status: number; message: string; body?: unknown };
export type ApiTelemetry = {
  lastUpdatedIso: string | null;
  lastLatencyMs: number | null;
};

let telemetry: ApiTelemetry = {
  lastUpdatedIso: null,
  lastLatencyMs: null,
};

function updateTelemetry(latencyMs: number | null) {
  telemetry = {
    lastUpdatedIso: new Date().toISOString(),
    lastLatencyMs: latencyMs,
  };
}

async function fetchWithTimeout(url: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), TIMEOUT_MS);
  const start = typeof performance !== "undefined" ? performance.now() : Date.now();
  try {
    const res = await fetch(url, { ...init, signal: controller.signal });
    const end = typeof performance !== "undefined" ? performance.now() : Date.now();
    updateTelemetry(Math.round(end - start));
    clearTimeout(id);
    return res;
  } catch (e) {
    updateTelemetry(null);
    clearTimeout(id);
    throw e;
  }
}

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = path.startsWith("http") ? path : `${BASE.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
  let lastError: unknown;
  for (let i = 0; i <= RETRIES; i++) {
    try {
      const res = await fetchWithTimeout(url, init);
      return res;
    } catch (e) {
      lastError = e;
      if (i < RETRIES) await new Promise((r) => setTimeout(r, 500 * (i + 1)));
    }
  }
  throw lastError;
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await apiFetch(path, init);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err: ApiError = { status: res.status, message: (body as { detail?: string })?.detail ?? res.statusText, body };
    throw err;
  }
  return body as T;
}

export function getApiBase(): string {
  return BASE || "";
}

export function getApiTelemetry(): ApiTelemetry {
  return telemetry;
}
