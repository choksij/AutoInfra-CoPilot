import json

from fastapi.testclient import TestClient

from backend.main import app


def test_webhook_ignores_non_pr_event():
    client = TestClient(app)
    resp = client.post(
        "/webhook",
        data=b"{}",
        headers={"X-GitHub-Event": "push"},
    )
    assert resp.status_code == 200
    assert resp.json().get("ignored") == "push"


def test_webhook_accepts_pr_event_but_may_ignore_action():
    client = TestClient(app)
    payload = {
        "action": "opened",
        "pull_request": {"number": 7, "head": {"sha": "cafebabe1234567890"}},
        "repository": {"full_name": "owner/repo"},
    }
    resp = client.post(
        "/webhook",
        data=json.dumps(payload).encode("utf-8"),
        headers={"X-GitHub-Event": "pull_request"},
    )
    # If SAMPLE_TF_PATH exists, route returns ok + summary
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert "pr_number" in data
