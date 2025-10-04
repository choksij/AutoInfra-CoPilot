import tempfile
from pathlib import Path

from backend.services.cost_estimator import estimate_monthly_cost


def test_cost_estimator_counts_resources():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "a.tf").write_text(
            '''
            resource "aws_instance" "x" { }
            resource "aws_instance" "y" { }
            resource "aws_lb" "z" { }
            resource "aws_s3_bucket" "b" { }
            ''',
            encoding="utf-8",
        )
        # COST_TABLE: instance=35, lb=18, s3=0 → total = 35*2 + 18 = 88
        cost = estimate_monthly_cost(tmp)
        assert isinstance(cost, float)
        assert cost >= 88.0  # allow >= in case you add more resource types later
