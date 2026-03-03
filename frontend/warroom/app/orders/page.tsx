"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getOrders } from "@/lib/orders";
import { getLatestSnapshot } from "@/lib/snapshots";

export default function OrdersPage() {
  const [showRaw, setShowRaw] = useState(false);
  const { data: ordersData, isError } = useQuery({
    queryKey: ["orders"],
    queryFn: () => getOrders(50),
    refetchInterval: 10000,
  });
  const { data: modeSnap } = useQuery({
    queryKey: ["snapshot", "operation_mode"],
    queryFn: () => getLatestSnapshot("operation_mode"),
    refetchInterval: 8000,
  });
  const items = ordersData?.items ?? [];
  const mode = modeSnap?.data && typeof modeSnap.data === "object" && "mode" in modeSnap.data
    ? String((modeSnap.data as { mode?: string }).mode) : "-";

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">주문/체결</h1>
      <p className="text-cic-muted text-sm mb-4">읽기 전용 주문 기록 화면입니다. 운용 모드는 스냅샷 기반으로 표시됩니다.</p>
      <div className="mb-4 p-3 rounded border border-cic-border bg-cic-card">
        <span className="text-cic-muted text-sm">운용 모드: </span>
        <span className="text-sm">{mode}</span>
      </div>
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">최근 50건</h2>
        {isError && <p className="text-cic-danger text-sm">주문 데이터를 불러오지 못했습니다.</p>}
        {!isError && (
          <>
            {showRaw ? (
              <pre className="text-xs overflow-auto max-h-96 bg-black/20 p-2 rounded">{JSON.stringify(items, null, 2)}</pre>
            ) : (
              <div className="space-y-2">
                {items.slice(0, 20).map((o) => (
                  <div key={o.id} className="text-sm border-b border-cic-border pb-2">
                    #{o.id} {o.symbol} {o.side} {o.quantity} - {o.execution_status} @ {o.created_at ?? "-"}
                  </div>
                ))}
                {items.length > 20 && <p className="text-cic-muted text-xs">외 {items.length - 20}건</p>}
              </div>
            )}
            <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
              {showRaw ? "원본 숨기기" : "원본 JSON 보기"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
