
"use client";

import type { Finding } from "../lib/types";
import { severityPillClass } from "../lib/format";

export default function FindingsTable({ findings }: { findings: Finding[] }) {
  if (!findings?.length) {
    return (
      <div className="text-sm text-white/60">No findings for this run.</div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-[var(--panel)] overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-white/5 text-white/60 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left p-3">Severity</th>
            <th className="text-left p-3">Rule</th>
            <th className="text-left p-3">Location</th>
            <th className="text-left p-3">Message</th>
            <th className="text-left p-3">Tool</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f, i) => {
            const firstLine = (f.message || "").split(/\r?\n/)[0] ?? "";
            return (
              <tr key={i} className="border-t border-white/10">
                <td className="p-3">
                  <span className={severityPillClass(String(f.severity).toUpperCase())}>
                    {String(f.severity).toUpperCase()}
                  </span>
                </td>
                <td className="p-3 font-mono text-xs">{f.rule_id}</td>
                <td className="p-3">
                  <span className="font-mono text-xs">{f.file}</span>
                  <span className="text-white/50">:{f.line}</span>
                </td>
                <td className="p-3">{firstLine}</td>
                <td className="p-3 text-white/70">{f.tool}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
