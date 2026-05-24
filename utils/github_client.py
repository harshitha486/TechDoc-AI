"""GitHub REST API client for fetching PR data and file contents."""

from __future__ import annotations

import os
import re
from typing import Any

import requests


class GitHubClient:
    """
    Thin wrapper around the GitHub REST API.

    Args:
        token: GitHub personal access token (or fine-grained token).
               Falls back to GITHUB_TOKEN environment variable.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self._session = requests.Session()
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self._session.headers.update(headers)

    # ------------------------------------------------------------------
    # PR operations
    # ------------------------------------------------------------------

    def get_pr(self, owner: str, repo: str, pr_number: int) -> dict[str, Any]:
        """
        Fetch metadata for a pull request.

        Args:
            owner: Repository owner (user or org).
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            PR metadata dict from the GitHub API.

        Raises:
            RuntimeError: If the API request fails.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        resp = self._get(url)
        return resp

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Fetch the raw unified diff for a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            Raw diff text.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        resp = self._session.get(url, headers={"Accept": "application/vnd.github.diff"})
        self._raise_for_status(resp)
        return resp.text

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """
        List all files changed in a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            List of file change dicts from the GitHub API.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        return self._get(url)  # type: ignore[return-value]

    def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> str:
        """
        Fetch the content of a file from a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.
            ref: Branch, tag, or commit SHA.

        Returns:
            File content as a string.
        """
        import base64

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        data = self._get(url, params={"ref": ref})
        if isinstance(data, dict) and data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return ""

    # ------------------------------------------------------------------
    # URL parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_pr_url(url: str) -> tuple[str, str, int]:
        """
        Extract owner, repo, and PR number from a GitHub PR URL.

        Args:
            url: GitHub PR URL like https://github.com/owner/repo/pull/123.

        Returns:
            Tuple of (owner, repo, pr_number).

        Raises:
            ValueError: If the URL format is not recognised.
        """
        match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
        if not match:
            raise ValueError(f"Cannot parse GitHub PR URL: {url!r}")
        return match.group(1), match.group(2), int(match.group(3))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, url: str, **kwargs: Any) -> Any:
        resp = self._session.get(url, **kwargs)
        self._raise_for_status(resp)
        return resp.json()

    @staticmethod
    def _raise_for_status(resp: requests.Response) -> None:
        if resp.status_code == 401:
            raise RuntimeError("GitHub authentication failed. Check your GITHUB_TOKEN.")
        if resp.status_code == 403:
            raise RuntimeError("GitHub rate limit exceeded or access denied.")
        if resp.status_code == 404:
            raise RuntimeError("GitHub resource not found. Check the URL/PR number.")
        if not resp.ok:
            raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")
