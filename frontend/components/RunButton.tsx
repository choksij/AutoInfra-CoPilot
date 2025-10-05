// components/RunButton.tsx
"use client";

import { useState } from "react";
import { postRun } from "../app/api.config";

export default function RunButton(props: {
  onKickoff: (runId: string) => void;
  repo?: string;
  prNumber?: number;
  commitSha?: string;
  tfPath?: string;
}) {
  const [loading, setLoading] = useState(false);

  async function click() {
    try {
      setLoading(true);
      const resp = await postRun({
        repo: props.repo || "demo/terraform",
        pr_number: props.prNumber ?? 1,
        commit_sha: props.commitSha || "deadbeef",
        tf_path: props.tfPath || "backend/sample/tf",
      });
      props.onKickoff(resp.run_id);
    } catch (e) {
      console.error(e);
      alert("Failed to start run (see console).");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={click}
      disabled={loading}
      className="inline-flex items-center gap-2 rounded-xl bg-emerald-500/90 hover:bg-emerald-500 text-black font-semibold px-4 py-2 disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {loading ? (
        <>
          <span className="inline-block size-2 rounded-full bg-black animate-pulse" />
          Running…
        </>
      ) : (
        <>
          <span className="inline-block size-2 rounded-full bg-black/80" />
          Run sample pipeline
        </>
      )}
    </button>
  );
}
