import { io, type Socket } from "socket.io-client";

/**
 * Realtime stream connector for dashboard updates.
 * UI remains read-only: incoming events should only trigger re-fetch/invalidate.
 */
export function createRealtimeClient(namespace = "/ws"): Socket {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  return io(baseUrl + namespace, {
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
  });
}
