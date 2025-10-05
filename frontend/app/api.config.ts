// app/api.config.ts
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export async function postRun(body: {
  repo: string;
  pr_number: number;
  commit_sha: string;
  tf_path?: string;
}) {
  const resp = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!resp.ok) throw new Error(`POST /run failed: ${resp.status}`);
  return (await resp.json()) as { run_id: string; status: string };
}

export async function getStatus(params: { run_id: string }) {
  const url = new URL(`${API_BASE}/status`);
  url.searchParams.set("run_id", params.run_id);
  const resp = await fetch(url.toString(), { cache: "no-store" });
  if (!resp.ok) throw new Error(`GET /status failed: ${resp.status}`);
  return (await resp.json()) as import("../lib/types").StatusResponse;
}

export async function getHistory(limit = 10) {
  const url = new URL(`${API_BASE}/history`);
  url.searchParams.set("limit", String(limit));
  const resp = await fetch(url.toString(), { cache: "no-store" });
  if (!resp.ok) throw new Error(`GET /history failed: ${resp.status}`);
  return (await resp.json()) as import("../lib/types").HistoryItem[];
}
