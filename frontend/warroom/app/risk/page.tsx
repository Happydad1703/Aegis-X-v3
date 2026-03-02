"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { getIncidents } from "@/lib/incidents";
import { SnapshotCard } from "@/components/SnapshotCard";
import { useState } from "react";

export default function RiskPage() {
  const [showRaw, setShowRaw] = useState(false);
  const { data: riskSnap, isError: riskErr } = useQuery({
    queryKey: ["snapshot", "risk_guard"],
    queryFn: () => getLatestSnapshot("risk_guard"),
    refetchInterval: 8000,
  });
  const { data: regimeSnap } = useQuery({
    queryKey: ["snapshot", "regime_current"],
    queryFn: () => getLatestSnapshot("regime_current"),
    refetchInterval: 8000,
  });
  const { data: incidentsData } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => getIncidents(30),
    refetchInterval: 10000,
  });

  const incidents = incidentsData?.items ?? [];

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Risk Guard / Incidents</h1>
      <p className="text-cic-muted text-sm mb-4">Read-only: risk_guard, regime_current, incident_log.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <SnapshotCard snapshotKey="risk_guard" snapshot={riskSnap} error={riskErr} />
        <SnapshotCard snapshotKey="regime_current" snapshot={regimeSnap} />
      </div>
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">incident_log (latest 30)</h2>
        {showRaw ? (
          <pre className="text-xs overflow-auto max-h-80 bg-black/20 p-2 rounded">{JSON.stringify(incidents, null, 2)}</pre>
        ) : (
          <ul className="space-y-2 text-sm">
            {incidents.slice(0, 15).map((i) => (
              <li key={i.id} className="border-b border-cic-border pb-2">
                [{i.severity}] {i.category ?? "—"} — {i.message.slice(0, 80)} {i.created_at ?? ""}
              </li>
            ))}
          </ul>
        )}
        <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
          {showRaw ? "Hide raw" : "Show raw JSON"}
        </button>
      </div>
    </div>
  );
}
