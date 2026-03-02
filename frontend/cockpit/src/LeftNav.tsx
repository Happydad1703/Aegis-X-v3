import React from "react";

export type PanelId =
  | "overview"
  | "battlefield"
  | "fleet"
  | "allocation"
  | "risk"
  | "orders"
  | "aar"
  | "system";

type Props = { active: PanelId; onSelect: (id: PanelId) => void };

const ITEMS: { id: PanelId; label: string }[] = [
  { id: "overview", label: "Global Overview" },
  { id: "battlefield", label: "Battlefield" },
  { id: "fleet", label: "Fleet Console" },
  { id: "allocation", label: "Allocation Matrix" },
  { id: "risk", label: "Risk Control" },
  { id: "orders", label: "Orders & Execution" },
  { id: "aar", label: "AAR" },
  { id: "system", label: "System Control" },
];

export function LeftNav({ active, onSelect }: Props) {
  return (
    <nav className="left-nav">
      {ITEMS.map(({ id, label }) => (
        <a
          key={id}
          href="#"
          className={active === id ? "active" : ""}
          onClick={(e) => { e.preventDefault(); onSelect(id); }}
        >
          {label}
        </a>
      ))}
    </nav>
  );
}
