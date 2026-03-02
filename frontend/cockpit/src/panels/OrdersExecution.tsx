import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchOrders } from "../api";

export function OrdersExecution() {
  const { data: ordersData } = useQuery({ queryKey: ["orders"], queryFn: () => fetchOrders(50) });
  const orders = (ordersData as { items?: Array<Record<string, unknown>> } | undefined)?.items ?? [];
  return (
    <>
      <h2>Orders & Execution</h2>
      <p className="meta">Read-only from order_log. operation_mode from engine_snapshot.</p>
      <div className="card">
        <h3>order_log (latest 50)</h3>
        <div className="data">
          {orders.length === 0 ? "No orders" : JSON.stringify(orders.slice(0, 20), null, 2)}
        </div>
      </div>
    </>
  );
}
