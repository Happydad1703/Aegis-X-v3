import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchIncidents } from "../api";

export function AAR() {
  const { data } = useQuery({ queryKey: ["incidents"], queryFn: () => fetchIncidents(50) });
  const items = (data as { items?: Array<Record<string, unknown>> } | undefined)?.items ?? [];
  return (
    <>
      <h2>AAR</h2>
      <p className="meta">Read-only from incident_log</p>
      <div className="card">
        <h3>incident_log (latest 50)</h3>
        <div className="data">
          {items.length === 0 ? "No incidents" : JSON.stringify(items.slice(0, 15), null, 2)}
        </div>
      </div>
    </>
  );
}
