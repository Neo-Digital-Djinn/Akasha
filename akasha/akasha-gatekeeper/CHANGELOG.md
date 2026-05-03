# CHANGELOG — akasha-gatekeeper

## v2.1.0 — 2026-05-02 — Akasha Constellation Admission

### Architectural Reconciliation with akasha-bridge

**Removed:**
- `Enforcer` component — all enforcement delegated to `akasha-bridge/executor`
- `AuthorityToken` — replaced with `CapabilityToken` (Bridge-compatible schema)
- `judgments.log` — replaced with `action_ir.log` (Bridge's ActionIR format)
- Hardcoded signing key in source — now via `GATEKEEPER_KEY` env var
- libelfmaster CGO dependency — ELF forensics delegated to `akasha-cipher-lab`

**Changed:**
- Arbiter now emits `ActionIR` (Bridge schema) instead of `Judgment`
- Output log renamed `observations.log` → shared with `akasha-observer` schema
- `action_ir.log` is read-only from Gatekeeper's perspective (Bridge executes)
- Sentinel fallback now reads `/proc/<pid>/comm` directly (Debian procfs)
- journald reader replaces Android logcat integration

**Added:**
- `repo-manifest.yaml` with full 10-axiom alignment
- `CONSTELLATION_ENTRY.md` — architectural split documented
- `CHANGELOG.md` (this file)
- Registered in `akasha-constellation/registry.yaml`

---

## v2.0.0 — 2026-02-14 — Gatekeeper (Termux/Android)

- Three-component: Sentinel, Arbiter, Enforcer
- osquery, Falco, Suricata integration
- libelfmaster CGO binary forensics
- HMAC AuthorityToken, judgment expiry, reversal plans
- Autonomous enforcement (kill, block, quarantine)
