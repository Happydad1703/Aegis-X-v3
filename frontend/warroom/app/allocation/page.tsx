"use client";

import { useQuery } from "@tanstack/react-query";
import { getLatestSnapshot } from "@/lib/snapshots";
import { SnapshotCard } from "@/components/SnapshotCard";

export default function AllocationPage() {
  const { data, isError } = useQuery({
    queryKey: ["snapshot", "allocation_matrix"],
    queryFn: () => getLatestSnapshot("allocation_matrix"),
    refetchInterval: 8000,
  });
  const { data: fleetData, isError: fleetErr } = useQuery({
    queryKey: ["snapshot", "fleet_budget_snapshot"],
    queryFn: () => getLatestSnapshot("fleet_budget_snapshot"),
    refetchInterval: 8000,
  });

  return (
    <div>
      <h1 className="text-xl font-semibold mb-2">배분 매트릭스/함대 예산</h1>
      <p className="text-cic-muted text-sm mb-4">읽기 전용. 원본 JSON 뷰어 제공.</p>
      <SnapshotCard snapshotKey="allocation_matrix" snapshot={data} error={isError} />
      <div className="mt-6">
        <h2 className="text-lg font-medium mb-2">함대 예산 스냅샷</h2>
        <SnapshotCard snapshotKey="fleet_budget_snapshot" snapshot={fleetData} error={fleetErr} />
      </div>
    </div>
  );
}
