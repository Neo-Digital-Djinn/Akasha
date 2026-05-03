# Constellation Entry — akasha-aetherius

## Registration

| Field | Value |
|---|---|
| Name | akasha-aetherius |
| Role | engine |
| Layer | management |
| Status | canonical |
| Maturity | stable |
| Lineage | Aetherius-Termux → akasha-aetherius |

## Purpose

Aetherius is the structured observation and management engine for GitHub
repository health within the Akasha constellation. It scans repositories,
ranks issues by priority, generates code stubs, and records every action
in an append-only Ledger. A sliding-window Governor enforces safe API
rate limits. Human stewards approve all writes and priority adjustments.

## Interfaces

**Consumes:**
- GitHub issue streams (via GitHub REST API)
- Human priority adjustments (POST /api/feedback)
- LLM code generation prompts (internal)
- Governor configuration commands (POST /api/governor)

**Produces:**
- Ranked issue lists (GET /api/issues)
- Ledger audit entries (GET /api/ledger)
- GitHub file updates (POST /api/update_file)
- Live SocketIO update events (WebSocket)
- Governor status snapshots (GET /api/governor)

## Dependencies

- akasha-axioms (constitutional governance)
- akasha-world (knowledge layer)
- akasha-constellation (ecosystem registry)

## Structural Position

```
akasha-axioms
    │
akasha-world
    │
akasha-aetherius ── GitHub API ── repositories
    │
    └── live dashboard (React/Vite, port 3000)
    └── REST + SocketIO API (Flask, port 5000)
    └── Ledger (in-process append-only store)
```

## Admission Notes

Ported from a Termux Android prototype to Debian 13.
Circular import resolved (engine ↔ backend).
GitHub API session hardened (SHA-aware file updates, error handling).
Governor refactored to use `deque` + `time.monotonic`.
Secrets moved to environment variables.
9/9 smoke tests passing.
All Akasha canonical documents present.
