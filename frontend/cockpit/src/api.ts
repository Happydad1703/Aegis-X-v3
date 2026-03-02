/**
 * API layer — DB-Only Read. No computation. Signal_Interface_ICD + Master_Process_Map.
 */
const BASE = "";

export async function fetchSnapshot(key: string): Promise<unknown> {
  const r = await fetch(`${BASE}/api/snapshot/latest?key=${encodeURIComponent(key)}`);
  if (!r.ok) throw new Error(`Snapshot ${key}: ${r.status}`);
  return r.json();
}

export async function fetchControlState(): Promise<unknown> {
  const r = await fetch(`${BASE}/api/control/state`);
  if (!r.ok) throw new Error(`Control state: ${r.status}`);
  return r.json();
}

export async function postCommand(commandType: string, payload?: Record<string, unknown>): Promise<unknown> {
  const r = await fetch(`${BASE}/api/control/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command_type: commandType, payload: payload ?? {} }),
  });
  return r.json();
}

export async function fetchOrders(limit = 50): Promise<unknown> {
  const r = await fetch(`${BASE}/api/orders?limit=${limit}`);
  if (!r.ok) throw new Error(`Orders: ${r.status}`);
  return r.json();
}

export async function fetchIncidents(limit = 50): Promise<unknown> {
  const r = await fetch(`${BASE}/api/incidents?limit=${limit}`);
  if (!r.ok) throw new Error(`Incidents: ${r.status}`);
  return r.json();
}

/** Allowed snapshot keys — must match Signal_Interface_ICD.md (SSOT: backend snapshot_keys.py). */
export const CORE_SNAPSHOT_KEYS = [
  "engine_heartbeat",
  "comm_health",
  "llm_status",
  "operation_mode",
  "regime_current",
  "risk_guard",
] as const;

export const ALL_PANEL_SNAPSHOT_KEYS = [
  ...CORE_SNAPSHOT_KEYS,
  "allocation_matrix",
  "fleet_budget_snapshot",
  "targets_core",
  "targets_swing",
  "targets_strike",
] as const;
