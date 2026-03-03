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
      <h1 className="text-xl font-semibold mb-2">국면 인텔리전스</h1>
      <p className="text-cic-muted text-sm mb-4">읽기 전용: regime_current. 디버깅용 원본 JSON 뷰어 포함.</p>
      <SnapshotCard snapshotKey="regime_current" snapshot={data} error={isError} />
    </div>
  );
}
