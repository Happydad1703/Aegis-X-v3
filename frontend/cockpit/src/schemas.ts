/**
 * Zod schemas for API responses — Signal_Interface_ICD.md contract.
 * If validation fails → show "Contract Break" (RED).
 */
import { z } from "zod";

export const SnapshotResponseSchema = z.object({
  snapshot_key: z.string(),
  data: z.record(z.unknown()),
  source_name: z.string().nullable().optional(),
  generated_at: z.string().nullable().optional(),
  refresh_rate_sec: z.number().nullable().optional(),
  freshness_status: z.string().nullable().optional(),
});

export type SnapshotResponse = z.infer<typeof SnapshotResponseSchema>;

export const ControlStateSchema = z.object({
  emergency_stop: z.boolean(),
  retract: z.boolean(),
});

export type ControlState = z.infer<typeof ControlStateSchema>;

export const CommandResponseSchema = z.object({
  status: z.string(),
  command_type: z.string().optional(),
  mode: z.string().optional(),
  detail: z.string().optional(),
});

export const OrdersResponseSchema = z.object({
  items: z.array(z.object({
    id: z.number(),
    symbol: z.string(),
    side: z.string(),
    quantity: z.number(),
    mode: z.string(),
    execution_status: z.string(),
    execution_payload: z.unknown().nullable().optional(),
    created_at: z.string().nullable().optional(),
  })),
  meta: z.object({ source: z.string() }).optional(),
});

export const IncidentsResponseSchema = z.object({
  items: z.array(z.object({
    id: z.number(),
    severity: z.string(),
    category: z.string().nullable().optional(),
    message: z.string(),
    related_snapshot_key: z.string().nullable().optional(),
    created_at: z.string().nullable().optional(),
  })),
  meta: z.object({ source: z.string() }).optional(),
});

export function parseSnapshotResponse(raw: unknown): { success: true; data: SnapshotResponse } | { success: false; error: string } {
  const result = SnapshotResponseSchema.safeParse(raw);
  if (result.success) return { success: true, data: result.data };
  return { success: false, error: result.error.message };
}
