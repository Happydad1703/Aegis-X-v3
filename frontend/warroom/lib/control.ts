/**
 * Control API. Single Write Path: UI only requests; backend records.
 * POST /api/control/command, GET /api/control/state.
 * If API not implemented: UI shows "NOT IMPLEMENTED" and disables.
 */

import { apiJson, apiFetch } from "./apiClient";

export type ControlState = { emergency_stop: boolean; retract: boolean };

export async function getControlState(): Promise<ControlState> {
  const res = await apiFetch("/api/control/state");
  if (!res.ok) throw new Error(`Control state: ${res.status}`);
  return res.json();
}

export type CommandPayload = { command_type: string; payload?: Record<string, unknown> };
export type CommandResult = { status: string; command_type?: string; mode?: string; detail?: string };

export async function postCommand(commandType: string, payload?: Record<string, unknown>): Promise<CommandResult> {
  return apiJson<CommandResult>("/api/control/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command_type: commandType, payload: payload ?? {} }),
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
