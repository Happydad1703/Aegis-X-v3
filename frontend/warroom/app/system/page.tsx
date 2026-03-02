"use client";

import { useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { getControlState, postCommand, isControlApiAvailable } from "@/lib/control";
import { SnapshotCard } from "@/components/SnapshotCard";

export default function SystemControlPage() {
  const { data: modeSnap } = useQuery({
    queryKey: ["snapshot", "operation_mode"],
    queryFn: () => getLatestSnapshot("operation_mode"),
    refetchInterval: 8000,
  });
  const { data: ctrlState } = useQuery({
    queryKey: ["controlState"],
    queryFn: getControlState,
    refetchInterval: 5000,
  });
  const { data: controlAvailable = false } = useQuery({
    queryKey: ["controlAvailable"],
    queryFn: isControlApiAvailable,
    retry: 0,
    staleTime: 60_000,
  });

  const send = (cmd: string, payload?: Record<string, unknown>) => {
    if (!controlAvailable) return;
    postCommand(cmd, payload).then(() => {}).catch(() => {});
  };

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">System Control</h1>
      <p className="text-cic-muted text-sm mb-4">
        Mode, commands via Control API only. No direct DB write. If API not implemented, buttons show NOT IMPLEMENTED.
      </p>
      <div className="space-y-4">
        <SnapshotCard snapshotKey="operation_mode" snapshot={modeSnap} />
        <div className="bg-cic-card border border-cic-border rounded-lg p-4">
          <h2 className="text-cic-accent font-medium mb-2">Gate state</h2>
          <p className="text-sm">E-Stop: {ctrlState?.emergency_stop ? "ON" : "OFF"} | Retract: {ctrlState?.retract ? "ON" : "OFF"}</p>
        </div>
        {controlAvailable ? (
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => send("RUN_ENGINE_CYCLE")} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              Run Engine Cycle
            </button>
            <button type="button" onClick={() => send("SET_MODE", { mode: "BACKTEST" })} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              Set BACKTEST
            </button>
            <button type="button" onClick={() => send("SET_MODE", { mode: "PAPER" })} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              Set PAPER
            </button>
            <button type="button" onClick={() => send("RETRACT", { reason: "Warroom" })} className="px-3 py-2 rounded border border-cic-warn text-cic-warn hover:bg-cic-warn/20 text-sm">
              Retract
            </button>
            <button type="button" onClick={() => send("EMERGENCY_STOP", { reason: "Warroom" })} className="px-3 py-2 rounded border border-cic-danger text-cic-danger hover:bg-cic-danger/20 text-sm">
              Emergency Stop
            </button>
          </div>
        ) : (
          <p className="text-cic-muted text-sm border border-cic-border rounded px-3 py-2">Control API: NOT IMPLEMENTED (server-side required)</p>
        )}
      </div>
    </div>
  );
}
