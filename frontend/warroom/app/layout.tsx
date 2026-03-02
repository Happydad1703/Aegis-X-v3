import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { CICHeader } from "@/components/CICHeader";
import { LeftNav } from "@/components/LeftNav";

export const metadata: Metadata = {
  title: "Aegis-X V3 Warroom / CIC",
  description: "DB-Only Read Dashboard. No computation.",
  manifest: "/manifest.json",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#161b22" />
      </head>
      <body className="min-h-screen flex flex-col">
        <Providers>
          <CICHeader />
          <div className="flex flex-1 min-h-0">
            <LeftNav />
            <main className="flex-1 overflow-auto p-6">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
