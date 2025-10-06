from __future__ import annotations

import io
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from ..models import Finding
from .checkov_runner import run_checkov
from .policy_engine import run_policy_checks



DIFF_FENCE_RE = re.compile(r"```diff\s+(?P<body>.+?)```", re.DOTALL)


def extract_first_diff(markdown: str) -> Optional[str]:
    
    m = DIFF_FENCE_RE.search(markdown or "")
    if not m:
        return None
    return "```diff\n" + m.group("body").strip("\n") + "\n```"


def extract_all_diffs(markdown: str) -> List[str]:
    
    return ["```diff\n" + m.strip("\n") + "\n```" for m in DIFF_FENCE_RE.findall(markdown or "")]


@dataclass
class SelfCheckResult:
    issues_before: int
    issues_after: int
    policy_before: int
    policy_after: int
    safe_to_merge: bool


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _apply_unified_diff(root: Path, patch_text: str) -> Tuple[bool, str]:
    
    try:
        start = patch_text.find("```diff")
        if start == -1:
            return False, "No diff fence found"
        end = patch_text.find("```", start + 7)
        if end == -1:
            return False, "Unclosed diff fence"
        diff_body = patch_text[start + len("```diff"): end].strip("\n")

        minus_lines: List[str] = []
        plus_lines: List[str] = []
        for raw in io.StringIO(diff_body):
            line = raw.rstrip("\n")
            if line.startswith("+++ ") or line.startswith("--- "):
                continue
            if line.startswith("+"):
                plus_lines.append(line[1:])
            elif line.startswith("-"):
                minus_lines.append(line[1:])

        candidates = list(root.rglob("*.tf"))
        for tf in candidates:
            text_lines = tf.read_text(encoding="utf-8", errors="ignore").splitlines()

            
            norm = lambda s: "".join(s.split())

            
            if minus_lines and not all(any(norm(m) in norm(ln) for ln in text_lines) for m in minus_lines):
                continue

            new_text: List[str] = []
            consumed_minus = set()
            i = 0
            while i < len(text_lines):
                ln = text_lines[i]
                replaced = False
                for m in minus_lines:
                    if m and (norm(m) in norm(ln)) and (m not in consumed_minus):
                        idx = minus_lines.index(m)
                        repl = plus_lines[idx] if idx < len(plus_lines) else None
                        if repl is not None:
                            new_text.append(repl)
                        consumed_minus.add(m)
                        replaced = True
                        break
                if not replaced:
                    new_text.append(ln)
                i += 1

            
            if len(plus_lines) > len(minus_lines):
                extras = plus_lines[len(minus_lines):]
                new_text.extend(extras)

            _write_text(tf, "\n".join(new_text) + "\n")
            return True, f"Patched {tf.name}"

        return False, "No target file matched for patch"
    except Exception as e:
        return False, f"Patch error: {e}"


def self_check_with_patch(sample_tf_dir: str, patch_markdown: str) -> SelfCheckResult:
    
    src = Path(sample_tf_dir).resolve()
    with tempfile.TemporaryDirectory() as tmpdir:
        dst = Path(tmpdir) / "tf"
        shutil.copytree(src, dst)

        before_findings: List[Finding] = run_checkov(str(dst)) + run_policy_checks(str(dst))
        issues_before = sum(1 for f in before_findings if f.tool == "checkov")
        policy_before = sum(1 for f in before_findings if f.tool == "policy")

        ok, _ = _apply_unified_diff(dst, patch_markdown)
        if not ok:
            return SelfCheckResult(
                issues_before=issues_before,
                issues_after=issues_before,
                policy_before=policy_before,
                policy_after=policy_before,
                safe_to_merge=False,
            )

        after_findings: List[Finding] = run_checkov(str(dst)) + run_policy_checks(str(dst))
        issues_after = sum(1 for f in after_findings if f.tool == "checkov")
        policy_after = sum(1 for f in after_findings if f.tool == "policy")

        reduced = (issues_after + policy_after) <= (issues_before + policy_before)
        safe = reduced and policy_after == 0

        return SelfCheckResult(
            issues_before=issues_before,
            issues_after=issues_after,
            policy_before=policy_before,
            policy_after=policy_after,
            safe_to_merge=safe,
        )


def self_check_with_patches(sample_tf_dir: str, patch_markdowns: List[str]) -> SelfCheckResult:
    
    src = Path(sample_tf_dir).resolve()
    with tempfile.TemporaryDirectory() as tmpdir:
        dst = Path(tmpdir) / "tf"
        shutil.copytree(src, dst)

        before_findings: List[Finding] = run_checkov(str(dst)) + run_policy_checks(str(dst))
        issues_before = sum(1 for f in before_findings if f.tool == "checkov")
        policy_before = sum(1 for f in before_findings if f.tool == "policy")

        any_applied = False
        for patch_md in patch_markdowns:
            ok, _ = _apply_unified_diff(dst, patch_md)
            any_applied = any_applied or ok

        if not any_applied:
            return SelfCheckResult(
                issues_before=issues_before,
                issues_after=issues_before,
                policy_before=policy_before,
                policy_after=policy_before,
                safe_to_merge=False,
            )

        after_findings: List[Finding] = run_checkov(str(dst)) + run_policy_checks(str(dst))
        issues_after = sum(1 for f in after_findings if f.tool == "checkov")
        policy_after = sum(1 for f in after_findings if f.tool == "policy")

        reduced = (issues_after + policy_after) <= (issues_before + policy_before)
        safe = reduced and policy_after == 0

        return SelfCheckResult(
            issues_before=issues_before,
            issues_after=issues_after,
            policy_before=policy_before,
            policy_after=policy_after,
            safe_to_merge=safe,
        )
