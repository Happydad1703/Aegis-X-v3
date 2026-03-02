import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchSnapshot, fetchControlState, postCommand } from "./api";
import { parseSnapshotResponse } from "./schemas";
import { ControlStateSchema } from "./schemas";

type Props = {
  healthy: boolean;
  onCommandSent: () => void;
};

export function Header({ healthy, onCommandSent }: Props) {
  const { data: modeSnap } = useQuery({
    queryKey: ["snapshot", "operation_mode"],
    queryFn: () => fetchSnapshot("operation_mode"),
  });
  const { data: regimeSnap } = useQuery({
    queryKey: ["snapshot", "regime_current"],
    queryFn: () => fetchSnapshot("regime_current"),
  });
  const { data: healthSnap } = useQuery({
    queryKey: ["snapshot", "comm_health"],
    queryFn: () => fetchSnapshot("comm_health"),
  });
  const { data: llmSnap } = useQuery({
    queryKey: ["snapshot", "llm_status"],
    queryFn: () => fetchSnapshot("llm_status"),
  });
  const { data: controlState } = useQuery({
    queryKey: ["controlState"],
    queryFn: fetchControlState,
  });

  const modeParsed = typeof modeSnap === "object" && modeSnap !== null ? parseSnapshotResponse(modeSnap) : null;
  const regimeParsed = typeof regimeSnap === "object" && regimeSnap !== null ? parseSnapshotResponse(regimeSnap) : null;
  const ctrl = controlState != null && ControlStateSchema.safeParse(controlState).success
    ? ControlStateSchema.parse(controlState)
    : { emergency_stop: false, retract: false };

  const mode = modeParsed?.success && modeParsed.data.data && typeof modeParsed.data.data === "object" && "mode" in modeParsed.data.data
    ? String((modeParsed.data.data as { mode?: string }).mode ?? "—")
    : "—";
  const regime = regimeParsed?.success && regimeParsed.data.data && typeof regimeParsed.data.data === "object" && "regime_label" in regimeParsed.data.data
    ? String((regimeParsed.data.data as { regime_label?: string }).regime_label ?? "—")
    : "—";
  const crisisProb = regimeParsed?.success && regimeParsed.data.data && typeof regimeParsed.data.data === "object" && "crisis_probability" in regimeParsed.data.data
    ? (regimeParsed.data.data as { crisis_probability?: number }).crisis_probability
    : null;
  const healthLabel = healthSnap != null && typeof healthSnap === "object" && "data" in healthSnap && typeof (healthSnap as { data?: unknown }).data === "object"
    ? "OK"
    : "—";
  const llmLabel = llmSnap != null && typeof llmSnap === "object" && "data" in llmSnap ? "OK" : "—";
  const freshnessLabel = healthSnap != null && typeof healthSnap === "object" && "freshness_status" in healthSnap
    ? String((healthSnap as { freshness_status?: string }).freshness_status ?? "—")
    : "—";

  const sendCommand = async (cmd: string, payload?: Record<string, unknown>) => {
    await postCommand(cmd, payload);
    onCommandSent();
  };

  return (
    <header style={{
      position: "sticky", top: 0, zIndex: 10, background: "#161b22", padding: "0.5rem 1rem",
      borderBottom: "1px solid #30363d", display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap",
    }}>
      <h1 style={{ margin: 0, fontSize: "1.1rem" }}>Aegis-X v3 Cockpit</h1>
      <HeaderBlock label="Mode" value={mode} />
      <HeaderBlock label="Regime" value={regime} />
      <HeaderBlock label="Crisis Prob" value={crisisProb != null ? `${(crisisProb * 100).toFixed(1)}%` : "—"} />
      <HeaderBlock label="Health" value={healthLabel} />
      <HeaderBlock label="LLM" value={llmLabel} />
      <HeaderBlock label="Freshness" value={freshnessLabel} />
      <HeaderBlock label="E-Stop" value={ctrl.emergency_stop ? "ON" : "OFF"} />
      <HeaderBlock label="Retract" value={ctrl.retract ? "ON" : "OFF"} />
      <div style={{ display: "flex", gap: "0.5rem", marginLeft: "auto", flexWrap: "wrap" }}>
        <button className="btn" disabled={!healthy} onClick={() => sendCommand("RUN_ENGINE_CYCLE")}>Run Cycle</button>
        <button className="btn" disabled={!healthy} onClick={() => sendCommand("SET_MODE", { mode: "PAPER" })}>Set PAPER</button>
        <button className="btn" disabled={!healthy} onClick={() => sendCommand("RETRACT", { reason: "Cockpit" })}>Retract</button>
        <button className="btn btn-danger" disabled={!healthy} onClick={() => sendCommand("EMERGENCY_STOP", { reason: "Cockpit" })}>E-Stop</button>
      </div>
    </header>
  );
}

function HeaderBlock({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: "0 0.75rem", borderRight: "1px solid #30363d" }}>
      <span style={{ fontSize: "0.7rem", color: "#8b949e", display: "block" }}>{label}</span>
      <span style={{ fontSize: "0.85rem" }}>{value}</span>
    </div>
  );
}
