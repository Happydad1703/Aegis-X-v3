/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 배포용 단일 실행 번들 생성
  output: "standalone",
  turbopack: {
    root: __dirname,
  },
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async headers() {
    return [{ source: "/:path*", headers: [{ key: "X-Frame-Options", value: "SAMEORIGIN" }] }];
  },
  async rewrites() {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    if (!base) return [];
    return [{ source: "/api/:path*", destination: `${base}/api/:path*` }];
  },
};

module.exports = nextConfig;
