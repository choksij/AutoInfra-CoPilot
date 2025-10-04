from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from ..models import Finding


def _read_file_lines(root: Path, rel_path: str) -> List[str]:
    try:
        text = (root / rel_path).read_text(encoding="utf-8", errors="ignore")
        return text.splitlines()
    except Exception:
        return []


def attach_code_context(findings: List[Finding], base_dir: str, context_radius: int = 3) -> List[Finding]:

    root = Path(base_dir)
    cache: Dict[str, List[str]] = {}

    enriched: List[Finding] = []
    for f in findings:
        lines = cache.get(f.file)
        if lines is None:
            lines = _read_file_lines(root, f.file)
            cache[f.file] = lines

        if 0 < f.line <= len(lines):
            start = max(0, f.line - 1 - context_radius)
            end = min(len(lines), f.line - 1 + context_radius + 1)
            snippet = "\n".join(lines[start:end])
            msg = f"{f.message}  [context lines {start+1}-{end}]\n{snippet}"
        else:
            msg = f.message

        enriched.append(
            Finding(
                tool=f.tool,
                rule_id=f.rule_id,
                severity=f.severity,  # type: ignore[arg-type]
                file=f.file,
                line=f.line,
                message=msg,
            )
        )

    return enriched
