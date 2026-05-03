# Akasha Alignment — Aetherius Issue Management Engine

This document records the structural fit analysis for akasha-aetherius's
admission as a canonical Akasha ecosystem member.

---

## Admission Test (per akasha-axioms/SYSTEM_REQUIREMENTS.md)

| Question | Answer |
|---|---|
| Aligns with the axioms? | Yes — see below |
| Has a declared role? | `engine` |
| Declares inputs and outputs? | Yes — in `repo-manifest.yaml` |
| Can be placed in the constellation? | Yes — `layer: management` |
| Can its purpose be explained clearly? | Yes — see below |

**Purpose:** Aetherius is the structured observation and management engine
for GitHub repository health within the Akasha constellation. It scans
declared repositories for open issues, ranks them by priority, generates
code stubs via a pluggable LLM interface, and records every action in an
append-only Ledger. A sliding-window Governor enforces rate limits.
Human feedback adjusts scores in real-time. The live React dashboard
surfaces all state to the steward.

---

## Axiom-by-Axiom Alignment

### Axiom 1 — Coherence
Contradictions (e.g. issue not found during feedback, GitHub API errors)
are treated as diagnostic and surface as explicit Ledger entries with
`WARNING` or `error` tags rather than silently ignored.

### Axiom 2 — Discoverability
Issues ranked by priority constitute a structured signal about where
gaps exist in a codebase. Label-aware scoring (`bug`, `critical`, `urgent`)
amplifies high-signal gaps. The Ledger accumulates a history of
what was discovered and when.

### Axiom 3 — Alignment
This document and `repo-manifest.yaml` constitute the formal alignment
declaration. Aetherius answers: its role (issue management engine),
what it consumes (GitHub issue streams, human feedback, governor commands),
what it produces (ranked lists, code stubs, ledger entries, file updates),
where it lives (layer: management), and how it aligns with each axiom.

### Axiom 4 — Augmentation
Aetherius expands the operator's capacity to observe repository state
at a glance and to generate initial code responses to issues without
manual triage. The pluggable LLM adapter allows progressively more
capable generation as the ecosystem grows.

### Axiom 5 — Traceability
Every governor decision, scan result, feedback adjustment, file update,
and LLM call is appended to `ledger_store` and exposed via `/api/ledger`.
Nothing happens without a Ledger entry. The `/api/health` endpoint
confirms which repos are being observed.

### Axiom 6 — Modularity
The Governor (`aetherius_governor.py`), Engine (`aetherius_engine.py`),
and Backend (`aetherius_backend.py`) are three independent modules.
The GitHub session, the LLM adapter, and the SocketIO transport are each
replaceable without collapsing the others. The frontend is a separate
Node.js project entirely.

### Axiom 7 — Transparency
`/api/governor` exposes live rate-limit state. `/api/ledger` exposes
the full audit trail. `/api/issues` exposes the ranked issue list.
All three are plain JSON. The Governor logs every throttle decision
via Python's `logging` module. No hidden state.

### Axiom 8 — Iteration
The background scan loop runs on a configurable interval (default 60s),
continuously re-ranking issues as repository state changes. Human
feedback folds back into scores in real-time, closing the
observe → rank → feedback → re-rank loop.

### Axiom 9 — Stewardship
File writes to GitHub require an explicit human-initiated POST to
`/api/update_file`. Priority adjustments require a human-initiated POST
to `/api/feedback`. The Governor limits are set by the human via the
Governor Panel. Aetherius observes and proposes; the human approves and
deploys.

### Axiom 10 — Continuity
`ledger_store` accumulates across the session. The `CHANGELOG.md` records
lineage from the Termux prototype. The manifest records source lineage.
The append-only design means no action is silently lost.

---

## Position in the Akasha World Lattice

Using the akasha-world structural vocabulary:

```yaml
id: akasha-aetherius
class: engine
layer: management
phase: continuous
stability: stable
process: scan_rank_generate   # issues → ranked list + code stubs
constraint: governor          # rate limiter enforces safe API usage
```

Aetherius sits at the **management observation boundary** of the Akasha
discovery loop applied to software repositories:

```
github_repos → [ISSUE STREAM] → akasha-aetherius → [RANKED ISSUES + LEDGER]
                                                          ↓
                                                   human steward
                                                   (approve / adjust / push)
```

---

## Constellation Position

```
Layer     : management
Depends on: akasha-axioms, akasha-world, akasha-constellation
Feeds into: (human steward decisions, downstream Akasha event pipeline)
```
