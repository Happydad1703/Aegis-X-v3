"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";
import { V2DashboardGrid } from "@/components/dashboard/V2DashboardGrid";

const DASH_KEYS = [
  "orders_latest",
  "risk_guard",
  "usd_exposure_status",
  "engine_heartbeat",
  "comm_health",
  "llm_status",
  "operation_mode",
] as const;

export default function DashboardPage() {
  const snapshots = useQueries({
    queries: DASH_KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
      retry: 1,
    })),
  });

  const freshness = snapshots.map((m) => String(m.data?.freshness_status ?? "UNKNOWN"));
  const redCount = freshness.filter((f) => f.toUpperCase() === "RED").length;
  const byKey = DASH_KEYS.reduce((acc, key, idx) => {
    acc[key] = snapshots[idx].data;
    return acc;
  }, {} as Record<(typeof DASH_KEYS)[number], (typeof snapshots)[number]["data"]>);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Phoenix Dashboard</h1>
      <p className="text-cic-muted text-sm mb-4">
        운영 모니터링 중심 화면입니다. V2 패널 순서를 채용했고, 모든 위젯은 `/api/snapshot/*` read-only 응답만 사용합니다.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Snapshot Nodes</p>
          <p className="text-sm font-semibold">{DASH_KEYS.length}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Freshness RED</p>
          <p className="text-sm font-semibold">{redCount}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Engine Health</p>
          <p className="text-sm font-semibold">{byKey.engine_heartbeat ? "ONLINE" : "N/A"}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Risk Guard</p>
          <p className="text-sm font-semibold">{byKey.risk_guard ? "TRACKING" : "N/A"}</p>
        </div>
      </div>

      <V2DashboardGrid data={byKey} />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {DASH_KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={snapshots[i].data} error={snapshots[i].isError} />
        ))}
      </div>
    </div>
  );
}
