
from __future__ import annotations

import os
import json
from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime

import httpx

from ..config.settings import get_settings
from ..models import RunSummary, Finding, HistoryItem

DB_NAME = "autoinfra"


class Storage(Protocol):
    def insert_run(
        self,
        run_id: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        status: str,
        summary: RunSummary,
    ) -> None: ...

    def insert_findings(self, run_id: str, findings: List[Finding]) -> None: ...

    def insert_outcome(
        self,
        run_id: str,
        issues_before: int,
        issues_after: int,
        policy_before: int,
        policy_after: int,
        safe_to_merge: Optional[bool],
    ) -> None: ...

    def insert_patch(
        self,
        run_id: str,
        patch_markdown: str,
        accepted: Optional[bool] = None,
    ) -> None: ...

    def history(self, limit: int = 20) -> List[HistoryItem]: ...

    def get_status(self, run_id: str) -> Dict[str, Any]: ...


class MemoryStorage:
    def __init__(self) -> None:
        
        self._runs: List[Dict[str, Any]] = []
        self._findings: Dict[str, List[Finding]] = {}
        self._outcomes: Dict[str, Dict[str, Any]] = {}
        self._patches: Dict[str, List[Dict[str, Any]]] = {}
        
        self._extras: Dict[str, Dict[str, Any]] = {}

    def insert_run(
        self,
        run_id: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        status: str,
        summary: RunSummary,
    ) -> None:
        row = {
            "run_id": run_id,
            "repo": repo,
            "pr_number": int(pr_number),
            "commit_sha": commit_sha,
            "status": status,
            "duration_ms": int(summary.duration_ms),
            "cost_usd_month": float(summary.cost_usd_month),
            "created_at": datetime.utcnow(),
        }
        self._runs.append(row)

    def insert_findings(self, run_id: str, findings: List[Finding]) -> None:
        self._findings[run_id] = list(findings)

    def insert_outcome(
        self,
        run_id: str,
        issues_before: int,
        issues_after: int,
        policy_before: int,
        policy_after: int,
        safe_to_merge: Optional[bool],
    ) -> None:
        self._outcomes[run_id] = {
            "issues_before": int(issues_before),
            "issues_after": int(issues_after),
            "policy_before": int(policy_before),
            "policy_after": int(policy_after),
            "safe_to_merge": None if safe_to_merge is None else bool(safe_to_merge),
        }

    def insert_patch(
        self,
        run_id: str,
        patch_markdown: str,
        accepted: Optional[bool] = None,
    ) -> None:
        self._patches.setdefault(run_id, []).append(
            {
                "patch_markdown": patch_markdown,
                "accepted": None if accepted is None else bool(accepted),
                "created_at": datetime.utcnow(),
            }
        )

    def history(self, limit: int = 20) -> List[HistoryItem]:
        items: List[HistoryItem] = []
        
        for row in sorted(self._runs, key=lambda r: r["created_at"], reverse=True)[:limit]:
            run_id = row["run_id"]
            findings = self._findings.get(run_id, [])
            issues = sum(1 for f in findings if getattr(f, "tool", "") == "checkov")
            fails = sum(1 for f in findings if getattr(f, "tool", "") == "policy")
            items.append(
                HistoryItem(
                    run_id=run_id,
                    commit_sha=row["commit_sha"],
                    issues=issues,
                    fails=fails,
                    cost=row["cost_usd_month"],
                    duration_ms=row["duration_ms"],
                    created_at=row["created_at"],
                )
            )
        return items

    def get_status(self, run_id: str) -> Dict[str, Any]:
        
        run_row = next((r for r in self._runs if r["run_id"] == run_id), None)
        if not run_row:
            raise KeyError("run_id not found")

        findings = self._findings.get(run_id, [])
        checkov_issues = sum(1 for f in findings if getattr(f, "tool", "") == "checkov")
        policy_fails = sum(1 for f in findings if getattr(f, "tool", "") == "policy")

        summary = {
            "checkov_issues": checkov_issues,
            "policy_fails": policy_fails,
            "cost_usd_month": float(run_row["cost_usd_month"]),
            "duration_ms": int(run_row["duration_ms"]),
        }

        extras = self._extras.get(run_id, {})
        outcome = self._outcomes.get(run_id, {})

        return {
            "run_id": run_id,
            "status": run_row["status"],
            "summary": summary,
            "findings": [f.model_dump() if hasattr(f, "model_dump") else dict(f) for f in findings],
            "llm_comment_markdown": extras.get("llm_comment_markdown"),
            "safe_to_merge": outcome.get("safe_to_merge"),
            "self_check": {
                "issues_before": outcome.get("issues_before", 0),
                "issues_after": outcome.get("issues_after", 0),
                "policy_before": outcome.get("policy_before", 0),
                "policy_after": outcome.get("policy_after", 0),
            }
            if outcome
            else None,
            "created_at": run_row["created_at"].isoformat(),
        }

    
    def set_extras(self, run_id: str, *, llm_comment_markdown: Optional[str] = None, self_check: Optional[Dict[str, Any]] = None) -> None:
        d = self._extras.setdefault(run_id, {})
        if llm_comment_markdown is not None:
            d["llm_comment_markdown"] = llm_comment_markdown
        if self_check is not None:
            d["self_check"] = self_check


class ClickHouseStorage:
    """
    Minimal HTTP-based ClickHouse client for our schema.
    Expects tables created via ops/clickhouse/init.sql.
    """

    def __init__(self, url: str, user: str = "default", password: str = "") -> None:
        # url examples: http://localhost:8123
        self.url = str(url).rstrip("/")  
        self.user = str(user or "")
        self.password = str(password or "")
        self._client = httpx.Client(timeout=10.0)

        
        try:
            self._exec("SELECT 1")
        except Exception:
            pass

    def _auth(self):
        
        return (self.user, self.password) if (self.user or self.password) else None

    def _exec(self, sql: str) -> str:
        
        params = {"database": DB_NAME, "query": sql}
        resp = self._client.post(f"{self.url}/", params=params, auth=self._auth())
        resp.raise_for_status()
        return resp.text

    def _exec_json(self, sql: str) -> Dict[str, Any]:
        
        sql_json = f"{sql} FORMAT JSON"
        params = {"database": DB_NAME, "query": sql_json}
        resp = self._client.post(f"{self.url}/", params=params, auth=self._auth())
        resp.raise_for_status()
        return resp.json()

    def insert_run(
        self,
        run_id: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        status: str,
        summary: RunSummary,
    ) -> None:
        sql = (
            "INSERT INTO autoinfra.runs "
            "(run_id, repo, pr_number, commit_sha, status, duration_ms, cost_usd_month) "
            f"VALUES ({_q(run_id)}, {_q(repo)}, {int(pr_number)}, {_q(commit_sha)}, {_q(status)}, "
            f"{int(summary.duration_ms)}, {float(summary.cost_usd_month)})"
        )
        self._exec(sql)

    def insert_findings(self, run_id: str, findings: List[Finding]) -> None:
        if not findings:
            return
        rows = []
        for f in findings:
            d = f.model_dump() if hasattr(f, "model_dump") else dict(f)
            rows.append(
                {
                    "run_id": run_id,
                    "tool": str(d.get("tool", "")),
                    "rule_id": str(d.get("rule_id", "")),
                    "severity": str(d.get("severity", "")),
                    "file": str(d.get("file", "")),
                    "line": int(d.get("line", 0) or 0),
                    "message": str(d.get("message", "")),
                }
            )
        payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
        sql = "INSERT INTO autoinfra.findings FORMAT JSONEachRow\n" + payload
        self._exec(sql)

    def insert_outcome(
        self,
        run_id: str,
        issues_before: int,
        issues_after: int,
        policy_before: int,
        policy_after: int,
        safe_to_merge: Optional[bool],
    ) -> None:
        safe_val = "NULL" if safe_to_merge is None else ("1" if safe_to_merge else "0")
        sql = (
            "INSERT INTO autoinfra.outcomes "
            "(run_id, issues_before, issues_after, policy_before, policy_after, safe_to_merge) "
            f"VALUES ({_q(run_id)}, {int(issues_before)}, {int(issues_after)}, "
            f"{int(policy_before)}, {int(policy_after)}, {safe_val})"
        )
        self._exec(sql)

    def insert_patch(
        self,
        run_id: str,
        patch_markdown: str,
        accepted: Optional[bool] = None,
    ) -> None:
        acc_val = "NULL" if accepted is None else ("1" if accepted else "0")
        sql = (
            "INSERT INTO autoinfra.patch_library (run_id, patch_markdown, accepted) "
            f"VALUES ({_q(run_id)}, {_q(patch_markdown)}, {acc_val})"
        )
        self._exec(sql)

    def history(self, limit: int = 20) -> List[HistoryItem]:
        sql = (
            "SELECT run_id, commit_sha, issues, fails, cost, duration_ms, created_at "
            f"FROM autoinfra.recent_runs ORDER BY created_at DESC LIMIT {int(limit)}"
        )
        obj = self._exec_json(sql)
        rows = obj.get("data", [])
        out: List[HistoryItem] = []
        for r in rows:
            created = str(r["created_at"])
            
            created_iso = created.replace(" ", "T")
            out.append(
                HistoryItem(
                    run_id=r["run_id"],
                    commit_sha=r["commit_sha"],
                    issues=int(r["issues"]),
                    fails=int(r["fails"]),
                    cost=float(r["cost"]),
                    duration_ms=int(r["duration_ms"]),
                    created_at=datetime.fromisoformat(created_iso),
                )
            )
        return out

    def get_status(self, run_id: str) -> Dict[str, Any]:
        # runs row
        runs_sql = (
            "SELECT run_id, repo, pr_number, commit_sha, status, duration_ms, cost_usd_month, created_at "
            f"FROM autoinfra.runs WHERE run_id = {_q(run_id)}"
        )
        runs_obj = self._exec_json(runs_sql)
        if not runs_obj.get("data"):
            raise KeyError("run_id not found")
        row = runs_obj["data"][0]
        created = str(row["created_at"]).replace(" ", "T")

        
        f_obj = self._exec_json(
            f"SELECT tool, rule_id, severity, file, line, message "
            f"FROM autoinfra.findings WHERE run_id = {_q(run_id)}"
        )
        findings = f_obj.get("data", []) if f_obj else []
        checkov_issues = sum(1 for f in findings if (f.get("tool") or "").lower() == "checkov")
        policy_fails = sum(1 for f in findings if (f.get("tool") or "").lower() == "policy")

        
        o_obj = self._exec_json(
            f"SELECT issues_before, issues_after, policy_before, policy_after, safe_to_merge "
            f"FROM autoinfra.outcomes WHERE run_id = {_q(run_id)} LIMIT 1"
        )
        outcome = (o_obj.get("data") or [None])[0]

        summary = {
            "checkov_issues": int(checkov_issues),
            "policy_fails": int(policy_fails),
            "cost_usd_month": float(row["cost_usd_month"]),
            "duration_ms": int(row["duration_ms"]),
        }

        self_check = None
        safe_to_merge = None
        if outcome:
            self_check = {
                "issues_before": int(outcome["issues_before"]),
                "issues_after": int(outcome["issues_after"]),
                "policy_before": int(outcome["policy_before"]),
                "policy_after": int(outcome["policy_after"]),
            }
            v = outcome.get("safe_to_merge")
            safe_to_merge = None if v is None else bool(v)

        return {
            "run_id": run_id,
            "status": row["status"],
            "summary": summary,
            "findings": findings,
            
            "llm_comment_markdown": None,
            "safe_to_merge": safe_to_merge,
            "self_check": self_check,
            "created_at": created,
        }


def _q(s: str) -> str:
    """Quote a string for SQL VALUES."""
    esc = (s or "").replace("\\", "\\\\").replace("'", "''")
    return f"'{esc}'"


_STORAGE_SINGLETON: Optional[Storage] = None


def get_storage() -> Storage:
    
    global _STORAGE_SINGLETON
    if _STORAGE_SINGLETON is not None:
        return _STORAGE_SINGLETON

    settings = get_settings()

    backend = (
        getattr(settings, "storage_backend", None)
        or os.getenv("STORAGE_BACKEND")
        or ""
    ).lower()

    
    raw_url = getattr(settings, "clickhouse_url", None)
    ch_url = (str(raw_url) if raw_url else os.getenv("CLICKHOUSE_URL") or "")
    ch_user = str(getattr(settings, "clickhouse_user", None) or os.getenv("CLICKHOUSE_USER") or "default")
    ch_pass = str(getattr(settings, "clickhouse_password", None) or os.getenv("CLICKHOUSE_PASSWORD") or "")

    if backend == "clickhouse" or (backend == "" and ch_url):
        try:
            _STORAGE_SINGLETON = ClickHouseStorage(ch_url, ch_user, ch_pass)
            print(f"[storage] Using ClickHouseStorage {ch_url}")
            return _STORAGE_SINGLETON
        except Exception as e:
            print(f"[storage] ClickHouse unavailable ({e}); falling back to MemoryStorage")

    _STORAGE_SINGLETON = MemoryStorage()
    print("[storage] Using MemoryStorage")
    return _STORAGE_SINGLETON
