/**
 * Warroom snapshot key groups.
 * UI only consumes backend snapshot keys (read-only).
 */

export const COMMANDER_STATUS_KEYS = [
  "operation_mode",
  "regime_current",
  "active_session",
  "session_state",
  "timezone",
  "comm_health",
  "engine_heartbeat",
  "llm_status",
] as const;

export const COMMANDER_STRATEGY_KEYS = [
  "allocation_matrix",
  "fleet_budget_snapshot",
] as const;

export const FLEET_FORCE_KEYS = [
  "core_force_state",
  "swing_force_state",
  "strike_force_state",
] as const;

export const TARGET_KEYS = [
  "targets_core",
  "targets_swing",
  "targets_strike",
] as const;

export const CONTROL_CHECK_KEYS = [
  "operation_mode",
  "risk_guard",
  "regime_current",
  "engine_heartbeat",
  "comm_health",
  "llm_status",
  "active_session",
] as const;
