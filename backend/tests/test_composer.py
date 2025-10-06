import json
from pathlib import Path

import pytest


try:
    from backend.services.composer import compose_comment  
    HAS_COMPOSER = True
except Exception:
    HAS_COMPOSER = False


@pytest.mark.skipif(not HAS_COMPOSER, reason="composer not implemented yet")
def test_compose_comment_with_golden_findings():
    golden = Path("backend/sample/findings_golden.json")
    assert golden.exists(), "golden findings file missing"
    findings = json.loads(golden.read_text(encoding="utf-8"))

    
    md = compose_comment(
        findings=findings,
        cost_estimate=128.0,
        repo="demo/terraform",
        pr_number=1,
        commit_sha="deadbeef",
    )
    assert isinstance(md, str)
    
    assert "AutoInfra" in md or "Policy" in md or "S3" in md
