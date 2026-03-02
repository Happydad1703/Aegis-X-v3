import React from "react";
import { useQueries } from "@tanstack/react-query";
import { fetchSnapshot } from "../api";
import { SnapshotCard } from "../SnapshotCard";

const KEYS = ["regime_current", "targets_core", "targets_swing", "targets_strike"] as const;

export function Battlefield() {
  const queries = useQueries({
    queries: KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => fetchSnapshot(key),
    })),
  });
  return (
    <>
      <h2>Battlefield</h2>
      <p className="meta">Documented keys: regime_current, targets_core, targets_swing, targets_strike</p>
      {KEYS.map((key, i) => (
        <SnapshotCard key={key} snapshotKey={key} raw={queries[i].data} />
      ))}
    </>
  );
}
