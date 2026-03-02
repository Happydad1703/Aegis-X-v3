/**
 * Health API. Read-only.
 * GET /api/health or /healthz (project standard).
 */

import { apiJson } from "./apiClient";

export type HealthPayload = {
  engine_heartbeat?: unknown;
  comm_health?: unknown;
  llm_status?: unknown;
  operation_mode?: unknown;
  meta?: { source?: string; required_keys?: string[] };
};

export async function getHealth(): Promise<HealthPayload> {
  try {
    return await apiJson<HealthPayload>("/api/health");
  } catch {
    try {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? ""}/healthz`);
      if (r.ok) return { meta: { source: "healthz" } };
    } catch {
      // ignore
    }
    throw new Error("Health unreachable");
  }
}
