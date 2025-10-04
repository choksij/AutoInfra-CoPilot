# AutoInfra CoPilot – Datadog Dashboard Notes

## Dashboard Structure

### 1. Overview Dashboard
Purpose: quick glance at system health and PR safety.
Widgets:
- Timeseries: `autoinfra.run.duration_ms` (p95 latency per repo)
- Timeseries: `autoinfra.run.issues_count` (stacked by severity)
- Query Value: % safe merges (`avg:autoinfra.outcome.safe_to_merge` by repo)
- Heatmap: duration vs cost

### 2. Findings Breakdown
Widgets:
- Top 10 repos with highest findings (`autoinfra.findings.checkov + autoinfra.findings.policy`)
- Pie chart: Severity distribution
- Table: Latest 20 PRs with run_id, issues, fails, safe_to_merge

### 3. Cost Monitoring
Widgets:
- Timeseries: `autoinfra.run.cost_usd_month` (over time, per repo)
- Monitor: Alert if cost delta > 30% between PRs

### 4. Errors & Reliability
Widgets:
- Count: `autoinfra.error.pipeline` grouped by stage
- Monitor: Alert if >5 errors in 10 minutes
- Logstream (optional if logs integrated): show error traces

---

## Suggested Monitors
1. **Pipeline Duration**
   - Query: `p95:autoinfra.run.duration_ms > 30000`
   - Alert: pipeline taking >30s
2. **Safe Merge Ratio**
   - Query: `avg:autoinfra.outcome.safe_to_merge < 0.5 by repo`
   - Alert: less than half of runs are safe
3. **High Severity Findings**
   - Query: `sum:autoinfra.findings.policy{severity:CRITICAL} > 0`
   - Alert: any critical policy violations
