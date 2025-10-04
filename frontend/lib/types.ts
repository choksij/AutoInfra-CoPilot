// lib/types.ts

export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Finding {
  tool: "checkov" | "policy" | string;
  rule_id: string;
  severity: Severity | string;
  file: string;
  line: number;
  message: string;
  // Optional: some backends include an inline context block
  context?: string;
}

export interface RunSummary {
  checkov_issues: number;
  policy_fails: number;
  cost_usd_month: number;
  duration_ms: number;
}

export interface SelfCheck {
  issues_before: number;
  issues_after: number;
  policy_before: number;
  policy_after: number;
}

export interface StatusResponse {
  run_id: string;
  status: "running" | "completed" | "failed";
  summary: RunSummary;
  findings: Finding[];
  llm_comment_markdown?: string | null;
  safe_to_merge?: boolean | null;
  self_check?: SelfCheck | null;
  created_at?: string; // ISO timestamp
}

export interface RunRequestBody {
  repo: string;
  pr_number: number;
  commit_sha: string;
  tf_path?: string;
}

export interface HistoryItem {
  run_id: string;
  commit_sha: string;
  issues: number;
  fails: number;
  cost: number;
  duration_ms: number;
  created_at: string; // ISO
}
