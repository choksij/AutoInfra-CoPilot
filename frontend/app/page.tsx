// app/page.tsx
"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { getHistory, getStatus } from "./api.config";
import type { HistoryItem, StatusResponse } from "../lib/types";
import { POLL_INTERVAL_MS, POLL_TIMEOUT_MS } from "../lib/constants";
import StatusCard from "../components/StatusCard";
import RunButton from "../components/RunButton";
import FindingsTable from "../components/FindingsTable";
import DiffBlock from "../components/DiffBlock";
import HistoryList from "../components/HistoryList";

export default function Page() {
  const [runId, setRunId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  // load initial history
  useEffect(() => {
    (async () => {
      try {
        const h = await getHistory(10);
        setHistory(h);
      } catch (e) {
        console.warn("history failed", e);
      }
    })();
  }, []);

  const kickoff = useCallback((rid: string) => {
    setRunId(rid);
    setStatus(null);
    setLoading(true);
  }, []);

  // poll status when we have a runId
  useEffect(() => {
    if (!runId) return;

    let stopped = false;
    const begun = Date.now();

    async function poll() {
      if (stopped) return;
      try {
        // runId is guaranteed non-null here due to the guard above
        const s = await getStatus({ run_id: runId! });
        setStatus(s);
        if (s.status === "completed" || s.status === "failed") {
          setLoading(false);
          // refresh history once
          try {
            const h = await getHistory(10);
            setHistory(h);
          } catch {}
          return;
        }
      } catch (e) {
        console.warn(e);
        setLoading(false);
        return;
      }

      if (Date.now() - begun > POLL_TIMEOUT_MS) {
        setLoading(false);
        return;
      }
      setTimeout(poll, POLL_INTERVAL_MS);
    }

    poll();
    return () => {
      stopped = true;
    };
  }, [runId]);

  const findings = useMemo(() => status?.findings ?? [], [status]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <RunButton onKickoff={kickoff} />
        {runId && (
          <span className="text-xs text-white/60">
            Run ID: <code className="font-mono">{runId}</code>
          </span>
        )}
        {loading && <span className="text-xs text-white/60">Polling status…</span>}
      </div>

      <StatusCard
        summary={status?.summary}
        llmMarkdown={status?.llm_comment_markdown}
        safe={status?.safe_to_merge ?? null}
      />

      <section className="space-y-3">
        <h2 className="text-sm font-semibold tracking-wide">Findings</h2>
        <FindingsTable findings={findings} />
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold tracking-wide">Suggested patches</h2>
        <DiffBlock markdown={status?.llm_comment_markdown} />
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold tracking-wide">Recent runs</h2>
        <HistoryList items={history} />
      </section>
    </div>
  );
}
