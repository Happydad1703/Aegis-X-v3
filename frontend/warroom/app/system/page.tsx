"use client";

import { useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { getControlState, postCommand, isControlApiAvailable, type ControlCommandType } from "@/lib/control";
import { SnapshotCard } from "@/components/SnapshotCard";

export default function SystemControlPage() {
  const { data: modeSnap } = useQuery({
    queryKey: ["snapshot", "operation_mode"],
    queryFn: () => getLatestSnapshot("operation_mode"),
    refetchInterval: 8000,
  });
  const { data: ctrlState } = useQuery({
    queryKey: ["controlState"],
    queryFn: getControlState,
    refetchInterval: 5000,
  });
  const { data: controlAvailable = false } = useQuery({
    queryKey: ["controlAvailable"],
    queryFn: isControlApiAvailable,
    retry: 0,
    staleTime: 60_000,
  });

  const send = (cmd: ControlCommandType, payload?: Record<string, unknown>) => {
    if (!controlAvailable) return;
    postCommand(cmd, payload).then(() => {}).catch(() => {});
  };

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">시스템 제어</h1>
      <p className="text-cic-muted text-sm mb-4">
        모드/명령은 Control API만 사용합니다. UI 직접 DB 쓰기는 금지됩니다. API 미구현 시 "미구현 (NOT IMPLEMENTED)"로 표시됩니다.
      </p>
      <div className="space-y-4">
        <SnapshotCard snapshotKey="operation_mode" snapshot={modeSnap} />
        <div className="bg-cic-card border border-cic-border rounded-lg p-4">
          <h2 className="text-cic-accent font-medium mb-2">게이트 상태</h2>
          <p className="text-sm">긴급 중지: {ctrlState?.emergency_stop ? "활성" : "비활성"} | 리트랙트: {ctrlState?.retract ? "활성" : "비활성"}</p>
        </div>
        {controlAvailable ? (
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => send("RUN_ENGINE_CYCLE")} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              엔진 사이클 실행
            </button>
            <button type="button" onClick={() => send("SET_MODE", { mode: "BACKTEST" })} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              백테스트 전환
            </button>
            <button type="button" onClick={() => send("SET_MODE", { mode: "PAPER" })} className="px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm">
              페이퍼 전환
            </button>
            <button type="button" onClick={() => send("RETRACT", { reason: "Warroom" })} className="px-3 py-2 rounded border border-cic-warn text-cic-warn hover:bg-cic-warn/20 text-sm">
              리트랙트
            </button>
            <button type="button" onClick={() => send("EMERGENCY_STOP", { reason: "Warroom" })} className="px-3 py-2 rounded border border-cic-danger text-cic-danger hover:bg-cic-danger/20 text-sm">
              긴급 중지
            </button>
          </div>
        ) : (
          <p className="text-cic-muted text-sm border border-cic-border rounded px-3 py-2">제어 API: 미구현</p>
        )}
      </div>
    </div>
  );
}
