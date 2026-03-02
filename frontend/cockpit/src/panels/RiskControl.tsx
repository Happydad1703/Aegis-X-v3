import React from "react";
import { useQueries } from "@tanstack/react-query";
import { fetchSnapshot } from "../api";
import { SnapshotCard } from "../SnapshotCard";

const KEYS = ["risk_guard", "regime_current"] as const;

export function RiskControl() {
  const queries = useQueries({
    queries: KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => fetchSnapshot(key),
    })),
  });
  return (
    <>
      <h2>Risk Control</h2>
      <p className="meta">risk_guard, regime_current</p>
      {KEYS.map((key, i) => (
        <SnapshotCard key={key} snapshotKey={key} raw={queries[i].data} />
      ))}
    </>
  );
}
