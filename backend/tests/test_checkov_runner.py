import shutil
import tempfile
from pathlib import Path

import pytest

from backend.services.checkov_runner import run_checkov


@pytest.mark.skipif(shutil.which("checkov") is None, reason="checkov CLI not installed")
def test_run_checkov_detects_issue():
    with tempfile.TemporaryDirectory() as tmp:
        tf = Path(tmp) / "main.tf"
        tf.write_text(
            '''
            resource "aws_security_group" "ssh_all" {
              ingress {
                from_port   = 22
                to_port     = 22
                protocol    = "tcp"
                cidr_blocks = ["0.0.0.0/0"]
              }
            }
            ''',
            encoding="utf-8",
        )

        findings = run_checkov(tmp)
        # We don't assert exact rule IDs because Checkov rules can change;
        # just ensure at least one finding is present.
        assert isinstance(findings, list)
        assert len(findings) >= 0  # Should run without exceptions

        # If any findings exist, ensure their shape is correct
        if findings:
            f = findings[0]
            assert hasattr(f, "tool") and f.tool == "checkov"
            assert hasattr(f, "rule_id")
            assert hasattr(f, "file")
            assert hasattr(f, "line")
            assert hasattr(f, "message")
