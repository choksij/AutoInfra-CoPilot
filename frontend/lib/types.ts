
export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Finding {
  tool: "checkov" | "policy" | string;
  rule_id: string;
  severity: Severity | string;
  file: string;
  line: number;
  message: string;
  // optional
  context?: string;
}

export interface StatusSummary {
  checkov_issues: number;
  policy_fails: number;
  cost_usd_month: number;
  duration_ms: number;
}

export interface StatusResponse {
  run_id: string;
  status: "running" | "completed" | "failed";
  summary: StatusSummary;
  findings: Finding[];
  llm_comment_markdown?: string;
  safe_to_merge?: boolean | null;
  self_check?: {
    issues_before: number;
    issues_after: number;
    policy_before: number;
    policy_after: number;
  } | null;
  created_at?: string;
}

export interface HistoryItem {
  run_id: string;
  commit_sha: string;
  issues: number;
  fails: number;
  cost: number;
  duration_ms: number;
  created_at: string;
}

export interface RunKickoff {
  repo: string;
  pr_number: number;
  commit_sha: string;
  tf_path?: string;
}
