"use client";

import { useQueries } from "@tanstack/react-query";
import { getLatestSnapshot, type SnapshotRow } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";
import { CommanderHeader } from "@/components/cic/CommanderHeader";
import {
  COMMANDER_STATUS_KEYS,
  COMMANDER_STRATEGY_KEYS,
  FLEET_FORCE_KEYS,
  TARGET_KEYS,
} from "@/lib/warroomKeys";

const CIC_KEYS = [
  ...COMMANDER_STATUS_KEYS,
  ...COMMANDER_STRATEGY_KEYS,
  ...FLEET_FORCE_KEYS,
  "risk_guard",
  "usd_exposure_status",
  ...TARGET_KEYS,
] as const;

function getSnapshot(queryData: (SnapshotRow | undefined)[], key: string) {
  return queryData[CIC_KEYS.indexOf(key as (typeof CIC_KEYS)[number])];
}

function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v));
}

/** V3 CIC Warroom Home — V2 CIC 정보구조를 snapshot read-only로 재현. */
export default function WarroomHome() {
  const queries = useQueries({
    queries: CIC_KEYS.map((key) => ({
      queryKey: ["snapshot", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
      retry: 1,
    })),
  });

  const snapshots = queries.map((q) => q.data);
  const anyRed = snapshots.some((s) => String(s?.freshness_status ?? "").toUpperCase() === "RED");
  const mode = asObject(getSnapshot(snapshots, "operation_mode")?.data).mode ?? "—";
  const session = asObject(getSnapshot(snapshots, "active_session")?.data).session ?? "—";
  const sessionState = asObject(getSnapshot(snapshots, "session_state")?.data).state ?? "—";
  const timezone = asObject(getSnapshot(snapshots, "timezone")?.data).timezone ?? "UTC";
  const regimeData = asObject(getSnapshot(snapshots, "regime_current")?.data);
  const riskData = asObject(getSnapshot(snapshots, "risk_guard")?.data);
  const commData = asObject(getSnapshot(snapshots, "comm_health")?.data);
  const alerts = [
    ...asList(riskData.alerts),
    ...asList(commData.alerts),
    ...asList(regimeData.alerts),
  ].slice(0, 8);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">총사령관 상황판</h1>
      <p className="text-cic-muted text-sm mb-4">
        V2 Warroom CIC 정보구조를 V3 스냅샷 계약으로 재구성했습니다. UI는 snapshot read-only이며 API 계산/직접 DB 조회를 하지 않습니다.
      </p>
      <CommanderHeader />
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-4">
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">운용 모드</p>
          <p className="text-sm font-semibold">{String(mode)}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">활성 세션</p>
          <p className="text-sm font-semibold">{String(session)} / {String(sessionState)}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">국면</p>
          <p className="text-sm font-semibold">{String(regimeData.regime_label ?? regimeData.regime ?? "—")}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">시간대</p>
          <p className="text-sm font-semibold">{String(timezone)}</p>
        </div>
      </div>
      {anyRed && (
        <div className="mb-4 p-3 rounded border border-cic-danger bg-cic-danger/10 text-cic-danger text-sm">
          Snapshot freshness RED 감지. 사령부 통제 명령 전 점검(Execution Check) 권장.
        </div>
      )}
      <div className="bg-cic-card border border-cic-border rounded p-4 mb-4">
        <h2 className="text-cic-accent font-medium mb-2">핵심 경보/사건</h2>
        {alerts.length === 0 ? (
          <p className="text-sm text-cic-muted">risk_guard, comm_health, regime_current 스냅샷에 경보 데이터가 없습니다.</p>
        ) : (
          <ul className="space-y-1 text-sm">
            {alerts.map((msg, idx) => (
              <li key={`${msg}-${idx}`} className="border-b border-cic-border pb-1">{msg}</li>
            ))}
          </ul>
        )}
      </div>
      <h2 className="text-cic-accent font-medium mb-2">함대/리스크/타깃 스냅샷 보드</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {CIC_KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={queries[i].data} error={queries[i].isError} locked={anyRed} />
        ))}
      </div>
    </div>
  );
}
