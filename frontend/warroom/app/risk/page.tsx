"use client";

import { useQueries, useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";
import { useState } from "react";

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v));
}

type NarrativeRow = {
  severity: "RED" | "AMBER" | "GREEN";
  category: string;
  action: string;
  summary: string;
  source: string;
};

function classifyNarrative(text: string): NarrativeRow {
  const t = text.toLowerCase();
  if (t.includes("stop") || t.includes("fail") || t.includes("error") || t.includes("halt")) {
    return { severity: "RED", category: "실행 리스크", action: "즉시 점검 발령", summary: text, source: "alerts" };
  }
  if (t.includes("warn") || t.includes("caution") || t.includes("latency") || t.includes("degraded")) {
    return { severity: "AMBER", category: "시스템 경고", action: "모니터링 강화", summary: text, source: "alerts" };
  }
  return { severity: "GREEN", category: "운영 참고", action: "상태 유지", summary: text, source: "alerts" };
}

function rowTone(severity: NarrativeRow["severity"]): string {
  if (severity === "RED") return "border-cic-danger text-cic-danger";
  if (severity === "AMBER") return "border-cic-warn text-cic-warn";
  return "border-emerald-400 text-emerald-300";
}

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
  const extra = useQueries({
    queries: [
      {
        queryKey: ["snapshot", "usd_exposure_status"],
        queryFn: () => getLatestSnapshot("usd_exposure_status"),
        refetchInterval: 8000,
      },
      {
        queryKey: ["snapshot", "session_state"],
        queryFn: () => getLatestSnapshot("session_state"),
        refetchInterval: 8000,
      },
      {
        queryKey: ["snapshot", "comm_health"],
        queryFn: () => getLatestSnapshot("comm_health"),
        refetchInterval: 8000,
      },
      {
        queryKey: ["snapshot", "incidents_latest"],
        queryFn: () => getLatestSnapshot("incidents_latest"),
        refetchInterval: 8000,
      },
    ],
  });

  const riskData = asObject(riskSnap?.data);
  const regimeData = asObject(regimeSnap?.data);
  const commData = asObject(extra[2].data?.data);
  const incidentsText = [
    ...asList(riskData.alerts),
    ...asList(regimeData.alerts),
    ...asList(commData.alerts),
  ];
  const incidentsLatest = asObject(extra[3].data?.data);
  const incidentItems = Array.isArray(incidentsLatest.items) ? incidentsLatest.items : [];
  const narrativeRows: NarrativeRow[] = [
    ...incidentItems.slice(0, 8).map((item) => {
      const o = asObject(item);
      const sev = String(o.severity ?? "AMBER").toUpperCase();
      const severity: NarrativeRow["severity"] = sev === "RED" ? "RED" : sev === "GREEN" ? "GREEN" : "AMBER";
      return {
        severity,
        category: String(o.category ?? o.type ?? "사건"),
        action: String(o.action ?? o.recommendation ?? "모니터링 강화"),
        summary: String(o.summary ?? o.message ?? JSON.stringify(o)),
        source: "incidents_latest",
      };
    }),
    ...incidentsText.slice(0, 10).map((line) => classifyNarrative(line)),
  ];

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">리스크 가드/사건</h1>
      <p className="text-cic-muted text-sm mb-4">읽기 전용 리스크/세션/통신 상태 스냅샷입니다.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <SnapshotCard snapshotKey="risk_guard" snapshot={riskSnap} error={riskErr} />
        <SnapshotCard snapshotKey="regime_current" snapshot={regimeSnap} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <SnapshotCard snapshotKey="usd_exposure_status" snapshot={extra[0].data} error={extra[0].isError} />
        <SnapshotCard snapshotKey="session_state" snapshot={extra[1].data} error={extra[1].isError} />
      </div>
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">사건 내러티브 매핑</h2>
        <p className="text-xs text-cic-muted mb-3">
          사건 스냅샷과 경보를 화면 표시용 분류(심각도/분류/권고)로 매핑합니다.
        </p>
        {showRaw ? (
          <pre className="text-xs overflow-auto max-h-80 bg-black/20 p-2 rounded">{JSON.stringify(narrativeRows, null, 2)}</pre>
        ) : (
          <div className="space-y-2 text-sm">
            {narrativeRows.slice(0, 15).map((row, idx) => (
              <div key={`${row.summary}-${idx}`} className="border border-cic-border rounded p-2">
                <div className="flex flex-wrap gap-2 mb-1">
                  <span className={`inline-flex px-2 py-0.5 rounded border text-xs ${rowTone(row.severity)}`}>{row.severity}</span>
                  <span className="text-xs text-cic-muted">{row.category}</span>
                  <span className="text-xs text-cic-muted">권고: {row.action}</span>
                </div>
                <p>{row.summary}</p>
              </div>
            ))}
            {narrativeRows.length === 0 && <p className="text-cic-muted">표시할 사건/경보가 없습니다.</p>}
          </div>
        )}
        <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
          {showRaw ? "원본 숨기기" : "원본 JSON 보기"}
        </button>
      </div>
    </div>
  );
}
