from __future__ import annotations

import json
from typing import Optional

import httpx

from ..config.settings import get_settings


class GitHubClient:
    """
    Minimal GitHub client using a Personal Access Token (PAT).
    - Supports: post PR comment (regular review comment on the PR's issue thread)
    - Optional: create a review with comments, open a fix branch/PR (not used in MVP)
    """

    def __init__(self, token: Optional[str] = None) -> None:
        s = get_settings()
        self.token = (token or s.github_token).strip()
        self.base = "https://api.github.com"
        self.enabled = bool(self.token)

    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "autoinfra-copilot",
        }

    async def post_pr_comment(
        self,
        repo_full_name: str,  # "owner/repo"
        pr_number: int,
        markdown_body: str,
    ) -> bool:
        """
        Posts a single consolidated PR comment to the issue thread (common pattern for bots).
        Returns True on success, False on failure or if disabled.
        """
        if not self.enabled:
            return False

        url = f"{self.base}/repos/{repo_full_name}/issues/{int(pr_number)}/comments"

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.post(url, headers=self._headers(), json={"body": markdown_body})
                return resp.status_code in (200, 201)
            except Exception:
                return False

    async def create_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
    ) -> bool:
        """
        Optional: create a PR review (less necessary for MVP).
        """
        if not self.enabled:
            return False

        url = f"{self.base}/repos/{repo_full_name}/pulls/{int(pr_number)}/reviews"
        payload = {"body": body, "event": event}

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.post(url, headers=self._headers(), json=payload)
                return resp.status_code in (200, 201)
            except Exception:
                return False
