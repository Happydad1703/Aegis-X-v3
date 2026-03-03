"use client";

import type { SnapshotRow } from "@/lib/snapshots";

type Props = {
  core?: SnapshotRow;
  swing?: SnapshotRow;
  strike?: SnapshotRow;
  budget?: SnapshotRow;
  allocation?: SnapshotRow;
};

function asObj(v: unknown): Record<string, unknown> {
  return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
}

function stateText(snapshot?: SnapshotRow): string {
  const data = asObj(snapshot?.data);
  return String(data.state ?? data.status ?? data.signal ?? "N/A");
}

function budgetText(snapshot?: SnapshotRow, key?: string): string {
  const data = asObj(snapshot?.data);
  const byFleet = asObj(data.by_fleet);
  const entry = key ? asObj(byFleet[key]) : {};
  if (Object.keys(entry).length === 0) return "N/A";
  return String(entry.budget ?? entry.weight ?? entry.value ?? "N/A");
}

export function FourForcesPanel({ core, swing, strike, budget, allocation }: Props) {
  const allocationData = asObj(allocation?.data);
  const reserveHint =
    String(allocationData.reserve ?? allocationData.reserved ?? "snapshot 기반 reserve 항목 없음");

  return (
    <section className="bg-cic-card border border-cic-border rounded-lg p-4 mb-4">
      <h2 className="text-cic-accent font-semibold mb-2">4군 체제 패널 (Core / Swing / Strike / Reserved)</h2>
      <p className="text-cic-muted text-xs mb-3">
        Reserved Fleet 표시는 계산 없이 `fleet_budget_snapshot` / `allocation_matrix`의 snapshot 필드만 해석합니다.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Core Fleet</p>
          <p className="text-sm font-semibold">{stateText(core)}</p>
          <p className="text-xs text-cic-muted mt-1">budget: {budgetText(budget, "core")}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Swing Fleet</p>
          <p className="text-sm font-semibold">{stateText(swing)}</p>
          <p className="text-xs text-cic-muted mt-1">budget: {budgetText(budget, "swing")}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Strike Fleet</p>
          <p className="text-sm font-semibold">{stateText(strike)}</p>
          <p className="text-xs text-cic-muted mt-1">budget: {budgetText(budget, "strike")}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">Reserved Fleet</p>
          <p className="text-sm font-semibold">{reserveHint}</p>
          <p className="text-xs text-cic-muted mt-1">budget: {budgetText(budget, "reserve")}</p>
        </div>
      </div>
    </section>
  );
}

