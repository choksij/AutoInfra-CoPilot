from backend.models import RunRequest
from backend.orchestrator import execute_run


def test_execute_run_returns_completed_status():
    req = RunRequest(
        repo="demo/terraform",
        pr_number=1,
        commit_sha="deadbeef",
        tf_path="backend/sample/tf",
    )
    status = execute_run(req)
    assert status.status in ("completed", "failed")
    assert status.summary.duration_ms >= 0
    
    assert isinstance(status.findings, list)
