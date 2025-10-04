from __future__ import annotations
from typing import Any, Iterable, List, Tuple


def _norm_findings(findings: Iterable[Any]) -> List[dict]:
    
    out: List[dict] = []
    for f in findings:
        if hasattr(f, "model_dump"):
            out.append(f.model_dump())
        elif isinstance(f, dict):
            out.append(f)
        else:
            out.append(
                {
                    "tool": getattr(f, "tool", "other"),
                    "rule_id": getattr(f, "rule_id", "UNKNOWN"),
                    "severity": str(getattr(f, "severity", "MEDIUM")).upper(),
                    "file": getattr(f, "file", "unknown"),
                    "line": int(getattr(f, "line", 0) or 0),
                    "message": str(getattr(f, "message", "")),
                }
            )
    return out


def _choose_example_diffs(fs: List[dict]) -> List[Tuple[str, str]]:
    
    diffs: List[Tuple[str, str]] = []

    # RDS publicly_accessible
    if any(f.get("rule_id") == "POLICY_003" or "publicly_accessible = true" in f.get("message", "") for f in fs):
        diffs.append((
            "RDS: disable public access",
            "```diff\n- publicly_accessible = true\n+ publicly_accessible = false\n```"
        ))

    # S3 public ACL / missing protections
    if any(f.get("rule_id") == "POLICY_002" or "public ACL" in f.get("message", "") for f in fs):
        diffs.append((
            "S3: harden bucket",
            "```diff\n- acl = \"public-read\"\n+ acl = \"private\"\n+ block_public_acls = true\n+ versioning { enabled = true }\n```"
        ))

    # SG open SSH
    if any(f.get("rule_id") == "POLICY_001" or "0.0.0.0/0" in f.get("message", "") for f in fs):
        diffs.append((
            "Security Group: restrict SSH",
            "```diff\n- cidr_blocks = [\"0.0.0.0/0\"]\n+ # TODO: replace with your office/VPN CIDR\n+ cidr_blocks = [\"10.0.0.0/16\"]\n```"
        ))

    return diffs[:3]


def compose_comment(
    *,
    findings: Iterable[Any],
    cost_estimate: float,
    repo: str,
    pr_number: int,
    commit_sha: str,
) -> str:
    
    fs = _norm_findings(findings)

    # Counts
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in fs:
        sev = str(f.get("severity", "MEDIUM")).upper()
        if sev not in sev_counts:
            sev = "MEDIUM"
        sev_counts[sev] += 1

    total = len(fs)

    # Short bullets for top items (first 5)
    bullets_lines: List[str] = []
    for f in fs[:5]:
        first_line = f.get("message", "").splitlines()[0]
        bullets_lines.append(f"- **{f.get('severity','')}** `{f.get('file','')}`:{f.get('line',0)} — {first_line}")
    bullets_text = "\n".join(bullets_lines) if bullets_lines else "_No issues found._"

    # Example diffs (for demo only)
    diffs = _choose_example_diffs(fs)
    diffs_md = "\n\n".join(f"**{title}**\n{block}" for title, block in diffs) if diffs else ""
    suggested_section = "### Suggested patches\n" + diffs_md if diffs_md else ""

    md = (
        f"## AutoInfra CoPilot — PR Review\n\n"
        f"**Repo:** `{repo}` • **PR** #{pr_number} • **Commit:** `{commit_sha}`\n\n"
        f"**Findings:** {total}  —  **CRITICAL:** {sev_counts['CRITICAL']} • **HIGH:** {sev_counts['HIGH']} "
        f"• **MEDIUM:** {sev_counts['MEDIUM']} • **LOW:** {sev_counts['LOW']}\n"
        f"**Estimated cost impact:** ${cost_estimate:.2f}/mo\n\n"
        f"### Top issues\n"
        f"{bullets_text}\n\n"
        f"{suggested_section}\n"
    )
    return md
