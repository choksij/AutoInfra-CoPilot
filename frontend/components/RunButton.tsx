// components/RunButton.tsx
"use client";

import { useState } from "react";
import { runPipeline } from "../app/api.config";

type Props = {
  onKickoff: (runId: string) => void;
};

const DEFAULT_PAYLOAD = {
  repo: "demo/terraform",
  pr_number: 2,
  commit_sha: "cafebabe",
  tf_path: "backend/sample/tf",
};

export default function RunButton({ onKickoff }: Props) {
  const [busy, setBusy] = useState(false);

  const onClick = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const res = await runPipeline(DEFAULT_PAYLOAD);
      if (!res?.run_id) {
        throw new Error("Response missing run_id");
      }
      onKickoff(res.run_id);
    } catch (e: any) {
      console.error("Failed to start run:", e);
      alert(`Failed to start run: ${e?.message || e}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 px-3 py-2 text-sm font-medium"
      title="Run sample pipeline"
    >
      {busy ? "Running…" : "Run sample pipeline"}
    </button>
  );
}
