export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://127.0.0.1:8000";

type Json = Record<string, any> | null;

async function request<T = any>(
  path: string,
  init?: RequestInit & { expectJson?: boolean }
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init?.headers || {}),
  };

  const res = await fetch(url, { ...init, headers });


  const text = await res.text();
  let data: Json = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e: any) {
      // Invalid JSON from server
      throw new Error(
        `Invalid JSON from ${url}: ${e?.message || e}. Body (first 200): ${text.slice(
          0,
          200
        )}`
      );
    }
  }

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.message)) || `${res.status} ${res.statusText}`;
    const err = new Error(`HTTP error from ${url}: ${msg}`);
    // @ts-ignore
    err.status = res.status;
    // @ts-ignore
    err.body = data ?? text;
    throw err;
  }

  return (data as unknown) as T;
}

export async function runPipeline(payload: {
  repo: string;
  pr_number: number;
  commit_sha: string;
  tf_path: string;
}) {
  return request<{ run_id: string }>("/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getStatus(params: { run_id: string }) {
  const q = new URLSearchParams({ run_id: params.run_id }).toString();
  return request(`/status?${q}`);
}

export async function getHistory(limit = 10) {
  const q = new URLSearchParams({ limit: String(limit) }).toString();
  return request(`/history?${q}`);
}
