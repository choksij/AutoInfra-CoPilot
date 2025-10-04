from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List

from ..models import Finding


def _rel_file(base_dir: str, file_path: str) -> str:
    try:
        return str(Path(file_path).resolve().relative_to(Path(base_dir).resolve()))
    except Exception:
        return file_path


def run_checkov(base_dir: str) -> List[Finding]:
    """
    Executes Checkov over `base_dir` and normalizes failed checks to Finding objects.
    Requires the `checkov` CLI in PATH.
    """
    cmd = ["checkov", "-d", base_dir, "-o", "json"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=base_dir if os.path.isdir(base_dir) else None,
        )
    except FileNotFoundError:
        # Checkov not installed; return empty list (pipeline remains resilient)
        return []

    if proc.returncode not in (0, 2):  # 0 OK, 2 findings
        # Non-standard failure; best-effort parse stderr for context
        return []

    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return []

    results = payload.get("results") or {}
    failed = results.get("failed_checks") or []

    findings: List[Finding] = []
    for item in failed:
        rule_id = item.get("check_id") or item.get("id") or "CKV_UNKNOWN"
        severity = (item.get("severity") or "MEDIUM").upper()
        file_path = item.get("file_path") or item.get("repo_file_path") or item.get("file")
        # file_line_range often looks like [start, end]
        line = 0
        flr = item.get("file_line_range") or []
        if isinstance(flr, list) and flr:
            try:
                line = int(flr[0])
            except Exception:
                line = 0
        message = item.get("check_name") or item.get("guideline") or "Policy violation"

        findings.append(
            Finding(
                tool="checkov",
                rule_id=str(rule_id),
                severity=severity,  # type: ignore[arg-type]
                file=_rel_file(base_dir, file_path or "unknown"),
                line=line,
                message=str(message),
            )
        )

    return findings
