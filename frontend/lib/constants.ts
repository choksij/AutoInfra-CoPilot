// lib/constants.ts

import type { Severity } from "./types";

export const POLL_MS_RUNNING = 1_000; // how often to poll while run is "running"
export const POLL_MS_IDLE = 10_000;   // background refresh when nothing is running
export const POLL_TIMEOUT_MS = 2 * 60 * 1_000; // 2 minutes safety cap

export const SEVERITY_ORDER: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export const SEVERITY_COLORS: Record<Severity, string> = {
  CRITICAL: "bg-red-600 text-white",
  HIGH: "bg-orange-500 text-white",
  MEDIUM: "bg-amber-400 text-black",
  LOW: "bg-emerald-400 text-black",
};

export const BADGE_COPY = {
  unknown: "🟡 Auto-check: not run",
  safe: "🟢 Auto-check: safe to merge",
  unsafe: "🔴 Auto-check: needs changes",
};
