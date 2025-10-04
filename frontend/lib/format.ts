// lib/format.ts

import type { Severity } from "./types";

export function formatMoneyUSD(n: number | string, opts: { maximumFractionDigits?: number } = {}) {
  const num = typeof n === "string" ? Number(n) : n;
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: opts.maximumFractionDigits ?? 2,
  }).format(Number.isFinite(num) ? (num as number) : 0);
}

export function formatDurationMs(ms: number | string) {
  const v = typeof ms === "string" ? Number(ms) : ms;
  if (!Number.isFinite(v)) return "-";
  if (v < 1000) return `${Math.round(v)} ms`;
  const s = v / 1000;
  if (s < 60) return `${s.toFixed(1)} s`;
  const m = Math.floor(s / 60);
  const rs = Math.round(s % 60);
  return `${m}m ${rs}s`;
}

export function formatDateTimeISO(iso: string) {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(d);
}

export function severityLabel(s: Severity | string): Severity | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" {
  const u = String(s || "MEDIUM").toUpperCase();
  if (u === "CRITICAL" || u === "HIGH" || u === "MEDIUM" || u === "LOW") return u;
  return "MEDIUM";
}
