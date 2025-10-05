// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingRoot: __dirname, // ensure project root
  experimental: {
    typedRoutes: true,
  },
};

export default nextConfig;
