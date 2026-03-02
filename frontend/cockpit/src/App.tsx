import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Header } from "./Header";
import { LeftNav, type PanelId } from "./LeftNav";
import { fetchSnapshot } from "./api";
import { parseSnapshotResponse } from "./schemas";
import { GlobalOverview } from "./panels/GlobalOverview";
import { Battlefield } from "./panels/Battlefield";
import { FleetConsole } from "./panels/FleetConsole";
import { AllocationMatrix } from "./panels/AllocationMatrix";
import { RiskControl } from "./panels/RiskControl";
import { OrdersExecution } from "./panels/OrdersExecution";
import { AAR } from "./panels/AAR";
import { SystemControl } from "./panels/SystemControl";

function useHealthy(): boolean {
  const { data } = useQuery({ queryKey: ["snapshot", "comm_health"], queryFn: () => fetchSnapshot("comm_health") });
  const parsed = useMemo(() => (data != null ? parseSnapshotResponse(data) : null), [data]);
  const freshness = parsed?.success ? parsed.data.freshness_status : null;
  return freshness === "GREEN";
}

export default function App() {
  const [panel, setPanel] = useState<PanelId>("overview");
  const healthy = useHealthy();

  const PanelContent = () => {
    switch (panel) {
      case "overview": return <GlobalOverview />;
      case "battlefield": return <Battlefield />;
      case "fleet": return <FleetConsole />;
      case "allocation": return <AllocationMatrix />;
      case "risk": return <RiskControl />;
      case "orders": return <OrdersExecution />;
      case "aar": return <AAR />;
      case "system": return <SystemControl />;
      default: return <GlobalOverview />;
    }
  };

  return (
    <div className="layout">
      <Header healthy={healthy} onCommandSent={() => { /* refetch handled by TanStack Query */ }} />
      <div className="body-row">
        <LeftNav active={panel} onSelect={setPanel} />
        <main className="main">
          <PanelContent />
        </main>
      </div>
      <footer style={{ padding: "0.35rem 1rem", borderTop: "1px solid #30363d", fontSize: "0.75rem", color: "#8b949e", background: "#161b22" }}>
        Incident / News feed (from DB snapshots)
      </footer>
    </div>
  );
}
