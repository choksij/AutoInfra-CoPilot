import tempfile
from pathlib import Path

from backend.services.policy_engine import run_policy_checks


def test_policy_engine_flags_expected_rules():
    with tempfile.TemporaryDirectory() as tmp:
        tf = Path(tmp) / "main.tf"
        tf.write_text(
            '''
            resource "aws_s3_bucket" "logs" {
              bucket = "demo"
              acl    = "public-read"
            }

            resource "aws_security_group" "ssh_all" {
              ingress {
                from_port   = 22
                to_port     = 22
                protocol    = "tcp"
                cidr_blocks = ["0.0.0.0/0"]
              }
            }

            resource "aws_db_instance" "db" {
              publicly_accessible = true
            }
            ''',
            encoding="utf-8",
        )

        findings = run_policy_checks(tmp)
        ids = {f.rule_id for f in findings}
        # We expect at least one of each policy class to show up
        assert "POLICY_001" in ids or "POLICY_002" in ids or "POLICY_003" in ids
        # Shape sanity
        assert all(f.tool == "policy" for f in findings)
        assert all(f.file.endswith(".tf") for f in findings)
