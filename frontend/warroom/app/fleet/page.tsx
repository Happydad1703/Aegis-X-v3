"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot, type SnapshotRow } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";
import { FLEET_FORCE_KEYS, TARGET_KEYS } from "@/lib/warroomKeys";
import { FourForcesPanel } from "@/components/fleet/FourForcesPanel";

const KEYS = ["fleet_budget_snapshot", "allocation_matrix", ...FLEET_FORCE_KEYS, ...TARGET_KEYS] as const;

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function summary(snapshot?: SnapshotRow): string {
  const data = asObject(snapshot?.data);
  if (typeof data.status === "string") return data.status;
  if (typeof data.state === "string") return data.state;
  if (typeof data.signal === "string") return data.signal;
  return "N/A";
}

export default function FleetPage() {
  const queries = useQueries({
    queries: KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
    })),
  });
  const snapshots = KEYS.map((_, i) => queries[i].data);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Fleet Command</h1>
      <p className="text-cic-muted text-sm mb-4">Core / Swing / Strike / Reserved Fleet 상황 보드. 모든 정보는 snapshot read-only 입니다.</p>

      <FourForcesPanel
        budget={queries[0].data}
        allocation={queries[1].data}
        core={queries[2].data}
        swing={queries[3].data}
        strike={queries[4].data}
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Core</p>
          <p className="text-sm font-semibold">{summary(snapshots[2])}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Swing</p>
          <p className="text-sm font-semibold">{summary(snapshots[3])}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Strike</p>
          <p className="text-sm font-semibold">{summary(snapshots[4])}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Reserved Fleet</p>
          <p className="text-sm font-semibold">{summary(snapshots[1])}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={queries[i].data} error={queries[i].isError} />
        ))}
      </div>
    </div>
  );
}
