"""
AetheriusGovernor
=================
Rate-limiter / throttle system for GitHub API and LLM calls.

Akasha alignment:
  Axiom 5 — Traceability : every allow/deny decision is logged.
  Axiom 7 — Transparency : limits are readable at runtime via the API.
  Axiom 9 — Stewardship  : humans set limits; the governor enforces them.

Debian 13 notes:
  - Uses only stdlib (threading, time, collections).  No Termux shims needed.
"""

import time
import logging
from collections import deque
from threading import Lock

log = logging.getLogger(__name__)


class AetheriusGovernor:
    """
    Sliding-window rate limiter.

    Parameters
    ----------
    github_limit_per_min : int
        Max GitHub API calls per rolling 60-second window.
    llm_limit_per_min : int
        Max LLM calls per rolling 60-second window.
    """

    def __init__(
        self,
        github_limit_per_min: int = 60,
        llm_limit_per_min: int = 20,
    ) -> None:
        self.github_limit: int = github_limit_per_min
        self.llm_limit: int = llm_limit_per_min

        # deque is cheaper than list for sliding-window trimming
        self.github_timestamps: deque = deque()
        self.llm_timestamps: deque = deque()
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _trim(self, timestamps: deque, window: float = 60.0) -> None:
        """Remove timestamps older than *window* seconds."""
        cutoff = time.monotonic() - window
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()

    def _check(self, timestamps: deque, limit: int, label: str) -> bool:
        """Return True and record timestamp if under limit, else False."""
        self._trim(timestamps)
        if len(timestamps) >= limit:
            log.warning("[AetheriusGovernor] %s throttled (%d/%d used)", label, len(timestamps), limit)
            return False
        timestamps.append(time.monotonic())
        return True

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def allow_github(self) -> bool:
        with self._lock:
            return self._check(self.github_timestamps, self.github_limit, "GitHub")

    def allow_llm(self) -> bool:
        with self._lock:
            return self._check(self.llm_timestamps, self.llm_limit, "LLM")

    def status(self) -> dict:
        """Return current usage snapshot (safe to serialize to JSON)."""
        with self._lock:
            self._trim(self.github_timestamps)
            self._trim(self.llm_timestamps)
            return {
                "github_limit": self.github_limit,
                "github_used": len(self.github_timestamps),
                "llm_limit": self.llm_limit,
                "llm_used": len(self.llm_timestamps),
            }
