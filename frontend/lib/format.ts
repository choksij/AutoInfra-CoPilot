
import { SEVERITY_COLORS } from "./constants";

export function formatMoney(n: number | undefined | null) {
  const v = Number(n ?? 0);
  return `$${v.toFixed(2)}/mo`;
}

export function formatDuration(ms: number | undefined | null) {
  const v = Number(ms ?? 0);
  if (v < 1000) return `${v} ms`;
  return `${(v / 1000).toFixed(1)} s`;
}

export function formatDate(iso?: string) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

export function severityPillClass(sev: string) {
  return `px-2 py-0.5 rounded-md text-[11px] font-medium ${SEVERITY_COLORS[sev] ?? "bg-white/10 text-white/70"}`;
}


export function firstLine(md?: string) {
  if (!md) return "";
  const idx = md.indexOf("\n");
  return idx === -1 ? md.trim() : md.slice(0, idx).trim();
}


export function extractDiffBlocks(md?: string): string[] {
  if (!md) return [];
  const re = /```diff\s+([\s\S]*?)```/g;
  const blocks: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(md)) !== null) {
    blocks.push("```diff\n" + m[1].trim() + "\n```");
  }
  return blocks;
}
