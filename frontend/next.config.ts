// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typedRoutes: true,                // ← moved out of experimental
  outputFileTracingRoot: __dirname, // quiet the multi-lockfile workspace warning
};

export default nextConfig;
