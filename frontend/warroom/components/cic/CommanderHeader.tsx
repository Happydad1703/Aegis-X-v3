"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";

const HEADER_KEYS = [
  "operation_mode",
  "session_state",
  "regime_current",
  "risk_guard",
  "comm_health",
  "llm_status",
  "engine_heartbeat",
] as const;

function asObj(v: unknown): Record<string, unknown> {
  return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
}

function badgeTone(value: string): string {
  const t = value.toUpperCase();
  if (t === "RED" || t === "FAIL" || t === "BLOCK") return "border-cic-danger text-cic-danger bg-cic-danger/10";
  if (t === "YELLOW" || t === "AMBER" || t === "WARN" || t === "CAUTION") return "border-cic-warn text-cic-warn bg-cic-warn/10";
  if (t === "GREEN" || t === "OK" || t === "PASS" || t === "NORMAL") return "border-emerald-400 text-emerald-300 bg-emerald-500/10";
  return "border-cic-border text-cic-muted bg-cic-card";
}

function freshnessTone(value: string): string {
  return badgeTone(value || "UNKNOWN");
}

export function CommanderHeader() {
  const qs = useQueries({
    queries: HEADER_KEYS.map((key) => ({
      queryKey: ["snapshot", "commanderHeader", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
      retry: 1,
    })),
  });

  const rows = HEADER_KEYS.reduce((acc, key, idx) => {
    acc[key] = qs[idx].data;
    return acc;
  }, {} as Record<(typeof HEADER_KEYS)[number], (typeof qs)[number]["data"]>);

  const mode = asObj(rows.operation_mode?.data).mode ?? "—";
  const session = asObj(rows.session_state?.data).state ?? asObj(rows.session_state?.data).session ?? "—";
  const regime = asObj(rows.regime_current?.data).regime_label ?? asObj(rows.regime_current?.data).regime ?? "—";
  const freshness = String(rows.engine_heartbeat?.freshness_status ?? "UNKNOWN");
  const riskData = asObj(rows.risk_guard?.data);
  const riskGate = String(riskData.gate_status ?? riskData.status ?? "UNKNOWN");
  const commState = String(asObj(rows.comm_health?.data).status ?? "UNKNOWN");
  const llmState = String(asObj(rows.llm_status?.data).status ?? "UNKNOWN");
  const hbState = String(asObj(rows.engine_heartbeat?.data).status ?? "UNKNOWN");
  const updatedAt =
    rows.engine_heartbeat?.generated_at ??
    rows.regime_current?.generated_at ??
    rows.operation_mode?.generated_at ??
    "—";

  return (
    <section className="bg-cic-card border border-cic-border rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h2 className="text-cic-accent font-semibold">지휘 요약 헤더</h2>
        <span className="text-xs text-cic-muted">최근 갱신: {String(updatedAt)}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-3">
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">운용 모드</p>
          <p className="text-sm font-semibold">{String(mode)}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">세션 상태</p>
          <p className="text-sm font-semibold">{String(session)}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">국면</p>
          <p className="text-sm font-semibold">{String(regime)}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">게이트 / 리스크</p>
          <span className={`inline-flex px-2 py-0.5 mt-1 rounded border text-xs ${badgeTone(riskGate)}`}>
            {riskGate}
          </span>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">통신 · LLM · 엔진</p>
          <p className="text-sm">{commState} / {llmState} / {hbState}</p>
        </div>
        <div className="border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">신선도</p>
          <span className={`inline-flex px-2 py-0.5 mt-1 rounded border text-xs ${freshnessTone(freshness)}`}>
            {freshness}
          </span>
        </div>
      </div>
    </section>
  );
}

