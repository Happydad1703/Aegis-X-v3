import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchSnapshot } from "../api";
import { SnapshotCard } from "../SnapshotCard";

export function AllocationMatrix() {
  const { data } = useQuery({ queryKey: ["snapshot", "allocation_matrix"], queryFn: () => fetchSnapshot("allocation_matrix") });
  return (
    <>
      <h2>Allocation Matrix</h2>
      <p className="meta">Snapshot key: allocation_matrix</p>
      <SnapshotCard snapshotKey="allocation_matrix" raw={data} />
    </>
  );
}
