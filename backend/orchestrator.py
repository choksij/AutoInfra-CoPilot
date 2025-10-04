from __future__ import annotations

import time
from datetime import datetime
from typing import List, Optional

from .config.settings import get_settings
from .models import Finding, RunRequest, RunSummary, StatusResponse
from .services.checkov_runner import run_checkov
from .services.policy_engine import run_policy_checks
from .services.cost_estimator import estimate_monthly_cost
from .services.code_context import attach_code_context
from .services.metrics import get_metrics
from .services.composer import compose_comment
from .services.patch_apply import extract_all_diffs, self_check_with_patches


def _summarize(findings: List[Finding], duration_ms: int, cost_usd_month: float) -> RunSummary:
    checkov_issues = sum(1 for f in findings if f.tool == "checkov")
    policy_fails = sum(1 for f in findings if f.tool == "policy")
    return RunSummary(
        checkov_issues=checkov_issues,
        policy_fails=policy_fails,
        cost_usd_month=round(float(cost_usd_month), 2),
        duration_ms=duration_ms,
    )


def _prepend_badge(md: str, safe: Optional[bool]) -> str:
    if safe is None:
        badge = "🟡 **Auto-check:** _not run_"
    elif safe:
        badge = "🟢 **Auto-check:** _safe to merge_"
    else:
        badge = "🔴 **Auto-check:** _needs changes_"
    return f"{badge}\n\n{md}"


def execute_run(req: RunRequest) -> StatusResponse:
    settings = get_settings()
    start = time.perf_counter()

    tf_path = req.tf_path or settings.sample_tf_path

    
    checkov_findings = run_checkov(tf_path)
    policy_findings = run_policy_checks(tf_path)
    findings: List[Finding] = checkov_findings + policy_findings

    # Enrich with small code context (helps human/LLM later)
    findings = attach_code_context(findings, base_dir=tf_path, context_radius=3)

    
    cost = estimate_monthly_cost(tf_path)

    
    comment_md = compose_comment(
        findings=findings,
        cost_estimate=cost,
        repo=req.repo,
        pr_number=req.pr_number,
        commit_sha=req.commit_sha,
    )


    diff_blocks = extract_all_diffs(comment_md or "")
    safe_to_merge: Optional[bool] = None
    self_check_payload = None
    result_tag = "success"

    if diff_blocks:
        try:
            sc = self_check_with_patches(tf_path, diff_blocks)
            safe_to_merge = sc.safe_to_merge
            self_check_payload = {
                "issues_before": sc.issues_before,
                "issues_after": sc.issues_after,
                "policy_before": sc.policy_before,
                "policy_after": sc.policy_after,
            }
            result_tag = "safe" if safe_to_merge else "unsafe"
        except Exception:
            # In case of patch/test error, keep running
            safe_to_merge = None
            result_tag = "success"

    final_md = _prepend_badge(comment_md, safe_to_merge)
    duration_ms = int((time.perf_counter() - start) * 1000)

    status_doc = StatusResponse(
        run_id=f"{datetime.utcnow().isoformat()}",
        status="completed",
        summary=_summarize(findings, duration_ms, cost),
        findings=findings,
        llm_comment_markdown=final_md,
        safe_to_merge=safe_to_merge,
        self_check=self_check_payload,
    )


    try:
        get_metrics().send_run_metrics(status_doc.summary, repo=req.repo, result=result_tag)
    except Exception:
        pass

    return status_doc
