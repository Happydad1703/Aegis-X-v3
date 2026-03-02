/**
 * Incidents read-only API. GET /api/incidents
 */

import { apiJson } from "./apiClient";

export type IncidentItem = {
  id: number;
  severity: string;
  category?: string | null;
  message: string;
  related_snapshot_key?: string | null;
  created_at?: string | null;
};

export type IncidentsResponse = { items: IncidentItem[]; meta?: { source: string } };

export async function getIncidents(limit = 50): Promise<IncidentsResponse> {
  return apiJson<IncidentsResponse>(`/api/incidents?limit=${limit}`);
}
