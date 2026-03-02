/**
 * Snapshot read-only API. DB-Only Read; no computation.
 * GET /api/snapshot/{key}, GET /api/snapshot/latest?key=...
 */

import { apiJson } from "./apiClient";

export type SnapshotRow = {
  snapshot_key: string;
  data: Record<string, unknown>;
  source_name?: string | null;
  generated_at?: string | null;
  refresh_rate_sec?: number | null;
  freshness_status?: string | null;
};

export async function getSnapshot(key: string): Promise<SnapshotRow> {
  return apiJson<SnapshotRow>(`/api/snapshot/${encodeURIComponent(key)}`);
}

export async function getLatestSnapshot(key: string): Promise<SnapshotRow> {
  return apiJson<SnapshotRow>(`/api/snapshot/latest?key=${encodeURIComponent(key)}`);
}

/** 6 core snapshot keys for Sensor Fusion (documented). */
export const CORE_SNAPSHOT_KEYS = [
  "regime_current",
  "allocation_matrix",
  "fleet_budget_snapshot",
  "risk_guard",
  "operation_mode",
  "engine_heartbeat",
] as const;

export const COMM_LLM_KEYS = ["comm_health", "llm_status"] as const;
