// components/HistoryList.tsx
"use client";

import type { HistoryItem } from "../lib/types";
import { formatDate, formatMoney, formatDuration } from "../lib/format";

export default function HistoryList({ items }: { items: HistoryItem[] }) {
  if (!items?.length) {
    return <div className="text-sm text-white/60">No history yet.</div>;
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-[var(--panel)] overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-white/5 text-white/60 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left p-3">Run ID</th>
            <th className="text-left p-3">Issues</th>
            <th className="text-left p-3">Policy</th>
            <th className="text-left p-3">Cost</th>
            <th className="text-left p-3">Duration</th>
            <th className="text-left p-3">When</th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.run_id} className="border-t border-white/10">
              <td className="p-3 font-mono text-xs truncate max-w-[280px]">{r.run_id}</td>
              <td className="p-3">{r.issues}</td>
              <td className="p-3">{r.fails}</td>
              <td className="p-3">{formatMoney(r.cost)}</td>
              <td className="p-3">{formatDuration(r.duration_ms)}</td>
              <td className="p-3">{formatDate(r.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
