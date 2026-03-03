"use client";

import { useEffect, useState } from "react";

type Props = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  defaultReason?: string;
  onCancel: () => void;
  onConfirm: (reason: string) => Promise<void> | void;
};

export function ConfirmActionModal({
  open,
  title,
  description,
  confirmLabel = "확인 실행",
  defaultReason = "",
  onCancel,
  onConfirm,
}: Props) {
  const [reason, setReason] = useState(defaultReason);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (open) {
      setReason(defaultReason);
      setRunning(false);
    }
  }, [open, defaultReason]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-cic-card border border-cic-border rounded-lg p-4">
        <h3 className="text-cic-accent font-semibold mb-2">{title}</h3>
        <p className="text-sm text-cic-muted mb-3">{description}</p>
        <label className="block text-xs text-cic-muted mb-1">사유(Reason)</label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={3}
          className="w-full rounded border border-cic-border bg-black/30 p-2 text-sm mb-4"
          placeholder="운영 사유를 입력하십시오."
        />
        <div className="flex justify-end gap-2">
          <button
            type="button"
            className="px-3 py-2 rounded border border-cic-border text-sm"
            onClick={onCancel}
            disabled={running}
          >
            취소
          </button>
          <button
            type="button"
            className="px-3 py-2 rounded border border-cic-warn text-cic-warn text-sm disabled:opacity-50"
            onClick={async () => {
              setRunning(true);
              try {
                await onConfirm(reason.trim());
                onCancel();
              } finally {
                setRunning(false);
              }
            }}
            disabled={running}
          >
            {running ? "실행 중..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

