"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS: { href: string; label: string }[] = [
  { href: "/", label: "Warroom Home" },
  { href: "/regime", label: "Regime Intelligence" },
  { href: "/allocation", label: "Allocation Matrix" },
  { href: "/fleet", label: "Fleet Console" },
  { href: "/orders", label: "Orders & Execution" },
  { href: "/risk", label: "Risk Guard / Incidents" },
  { href: "/aar", label: "AAR / Battle Reports" },
  { href: "/system", label: "System Control" },
];

export function LeftNav() {
  const pathname = usePathname();
  return (
    <nav className="w-52 min-w-[12rem] bg-cic-card border-r border-cic-border py-4 flex flex-col">
      {ITEMS.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={`px-4 py-2 text-sm ${pathname === href ? "text-cic-accent bg-cic-border/30 border-l-2 border-cic-accent" : "text-cic-muted hover:text-cic-accent hover:bg-cic-border/20"}`}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
}
