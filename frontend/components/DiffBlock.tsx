// components/DiffBlock.tsx
"use client";

import { extractDiffBlocks } from "../lib/format";

export default function DiffBlock({ markdown }: { markdown?: string }) {
  const blocks = extractDiffBlocks(markdown);
  if (!blocks.length) {
    return (
      <div className="text-sm text-white/60">No suggested patches.</div>
    );
  }

  return (
    <div className="space-y-3">
      {blocks.map((b, i) => (
        <CodeCard key={i} code={b} />
      ))}
    </div>
  );
}

function CodeCard({ code }: { code: string }) {
  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
    } catch {
      // ignore
    }
  }
  return (
    <div className="rounded-2xl border border-white/10 bg-[var(--panel)] p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs uppercase tracking-wide text-white/50">Suggested patch</div>
        <button
          onClick={copy}
          className="text-xs rounded-md border border-white/10 px-2 py-1 hover:bg-white/5"
        >
          Copy
        </button>
      </div>
      <pre className="overflow-x-auto text-[13px] leading-5">
        <code className="block whitespace-pre text-white/90">{code}</code>
      </pre>
    </div>
  );
}
