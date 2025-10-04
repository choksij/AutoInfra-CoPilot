# AutoInfra CoPilot – Metrics Naming Guide

## Conventions
- Prefix: `autoinfra.`
- Units in suffix if applicable (`_ms`, `_usd`, `_count`)
- Always tag by:
  - `repo`
  - `pr_number`
  - `result` (safe|unsafe|success|error)

---

## Core Metrics

### Run Metrics
- **`autoinfra.run.duration_ms`**
  - Type: Histogram / Distribution
  - Unit: milliseconds
  - Description: End-to-end pipeline runtime.
  - Tags: repo, pr_number, result
  - Example: `autoinfra.run.duration_ms:1243|ms|#repo:demo,pr:42,result:safe`

- **`autoinfra.run.cost_usd_month`**
  - Type: Gauge
  - Unit: USD/month
  - Description: Estimated monthly cost impact from Terraform plan.
  - Tags: repo, pr_number
  - Example: `autoinfra.run.cost_usd_month:72.5|g|#repo:demo,pr:42`

- **`autoinfra.run.issues_count`**
  - Type: Count
  - Unit: integer
  - Description: Total Checkov + policy findings.
  - Tags: repo, pr_number
  - Example: `autoinfra.run.issues_count:5|c|#repo:demo,pr:42`

### Findings Metrics
- **`autoinfra.findings.checkov`**
  - Type: Count
  - Description: Number of Checkov issues detected.
  - Tags: repo, pr_number, severity
  - Example: `autoinfra.findings.checkov:3|c|#repo:demo,pr:42,severity:HIGH`

- **`autoinfra.findings.policy`**
  - Type: Count
  - Description: Number of policy violations detected.
  - Tags: repo, pr_number, severity
  - Example: `autoinfra.findings.policy:2|c|#repo:demo,pr:42,severity:CRITICAL`

### Outcomes
- **`autoinfra.outcome.safe_to_merge`**
  - Type: Gauge
  - Unit: boolean (1/0)
  - Description: Whether suggested patches reduced violations and passed policy.
  - Tags: repo, pr_number
  - Example: `autoinfra.outcome.safe_to_merge:1|g|#repo:demo,pr:42`

### Errors
- **`autoinfra.error.pipeline`**
  - Type: Count
  - Description: Pipeline execution errors (parsing, scanner crash, patch apply fail).
  - Tags: repo, pr_number, stage
  - Example: `autoinfra.error.pipeline:1|c|#repo:demo,pr:42,stage:patch_apply`
