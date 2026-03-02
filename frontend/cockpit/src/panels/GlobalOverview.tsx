import React from "react";
import { useQueries } from "@tanstack/react-query";
import { fetchSnapshot, CORE_SNAPSHOT_KEYS } from "../api";
import { SnapshotCard } from "../SnapshotCard";

export function GlobalOverview() {
  const queries = useQueries({
    queries: CORE_SNAPSHOT_KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => fetchSnapshot(key),
    })),
  });
  return (
    <>
      <h2>Global Overview — 6 core snapshot panels</h2>
      <p className="meta">source_name, generated_at, refresh_rate_sec, freshness_status (Sensor Fusion Rule)</p>
      {CORE_SNAPSHOT_KEYS.map((key, i) => (
        <SnapshotCard key={key} snapshotKey={key} raw={queries[i].data} />
      ))}
    </>
  );
}
