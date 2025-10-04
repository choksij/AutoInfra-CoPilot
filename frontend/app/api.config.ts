// app/api.config.ts

import type { HistoryItem, RunRequestBody, StatusResponse } from "@/lib/types";

const BASE =
  (typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_BASE as string) || ""
    : process.env.NEXT_PUBLIC_API_BASE) || "http://127.0.0.1:8000";

function url(path: string) {
  return `${BASE.replace(/\/$/, "")}${path.startsWith("/") ? "" : "/"}${path}`;
}

async function json<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} ${text}`.trim());
  }
  return res.json() as Promise<T>;
}

/** Kick off a run; returns the run_id immediately. */
export async function apiRun(body: RunRequestBody): Promise<{ run_id: string; status: string }> {
  return json(url("/run"), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Get status for a given run_id. */
export async function apiStatus(run_id: string): Promise<StatusResponse> {
  const u = new URL(url("/status"));
  u.searchParams.set("run_id", run_id);
  return json<StatusResponse>(u.toString());
}

/** Get recent history items (defaults to 20). */
export async function apiHistory(limit = 20): Promise<HistoryItem[]> {
  const u = new URL(url("/history"));
  u.searchParams.set("limit", String(limit));
  return json<HistoryItem[]>(u.toString());
}

/** Simple health ping, useful for gating UI. */
export async function apiHealth(): Promise<{ ok: boolean; env?: string; sync?: boolean }> {
  // backend health returns a small table; try to parse boolean
  const res = await fetch(url("/health"));
  if (!res.ok) return { ok: false };
  return { ok: true };
}

export const API_BASE = BASE;
