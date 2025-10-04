// lib/usePolling.ts

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { apiStatus } from "@/app/api.config";
import type { StatusResponse } from "./types";
import { POLL_MS_RUNNING, POLL_TIMEOUT_MS } from "./constants";

/**
 * Polls /status for a given run_id until status !== 'running' (or timeout).
 * Returns {data, loading, error, refresh}.
 */
export function usePolling(runId?: string | null) {
  const [data, setData] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(runId));
  const [error, setError] = useState<string | null>(null);

  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startedAt = useRef<number | null>(null);

  const clear = () => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
  };

  const tick = useCallback(async () => {
    if (!runId) return;
    try {
      const res = await apiStatus(runId);
      setData(res);
      setError(null);

      if (res.status === "running") {
        // keep polling
        if (startedAt.current && Date.now() - startedAt.current > POLL_TIMEOUT_MS) {
          setError("Timed out while waiting for the run to finish.");
          setLoading(false);
          clear();
          return;
        }
        timer.current = setTimeout(tick, POLL_MS_RUNNING);
      } else {
        // completed or failed
        setLoading(false);
        clear();
      }
    } catch (e: any) {
      setError(e?.message ?? "Failed to fetch status");
      setLoading(false);
      clear();
    }
  }, [runId]);

  const refresh = useCallback(() => {
    if (!runId) return;
    clear();
    setLoading(true);
    startedAt.current = Date.now();
    tick();
  }, [runId, tick]);

  useEffect(() => {
    if (!runId) return;
    startedAt.current = Date.now();
    setLoading(true);
    tick();
    return clear;
  }, [runId, tick]);

  return { data, loading, error, refresh, setData };
}
