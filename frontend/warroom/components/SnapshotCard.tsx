"use client";

import { useState } from "react";
import type { SnapshotRow } from "@/lib/snapshots";

type Props = {
  snapshot: SnapshotRow | null | undefined;
  snapshotKey: string;
  error?: boolean;
  /** When true (freshness RED/STALE), show read-only lock overlay and block control. */
  locked?: boolean;
};

export function SnapshotCard({ snapshot, snapshotKey, error, locked }: Props) {
  const [showRaw, setShowRaw] = useState(false);
  const freshness = snapshot?.freshness_status ?? "";
  const fClass = freshness === "RED" || freshness === "red" ? "freshness-red" : freshness === "YELLOW" || freshness === "yellow" ? "freshness-yellow" : "freshness-green";

  if (error || !snapshot) {
    return (
      <div className="bg-cic-card border border-cic-border rounded-lg p-4 border-l-4 border-cic-danger">
        <h3 className="text-cic-accent font-medium mb-2">{snapshotKey}</h3>
        <p className="text-cic-danger text-sm">Error or no data. Retry or check API.</p>
      </div>
    );
  }

  return (
    <div className={`bg-cic-card border border-cic-border rounded-lg p-4 ${fClass} relative`}>
      {locked && (
        <div className="absolute inset-0 bg-black/40 rounded-lg flex items-center justify-center z-10">
          <span className="bg-cic-warn/90 text-black px-3 py-1 rounded text-sm font-medium">Read-only — 사령부 승인 필요</span>
        </div>
      )}
      <h3 className="text-cic-accent font-medium mb-2">{snapshot.snapshot_key}</h3>
      {/* Audit-first: source_name, generated_at, refresh_rate_sec, freshness_status */}
      <div className="text-xs text-cic-muted space-y-0.5 mb-2">
        <span>source_name: {snapshot.source_name ?? "—"}</span>
        <span className="block">generated_at: {snapshot.generated_at ?? "—"}</span>
        <span className="block">refresh_rate_sec: {snapshot.refresh_rate_sec ?? "—"}</span>
        <span className="block">freshness_status: {snapshot.freshness_status ?? "—"}</span>
      </div>
      {showRaw ? (
        <pre className="text-xs overflow-auto max-h-64 bg-black/20 p-2 rounded break-all whitespace-pre-wrap">
          {JSON.stringify(snapshot.data, null, 2)}
        </pre>
      ) : (
        <pre className="text-sm overflow-auto max-h-40 truncate text-ellipsis">
          {JSON.stringify(snapshot.data).slice(0, 300)}…
        </pre>
      )}
      <button
        type="button"
        onClick={() => setShowRaw(!showRaw)}
        className="mt-2 text-xs text-cic-accent hover:underline"
      >
        {showRaw ? "Hide raw" : "Show raw JSON"}
      </button>
    </div>
  );
}
