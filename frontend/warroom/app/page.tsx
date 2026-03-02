"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot, CORE_SNAPSHOT_KEYS } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";

/** Warroom Home — Sensor Fusion: 6 core snapshots. Display only; no calculation. */
export default function WarroomHome() {
  const queries = useQueries({
    queries: CORE_SNAPSHOT_KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
      retry: 1,
    })),
  });

  const anyRed = queries.some((q) => {
    const s = q.data as { freshness_status?: string } | undefined;
    return s?.freshness_status === "RED" || s?.freshness_status === "red";
  });

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Sensor Fusion Overview</h1>
      <p className="text-cic-muted text-sm mb-4">
        6 core snapshots. Each card: snapshot_key, generated_at, source_name, refresh_rate_sec, freshness_status. No UI computation.
      </p>
      {anyRed && (
        <div className="mb-4 p-3 rounded border border-cic-danger bg-cic-danger/10 text-cic-danger text-sm">
          One or more snapshots are RED. Control commands may be blocked until freshness is restored.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {CORE_SNAPSHOT_KEYS.map((key, i) => (
          <SnapshotCard
            key={key}
            snapshotKey={key}
            snapshot={queries[i].data}
            error={queries[i].isError}
            locked={anyRed}
          />
        ))}
      </div>
    </div>
  );
}
