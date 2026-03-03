"use client";

import { useMemo, useState } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { getControlState, isControlApiAvailable, postCommand, postResume, type ControlCommandType } from "@/lib/control";
import { CONTROL_CHECK_KEYS } from "@/lib/warroomKeys";
import { SnapshotCard } from "@/components/SnapshotCard";
import { ConfirmActionModal } from "@/components/control/ConfirmActionModal";

type ActionSpec = {
  key: string;
  label: string;
  description: string;
  cmd: "COMMAND" | "RESUME";
  commandType?: string;
  payload?: Record<string, unknown>;
  defaultReason: string;
  tone?: "normal" | "danger" | "warn";
};

const ACTIONS: ActionSpec[] = [
  {
    key: "RUN_ENGINE_CYCLE",
    label: "엔진 사이클 실행",
    description: "엔진 1사이클 실행을 발령합니다.",
    cmd: "COMMAND",
    commandType: "RUN_ENGINE_CYCLE",
    defaultReason: "Commander cycle order",
  },
  {
    key: "SET_MODE_BACKTEST",
    label: "모드 전환 백테스트",
    description: "운용 모드를 BACKTEST로 전환합니다.",
    cmd: "COMMAND",
    commandType: "SET_MODE",
    payload: { mode: "BACKTEST" },
    defaultReason: "Mode transition to BACKTEST",
  },
  {
    key: "SET_MODE_PAPER",
    label: "모드 전환 페이퍼",
    description: "운용 모드를 PAPER로 전환합니다.",
    cmd: "COMMAND",
    commandType: "SET_MODE",
    payload: { mode: "PAPER" },
    defaultReason: "Mode transition to PAPER",
  },
  {
    key: "SET_MODE_PILOT",
    label: "모드 전환 파일럿",
    description: "운용 모드를 PILOT로 전환합니다.",
    cmd: "COMMAND",
    commandType: "SET_MODE",
    payload: { mode: "PILOT" },
    defaultReason: "Mode transition to PILOT",
  },
  {
    key: "EMERGENCY_STOP",
    label: "긴급 중지",
    description: "즉시 긴급중지(E-Stop)를 발령합니다.",
    cmd: "COMMAND",
    commandType: "EMERGENCY_STOP",
    defaultReason: "Commander emergency stop",
    tone: "danger",
  },
  {
    key: "RETRACT",
    label: "리트랙트",
    description: "리스크 통제를 위해 리트랙트를 발령합니다.",
    cmd: "COMMAND",
    commandType: "RETRACT",
    defaultReason: "Commander risk containment",
    tone: "warn",
  },
  {
    key: "LLM_BLACKOUT_ON",
    label: "LLM 블랙아웃 켜기",
    description: "LLM blackout policy를 활성화합니다.",
    cmd: "COMMAND",
    commandType: "SET_LLM_BLACKOUT",
    payload: { active: true },
    defaultReason: "Blackout policy on",
    tone: "warn",
  },
  {
    key: "LLM_BLACKOUT_OFF",
    label: "LLM 블랙아웃 끄기",
    description: "LLM blackout policy를 비활성화합니다.",
    cmd: "COMMAND",
    commandType: "SET_LLM_BLACKOUT",
    payload: { active: false },
    defaultReason: "Blackout policy off",
  },
  {
    key: "RESUME",
    label: "운영 재개",
    description: "중지/리트랙트 상태를 해제하고 운영을 재개합니다.",
    cmd: "RESUME",
    defaultReason: "Commander release",
  },
];

export default function ControlPage() {
  const [busy, setBusy] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<ActionSpec | null>(null);

  const checks = useQueries({
    queries: CONTROL_CHECK_KEYS.map((key) => ({
      queryKey: ["snapshot", "control", key],
      queryFn: () => getLatestSnapshot(key),
      refetchInterval: 8000,
    })),
  });

  const { data: controlAvailable = false } = useQuery({
    queryKey: ["controlAvailable"],
    queryFn: isControlApiAvailable,
    retry: 0,
  });

  const { data: state } = useQuery({
    queryKey: ["controlState"],
    queryFn: getControlState,
    refetchInterval: 5000,
  });

  const checkSummary = useMemo(() => {
    const red = checks.filter((q) => String(q.data?.freshness_status ?? "").toUpperCase() === "RED").length;
    const ok = checks.filter((q) => q.data && !q.isError).length;
    return { red, ok, total: checks.length };
  }, [checks]);

  const send = async (cmd: ControlCommandType, payload?: Record<string, unknown>) => {
    if (!controlAvailable) return;
    setBusy(cmd);
    try {
      await postCommand(cmd, payload);
    } finally {
      setBusy(null);
    }
  };

  const resume = async (reason: string) => {
    if (!controlAvailable) return;
    setBusy("RESUME");
    try {
      await postResume(reason || "Commander release");
    } finally {
      setBusy(null);
    }
  };

  const runWithConfirm = async (spec: ActionSpec, reason: string) => {
    if (spec.cmd === "RESUME") {
      await resume(reason);
      return;
    }
    const payload = { ...(spec.payload ?? {}), reason: reason || spec.defaultReason };
    await send((spec.commandType ?? "RUN_ENGINE_CYCLE") as ControlCommandType, payload);
  };

  const buttonClass = (tone?: ActionSpec["tone"]) => {
    if (tone === "danger") return "px-3 py-2 rounded border border-cic-danger text-cic-danger hover:bg-cic-danger/20 text-sm disabled:opacity-50";
    if (tone === "warn") return "px-3 py-2 rounded border border-cic-warn text-cic-warn hover:bg-cic-warn/20 text-sm disabled:opacity-50";
    return "px-3 py-2 rounded border border-cic-border bg-cic-card hover:bg-cic-border text-sm disabled:opacity-50";
  };

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">제어 패널 (총사령관)</h1>
      <p className="text-cic-muted text-sm mb-4">
        실행상태 점검 + 작전 제어 패널입니다. 쓰기 동작은 Control API만 호출하며, UI에서 직접 DB를 갱신하지 않습니다.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">실행 점검</p>
          <p className="text-sm font-semibold">{checkSummary.ok}/{checkSummary.total} 정상</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">신선도 적색</p>
          <p className="text-sm font-semibold">{checkSummary.red}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">긴급 중지</p>
          <p className="text-sm font-semibold">{state?.emergency_stop ? "활성" : "비활성"}</p>
        </div>
        <div className="bg-cic-card border border-cic-border rounded p-3">
          <p className="text-xs text-cic-muted">리트랙트 / LLM 블랙아웃</p>
          <p className="text-sm font-semibold">{state?.retract ? "활성" : "비활성"} / {state?.llm_blackout ? "활성" : "비활성"}</p>
        </div>
      </div>

      {controlAvailable ? (
        <div className="bg-cic-card border border-cic-border rounded p-4 mb-4">
          <h2 className="text-cic-accent font-medium mb-1">운영 명령</h2>
          <p className="text-xs text-cic-muted mb-3">V2 흐름: 발령 버튼 → 사유 입력/확인 → 상태 반영</p>
          <div className="flex flex-wrap gap-2">
            {ACTIONS.map((spec) => (
              <button
                key={spec.key}
                type="button"
                disabled={busy !== null}
                onClick={() => setPendingAction(spec)}
                className={buttonClass(spec.tone)}
              >
                {spec.label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-cic-muted text-sm border border-cic-border rounded px-3 py-2 mb-4">
          제어 API: 미구현
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {CONTROL_CHECK_KEYS.map((key, i) => (
          <SnapshotCard key={key} snapshotKey={key} snapshot={checks[i].data} error={checks[i].isError} />
        ))}
      </div>

      <ConfirmActionModal
        open={pendingAction !== null}
        title={pendingAction?.label ?? "명령 확인"}
        description={pendingAction?.description ?? ""}
        confirmLabel="명령 실행"
        defaultReason={pendingAction?.defaultReason ?? ""}
        onCancel={() => setPendingAction(null)}
        onConfirm={async (reason) => {
          if (!pendingAction) return;
          await runWithConfirm(pendingAction, reason);
        }}
      />
    </div>
  );
}
