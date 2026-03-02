"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";

const KEYS = ["fleet_budget_snapshot", "targets_core", "targets_swing", "targets_strike"] as const;

export default function FleetPage() {
  const queries = useQueries({
    queries: KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
    })),
  });

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Fleet Console</h1>
      <p className="text-cic-muted text-sm mb-4">Read-only snapshots.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={queries[i].data} error={queries[i].isError} />
        ))}
      </div>
    </div>
  );
}
