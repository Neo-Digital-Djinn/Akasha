# Changelog — akasha-aetherius

## v1.0.0 — Akasha Canonicalization (2026-05-02)

### Lineage
Ported and canonicalized from `Aetherius` (Termux Android prototype)
by TheGreatOleander. First canonical Akasha release.

### Changes from Termux prototype

**Architecture**
- Resolved circular import: `aetherius_engine` imported from
  `aetherius_backend` in original. `issues_store` / `ledger_store` now
  owned by `aetherius_engine`; backend imports engine, never vice-versa.
- Consolidated `run_aetherius.py`, `launcher.py`, `mega_deploy.py`
  (all were identical copies) into the background thread inside
  `aetherius_backend.py`.

**Governor (`aetherius_governor.py`)**
- Replaced `list` with `collections.deque` for O(1) sliding-window trim.
- Replaced `time.time()` with `time.monotonic()` (immune to clock jumps).
- Added `status()` method returning serializable dict.
- Added structured logging via `logging` module.

**Engine (`aetherius_engine.py`)**
- Replaced placeholder HTTP stub with real `requests.Session` against
  GitHub REST API v2022-11-28.
- `create_or_update_file` now retrieves existing SHA before PUT
  (required by GitHub Contents API for updates).
- `compute_score` now label-aware: bug/critical/urgent/high-priority +50.
- `apply_human_feedback` now emits WARNING ledger entry when issue not found.
- `generate_llm_code` returns structured stub ready for LLM wiring.
- Token and repo list loaded from environment variables.

**Backend (`aetherius_backend.py`)**
- All secrets (token, secret key) loaded from environment variables.
- Background scan loop moved here with configurable `SCAN_INTERVAL`.
- Added `/api/health` endpoint.
- Input validation added to `/api/feedback` and `/api/update_file`.
- `async_mode="threading"` set explicitly; eventlet optional for prod.

**Frontend**
- Consolidated single-component JSX into full multi-panel dashboard:
  GovernorPanel, IssueCard (with inline code editor + GitHub push),
  LedgerPanel, live connection indicator.
- Migrated from Create React App to Vite for Debian 13 compatibility.
- Added `socket.io-client` for live updates.
- Added `vite.config.js` with proxy for backend API.

**Akasha Canonicalization**
- `repo-manifest.yaml` — full canonical manifest.
- `AKASHA_ALIGNMENT.md` — axiom-by-axiom alignment analysis.
- `CONSTELLATION_ENTRY.md` — constellation registration record.
- `install-debian.sh` — one-script Debian 13 bootstrap.
- `pyproject.toml` — PEP 517 package definition.
- `tests/test_smoke.py` — 9 smoke tests, all passing.
- `.gitignore` — standard Python + Node ignores.
