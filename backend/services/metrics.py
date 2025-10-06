from __future__ import annotations

import time
from typing import Dict, List, Optional

try:
    from datadog import initialize, api  # type: ignore
except Exception:
    initialize = None
    api = None

from ..config.settings import get_settings
from ..models import RunSummary


class Metrics:
    

    def __init__(self) -> None:
        self.enabled = False
        self.site_api_host: Optional[str] = None

        settings = get_settings()
        if not settings.dd_api_key or initialize is None or api is None:
            self.enabled = False
            return

        site = (settings.dd_site or "datadoghq.com").strip()
        api_host = site if site.startswith("http") else f"https://api.{site}"

        initialize(api_key=settings.dd_api_key, api_host=api_host)
        self.enabled = True
        self.site_api_host = api_host

    def send_run_metrics(
        self,
        summary: RunSummary,
        repo: str,
        result: str = "success",
        extra_tags: Optional[List[str]] = None,
    ) -> None:
        if not self.enabled:
            return
        try:
            ts = int(time.time())
            tags = [f"repo:{repo}", f"result:{result}"]
            if extra_tags:
                tags.extend(extra_tags)

            payload: List[Dict] = [
                {"metric": "autoinfra.run.duration_ms", "points": [(ts, float(summary.duration_ms))], "type": "gauge", "tags": tags},
                {"metric": "autoinfra.checkov.issues", "points": [(ts, float(summary.checkov_issues))], "type": "gauge", "tags": tags},
                {"metric": "autoinfra.policy.fails", "points": [(ts, float(summary.policy_fails))], "type": "gauge", "tags": tags},
                {"metric": "autoinfra.cost.estimate_usd", "points": [(ts, float(summary.cost_usd_month))], "type": "gauge", "tags": tags},
            ]
            api.Metric.send(payload)
        except Exception:
            
            return


_metrics = Metrics()


def get_metrics() -> Metrics:
    return _metrics
