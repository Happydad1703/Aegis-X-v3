"use client";

import { useState } from "react";
import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";

const AAR_KEYS = ["regime_current", "risk_guard", "operation_mode", "comm_health", "incidents_latest"] as const;

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v));
}

function categoryFromText(line: string): string {
  const t = line.toLowerCase();
  if (t.includes("risk") || t.includes("loss") || t.includes("mdd")) return "리스크";
  if (t.includes("engine") || t.includes("latency") || t.includes("comm")) return "시스템";
  if (t.includes("order") || t.includes("position") || t.includes("entry")) return "실행";
  return "일반";
}

export default function AARPage() {
  const [showRaw, setShowRaw] = useState(false);
  const queries = useQueries({
    queries: AAR_KEYS.map((key) => ({
      queryKey: ["snapshot", "aar", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
    })),
  });

  const riskData = asObject(queries[1].data?.data);
  const commData = asObject(queries[3].data?.data);
  const incidentData = asObject(queries[4].data?.data);
  const incidentItems = Array.isArray(incidentData.items) ? incidentData.items : [];
  const reflections = [
    ...asList(riskData.lessons),
    ...asList(riskData.reflection),
    ...asList(commData.lessons),
  ];
  const suggestions = [
    ...asList(riskData.suggestions),
    ...asList(commData.suggestions),
  ];

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">사후보고</h1>
      <p className="text-cic-muted text-sm mb-4">스냅샷 기반 사후보고 요약입니다. 사건 로그 직접 조회는 사용하지 않습니다.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-4">
        {AAR_KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={queries[i].data} error={queries[i].isError} />
        ))}
      </div>
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">워룸 회고</h2>
        {showRaw ? (
          <pre className="text-xs overflow-auto max-h-96 bg-black/20 p-2 rounded">
            {JSON.stringify({ reflections, suggestions }, null, 2)}
          </pre>
        ) : (
          <ul className="space-y-2 text-sm">
            {reflections.slice(0, 10).map((line, idx) => (
              <li key={`${line}-${idx}`} className="border-b border-cic-border pb-2">
                {line}
              </li>
            ))}
            {reflections.length === 0 && <li className="text-cic-muted">반영할 회고 데이터가 없습니다.</li>}
          </ul>
        )}
        {!showRaw && suggestions.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm text-cic-accent mb-1">내일 전략</h3>
            <ul className="space-y-1 text-sm">
              {suggestions.slice(0, 6).map((line, idx) => (
                <li key={`${line}-${idx}`}>- {line}</li>
              ))}
            </ul>
          </div>
        )}
        {!showRaw && (
          <div className="mt-4">
            <h3 className="text-sm text-cic-accent mb-1">사건 분류</h3>
            <div className="space-y-1 text-sm">
              {incidentItems.slice(0, 6).map((item, idx) => {
                const o = asObject(item);
                const msg = String(o.summary ?? o.message ?? JSON.stringify(o));
                const sev = String(o.severity ?? "AMBER").toUpperCase();
                const action = String(o.action ?? o.recommendation ?? "상황실 후속조치 검토");
                return (
                  <div key={`${msg}-${idx}`} className="border border-cic-border rounded p-2">
                    <p className="text-xs text-cic-muted">{sev} · {categoryFromText(msg)} · 권고: {action}</p>
                    <p>{msg}</p>
                  </div>
                );
              })}
              {incidentItems.length === 0 && (
                <p className="text-cic-muted">표시할 사건 항목이 없습니다.</p>
              )}
            </div>
          </div>
        )}
        <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
          {showRaw ? "원본 숨기기" : "원본 JSON 보기"}
        </button>
      </div>
    </div>
  );
}
