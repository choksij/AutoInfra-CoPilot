
"use client";

import { useEffect, useRef, useState } from "react";

interface Options<T> {
  intervalMs: number;
  timeoutMs?: number;
  until?: (value: T | undefined) => boolean;
}

export function usePolling<T>(fn: () => Promise<T>, opts: Options<T>) {
  const { intervalMs, timeoutMs = 20_000, until } = opts;
  const [data, setData] = useState<T | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(undefined);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stoppedRef = useRef(false);

  useEffect(() => {
    async function tick() {
      try {
        const v = await fn();
        setData(v);
        if (!until || until(v)) {
          stop();
        }
      } catch (e) {
        setError(e);
        
        stop();
      }
    }

    function stop() {
      if (stoppedRef.current) return;
      stoppedRef.current = true;
      if (timerRef.current) clearInterval(timerRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      setLoading(false);
    }

    
    setLoading(true);
    stoppedRef.current = false;
    tick();
    timerRef.current = setInterval(tick, intervalMs);
    timeoutRef.current = setTimeout(stop, timeoutMs);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      stoppedRef.current = true;
    };
    
  }, [intervalMs, timeoutMs]);

  return { data, loading, error };
}
