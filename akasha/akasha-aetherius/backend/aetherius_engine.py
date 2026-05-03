"""
AetheriusEngine
===============
Core scan-rank-generate loop for Aetherius.

Akasha alignment:
  Axiom 2 — Discoverability : gaps in repos surface as ranked issues.
  Axiom 4 — Augmentation    : generates code to resolve discovered issues.
  Axiom 5 — Traceability    : every action appends to the ledger.
  Axiom 6 — Modularity      : GitHub fetch, LLM generation, and scoring
                               are independently replaceable methods.
  Axiom 8 — Iteration       : continuous scan loop; knowledge compounds.

Debian 13 notes:
  - Circular import from original (engine ↔ backend) is eliminated.
    Engine now owns its own state; the backend imports engine, never vice-versa.
  - requests replaces any Termux-specific HTTP shims.
  - Requires: pip install requests
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

from aetherius_governor import AetheriusGovernor

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared in-process stores (owned here; imported by backend, never reverse)
# ---------------------------------------------------------------------------
issues_store: list[dict] = []
ledger_store: list[str] = []


class AetheriusEngine:
    """
    Scans GitHub issues, ranks them by priority, generates LLM code stubs,
    and applies human feedback adjustments.

    Parameters
    ----------
    token : str
        GitHub personal access token (read: issues, write: file contents).
    repo_list : list[str]
        Repositories to scan in ``owner/repo`` format.
    llm_base_url : str
        Base URL for the LLM generation endpoint.  Defaults to the
        Anthropic messages API; override for local models.
    """

    GITHUB_API = "https://api.github.com"

    def __init__(
        self,
        token: str,
        repo_list: list[str],
        llm_base_url: str = "https://api.anthropic.com/v1/messages",
    ) -> None:
        self.token = token
        self.repo_list = list(repo_list)
        self.llm_base_url = llm_base_url
        self.governor = AetheriusGovernor()
        self._gh_session = self._build_github_session()

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    def _build_github_session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update(
            {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        return s

    # ------------------------------------------------------------------
    # Main loop entry-point
    # ------------------------------------------------------------------

    def scan_and_rank_issues(self) -> None:
        """Fetch all issues, rank by priority, refresh issues_store."""
        ranked: list[dict] = []
        for repo in self.repo_list:
            for issue in self.fetch_github_issues(repo):
                ranked.append(
                    {
                        "repo": repo,
                        "number": issue["number"],
                        "title": issue["title"],
                        "body": issue.get("body") or "",
                        "priority": self.compute_score(issue),
                        "labels": [lb["name"] for lb in issue.get("labels", [])],
                        "code": "",
                    }
                )
        ranked.sort(key=lambda x: x["priority"], reverse=True)
        issues_store.clear()
        issues_store.extend(ranked)
        self._ledger(f"[Aetherius] Scan complete — {len(ranked)} issues ranked.")

    # ------------------------------------------------------------------
    # GitHub helpers
    # ------------------------------------------------------------------

    def fetch_github_issues(self, repo: str) -> list[dict]:
        if not self.governor.allow_github():
            self._ledger(f"[Aetherius] GitHub fetch throttled: {repo}")
            return []
        url = f"{self.GITHUB_API}/repos/{repo}/issues"
        try:
            resp = self._gh_session.get(url, params={"state": "open", "per_page": 50}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            log.error("GitHub fetch failed for %s: %s", repo, exc)
            self._ledger(f"[Aetherius] GitHub fetch error: {repo} — {exc}")
            return []

    def create_or_update_file(
        self, repo: str, path: str, content: str, message: str = ""
    ) -> None:
        """
        Create or update a file in a GitHub repo via the Contents API.
        Retrieves current SHA if file exists so the update succeeds.
        """
        if not self.governor.allow_github():
            self._ledger(f"[Aetherius] File update throttled: {repo}/{path}")
            return

        url = f"{self.GITHUB_API}/repos/{repo}/contents/{path}"
        sha: str | None = None

        # Retrieve existing SHA if file already exists
        try:
            r = self._gh_session.get(url, timeout=10)
            if r.status_code == 200:
                sha = r.json().get("sha")
        except requests.RequestException:
            pass

        import base64
        payload: dict[str, Any] = {
            "message": message or f"aetherius: update {path}",
            "content": base64.b64encode(content.encode()).decode(),
        }
        if sha:
            payload["sha"] = sha

        try:
            resp = self._gh_session.put(url, json=payload, timeout=10)
            resp.raise_for_status()
            self._ledger(f"[Aetherius] File updated: {repo}/{path}")
        except requests.RequestException as exc:
            log.error("File update failed for %s/%s: %s", repo, path, exc)
            self._ledger(f"[Aetherius] File update error: {repo}/{path} — {exc}")

    # ------------------------------------------------------------------
    # LLM code generation
    # ------------------------------------------------------------------

    def generate_llm_code(self, prompt: str) -> str:
        """
        Generate code for a given prompt.
        Currently returns a structured stub; wire to your LLM of choice.
        """
        if not self.governor.allow_llm():
            self._ledger("[Aetherius] LLM generation throttled")
            return "# Throttled — retry after rate window resets"

        # Stub: replace body with real API call as needed
        result = (
            f"# Aetherius generated stub for: {prompt}\n"
            "# TODO: replace with live LLM response\n"
            "pass\n"
        )
        self._ledger(f"[Aetherius] LLM generation: {prompt[:60]}")
        return result

    # ------------------------------------------------------------------
    # Human feedback
    # ------------------------------------------------------------------

    def apply_human_feedback(
        self, repo: str, issue_number: int, adjustment: float
    ) -> None:
        for issue in issues_store:
            if issue["repo"] == repo and issue["number"] == issue_number:
                issue["priority"] += adjustment
                self._ledger(
                    f"[Feedback] {repo}#{issue_number} priority adjusted by {adjustment:+.1f}"
                )
                return
        self._ledger(
            f"[Feedback] WARNING — issue not found: {repo}#{issue_number}"
        )

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def compute_score(self, issue: dict) -> float:
        """
        Heuristic priority score.
        Longer body = more context = likely more critical.
        Bug/critical labels boost the score.
        """
        body = issue.get("body") or ""
        score = float(len(body)) / 10.0
        labels = {lb["name"].lower() for lb in issue.get("labels", [])}
        if labels & {"bug", "critical", "urgent", "high-priority"}:
            score += 50.0
        return round(score, 2)

    # ------------------------------------------------------------------
    # Ledger helper (emit to socket handled by backend)
    # ------------------------------------------------------------------

    def _ledger(self, msg: str) -> None:
        log.info(msg)
        ledger_store.append(msg)
