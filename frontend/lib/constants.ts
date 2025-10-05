// lib/constants.ts
export const API_TIMEOUT_MS = 25_000;

// Polling
export const POLL_MS = 1_200; // 1.2s
export const POLL_MAX_MS = 30_000; // 30s cap

// Severity colors (Tailwind classes)
export const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
  HIGH: "bg-orange-500/15 text-orange-300 ring-orange-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  LOW: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  INFO: "bg-sky-500/15 text-sky-300 ring-sky-500/30",
};
