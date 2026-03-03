/**
 * Control API. Single Write Path: UI only requests; backend records.
 * POST /api/control/command, GET /api/control/state.
 * If API not implemented: UI shows "NOT IMPLEMENTED" and disables.
 */

import { apiJson, apiFetch } from "./apiClient";

export type ControlState = { emergency_stop: boolean; retract: boolean };
export type ControlStateExtended = ControlState & { llm_blackout?: boolean };

export async function getControlState(): Promise<ControlStateExtended> {
  const res = await apiFetch("/api/control/state");
  if (!res.ok) throw new Error(`Control state: ${res.status}`);
  return res.json();
}

export type CommandPayload = { command_type: string; payload?: Record<string, unknown> };
export type CommandResult = { status: string; command_type?: string; mode?: string; detail?: string };
export type ControlCommandType =
  | "RUN_ENGINE_CYCLE"
  | "SET_MODE"
  | "EMERGENCY_STOP"
  | "RETRACT"
  | "SET_LLM_BLACKOUT";

export async function postCommand(commandType: ControlCommandType, payload?: Record<string, unknown>): Promise<CommandResult> {
  return apiJson<CommandResult>("/api/control/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command_type: commandType, payload: payload ?? {} }),
  });
}

export async function postResume(reason?: string): Promise<CommandResult> {
  return apiJson<CommandResult>("/api/control/resume", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason: reason ?? "Warroom Control Panel" }),
  });
}

/** Check if control API is available (for "NOT IMPLEMENTED" UX). */
export async function isControlApiAvailable(): Promise<boolean> {
  try {
    const r = await apiFetch("/api/control/state");
    return r.ok;
  } catch {
    return false;
  }
}
