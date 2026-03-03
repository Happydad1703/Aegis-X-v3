import { apiJson } from "./apiClient";

export type NewsFeedItem = {
  id: number;
  source_name: string;
  event_type: string;
  title: string;
  link?: string | null;
  received_at?: string | null;
  payload?: Record<string, unknown>;
};

export type NewsFeedResponse = {
  items: NewsFeedItem[];
  meta?: { source: string };
};

export async function getNewsSources(limit = 40): Promise<NewsFeedResponse> {
  return apiJson<NewsFeedResponse>(`/api/news/sources?limit=${limit}`);
}
