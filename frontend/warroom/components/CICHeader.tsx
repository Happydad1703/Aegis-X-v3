"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { getControlState, postCommand, isControlApiAvailable } from "@/lib/control";

type ConnectionStatus = "ok" | "degraded" | "disconnected";

export function CICHeader() {
  const { data: modeSnap, isSuccess: modeOk } = useQuery({
    queryKey: ["snapshot", "operation_mode"],
    queryFn: () => getLatestSnapshot("operation_mode"),
    retry: 1,
    refetchInterval: 8000,
  });
  const { data: regimeSnap, isSuccess: regimeOk } = useQuery({
    queryKey: ["snapshot", "regime_current"],
    queryFn: () => getLatestSnapshot("regime_current"),
    retry: 1,
    refetchInterval: 8000,
  });
  const { data: commSnap } = useQuery({
    queryKey: ["snapshot", "comm_health"],
    queryFn: () => getLatestSnapshot("comm_health"),
    retry: 1,
    refetchInterval: 8000,
  });
  const { data: llmSnap } = useQuery({
    queryKey: ["snapshot", "llm_status"],
    queryFn: () => getLatestSnapshot("llm_status"),
    retry: 1,
    refetchInterval: 8000,
  });
  const { data: ctrlState, isSuccess: ctrlOk } = useQuery({
    queryKey: ["controlState"],
    queryFn: getControlState,
    retry: 1,
    refetchInterval: 5000,
  });
  const { data: controlAvailable = false } = useQuery({
    queryKey: ["controlAvailable"],
    queryFn: isControlApiAvailable,
    retry: 0,
    staleTime: 60_000,
  });

  const connectionStatus: ConnectionStatus = modeOk && regimeOk ? "ok" : commSnap ? "degraded" : "disconnected";
  const freshnessRed = commSnap?.freshness_status === "RED" || commSnap?.freshness_status === "red";
  const controlDisabled = !controlAvailable || connectionStatus === "disconnected" || freshnessRed;
  const mode = modeSnap?.data && typeof modeSnap.data === "object" && "mode" in modeSnap.data ? String((modeSnap.data as { mode?: string }).mode) : "—";
  const regime = regimeSnap?.data && typeof regimeSnap.data === "object" && "regime_label" in regimeSnap.data ? String((regimeSnap.data as { regime_label?: string }).regime_label) : "—";
  const confidence = regimeSnap?.data && typeof regimeSnap.data === "object" && "confidence_score" in regimeSnap.data ? (regimeSnap.data as { confidence_score?: number }).confidence_score : null;
  const crisisProb = regimeSnap?.data && typeof regimeSnap.data === "object" && "crisis_probability" in regimeSnap.data ? (regimeSnap.data as { crisis_probability?: number }).crisis_probability : null;
  const lastUpdated = regimeSnap?.generated_at ?? modeSnap?.generated_at ?? null;
  const freshness = commSnap?.freshness_status ?? "—";

  const sendCommand = async (cmd: string, payload?: Record<string, unknown>) => {
    if (!controlAvailable) return;
    try {
      await postCommand(cmd, payload);
    } catch {
      // show toast or leave to error boundary
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-cic-card border-b border-cic-border px-4 py-2 flex flex-wrap items-center gap-4">
      <Link href="/" className="font-semibold text-cic-accent hover:underline">
        Aegis-X V3 CIC
      </Link>

      {/* Connection / Degradation badge */}
      {connectionStatus === "disconnected" && (
        <span className="px-2 py-0.5 rounded bg-cic-danger/20 text-cic-danger text-sm font-medium">DISCONNECTED</span>
      )}
      {connectionStatus === "degraded" && (
        <span className="px-2 py-0.5 rounded bg-cic-warn/20 text-cic-warn text-sm font-medium">DEGRADED</span>
      )}
      {commSnap && !["GREEN", "green"].includes(String(freshness)) && (
        <span className="px-2 py-0.5 rounded bg-cic-warn/20 text-cic-warn text-sm">STALE</span>
      )}

      <HeaderBlock label="Mode" value={mode} />
      <HeaderBlock label="Regime" value={regime} />
      {confidence != null && <HeaderBlock label="Confidence" value={`${(Number(confidence) * 100).toFixed(0)}%`} />}
      {crisisProb != null && <HeaderBlock label="Crisis" value={`${(Number(crisisProb) * 100).toFixed(1)}%`} />}
      <HeaderBlock label="Health" value={commSnap ? "OK" : "—"} />
      <HeaderBlock label="LLM" value={llmSnap ? "OK" : "—"} />
      <HeaderBlock label="Freshness" value={String(freshness)} />
      <HeaderBlock label="E-Stop" value={ctrlOk && ctrlState?.emergency_stop ? "ON" : "OFF"} />
      <HeaderBlock label="Retract" value={ctrlOk && ctrlState?.retract ? "ON" : "OFF"} />

      {lastUpdated && (
        <span className="text-cic-muted text-xs">
          Last: {lastUpdated} (UTC)
        </span>
      )}

      <div className="ml-auto flex gap-2 flex-wrap">
        {controlAvailable ? (
          <>
            {freshnessRed && (
              <span className="text-cic-warn text-xs self-center">사령부 승인 필요 (Freshness RED)</span>
            )}
            <button
              type="button"
              disabled={controlDisabled}
              onClick={() => sendCommand("RUN_ENGINE_CYCLE")}
              className="px-3 py-1.5 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Run Cycle
            </button>
            <button
              type="button"
              disabled={controlDisabled}
              onClick={() => sendCommand("RETRACT", { reason: "CIC" })}
              className="px-3 py-1.5 rounded border border-cic-warn text-cic-warn hover:bg-cic-warn/20 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Retract
            </button>
            <button
              type="button"
              disabled={controlDisabled}
              onClick={() => sendCommand("EMERGENCY_STOP", { reason: "CIC" })}
              className="px-3 py-1.5 rounded border border-cic-danger text-cic-danger hover:bg-cic-danger/20 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              E-Stop
            </button>
          </>
        ) : (
          <span className="text-cic-muted text-xs px-2 py-1 border border-cic-border rounded">Control: NOT IMPLEMENTED</span>
        )}
      </div>
    </header>
  );
}

function HeaderBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-r border-cic-border pr-3 last:border-r-0">
      <span className="block text-xs text-cic-muted">{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  );
}
