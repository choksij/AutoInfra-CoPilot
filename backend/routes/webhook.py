from __future__ import annotations

import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request

from ..models import RunRequest
from ..orchestrator import execute_run
from ..services.github_client import GitHubClient
from ..services.webhook_verify import verify_github_signature

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _extract_pr_payload(evt: Dict[str, Any]) -> Optional[RunRequest]:
    action = evt.get("action")
    if action not in {"opened", "synchronize", "ready_for_review", "reopened"}:
        return None

    pull = evt.get("pull_request") or {}
    repo = evt.get("repository") or {}
    full_name = repo.get("full_name") or ""  # "owner/repo"

    pr_number = int(pull.get("number") or 0)
    head = (pull.get("head") or {}).get("sha") or ""
    if not (full_name and pr_number and head):
        return None

    # Always analyze local sample TF for demo; swap for real checkout later.
    return RunRequest(
        repo=full_name,
        pr_number=pr_number,
        commit_sha=head[:12],
        tf_path="backend/sample/tf",
    )


@router.post("")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(default=None, alias="X-GitHub-Event"),
    x_hub_signature_256: Optional[str] = Header(default=None, alias="X-Hub-Signature-256"),
):
    body = await request.body()

    if not verify_github_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event != "pull_request":
        return {"ok": True, "ignored": x_github_event or "unknown"}

    evt = json.loads(body.decode("utf-8"))
    req = _extract_pr_payload(evt)
    if req is None:
        return {"ok": True, "ignored": "unsupported_action_or_payload"}

    status_doc = execute_run(req)

    # Post the final markdown (includes the badge if self-check ran)
    gh = GitHubClient()
    if status_doc.llm_comment_markdown:
        await gh.post_pr_comment(req.repo, req.pr_number, status_doc.llm_comment_markdown)

    return {
        "ok": True,
        "run_id": status_doc.run_id,
        "repo": req.repo,
        "pr_number": req.pr_number,
        "summary": status_doc.summary.model_dump(),
        "safe_to_merge": status_doc.safe_to_merge,
        "self_check": status_doc.self_check,
    }
