// components/StatusCard.tsx
"use client";

import { firstLine, formatMoney, formatDuration } from "../lib/format";
import type { StatusSummary } from "../lib/types";

export default function StatusCard(props: {
  summary: StatusSummary | undefined;
  llmMarkdown?: string;
  safe?: boolean | null;
}) {
  const badge = firstLine(props.llmMarkdown || "");
  const s = props.summary;

  const chip = (label: string, value: string) => (
    <div className="rounded-lg bg-white/5 border border-white/10 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wide text-white/50">{label}</div>
      <div className="text-sm font-semibold">{value}</div>
    </div>
  );

  const safeDot =
    props.safe === true
      ? "bg-emerald-500"
      : props.safe === false
      ? "bg-rose-500"
      : "bg-amber-500";

  return (
    <div className="rounded-2xl border border-white/10 bg-[var(--panel)] p-4 md:p-5">
      {/* Badge line */}
      <div className="flex items-center gap-2 text-sm mb-4">
        <span className={`inline-block size-2 rounded-full ${safeDot}`} />
        <span className="font-medium">{badge || "—"}</span>
      </div>

      {/* Chips */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {chip("Checkov issues", String(s?.checkov_issues ?? 0))}
        {chip("Policy fails", String(s?.policy_fails ?? 0))}
        {chip("Est. cost", formatMoney(s?.cost_usd_month))}
        {chip("Duration", formatDuration(s?.duration_ms))}
      </div>
    </div>
  );
}
