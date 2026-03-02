"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getIncidents } from "@/lib/incidents";

export default function AARPage() {
  const [showRaw, setShowRaw] = useState(false);
  const { data, isError } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => getIncidents(50),
    refetchInterval: 10000,
  });

  const items = data?.items ?? [];

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">AAR / Battle Reports</h1>
      <p className="text-cic-muted text-sm mb-4">Read-only incident_log.</p>
      {isError && <p className="text-cic-danger text-sm mb-4">Failed to load incidents.</p>}
      <div className="bg-cic-card border border-cic-border rounded-lg p-4">
        <h2 className="text-cic-accent font-medium mb-2">incident_log</h2>
        {showRaw ? (
          <pre className="text-xs overflow-auto max-h-96 bg-black/20 p-2 rounded">{JSON.stringify(items, null, 2)}</pre>
        ) : (
          <ul className="space-y-2 text-sm">
            {items.map((i) => (
              <li key={i.id} className="border-b border-cic-border pb-2">
                <span className="text-cic-muted">{i.created_at}</span> [{i.severity}] {i.message}
              </li>
            ))}
          </ul>
        )}
        <button type="button" onClick={() => setShowRaw(!showRaw)} className="mt-2 text-xs text-cic-accent hover:underline">
          {showRaw ? "Hide raw" : "Show raw JSON"}
        </button>
      </div>
    </div>
  );
}
