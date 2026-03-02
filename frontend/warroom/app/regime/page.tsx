"use client";

import { useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";

export default function RegimePage() {
  const { data, isError } = useQuery({
    queryKey: ["snapshot", "regime_current"],
    queryFn: () => getLatestSnapshot("regime_current"),
    refetchInterval: 8000,
  });

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">Regime Intelligence</h1>
      <p className="text-cic-muted text-sm mb-4">Read-only: regime_current. Raw JSON viewer for debugging.</p>
      <SnapshotCard snapshotKey="regime_current" snapshot={data} error={isError} />
    </div>
  );
}
