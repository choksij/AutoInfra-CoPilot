from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Dict


RESOURCE_RE = re.compile(r'resource\s+"(?P<type>[a-zA-Z0-9_]+)"\s+"[^"]*"\s*{', re.MULTILINE)



COST_TABLE: Dict[str, float] = {
    "aws_instance": 35.0,
    "aws_lb": 18.0,
    "aws_db_instance": 75.0,
    "aws_s3_bucket": 0.0,
    "aws_security_group": 0.0,
}


def _scan_tf_for_resources(base_dir: str) -> Counter:
    c = Counter()
    for p in Path(base_dir).rglob("*.tf"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in RESOURCE_RE.finditer(text):
            rtype = m.group("type")
            c[rtype] += 1
    return c


def estimate_monthly_cost(base_dir: str) -> float:
    
    counts = _scan_tf_for_resources(base_dir)
    total = 0.0
    for rtype, n in counts.items():
        unit = COST_TABLE.get(rtype, 0.0)
        total += unit * float(n)
    return round(total, 2)
