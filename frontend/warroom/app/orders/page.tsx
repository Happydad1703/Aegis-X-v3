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
      <h1 className="text-xl font-semibold mb-2">Orders and Execution</h1>
      <p className="text-cic-muted text-sm mb-4">Read-only order_log. operation_mode from snapshot.</p>
      <div className="mb-4 p-3 rounded border border-cic-border bg-cic-card">
        <span className="text-cic-muted text-sm">operation_mode: </span>
        <span className="text-sm">{mode}</span>
      </div>
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">order_log latest 50</h2>
        {isError && <p className="text-cic-danger text-sm">Failed to load orders.</p>}
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
                {items.length > 20 && <p className="text-cic-muted text-xs">and {items.length - 20} more</p>}
              </div>
            )}
            <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
              {showRaw ? "Hide raw" : "Show raw JSON"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
