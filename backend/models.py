from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional, Dict, Any

from pydantic import BaseModel, Field

Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RunStatus = Literal["running", "completed", "failed"]


class RunRequest(BaseModel):
    repo: str = Field(examples=["org/sample-tf"])
    pr_number: int = Field(examples=[42])
    commit_sha: str = Field(examples=["deadbeef"])
    tf_path: str = Field(default="backend/sample/tf", examples=["backend/sample/tf"])


class Finding(BaseModel):
    tool: Literal["checkov", "policy", "cost", "other"]
    rule_id: str
    severity: Severity
    file: str
    line: int
    message: str


class RunSummary(BaseModel):
    checkov_issues: int = 0
    policy_fails: int = 0
    cost_usd_month: float = 0.0
    duration_ms: int = 0


class StatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    summary: RunSummary
    findings: List[Finding] = []
    llm_comment_markdown: Optional[str] = None
    
    safe_to_merge: Optional[bool] = None
    self_check: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HistoryItem(BaseModel):
    run_id: str
    commit_sha: str
    issues: int
    fails: int
    cost: float
    duration_ms: int
    created_at: datetime
