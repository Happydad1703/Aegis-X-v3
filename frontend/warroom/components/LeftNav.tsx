"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getNewsSources } from "@/lib/news";

const ITEMS: { href: string; label: string }[] = [
  { href: "/", label: "워룸 홈" },
  { href: "/regime", label: "국면 인텔리전스" },
  { href: "/allocation", label: "배분 매트릭스" },
  { href: "/fleet", label: "함대 콘솔" },
  { href: "/orders", label: "주문/체결" },
  { href: "/risk", label: "리스크/사건" },
  { href: "/aar", label: "사후보고" },
  { href: "/system", label: "시스템 제어" },
];

export function LeftNav() {
  const pathname = usePathname();
  const { data: newsData } = useQuery({
    queryKey: ["newsSourcesLeftNav"],
    queryFn: () => getNewsSources(30),
    refetchInterval: 15000,
    retry: 1,
  });
  const newsItems = newsData?.items ?? [];

  return (
    <nav className="w-80 min-w-[18rem] bg-cic-card border-r border-cic-border py-4 flex flex-col">
      <div className="mb-2">
        {ITEMS.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`px-4 py-2 text-sm block ${pathname === href ? "text-cic-accent bg-cic-border/30 border-l-2 border-cic-accent" : "text-cic-muted hover:text-cic-accent hover:bg-cic-border/20"}`}
          >
            {label}
          </Link>
        ))}
      </div>

      <div className="px-3 pt-3 border-t border-cic-border flex-1 min-h-0">
        <p className="text-xs text-cic-muted mb-2">뉴스/공시/자료 통합</p>
        <div className="space-y-2 overflow-auto max-h-[48vh] pr-1">
          {newsItems.length === 0 && (
            <p className="text-xs text-cic-muted">표시할 뉴스가 없습니다.</p>
          )}
          {newsItems.map((n) => (
            <div key={n.id} className="border border-cic-border rounded p-2">
              <p className="text-[11px] text-cic-muted">
                {n.source_name} · {n.event_type}
              </p>
              <p className="text-xs leading-snug mt-1 break-words">
                {n.title || "제목 없음"}
              </p>
              {n.link && (
                <a
                  href={n.link}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-cic-accent hover:underline break-all"
                >
                  원문 보기
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </nav>
  );
}
