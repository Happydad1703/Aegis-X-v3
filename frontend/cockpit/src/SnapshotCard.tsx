import React from "react";
import { parseSnapshotResponse, type SnapshotResponse } from "./schemas";

type Props = {
  snapshotKey: string;
  raw: unknown;
};

export function SnapshotCard({ snapshotKey, raw }: Props) {
  const parsed = parseSnapshotResponse(raw);
  if (!parsed.success) {
    return (
      <div className="card contract-break freshness-RED">
        <h3>{snapshotKey}</h3>
        <p className="data">Contract Break — validation failed</p>
        <p className="meta">{parsed.error}</p>
      </div>
    );
  }
  const d = parsed.data as SnapshotResponse;
  const freshness = (d.freshness_status || "").toUpperCase();
  const isGreen = freshness === "GREEN";
  const isRed = freshness === "RED";
  return (
    <div className={`card freshness-${freshness || "GREEN"}`} style={{ position: "relative" }}>
      {!isGreen && <div className={isRed ? "overlay-red" : "overlay-yellow"} />}
      <h3>{d.snapshot_key}</h3>
      <div className="data">{JSON.stringify(d.data || {}, null, 2).slice(0, 500)}</div>
      <div className="meta">
        <span>source_name: {d.source_name ?? "—"}</span>
        <span>generated_at: {d.generated_at ?? "—"}</span>
        <span>refresh_rate_sec: {d.refresh_rate_sec ?? "—"}</span>
        <span>freshness_status: {d.freshness_status ?? "—"}</span>
      </div>
    </div>
  );
}
