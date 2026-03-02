import React from "react";
import { useQueries } from "@tanstack/react-query";
import { fetchSnapshot, fetchControlState, postCommand } from "../api";
import { ControlStateSchema } from "../schemas";

export function SystemControl() {
  const results = useQueries({
    queries: [
      { queryKey: ["controlState"], queryFn: fetchControlState },
      { queryKey: ["snapshot", "operation_mode"], queryFn: () => fetchSnapshot("operation_mode") },
    ],
  });
  const stateQuery = results[0];
  const modeQuery = results[1];
  const ctrl = stateQuery.data != null && ControlStateSchema.safeParse(stateQuery.data).success
    ? ControlStateSchema.parse(stateQuery.data)
    : { emergency_stop: false, retract: false };
  const modeData = modeQuery.data as { data?: { mode?: string } } | undefined;
  const mode = modeData?.data?.mode ?? "—";

  const send = (cmd: string, payload?: Record<string, unknown>) => {
    postCommand(cmd, payload).then(() => { stateQuery.refetch(); modeQuery.refetch(); });
  };

  return (
    <>
      <h2>System Control</h2>
      <p className="meta">Commands via POST /api/control/command only. No optimistic UI.</p>
      <div className="card">
        <h3>operation_mode</h3>
        <div className="data">Current mode: {mode}</div>
      </div>
      <div className="card">
        <h3>Gate state</h3>
        <div className="data">EmergencyStop: {ctrl.emergency_stop ? "ON" : "OFF"} | Retract: {ctrl.retract ? "ON" : "OFF"}</div>
      </div>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button className="btn" onClick={() => send("RUN_ENGINE_CYCLE")}>Run Engine Cycle</button>
        <button className="btn" onClick={() => send("SET_MODE", { mode: "BACKTEST" })}>Set BACKTEST</button>
        <button className="btn" onClick={() => send("SET_MODE", { mode: "PAPER" })}>Set PAPER</button>
        <button className="btn" onClick={() => send("RETRACT", { reason: "Cockpit" })}>Retract</button>
        <button className="btn btn-danger" onClick={() => send("EMERGENCY_STOP", { reason: "Cockpit" })}>Emergency Stop</button>
      </div>
    </>
  );
}
