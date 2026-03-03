"use client";

import type { SnapshotRow } from "@/lib/snapshots";

type Props = {
  data: Record<string, SnapshotRow | undefined>;
};

function asObj(v: unknown): Record<string, unknown> {
  return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
}

function panelValue(snapshot?: SnapshotRow, fallback = "N/A"): string {
  const data = asObj(snapshot?.data);
  return String(data.status ?? data.state ?? data.signal ?? data.mode ?? fallback);
}

export function V2DashboardGrid({ data }: Props) {
  const orders = asObj(data.orders_latest?.data);
  const orderItems = Array.isArray(orders.items) ? orders.items.length : 0;
  const risk = asObj(data.risk_guard?.data);
  const riskAlerts = Array.isArray(risk.alerts) ? risk.alerts.length : 0;

  const PANELS = [
    { title: "Execution Control Panel", key: "operation_mode", desc: "Promotion Pipeline / 운용 모드" },
    { title: "Fleet Control Panel", key: "orders_latest", desc: "Fleet 주문/집행 스냅샷" },
    { title: "Status Monitoring", key: "engine_heartbeat", desc: "엔진 heartbeat / freshness" },
    { title: "Strategy Intelligence", key: "llm_status", desc: "LLM 상태 및 전략 지원" },
    { title: "Risk Guard", key: "risk_guard", desc: "리스크 경보 및 게이트 상태" },
    { title: "Health Monitoring", key: "comm_health", desc: "통신/시스템 헬스" },
    { title: "USD Exposure", key: "usd_exposure_status", desc: "달러 노출 및 환율 민감도" },
  ] as const;

  return (
    <section className="bg-cic-card border border-cic-border rounded-lg p-4 mb-4">
      <h2 className="text-cic-accent font-semibold mb-2">Phoenix Dashboard Panels (V2 Order)</h2>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
        {PANELS.map((panel, idx) => (
          <div
            key={panel.title}
            className={`border border-cic-border rounded p-3 ${idx < 3 ? "lg:col-span-4" : "lg:col-span-3"}`}
          >
            <p className="text-xs text-cic-muted">{panel.title}</p>
            <p className="text-sm font-semibold mt-1">{panelValue(data[panel.key])}</p>
            <p className="text-xs text-cic-muted mt-1">{panel.desc}</p>
            {panel.key === "orders_latest" && (
              <p className="text-xs text-cic-muted mt-1">orders_latest.items: {orderItems}</p>
            )}
            {panel.key === "risk_guard" && (
              <p className="text-xs text-cic-muted mt-1">alerts: {riskAlerts}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

