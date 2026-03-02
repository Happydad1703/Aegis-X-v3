/**
 * Orders read-only API. GET /api/orders
 */

import { apiJson } from "./apiClient";

export type OrderItem = {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  mode: string;
  execution_status: string;
  execution_payload?: unknown;
  created_at?: string | null;
};

export type OrdersResponse = { items: OrderItem[]; meta?: { source: string } };

export async function getOrders(limit = 50): Promise<OrdersResponse> {
  return apiJson<OrdersResponse>(`/api/orders?limit=${limit}`);
}
