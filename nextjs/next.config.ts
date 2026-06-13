import type { NextConfig } from "next";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const nextConfigDir = dirname(fileURLToPath(import.meta.url));
const apiProxyTarget = process.env.API_PROXY_TARGET ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  turbopack: {
    root: nextConfigDir,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiProxyTarget}/:path*`,
      },
    ];
  },
};

export default nextConfig;
