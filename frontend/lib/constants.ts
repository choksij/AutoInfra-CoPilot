// lib/constants.ts
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export const POLL_INTERVAL_MS = 1000;   // how often we re-check /status
export const POLL_TIMEOUT_MS  = 15000;  // stop polling after 15s

export const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "bg-rose-500/20 text-rose-300 border border-rose-500/40",
  HIGH:     "bg-amber-500/20 text-amber-300 border border-amber-500/40",
  MEDIUM:   "bg-sky-500/20 text-sky-300 border border-sky-500/40",
  LOW:      "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40",
};

export const BADGE_COLORS = {
  safe:   "text-emerald-400",
  unsafe: "text-rose-400",
  idle:   "text-amber-400",
} as const;
